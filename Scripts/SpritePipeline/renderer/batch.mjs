// One private Chrome per worker. Requests arrive as JSON lines on stdin.
import {spawn} from 'node:child_process';
import {readFile, writeFile} from 'node:fs/promises';
import readline from 'node:readline';
import path from 'node:path';
import {prepareRendererProfile} from './profile.mjs';

const [chrome, url, profile] = process.argv.slice(2);
await prepareRendererProfile(profile);
const child = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-extensions',
  '--hide-scrollbars', '--mute-audio', '--use-angle=swiftshader',
  '--enable-unsafe-swiftshader', '--remote-debugging-port=0',
  `--user-data-dir=${profile}`, 'about:blank'], {stdio:'ignore', windowsHide:true});
let socket;
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const exited = new Promise(resolve => { child.once('exit', resolve); child.once('error', resolve); });
try {
  let port;
  for (let attempt=0; attempt<100; attempt++) {
    try { port=(await readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n'); break; }
    catch { await delay(100); }
  }
  if (!port) throw new Error('Dedicated renderer did not start');
  socket = new WebSocket(`ws://127.0.0.1:${port[0]}${port[1]}`);
  await new Promise((resolve,reject) => {
    const timer=setTimeout(() => reject(new Error('Renderer connection timeout')),5000);
    socket.onopen=() => {clearTimeout(timer);resolve();};
    socket.onerror=error => {clearTimeout(timer);reject(error);};
    socket.onclose=() => {clearTimeout(timer);reject(new Error('Renderer disconnected'));};
  });
  let nextId=0;
  const pending=new Map();
  socket.onmessage=event => {
    const response=JSON.parse(event.data);
    const waiter=pending.get(response.id);
    if (!waiter) return;
    pending.delete(response.id);clearTimeout(waiter.timer);
    if(response.error) waiter.reject(new Error(JSON.stringify(response.error)));
    else waiter.resolve(response.result);
  };
  socket.onclose=() => {
    for(const waiter of pending.values()) {clearTimeout(waiter.timer);waiter.reject(new Error('Renderer disconnected'));}
    pending.clear();
  };
  const send=(method,params={},sessionId) => new Promise((resolve,reject) => {
    const id=++nextId;
    const timer=setTimeout(() => {pending.delete(id);reject(new Error(`CDP timeout: ${method}`));},45000);
    pending.set(id,{resolve,reject,timer});
    socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
  });
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const page=(method,params) => send(method,params,sessionId);
  await page('Page.enable');
  await page('Emulation.setDeviceMetricsOverride',{width:256,height:256,deviceScaleFactor:1,mobile:false});
  await page('Emulation.setDefaultBackgroundColorOverride',{color:{r:0,g:0,b:0,a:0}});
  await page('Page.navigate',{url});
  let ready=false;
  const deadline=Date.now()+35000;
  while(Date.now()<deadline) {
    const state=await page('Runtime.evaluate',{expression:'JSON.stringify({ready:document.documentElement.dataset.ready,error:document.documentElement.dataset.error})',returnByValue:true});
    const result=JSON.parse(state.result.value||'{}');
    if(result.error) throw new Error(result.error);
    if(result.ready==='true') {ready=true;break;}
    await delay(100);
  }
  if(!ready) throw new Error('Timed out loading model');
  process.stdout.write(JSON.stringify({ready:true,chromePid:child.pid})+'\n');
  for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})) {
    if(!line.trim()) continue;
    const request=JSON.parse(line);
    if(request.stop) break;
    try {
      await page('Emulation.setDeviceMetricsOverride',{width:request.size,height:request.size,deviceScaleFactor:1,mobile:false});
      const result=await page('Runtime.evaluate',{
        expression:`window.renderNext(${JSON.stringify(request)})`,awaitPromise:true,returnByValue:true});
      if(result.exceptionDetails || result.result?.value !== true)
        throw new Error(result.exceptionDetails?.text || 'Render did not complete');
      const screenshot=await page('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
      await writeFile(request.output,Buffer.from(screenshot.data,'base64'));
      process.stdout.write(JSON.stringify({ok:true})+'\n');
    } catch(error) {
      process.stdout.write(JSON.stringify({ok:false,error:String(error)})+'\n');
    }
  }
  // Closing the owned socket/child below avoids waiting on a CDP reply while
  // Chrome is already shutting down.
} catch(error) {
  process.stdout.write(JSON.stringify({fatal:String(error)})+'\n');
  process.exitCode=1;
} finally {
  socket?.close();
  child.kill();
  let timer;
  await Promise.race([exited,new Promise(resolve => {timer=setTimeout(resolve,3000);})]);
  clearTimeout(timer);
}
