"""Import original Wikimon art; prefer matching transparent PNGs without resizing."""
import concurrent.futures
import hashlib
import html
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin
from urllib.request import Request, urlopen
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'DataAsset/Digimon'
def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'PMDODump-Digimon artwork import (development)'}),timeout=40) as response:
        return response.read()
def norm(value): return re.sub('[^a-z0-9]','',value.lower())
def original(url):
    url=urljoin('https://wikimon.net',html.unescape(url))
    return re.sub(r'/images/thumb/(.+?)/[^/]+$','/images/\\1',url)

def main():
    listing=fetch('https://wikimon.net/Visual_List_of_Digimon').decode()
    lookup={norm(html.unescape(name)):(html.unescape(name),url,original(src)) for url,name,src in
        re.findall(r'<a href="([^"]+)" title="([^"]+)"><img[^>]+src="([^"]+)"',listing)}
    aliases=json.loads((ROOT/'Scripts/digimon_art_aliases.json').read_text())
    old=json.loads((DATA/'image_sources.json').read_text())
    for e in old['images']: lookup[norm(e['species'])]=(e['wikimon_name'],e['page_url'],e['source_url'])
    manifest=json.loads((DATA/'phase2_manifest.json').read_text())
    output=DATA/'phase2_image_provenance.json'
    records={e['species']:e for e in json.loads(output.read_text())['images']} if output.exists() else {}
    def load(entry):
        sid=entry['id']; path=DATA/f'Images/{sid}.png'
        previous=records.get(sid)
        if previous and path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==previous['png_sha256']:return previous
        name,page,primary=lookup[norm(aliases.get(sid,sid))] if norm(aliases.get(sid,sid)) in lookup else lookup[norm(entry['name'])]
        page=urljoin('https://wikimon.net',page)
        candidates=[primary]
        # Only accept same-name PNG originals, never cards, screenshots or recolors.
        try:
            body=fetch(page).decode()
            for src in re.findall(r'<img[^>]+src="([^"]+)"',body):
                url=original(src); stem=unquote(url.rsplit('/',1)[-1]).rsplit('.',1)[0]
                if url.lower().endswith('.png') and norm(stem)==norm(name): candidates.insert(0,url)
        except Exception: pass # attributed visual-list original remains valid
        best=None
        for url in dict.fromkeys(candidates):
            data=fetch(url)
            with Image.open(io.BytesIO(data)) as image:
                image.load(); rgba=image.convert('RGBA')
                transparent=rgba.getchannel('A').getextrema()[0]<255
                candidate=(url,data,rgba,image.format,transparent)
                if best is None or transparent: best=candidate
                if transparent:break
        url,data,image,fmt,transparent=best
        path.parent.mkdir(parents=True,exist_ok=True);image.save(path)
        return {'species':sid,'wikimon_name':name,'page_url':page,'source_url':url,'path':f'Images/{sid}.png',
            'source_sha256':hashlib.sha256(data).hexdigest(),'png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'width':image.width,'height':image.height,'transparent':transparent,'original_format':fmt,
            'processing':'Lossless RGBA PNG encoding; original dimensions and background retained.',
            'variant_note':'Shared base-form illustration for NX or stripped mode.' if sid.endswith('_nx') or sid=='magnagarurumon_sv' else '',
            'retrieved_utc':datetime.now(timezone.utc).isoformat()}
    errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(load,e):e['id'] for e in manifest['digimon']}
        for future in concurrent.futures.as_completed(futures):
            try:
                record=future.result();records[record['species']]=record
                output.write_text(json.dumps({'images':[records[k] for k in sorted(records)]},indent=2)+'\n')
                print(record['species'], 'transparent' if record['transparent'] else 'opaque',flush=True)
            except Exception as error: errors.append((futures[future],str(error))); print('ERROR',errors[-1],flush=True)
    if errors: raise RuntimeError(errors)

if __name__=='__main__':main()
