"""Generate source-inheritable single-use TMs and restore their native chest categories."""
import copy
import json
from collections import Counter
from digimon_runtime_assets import ASSETS, DATA, read, write, original, native_skill


def common_skills(manifest):
    return [s for s in manifest['skills'] if all(v['source']['Inheritable'] == 'Yes' for v in s['variants'])]


def tm_id(skill):
    return 'digi_tm_' + skill['id']


def contains_tm(node):
    if isinstance(node, str): return node.startswith('tm_')
    if isinstance(node, dict): return any(contains_tm(v) for v in node.values())
    if isinstance(node, list): return any(contains_tm(v) for v in node)
    return False


def chest_replacements(baseline, common):
    """Identify original box categories that contained TMs without restoring banned loot."""
    result = set()
    if isinstance(baseline, dict):
        if 'BoxID' in baseline and contains_tm(baseline.get('BaseSpawner')):
            result.add(baseline['BoxID'])
        for child in baseline.values(): result.update(chest_replacements(child, common))
    elif isinstance(baseline, list):
        for child in baseline: result.update(chest_replacements(child, common))
    return result


def populate_chests(node, categories, common):
    count = 0
    if isinstance(node, dict):
        if node.get('BoxID') in categories:
            # BoxSpawner supplies the map context; all native TM chest slots now
            # draw one consumable disc from the complete source-inheritable pool.
            context = node['$type'].split('[[', 1)[1].split(']]', 1)[0]
            item_type = 'RogueEssence.Dungeon.MapItem, RogueEssence'
            node['BaseSpawner'] = {
                '$type': f'RogueElements.PickerSpawner`2[[{context}],[{item_type}]], RogueElements',
                'Picker': {'$type': f'RogueElements.LoopedRand`1[[{item_type}]], RogueElements',
                    'Spawner': {'$type': f'RogueElements.SpawnList`1[[{item_type}]], RogueElements',
                        '$values': [{'Spawn': {'IsMoney':False,'Cursed':False,'Value':tm_id(s),
                            'HiddenValue':'','Amount':1,'Price':0,'TileLoc':{'X':0,'Y':0}},'Rate':10} for s in common]},
                    'AmountSpawner': {'$type':'RogueElements.RandRange, RogueElements','Min':1,'Max':1}}}
            count += 1
        for child in node.values(): count += populate_chests(child, categories, common)
    elif isinstance(node, list):
        for child in node: count += populate_chests(child, categories, common)
    return count


def main():
    manifest = read(DATA/'phase2_manifest.json')
    common = common_skills(manifest)
    adaptations = []
    for index, skill in enumerate(manifest['skills']):
        data, adaptation = native_skill(skill, index)
        write(ASSETS/f"Data/Skill/digi_{skill['id']}.json", data)
        adaptations.append(adaptation)
    write(DATA/'phase2_skill_adaptations.json', adaptations)
    prototype = json.loads(original('Data/Item/tm_flamethrower.json'))
    for skill in common:
        item = copy.deepcopy(prototype)
        obj = item['Object']; sid = 'digi_'+skill['id']
        obj.update(Name={'DefaultText':'TM '+skill['name'],'LocalTexts':{}},
            Desc={'DefaultText':'Teaches '+skill['name']+' to any Digimon. Consumed after successful use.','LocalTexts':{}},
            Released=True, MaxStack=1, Comment='Digimon common skill TM; source Inheritable=Yes.')
        obj['ItemStates'][0]['ID'] = sid
        obj['GroundUseActions'][0]['Skill'] = sid
        write(ASSETS/f'Data/Item/{tm_id(skill)}.json', item)
    teach = [{'Skill':'digi_'+s['id']} for s in common]
    for species in manifest['digimon']:
        path = ASSETS/f"Data/Monster/{species['id']}.json"
        data = read(path)
        for form in data['Object']['Forms']: form['TeachSkills'] = teach
        write(path, data)
    categories = set()
    for path in sorted((ASSETS/'Data/Zone').glob('*.json')):
        categories.update(chest_replacements(json.loads(original('Data/Zone/'+path.name)), common))
    chests = 0
    for path in sorted((ASSETS/'Data/Zone').glob('*.json')):
        data = read(path)
        count = populate_chests(data, categories, common)
        if count: write(path, data)
        chests += count
    write(DATA/'attachment_skills.json', {'classification':'CSV Inheritable=Yes',
        'consumable':True,'chest_categories':sorted(categories),'chest_spawners':chests,
        'skills':[{'skill':'digi_'+s['id'],'item':tm_id(s)} for s in common],
        'signature_skills':['digi_'+s['id'] for s in manifest['skills'] if s not in common],
        'visual_templates':dict(Counter(a['template'] for a in adaptations))})
    print(f'Generated {len(adaptations)} skills, {len(common)} single-use TMs, {chests} chest spawners in {sorted(categories)}.')


if __name__ == '__main__': main()
