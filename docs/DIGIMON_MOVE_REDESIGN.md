# Digimon move redesign

Implemented 506 imported move definitions through the existing PMDO skill generator. The installed catalog contains 522 Digimon skills: those 506 plus 16 unchanged 20-power/20-PP starter attacks. Terra agents audited native mechanics and source access, designed three non-overlapping batches, and independently reviewed the result. The main agent integrated the compiler and corrected cross-batch and runtime regressions.

All skill IDs, source CSVs, species learning assignments, learning levels, Digimon stats, family items, and submodule pins are unchanged. No battle engine classes were added. The 506 native JSON definitions and the Skill index are the only changed DumpAsset files.

## Tactical changes

| Native geometry | Physical before | Physical after | Special before | Special after |
|---|---:|---:|---:|---:|
| close | 230 | 111 | 0 | 11 |
| sweep | 0 | 16 | 0 | 0 |
| ranged | 0 | 46 | 115 | 58 |
| thrown | 0 | 21 | 0 | 11 |
| line/beam | 0 | 14 | 0 | 32 |
| broad line | 0 | 6 | 0 | 8 |
| dash/lunge | 9 | 39 | 0 | 3 |
| cone | 0 | 8 | 0 | 15 |
| AOE/blast | 58 | 27 | 55 | 21 |
| offset blast | 0 | 9 | 0 | 11 |

| Damaging moves with… | Before | After |
|---|---:|---:|
| Ally risk | 13 | 38 |
| Negative stat stages | 0 | 23 |
| Target status ailments | 0 | 64 |
| Positive secondary effects / drain | 0 | 57 |
| Damage only | 467 | 274 |

Effect counts overlap when a move has more than one effect. The audit reads actual native events rather than inferring effects from move names.

## PP and power

| Statistic | Before | After |
|---|---:|---:|
| PP minimum | 20 | 8 |
| PP median | 39.0 | 20.0 |
| PP mean | 42.43 | 19.37 |
| PP maximum | 59 | 29 |
| Power minimum per hit | 20 | 10 |
| Power median per hit | 47 | 35 |
| Power mean per hit | 54.33 | 35.42 |
| Power maximum per hit | 94 | 65 |

Multi-hit moves use 2 or 3 individually weaker strikes. Total nominal power remains at least 20; no single-hit damage-only attack falls below the starter baseline. Total nominal power is 20–65 (median 38). This is a balancing measure, not a claim that actual damage equals power times hits.

| Natural stage access | Old mean power | New mean per-hit power | New mean total power |
|---|---:|---:|---:|
| Rookie | 22.1 | 24.77 | 25.72 |
| Champion | 41.01 | 31.79 | 34.69 |
| Ultimate | 56.37 | 40.48 | 42.7 |
| Mega | 75.82 | 45.57 | 49.64 |

Shared moves appear in every applicable stage above. Baby/In-Training are grouped with Rookie in that table; their intentional 20-power starting role is preserved. Armor follows Champion and Ultra follows Mega.

The source-access guide weights each learner by `1 / (1 + learnLevel / 50)`, then blends 25% of the earliest stage center with 75% of that weighted mean. Centers are 25/35/45/55 (20 for Baby/In-Training). Designers trade that guide against area, reach, accuracy, effects, ally risk, and PP. A shared skill has one definition for all users; it is never promoted to Mega strength merely because a Mega learns it. Higher-level numbered generic skills may exceed the guide in exchange for fewer uses. Source skills with no current natural learners remain defined and are identified by empty access rows.

## Representative designs and review decisions

- Lightning Paw remains Special and now strikes adjacent targets. Its source fixed-damage variant deals 35 fixed damage, with a confusion chance; fixed damage continues to bypass ordinary attack-stat scaling.
- Ice Archery I/II/III are ranged Physical arrows: 25/35/45 power and 24/20/16 PP.
- Fifth Rush uses a three-hit dash, 10 power per hit. Weak per-hit values do not become triple-strength attacks merely to meet a per-move floor.
- Infinity Cannon uses a broad piercing wave with ally risk. Transcendent Sword sweeps the three forward tiles, including allies.
- Strike of the Seven Stars is a three-impact 3-by-3 blast three tiles ahead; its 48 total nominal power and 14 PP pay for repeated area coverage.
- Revenge Flame is a 25-power adjacent Special strike that grants native Counter and Mirror Coat after dealing damage, at 12 PP. This preserves both counterattack identity and the existing passive damage bonus linked to the move.
- Cure moves cure their named native ailments; Heal/X-Heal/Final Heal restore 25/50/75% HP, while Aura variants heal nearby party members. Dispel removes negative stat changes without erasing beneficial ones.
- Native revival currently restores every fallen teammate to full HP. Revive and Perfect Revival therefore share the same 10 PP; neither points to the unfinished upstream Revival Blessing move.

