#!/usr/bin/env python3
"""Apply the Digimon family-type policy to installed data and write the family doc.

The policy (type merges, then the small-family rule) lives in digimon_runtime_assets so a
full regeneration reproduces it. This script applies the same assignments in place to the
installed Monster records and Lua runtime catalog, and rewrites docs/DIGIMON_FAMILY_TYPES.md.
Run after editing FAMILY_MERGES or MIN_FAMILY_MEMBERS, then rebuild the Monster index.
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

from digimon_runtime_assets import (ASSETS, DATA, FAMILY_MERGES, MIN_FAMILY_MEMBERS, family_assignments,
                                    family_type_list, lua, read, write)

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs' / 'DIGIMON_FAMILY_TYPES.md'


def apply_to_data(assignments: dict[str, list[str]]) -> tuple[int, int]:
    changed = 0
    for path in sorted((ASSETS / 'Data/Monster').glob('*.json')):
        if path.stem not in assignments:
            continue
        data = read(path)
        touched = False
        for form in data['Object']['Forms']:
            if form.get('Family_Types') != assignments[path.stem]:
                form.pop('Family_Type', None)
                form['Family_Types'] = assignments[path.stem]
                touched = True
        if touched:
            write(path, data)
            changed += 1
    catalog = ASSETS / 'Data/Script/origin/digimon/runtime_catalog.lua'
    text = catalog.read_text(encoding='utf-8')
    replaced = 0
    for species_id, types in assignments.items():
        pattern = re.compile(r'(\["' + re.escape(species_id) + r'"\]=\{\["name"\]="[^"]*",\["stage"\]="[^"]*",)'
                             r'(?:\["family_types"\]=\{[^}]*\},)?')
        text, count = pattern.subn(lambda m: m.group(1) + '["family_types"]=' + lua(types) + ',', text, count=1)
        replaced += count
    if replaced != len(assignments):
        raise ValueError(f'Lua catalog covered {replaced} of {len(assignments)} species')
    catalog.write_text(text, encoding='utf-8', newline='\n')
    return changed, replaced


def write_doc(rows, assignments, removed, orphans) -> None:
    name = {r['id']: r['name'] for r in rows}
    raw = {r['id']: family_type_list(r) for r in rows}
    members = collections.defaultdict(list)
    for species_id, types in assignments.items():
        for t in types:
            members[t].append(name[species_id])
    kept = sorted((t for t in members if t not in removed), key=lambda t: (-len(members[t]), t))
    merged_into = collections.defaultdict(list)
    for source, target in FAMILY_MERGES.items():
        merged_into[target].append(source)
    lines = [
        '# Digimon family types', '',
        'Source: `DataAsset/Digimon/digimon_family_types.json` (Digimon Wiki physical types, retrieved 2026-09-13).',
        'This is the family notion the exclusive-item work uses. The Phase 2 lineage families and the',
        'treasure-box TM fallback comment are superseded by it.', '',
        '## Runtime representation', '',
        'Every listed wiki type is stored, in wiki order, as `Family_Types` on the Digimon form and',
        '`family_types` in the Lua runtime catalog. The `NO DATA` placeholder is dropped. The summary',
        'screen joins them with a slash. A Digimon with several types belongs to every one of them.', '',
        '## Policy', '',
        'Owner decisions (2026-09-13), in order:', '',
        '1. Wiki types are merged per the table below (`FAMILY_MERGES` in `Scripts/digimon_runtime_assets.py`).',
        f'2. Families with fewer than {MIN_FAMILY_MEMBERS} members are dropped (`MIN_FAMILY_MEMBERS`).',
        '3. A species whose every family was dropped keeps its source types and is listed for a decision.', '',
        'Apply changes with `python Scripts/digimon_family_types.py`, then rebuild the Monster index.', '',
        '### Merges', '', '| Family | Merged from |', '| --- | --- |',
    ]
    for target in sorted(merged_into):
        lines.append(f"| {target} | {', '.join(sorted(merged_into[target]))} |")
    lines += ['', f'## Families ({len(kept)})', '', '| Family | Members | Species |', '| --- | ---: | --- |']
    for t in kept:
        lines.append(f"| {t} | {len(members[t])} | {', '.join(sorted(members[t]))} |")
    lines += ['', f'## Dropped families ({len(removed)})', '',
              ', '.join(f'{t} ({len(members[t])})' for t in sorted(removed)) or 'None', '',
              f'## Digimon with no remaining family ({len(orphans)})', '']
    if orphans:
        lines += ['These keep their source types until reassigned.', '', '| Digimon | Source types |', '| --- | --- |']
        lines += [f"| {name[s]} | {', '.join(raw[s])} |" for s in sorted(orphans, key=lambda s: name[s])]
    else:
        lines.append('None.')
    DOC.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> None:
    rows = read(DATA / 'digimon_family_types.json')['family_types']
    assignments, removed, orphans = family_assignments(rows)
    changed, replaced = apply_to_data(assignments)
    write_doc(rows, assignments, removed, orphans)
    families = {t for types in assignments.values() for t in types if t not in removed}
    print(f'{len(families)} families; {len(removed)} dropped; {len(orphans)} unassigned species; '
          f'{changed} Monster records updated; {replaced} Lua entries written.')
    for species_id in orphans:
        print('  unassigned:', species_id, assignments[species_id])


if __name__ == '__main__':
    main()
