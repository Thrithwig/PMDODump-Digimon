# EXP, encounter stages and dungeon names

## Causes and fixes

- Test Power's 9999-damage basic attack could defeat an enemy without PMDO's `EXPMarked` flag. Its landed-hit events now mark EXP before applying damage. Misses, allies and disabled Test Power are unaffected; normal reward formulas, recipient-stage bonuses and the overlevel farming penalty remain intact.
- Freezeland Path (`snowbound_path`) and Infinity Approach (`champions_road`) inherited `ExpPercent = 0`. Both now use 100%, in source and installed zone data. Every released combat dungeon is checked for a positive EXP multiplier.
- The dungeon generator's broad Pokémon-to-Digimon substitution bypassed the old Python stage retune. The old retune also skipped Tropical Path entirely and did not account for levels changed by `MobSpawnLevelScale`.
- `DigimonDungeonRules` now runs after fallback tables and loot sanitation, before saving generated zones. It installs `MobSpawnDigimonTier` after level-scaling features and before other spawn modifiers. This PMDC feature rolls the stage at the enemy's final level, then picks a species, its learnable moves and its passive. It applies equally to initial enemies and later respawns. Spawn levels, floor ranges, team sizes, spawn weights and loot are preserved.
- Boss-flagged encounters, explorer teams, rescue actors and interactable shopkeepers retain their identities. Tropical Jungle's ordinary pool is limited to the original eight starter lines' twelve available Baby/In-Training species; its Koromon guardian is preserved.
- Display names come from `storyboard_routes.json`. Its hidden-route alias table renders renamed branches as `<current dungeon name> (Hidden)`. Both generator output and installed dialogue/map resources use these names. Internal IDs and quest/save flags remain unchanged.

## Stage odds

| Final enemy level | Stages | Upper-stage probability |
|---|---|---|
| 1–7 | Baby / In-Training | 50% |
| 8–13 | In-Training / Rookie | 60% |
| 14–27 | Rookie / Champion | 20% → 50% |
| 28–54 | Champion / Ultimate | 20% → 50% |
| 55+ | Ultimate / Mega | 20% at 55 → 50% at 75, then capped |

These are probabilities per spawned enemy, not an approximate share of static table entries. The editor/table species is a valid preview; final-level selection is authoritative. NX forms remain excluded from ordinary wild pools, as before. Source stages correspond to the installed `digi_*` growth groups, which already carry the conversion's stage-based EXP bonuses.

## Verification

- [Encounter audit](DIGIMON_ENCOUNTER_AUDIT.csv): 40 released dungeons, 3,518 ordinary spawn records, 605 floor-scaled records, 29 protected actors. Tropical Jungle has 44 ordinary records and three protected records.
- Seven targeted Python tests pass, covering every released spawn table, ordering after level scaling, introductory roster, protected actors, EXP availability, names/aliases, idempotence, stable IDs and cheat behavior.
- Native checks execute the real cheat EXP marker and death handout: unmarked foe = no reward; marked level-5 Koromon = 150 queued EXP for a level-5 Rookie under normal reward rules.
- Native checks exercise 13,200 seeded spawn rolls at all tier boundaries, checking probabilities, valid species stages, unchanged levels, species-appropriate moves/passives, full HP and formation history.
- Native dungeon checks cover 341 forms, 49 converted items, all 40 released dungeons, 567 seeded floors, actual enemy stages, rescue uniqueness, stairs and 93 family-item boxes.
- Full solution build: `dotnet build PMDOData.sln --no-restore` passes with zero errors and existing warnings.
- Release win-x64 publish succeeds. All 7,551 published Data files match the workspace payload byte for byte. An isolated 15-second launch reached Lua engine ready and stayed running without logged errors; this is a launch smoke test, not a visual gameplay review.
- One additional existing raw-ground NPC snapshot assertion fails (`noctowl` vs `clockmon` in the authored map). Runtime NPC casting is exercised separately by the passing native checks; this unrelated source snapshot has not been rewritten in this repair.

## Rebuild and playtest

### Cliff Camp missing after returning to Base Camp

