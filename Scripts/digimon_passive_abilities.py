"""Materialize the reviewed passive catalog using existing PMDO intrinsic events.

The catalog is the editable authority. No event behavior is inferred from prose.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'DataAsset/Digimon/passive_abilities.json'
ASSETS = ROOT / 'DumpAsset/Data'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text(encoding='utf-8-sig') != text:
        path.write_text(text, encoding='utf-8', newline='\n')


def priority(event):
    return {'Key': {'str': [0]}, 'Value': copy.deepcopy(event)}


def intrinsic(row):
    result = copy.deepcopy(read(ASSETS / 'Intrinsic/none.json'))
    obj = result['Object']
    for key, value in obj.items():
        if isinstance(value, list):
            obj[key] = []
    proximity = obj['ProximityEvent']
    for key, value in proximity.items():
        if isinstance(value, list):
            proximity[key] = []
    proximity['Radius'] = -1
    proximity['TargetAlignments'] = 0
    obj.update(Name={'DefaultText': row['ability_name'], 'LocalTexts': {}},
               Desc={'DefaultText': row['description'], 'LocalTexts': {}},
               Released=True, IndexNum=15000 + row['number'],
               Comment='Digimon playtest passive; source: DataAsset/Digimon/passive_abilities.json')
    for effect in row['effects']:
        target = obj
        if effect['scope'] == 'allies':
            target = proximity
            target['Radius'] = 2
            target['TargetAlignments'] = 2
        target[effect['hook']].append(priority(effect['event']))
    return result


def assign_spawns(value, mapping):
    changed = False
    if isinstance(value, dict):
        species = value.get('BaseForm', {}).get('Species')
        if species in mapping and 'Intrinsic' in value:
            expected = mapping[species]
            if value['Intrinsic'] != expected:
                value['Intrinsic'] = expected
                changed = True
        for child in value.values():
            changed = assign_spawns(child, mapping) or changed
    elif isinstance(value, list):
        for child in value:
            changed = assign_spawns(child, mapping) or changed
    return changed


def apply():
    catalog = read(CATALOG)
    rows = catalog['abilities']
    assert len(rows) == 341
    assert len({r['ability_id'] for r in rows}) == len(rows)
    assert len({json.dumps(r['effects'], sort_keys=True) for r in rows}) == len(rows)
    mapping = {r['species']: r['ability_id'] for r in rows}
    for row in rows:
        write(ASSETS / 'Intrinsic' / (row['ability_id'] + '.json'), intrinsic(row))
        path = ASSETS / 'Monster' / (row['species'] + '.json')
        monster = read(path)
        for form in monster['Object']['Forms']:
            form['Intrinsic1'] = row['ability_id']
            form['Intrinsic2'] = 'none'
            form['Intrinsic3'] = 'none'
        write(path, monster)
    zones = 0
    for path in sorted((ASSETS / 'Zone').glob('*.json')):
        zone = read(path)
        if assign_spawns(zone, mapping):
            write(path, zone)
            zones += 1
    print(f'Assigned {len(rows)} executable Digimon passives; updated spawn intrinsics in {zones} zones.')
    return mapping


if __name__ == '__main__':
    apply()
