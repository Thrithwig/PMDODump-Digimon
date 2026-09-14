"""Apply scoped mission-hook and move-baseline repairs to installed conversion data."""
import re
from digimon_runtime_assets import ASSETS, DATA, native_skill, read, write
from digimon_move_balance import generate, values

def repair():
    generate()
    universal = read(ASSETS / 'Data/Universal.json')['Object']['ZoneSteps']
    assert sum(s.get('Script') == 'SpawnMissionNpcFromSV' for s in universal) == 1
    zones = 0
    for path in (ASSETS / 'Data/Zone').glob('*.json'):
        obj = read(path)
        changed = False
        for segment in obj['Object']['Segments']:
            steps = segment.get('ZoneSteps', [])
            filtered = [s for s in steps if s.get('Script') != 'SpawnMissionNpcFromSV']
            if filtered != steps:
                segment['ZoneSteps'] = filtered
                changed = True
        if changed:
            write(path, obj)
            zones += 1
    skills = 0
    for index, entry in enumerate(read(DATA / 'phase2_manifest.json')['skills']):
        path = ASSETS / 'Data/Skill' / ('digi_' + entry['id'] + '.json')
        current = read(path)
        generated, _ = native_skill(entry, index)
        obj, new = current['Object'], generated['Object']
        before = repr(obj)
        obj['BaseCharges'] = new['BaseCharges']
        balance = values(entry)
        for state in obj['Data']['SkillStates']:
            if 'BasePowerState' in state.get('$type', ''):
                if balance['power'] is not None: state['Power'] = balance['power']
        for event in obj['Data']['OnHits']:
            effect = event['Value']
            if 'SpecificDamageEvent' in effect.get('$type', ''):
                effect['Damage'] = balance['power']
        if balance['power'] is not None:
            obj['Data']['HitRate'] = new['Data']['HitRate']
            obj['Desc']['DefaultText'] = re.sub(r'Power (\d+)\.', f'Power {balance["power"]}.', obj['Desc']['DefaultText'])
            obj['Desc']['DefaultText'] = re.sub(r'Deals (\d+) fixed damage', f'Deals {balance["power"]} fixed damage', obj['Desc']['DefaultText'])
        if repr(obj) != before:
            write(path, current)
            skills += 1
    print(f'Removed duplicate mission hooks from {zones} zones; updated {skills} attacks.')

if __name__ == '__main__':
    repair()