Ground-map junction tables capture `ExpositionComplete` at script load. The shared
`dungeon_access.grounds` adapter now re-reads visited-camp flags whenever the menu
opens, including the summit's completion flag. Cliff Camp also recognizes cleared
Signpost Forest / its debrief, matching the dungeon's existing Cliff Camp exit.
Existing saves recover access without editing their flags or skipping progression.

Regression scenarios reuse stale junction tables before and after discovery,
verify five visited camps remain available, and preserve entry coordinates and
unrelated-zone restrictions. The isolated Lua terminal/runtime/access checks pass.
The full combined Lua suite stops earlier at the existing mission-order assertion
in `test_digimon_story_missions.lua:59`; it does not reach the access tests.
The corrected Lua script is copied to the workspace's published playtest build
and hash-verified. Restart that build to reload it. This script-only update does
not replace the executable containing the separate spawn-initialization fix.

### Initial enemies missing after floor 1

The stage selector originally called `RestoreForm()` during spawn generation. On a
stair transition, the engine remains in `DungeonScene` but clears `CurrentMap`
before generating the next floor. The form restore tried to refresh proximity
passives against that null map. The generation step caught the exception and
abandoned the entire initial enemy group. Protected NPCs/bosses bypassed the
selector, and timed respawns worked once the map existed.

`MobSpawnDigimonTier` now sets the current form and uses the existing
`FullRestore(false)` initialization path, avoiding map-dependent events while
setting the new species' elements, intrinsic, skills and HP. This shared fix
covers every ordinary encounter using the selector; zone tables and serialized
data do not need regeneration. No RogueEssence source or submodule pins change.

The native regression compares seeded initial actors under the neutral check
scene and actual `DungeonScene` floor transitions for every released zone. It
fails on any stage-selector exception or changed actors and reports pre-existing layout
errors separately, requiring those errors to match between both scenes.
The original Tropical Jungle and Drill Tunnel reproduction now gives identical
populated floors in both modes. Previously, floors 2–4 lost all ordinary enemies.

Validation: the full solution build passes with zero errors; all five dungeon-rule
Python tests pass; native checks pass, including 13,200 stage rolls and matching
initial actors across all 40 released zones / 567 floors in both scenes.

The stricter error capture also exposes 19 pre-existing floor-generation issues,
identical in both scenes (segment and floor IDs below are zero-based):

- All seven lairs, segment 0 floor 7: `GridPathStartStepGeneric` encounters a null
  path configuration in the reward-room generator.
- `geode_crevice`, segment 0 floors 4–12: pattern placement expects
  `MapGenContext` but receives `ListMapGenContext`.
- `champions_road`, segment 0 floor 12 and segment 1 floor 0; `veiled_ridge`,
  segment 0 floor 12: scheduled placement steps expect `ListMapGenContext` but
  receive `MapLoadContext`. These include an optional enemy placement step.

Those separate layout/placement issues are reported, not silently treated as
error-free floors, and are not changed by this spawn-initialization repair.
This repair builds the source; it does not replace the currently running
published executable or modify existing saved dungeon floors.

The subsequent [evolution, quest, and loot review](PLAYTEST_REVIEW_2026_09_16.md)
corrected these layout/context errors and added a strict zero-generation-error
gate. The historical findings above describe the earlier spawn-only repair.

Run from the repository root:

```powershell
dotnet build PMDOData.sln --no-restore
# Normal zone generation now applies the rules automatically. To repair existing data without rebuilding geometry:
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../DumpAsset/ -gen DataAsset/ -digimon-dungeons
python Scripts/digimon_dungeon_names.py
python Scripts/digimon_story_npcs.py
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../DumpAsset/ -index Zone
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-check
dotnet publish PMDC/PMDC/PMDC.csproj -c Release -r win-x64 --self-contained true --no-restore
```

Use the available Python interpreter in place of `python` if needed. Existing in-progress dungeon saves may contain old generated maps/tables; leave the current expedition and enter again to load the repaired content. No player saves are edited. No submodule pins or `.gitmodules` were changed. The new PMDC spawn feature is a local engine source addition and must accompany the parent project's data when sharing future source commits.
