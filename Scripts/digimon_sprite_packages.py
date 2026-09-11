"""Find attributed transparent Wikimon art and assemble eight-direction PMDO packages.

Source images retain their resolution; only package frames are fitted to --size.
No background removal, game-data changes, or edits to upstream assets are performed.
"""
import argparse
import concurrent.futures
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import unquote, urljoin

from PIL import Image, ImageOps
from digimon_full_art import DATA, ROOT, fetch, norm, original

OUTPUT = DATA / 'SpritePackages'
# CharSheet.Import converts clockwise sheet rows to counterclockwise Dir8 values.
ROWS = ['Down', 'DownRight', 'Right', 'UpRight', 'Up', 'UpLeft', 'Left', 'DownLeft']


def transparent(image):
    alpha = image.getchannel('A')
    histogram = alpha.histogram()
    clear = sum(histogram[:16]) / (image.width * image.height)
    corners = [alpha.getpixel(p) for p in [(0, 0), (image.width-1, 0),
                                          (0, image.height-1), (image.width-1, image.height-1)]]
    return 0.05 < clear < 0.98 and max(corners) < 16 and alpha.getbbox() is not None


def score(url, name):
    stem = unquote(url.rsplit('/', 1)[-1]).rsplit('.', 1)[0]
    key = re.sub('mode(?!l)', '', norm(stem)).replace('awakened', 'awake').replace('awaken', 'awake')
    base = re.sub('mode(?!l)', '', norm(name)).replace('awakened', 'awake').replace('awaken', 'awake')
    if key == base:
        return 0
    # Only known single-character illustrations/renders; never screenshots/cards.
    if not key.startswith(base):
        return None
    suffix = key[len(base):]
    preferred = ['newcentury', 'encounters', 'tri', 'rearise',
                 'linkz', 'modelcyber', 'modeldsr', 'modelsourcecode',
                 'modelencounters', 'newcenturymodel', 'modelsc', 'gogodigimon',
                 'survive', 'referenceart', 'dmo', 'cs', 'dsammodel', 'hmmodel',
                 'modeldw', 'modeldw3', 'tsmodel', 'modelts', 'fortune', 'collectors']
    for rank, value in enumerate(preferred, 1):
        if suffix == value or (suffix.startswith(value) and suffix[len(value):].isdigit()):
            return rank
    if suffix.isdigit():
        return 20
    return None


def acquire(record):
    record = dict(record)
    # Cyber Sleuth uses the Savers variants and Terriermon's evolution, not the
    # original Falcomon/Kudamon designs or the armor Digimon called Gargomon.
    overrides = {
        'falcomon': ('Falcomon 2006', 'https://wikimon.net/Falcomon_(2006_Anime_Version)'),
        'kudamon': ('Kudamon 2006', 'https://wikimon.net/Kudamon_(2006_Anime_Version)'),
        'gargomon': ('Galgomon', 'https://wikimon.net/Galgomon'),
        'omnimon': ('Omegamon', 'https://wikimon.net/Omegamon'),
        'omnimon_nx': ('Omegamon', 'https://wikimon.net/Omegamon'),
    }
    if record['species'] in overrides:
        record['wikimon_name'], record['page_url'] = overrides[record['species']]
    sid = record['species']
    target = OUTPUT / 'Sources' / (sid + '.png')
    old = OUTPUT / 'Records' / (sid + '.json')
    if old.exists() and target.exists():
        result = json.loads(old.read_text())
        if result.get('selection_version') == 2 and hashlib.sha256(target.read_bytes()).hexdigest() == result['png_sha256']:
            return result
    body = fetch(record['page_url']).decode()
    if 'Fatal error' in body:
        body = fetch('https://wikimon.net/index.php?title=' + record['page_url'].rsplit('/', 1)[-1] + '&action=render').decode()
    bodies = [body]
    for link in dict.fromkeys(re.findall(r'href="([^"]*Gallery:[^"]*)"', body)):
        if link.endswith('/Bandai') or link.endswith('/Toei'):
            bodies.append(fetch(urljoin('https://wikimon.net', link)).decode())
    urls = {original(src) for text in bodies for src in re.findall(r'<img[^>]+src="([^"]+)"', text)
            if original(src).lower().endswith('.png')}
    candidates = [(score(url, record['wikimon_name']), url) for url in urls]
    candidates = sorted((rank, url) for rank, url in candidates if rank is not None)
    # These filenames were visually checked on their species pages. The UP
    # sprites are native pixel-art fallbacks, retained without enlargement.
    reviewed = {
        'guardromon_gold': 'Guardromon_CS.png',
        'durandamon': 'Durandamon_up.png',
        'zubamon': 'Zubamon_up.png',
        'zubaeagermon': 'Zubaeagermon_up.png',
    }
    if sid in reviewed:
        candidates = [(-1, url) for url in urls if unquote(url.rsplit('/', 1)[-1]) == reviewed[sid]] + candidates
    errors = []
    for _, url in candidates:
        try:
            raw = fetch(url)
            image = Image.open(io.BytesIO(raw)).convert('RGBA')
            pixel_fallback = sid in reviewed and url.endswith('_up.png')
            if (min(image.size) < (32 if pixel_fallback else 96)) or not transparent(image):
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target)
            result = {'species': sid, 'selection_version': 2, 'page_url': record['page_url'], 'source_url': url,
                      'source_sha256': hashlib.sha256(raw).hexdigest(),
                      'png_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                      'width': image.width, 'height': image.height,
                      'quality_note': 'Native pixel-art fallback; higher-resolution illustration still wanted.' if pixel_fallback else '',
                      'processing': 'Lossless RGBA PNG; source dimensions and alpha retained.'}
            old.parent.mkdir(parents=True, exist_ok=True)
            old.write_text(json.dumps(result, indent=2) + '\n')
            return result
        except Exception as error:
            errors.append(str(error))
    raise ValueError(f'No qualifying transparent illustration ({len(candidates)} candidates); {errors}')


