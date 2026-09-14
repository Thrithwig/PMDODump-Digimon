"""Move-level progression policy; never checks the attacking Digimon's identity."""
import csv
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'DataAsset/Digimon/move_balance.json'
STAGES = {'Baby': 0, 'In-Training': 0, 'Rookie': 0, 'None': 0,
          'Champion': 1, 'Armor': 1, 'Ultimate': 2, 'Mega': 3, 'Ultra': 3}
NAMES = ['Rookie and lower', 'Champion', 'Ultimate', 'Mega']

@lru_cache(maxsize=1)
def catalog():
    return json.loads(POLICY.read_text(encoding='utf-8'))['moves'] if POLICY.exists() else {}

def values(entry):
    return catalog().get(entry['id'])

def generate():
    manifest = json.loads((ROOT / 'DataAsset/Digimon/phase2_manifest.json').read_text(encoding='utf-8-sig'))
    access = {}
    for digimon in manifest['digimon']:
        for learned in digimon['skills']:
            access.setdefault(learned['skill'], set()).add(STAGES[digimon['stage']])
    moves = {}
    for entry in manifest['skills']:
        source = entry['variants'][0]['source']
        stages = sorted(access.get(entry['id'], {0}))
        tier = min(stages)
        # Compare like-for-like damage/PP across disjoint stage bands. Source
        # strength still ranks attacks within each band; weak attacks get more PP.
        strength = min(19, max(0, (int(source['Power']) - 20) * 19 // 230))
        moves[entry['id']] = {
            'tier': tier, 'learned_by_tiers': stages,
            'power': 20 + 20 * tier + strength if source['Type'] != 'Support' else None,
            'pp': 20 + 10 * tier + (9 - strength * 9 // 19),
            'shared_exception': len(stages) > 1,
        }
    POLICY.write_text(json.dumps({'policy': 'Move-owned tiers from earliest source learner stage. Shared moves retain one identity and are explicit cross-stage exceptions. No species checks, variant moves, or learnset gates. Damage bands 20-39/40-59/60-79/80-99; PP bands 20-29/30-39/40-49/50-59. Starter attacks stay 20 power and 20 PP. Source move effects and targeting are preserved.', 'moves': moves}, indent=2) + '\n', encoding='utf-8')
    with (ROOT / 'docs/DIGIMON_SHARED_MOVE_EXCEPTIONS.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['move_id', 'move_name', 'balance_tier', 'source_learning_stages', 'reason'])
        for entry in manifest['skills']:
            row = moves[entry['id']]
            if row['shared_exception']:
                writer.writerow([entry['id'], entry['name'], NAMES[row['tier']], '; '.join(NAMES[t] for t in row['learned_by_tiers']), 'Shared source learnset; same move works identically for every Digimon'])
    catalog.cache_clear()
    print(f'Balanced {len(moves)} moves; {sum(row["shared_exception"] for row in moves.values())} shared-source exceptions documented.')

if __name__ == '__main__':
    generate()