## Source and regeneration

The canonical adaptations live in `DataAsset/Digimon/MoveRedesign/designs/{generic,signature_a,signature_b}.json`. `Scripts/digimon_move_designs.py` validates and compiles them into native SkillData before writing any output. `digimon_runtime_assets.native_skill` delegates imported moves to that compiler. The previous `digimon_move_balance.py` entry point now produces a report from the reviewed designs and cannot restore the obsolete rigid bands.

```powershell
python Scripts/digimon_move_designs.py
python Scripts/digimon_move_balance.py
python Scripts/digimon_move_audit.py --output docs/move_redesign/after.json
dotnet build PMDOData.sln --no-restore
# From DataGenerator/bin/Debug/net8.0:
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -index Skill
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-check
```

No manifest is parsed during combat. Runtime uses the normal cached PMDO skill records. Existing serializers, actions, effects, visuals, sound assets, and move-detail UI remain in use.

## Validation and playable output

- Full solution build: passed, zero errors; existing upstream warnings remain.
- New move tests: 8 passed, including source/learnset stability, complete generation, PP and power checks, geometry, status/event references, graphics/sounds, real support effects, and byte-identical starters.
- Full Python suite: 73 of 75 passed. The two pre-existing failures need the ignored `DataAsset/Digimon/SpritePackages/Packages` source directory. Installed runtime art exists; this move task does not reconstruct or modify those sprite sources.
- Native checks passed for all 522 skill serialization round trips, all 341 Digimon, all 35 released zones and 568 seeded floors, and existing save/matchup/quest/item checks.
- Independent final audit verified all 668 existing passive accepted-move references remain effective.
- Startup smoke: published process remained responsive with no errors in its startup log, then was closed. Final numeric revisions were also republished and checked against source hashes.
- Published self-contained Windows build with `--no-restore`; all 522 move files plus the Skill index match source hashes in the published folder.

Playable executable: `PMDC/publish/win-x64/PMDC/PMDC.exe` in this checkout. The executable needs the accompanying published data/content directories. No generated build or publish output is staged or committed.

## Remaining limits

These checks validate data and native serialization and generate real dungeon floors; they do not constitute a manual battle playthrough of every skill. Balance still needs playtesting, particularly 60–65-power tier-III inherited skills, multi-hit attacks, repeated status rolls, and the dual-counter stance. Source-only concepts such as combo meters, Bug/Dot, and one-turn protections use documented native equivalents. No new room-wide targeting system was added.

## Changed files and review artifacts

- Source: `DataAsset/Digimon/MoveRedesign/access.json`, three `designs/*.json` files, `DataAsset/Digimon/move_balance.json`, and `phase2_skill_adaptations.json`.
- Pipeline: `Scripts/digimon_move_access.py`, `digimon_move_audit.py`, `digimon_move_designs.py`, `digimon_move_balance.py`, and the delegation in `digimon_runtime_assets.py`.
- Native verification: `DataGenerator/DigimonMoveChecks.cs`, registered in `DataGenerator.csproj` and `DigimonRuntimeChecks.cs`.
- Python verification: `tests/test_digimon_move_redesign.py`; obsolete band/geometry assertions replaced in `test_digimon_playtest_repairs.py` and `test_digimon_skills.py`. Mission, TM, and chest checks remain.
- Generated runtime assets: 506 `DumpAsset/Data/Skill/digi_*.json` files and `Data/Skill/index.idx`.
- Documentation: this report, updated `DIGIMON_PLAYTEST_FIXES.md` and `DIGIMON_SHARED_MOVE_EXCEPTIONS.csv`, and the mechanics/design/access/audit artifacts under `docs/move_redesign/`.

[Full move matrix](move_redesign/MOVE_MATRIX.csv) · [Before audit](move_redesign/before.json) · [After audit](move_redesign/after.json) · [Independent review](move_redesign/FINAL_AUDIT.md)
