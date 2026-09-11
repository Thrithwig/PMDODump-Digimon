"""Repair empty procedural encounter/loot tables and audit released dungeons."""
import copy
import json
from pathlib import Path
from digimon_early_zones import ROOT, ZONE_DIR, load, convert, stage_pool, known_skills, restore_placement_ranges, baseline_zone


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def main():
    output = ROOT / 'DataAsset/Digimon/dungeon_audit.json'
    previous = {r['id']: r.get('repairs', []) for r in load(output)['zones']} if output.exists() else {}
    species = load(ROOT / 'DataAsset/Digimon/phase2_gameplay.json')['species']
    donor = load(ZONE_DIR / 'tiny_tunnel.json')['Object']['Segments'][0]
    loot = next(x for x in donor['ZoneSteps'] if 'ItemSpawnZoneStep' in x['$type'])
    monster = next(x for x in donor['ZoneSteps'] if 'TeamSpawnZoneStep' in x['$type'])['Spawns'][0]
    report = []
    for path in sorted(ZONE_DIR.glob('*.json')):
        data = load(path)
        obj = data['Object']
        if not obj.get('Released'):
            continue
        before = copy.deepcopy(data)
        restore_placement_ranges(data, baseline_zone(path.stem))
        level = max(5, obj.get('Level', 5))
        pool = stage_pool(species, level)
        repairs = list(previous.get(path.stem, []))
        removed = 0
        for node in walk(data):
            if isinstance(node.get('GenSteps'), list):
                steps = node['GenSteps']
                valid = [row for row in steps if row.get('Value') is not None]
                removed += len(steps) - len(valid)
                node['GenSteps'] = valid
        if removed:
            repairs.append(f'removed {removed} null generation steps')
        for index, segment in enumerate(obj['Segments']):
            floors = segment.get('Floors', [])
            # Fixed rooms (shops, treasure rooms, bosses) need no random tables.
            procedural = any('PlaceRandomMobsStep' in n.get('$type', '') for n in walk(floors))
            if not procedural:
                continue
            ranges = [n['Range']['Max'] for n in walk(segment) if isinstance(n.get('Range'), dict) and isinstance(n['Range'].get('Max'), int)]
            end = max([len(floors)] + ranges)
            for step in segment.get('ZoneSteps', []):
                if 'TeamSpawnZoneStep' in step['$type'] and not step['Spawns'] and not step['SpecificSpawns']:
                    for floor in range(end):
                        for offset in range(min(4, len(pool))):
                            row = copy.deepcopy(monster)
                            sid = pool[(floor + offset + sum(map(ord, path.stem))) % len(pool)]['id']
                            enemy = row['Spawn']['Spawn']
                            enemy_level = min(99, level + floor)
                            enemy['BaseForm'].update(Species=sid, Form=0, Skin='normal', Gender=-1)
                            enemy['Level'] = {'Min': enemy_level, 'Max': enemy_level}
                            enemy['SpecifiedSkills'] = known_skills(sid, enemy_level)
                            enemy['SpawnConditions'] = []
                            enemy['SpawnFeatures'] = []
                            row['Range'] = {'Min': floor, 'Max': floor+1}
                            step['Spawns'].append(row)
                    step['TeamSizes'] = [{'Spawn': 1, 'Rate': 10, 'Range': {'Min': 0, 'Max': end}}]
                    repairs.append(f'segment {index}: supplied enemies on {end} floors')
                if 'ItemSpawnZoneStep' in step['$type'] and not step['Spawns']:
                    step['Spawns'] = copy.deepcopy(loot['Spawns'])
                    for row in walk(step['Spawns']):
                        if 'Range' in row:
                            row['Range'] = {'Min': 0, 'Max': end}
                    repairs.append(f'segment {index}: supplied loot on {end} floors')
        # Existing encounter geometry, special rewards and story steps are retained.
        for node in walk(data):
            base = node.get('BaseForm')
            if isinstance(base, dict) and path.stem == 'guildmaster_island' and base.get('Species') == 'snorlax':
                base.update(Species='monzaemon', Form=0, Skin='normal', Gender=-1)
                if 'SpecifiedSkills' in node:
                    node['SpecifiedSkills'] = known_skills('monzaemon', level)
        count = convert(data, zone_id=path.stem, start_level=level, pool=pool)
        if data != before:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        report.append({'id': path.stem, 'level': level, 'digimon_encounter_records': count, 'repairs': repairs})
    output.write_text(json.dumps({'zones': report}, indent=2)+'\n', encoding='utf-8')
    for row in report:
        if row['repairs']:
            print(row['id'], '; '.join(row['repairs']))
    print(f'Audited {len(report)} released zones.')


if __name__ == '__main__':
    main()