def package(sid, size=96, destination=None):
    image = Image.open(OUTPUT / 'Sources' / (sid + '.png')).convert('RGBA')
    if not transparent(image):
        raise ValueError(sid + ': source lacks a transparent background')
    cropped = image.crop(image.getchannel('A').getbbox())
    cropped.thumbnail((size-4, size-4), Image.Resampling.LANCZOS)
    frame = Image.new('RGBA', (size, size))
    frame.alpha_composite(cropped, ((size-cropped.width)//2, (size-cropped.height)//2))
    sheet = Image.new('RGBA', (size, size*8))
    offsets = Image.new('RGBA', sheet.size)
    shadow = Image.new('RGBA', sheet.size)
    for row, direction in enumerate(ROWS):
        sheet.paste(ImageOps.mirror(frame) if 'Left' in direction else frame, (0, row*size))
        # White combines the red/green/blue markers at the body center.
        offsets.putpixel((size//2, row*size+size//2), (255, 255, 255, 255))
        shadow.putpixel((size//2, row*size+size//2), (255, 255, 255, 255))
    destination = destination or OUTPUT / 'Packages' / sid
    destination.mkdir(parents=True, exist_ok=True)
    root = ET.Element('AnimData')
    ET.SubElement(root, 'ShadowSize').text = '0'
    anims = ET.SubElement(root, 'Anims')
    actions = ET.parse(ROOT / 'DumpAsset/Base/GFXParams.xml').findall('.//Actions/Action')
    names = [action.findtext('Name') for action in actions]
    if 'Idle' not in names:
        raise ValueError('Could not read PMDO action names')
    for index, name in enumerate(names):
        anim = ET.SubElement(anims, 'Anim')
        ET.SubElement(anim, 'Name').text = name
        ET.SubElement(anim, 'Index').text = str(index)
        if name != 'Idle':
            ET.SubElement(anim, 'CopyOf').text = 'Idle'
        else:
            ET.SubElement(anim, 'FrameWidth').text = str(size)
            ET.SubElement(anim, 'FrameHeight').text = str(size)
            for marker in ['RushFrame', 'HitFrame', 'ReturnFrame']:
                ET.SubElement(anim, marker).text = '0'
            ET.SubElement(ET.SubElement(anim, 'Durations'), 'Duration').text = '8'
    ET.indent(root)
    ET.ElementTree(root).write(destination / 'AnimData.xml', encoding='utf-8', xml_declaration=True)
    for name, content in [('Anim', sheet), ('Offsets', offsets), ('Shadow', shadow)]:
        content.save(destination / ('Idle-' + name + '.png'))
    with zipfile.ZipFile(destination.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(destination.iterdir()):
            archive.write(path, path.name)
    return {'species': sid, 'frame_size': size, 'sheet_rows': ROWS,
            'package': str(destination.relative_to(DATA if destination.is_relative_to(DATA) else ROOT)).replace('\\', '/')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roster', choices=['initial', 'all'], default='initial')
    parser.add_argument('--size', type=int, default=96)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    if args.size < 8 or args.size % 2:
        parser.error('--size must be an even number >= 8')
    initial = {sid for line in json.loads((DATA / 'phase1_roster.json').read_text())['lines'] for sid in line['species']}
    records = json.loads((DATA / 'phase2_image_provenance.json').read_text())['images']
    records = [r for r in records if args.roster == 'all' or r['species'] in initial]
    records.sort(key=lambda r: (r['species'] not in initial, r['species']))
    successes, failures = [], []
    def run(record):
        if not args.offline:
            acquire(record)
        return package(record['species'], args.size)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(run, record): record['species'] for record in records}
        for future in concurrent.futures.as_completed(futures):
            sid = futures[future]
            try:
                successes.append(future.result())
                print('OK', sid, flush=True)
            except Exception as error:
                failures.append({'species': sid, 'reason': str(error)})
                print('MISSING', sid, str(error), flush=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / (args.roster + '_report.json')).write_text(json.dumps({
        'packages': sorted(successes, key=lambda r: r['species']),
        'unresolved': sorted(failures, key=lambda r: r['species'])}, indent=2) + '\n')
    print(f'{len(successes)} packages; {len(failures)} unresolved', flush=True)


if __name__ == '__main__':
    main()
