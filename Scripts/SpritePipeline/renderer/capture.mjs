// Own a dedicated headless render process and wait for explicit render readiness.
// No connection to the user's browser/profile; no additional npm dependency.
import {spawn} from 'node:child_process';
import {readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {prepareRendererProfile} from './profile.mjs';
const [chrome,url,output,sizeText,profile]=process.argv.slice(2);
const size=Number(sizeText);
await prepareRendererProfile(profile);
const child=spawn(chrome,['--headless=new','--no-sandbox','--disable-extensions',
  '--hide-scrollbars','--mute-audio','--use-angle=swiftshader',
  '--enable-unsafe-swiftshader','--remote-debugging-port=0',
  `--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore',windowsHide:true});
let socket;
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const exited=new Promise(resolve=>{child.once('exit',resolve);child.once('error',resolve);});
try {
  let port;
  for(let attempt=0;attempt<100;attempt++) {
    try {port=(await readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n');break;}
    catch {await delay(100);}
  }
  if(!port)throw new Error('Dedicated renderer did not start');
  socket=new WebSocket(`ws://127.0.0.1:${port[0]}${port[1]}`);
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Dedicated renderer connection timeout')),5000);
    socket.onopen=()=>{clearTimeout(timer);resolve();};
    socket.onerror=error=>{clearTimeout(timer);reject(error);};
    socket.onclose=()=>{clearTimeout(timer);reject(new Error('Dedicated renderer closed before connection'));};
  });
  let nextId=0;const pending=new Map();
  socket.onmessage=event=>{
    const response=JSON.parse(event.data);const waiter=pending.get(response.id);
    if(!waiter)return;pending.delete(response.id);clearTimeout(waiter.timer);
    if(response.error)waiter.reject(new Error(JSON.stringify(response.error)));else waiter.resolve(response.result);
  };
  socket.onclose=()=>{
    for(const waiter of pending.values()){clearTimeout(waiter.timer);waiter.reject(new Error('Dedicated renderer disconnected'));}
    pending.clear();
  };
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{
    const id=++nextId;
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error(`CDP command timeout: ${method}`));},5000);
    pending.set(id,{resolve,reject,timer});
    socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
  });
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const page=(method,params)=>send(method,params,sessionId);
  await page('Page.enable');
  await page('Emulation.setDeviceMetricsOverride',{width:size,height:size,deviceScaleFactor:1,mobile:false});
  await page('Emulation.setDefaultBackgroundColorOverride',{color:{r:0,g:0,b:0,a:0}});
  await page('Page.navigate',{url});
  let ready=false;
  const deadline=Date.now()+35000;
  while(Date.now()<deadline) {
    const state=await page('Runtime.evaluate',{expression:'JSON.stringify({ready:document.documentElement.dataset.ready,error:document.documentElement.dataset.error})',returnByValue:true});
    const result=JSON.parse(state.result.value||'{}');
    if(result.error)throw new Error(result.error);
    if(result.ready==='true'){ready=true;break;}
    await delay(100);
  }
  if(!ready)throw new Error('Timed out waiting for model, textures, animation and geometry passes');
  const screenshot=await page('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  await writeFile(output,Buffer.from(screenshot.data,'base64'));
  await send('Browser.close').catch(()=>{});
} finally {
  socket?.close();
  child.kill();
  let shutdownTimer;
  await Promise.race([exited,new Promise(resolve=>{shutdownTimer=setTimeout(resolve,3000);})]);
  clearTimeout(shutdownTimer);
}
