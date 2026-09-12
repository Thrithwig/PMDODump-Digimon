"""Derived low-stage starter attacks; original Cyber Sleuth rows stay unchanged."""
import copy
from digimon_runtime_assets import ASSETS, DATA, read, write, lua, native_skill

STAGES = {'Baby', 'In-Training', 'Rookie'}
NAMES = {
    'Neutral': ('Data Jab', 'Data Pulse'), 'Fire': ('Ember Claw', 'Ember Spark'),
    'Water': ('Aqua Strike', 'Aqua Drop'), 'Plant': ('Sprout Slash', 'Sprout Orb'),
    'Electric': ('Static Strike', 'Static Spark'), 'Earth': ('Pebble Strike', 'Pebble Shot'),
    'Wind': ('Breeze Cut', 'Breeze Orb'), 'Light': ('Gleam Strike', 'Gleam Orb'),
    'Dark': ('Shade Claw', 'Shade Orb'),
}

def eligible(entry):
    return entry['stage'] in STAGES or entry['id'] == 'shoutmon'

def assignment(entry):
    # Cyber Sleuth level-1 ATK/INT is the authoritative offensive affinity.
    # A tie selects Magic so balanced early forms have a reliable special option.
    stats = entry['stats_by_level']['1']
    category = 'Physical' if int(stats['atk']) > int(stats['int']) else 'Magic'
    element = 'Electric' if entry['attribute'] == 'Thunder' else entry['attribute']
    return element, category

def skill_id(element, category):
    return 'digi_starter_' + element.lower() + '_' + category.lower()

def learnset(entry, current):
    if not eligible(entry): return copy.deepcopy(current)
    element, category = assignment(entry)
    return [{'Level':1, 'Skill':skill_id(element, category)}] + [copy.deepcopy(s) for s in current if not s['Skill'].startswith('digi_starter_')]

def generate(manifest):
    pairs = sorted({assignment(e) for e in manifest['digimon'] if eligible(e)})
    for index, (element, category) in enumerate(pairs):
        sid = skill_id(element, category)
        source = {'Type':category, 'Attribute':element, 'Power':'40', 'SP Cost':'3',
                  'Description':'Original dungeon starter adaptation: reliable single-target elemental damage.'}
        entry = {'id':sid.removeprefix('digi_'), 'name':NAMES[element][category == 'Magic'],
                 'variants':[{'id':sid, 'source':source}]}
        obj, _ = native_skill(entry, 1000 + index)
        obj['Object']['BaseCharges'] = 20
        obj['Object']['Desc']['DefaultText'] = obj['Object']['Desc']['DefaultText'].replace(' Phase 1: source secondary effects are not applied.', '')
        obj['Object']['Comment'] = 'Original PMDO Digimon starter adaptation; not a source Cyber Sleuth move.'
        write(ASSETS/f'Data/Skill/{sid}.json', obj)
    records = []
    for entry in manifest['digimon']:
        if not eligible(entry): continue
        element, category = assignment(entry)
        records.append({'species':entry['id'], 'stage':entry['stage'], 'element':element,
                        'category':category, 'skill':skill_id(element,category), 'level':1, 'power':20, 'pp':20})
    write(DATA/'starter_skills.json', {'policy':'Level-1 source ATK > INT selects Physical; ties select Magic. Source learnsets are preserved after an added level-1 starter. No automatic replacement of existing learned skills.', 'species':records})
    return records

def main():
    manifest = read(DATA/'phase2_manifest.json')
    records = generate(manifest)
    catalog_path = ASSETS/'Data/Script/origin/digimon/runtime_catalog.lua'
    catalog = catalog_path.read_text(encoding='utf-8-sig')
    for entry in manifest['digimon']:
        if not eligible(entry): continue
        path = ASSETS/f"Data/Monster/{entry['id']}.json"
        obj = read(path)
        form = obj['Object']['Forms'][0]
        old = form['LevelSkills']
        new = learnset(entry, old)
        # Restrict replacement to this species' catalog row, not shared learnsets.
        start = catalog.index('["' + entry['id'] + '"]={')
        skills_start = catalog.index('["skills"]=', start) + len('["skills"]=')
        old_text = lua(old)
        assert catalog[skills_start:skills_start+len(old_text)] == old_text, entry['id']
        catalog = catalog[:skills_start] + lua(new) + catalog[skills_start+len(old_text):]
        form['LevelSkills'] = new
        write(path,obj)
    catalog_path.write_text(catalog,encoding='utf-8',newline='\n')
    print(f'Added reliable elemental starters for {len(records)} low-stage Digimon.')

if __name__ == '__main__': main()
