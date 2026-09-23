# Evolution, residents, quests, and loot review

Terra implemented the requested changes in two workstreams. Astra reviewed the source, native UI rendering, and integration results before publishing the playable build.

## Player-facing changes

- The Tree of Life form list and target preview have separate Back actions. Evolution and scan restoration share a generic target preview: name, stage, element, attribute, Family Type, art, and ability. Long ability descriptions and requirements have their own pages. Evolution and de-evolution use the original Tree presentation around the existing form-change transaction.
- Converted residents no longer fall through to their original conversational lines. Native service actions remain. Thirteen instructors replace the former checkpoint/dungeon teachers on the reachable Green Gym Maze entry floor (map ID 4, displayed floor 5).
- Clockmon debriefs the completed primary request and assigns the next eligible primary request in the same conversation. Native Forest Trail (level 10) precedes Drill Tunnel (level 15); active records from older saves are preserved.
- Nursery Courier places Falcomon on floor 2 and Botamon/Punimon on floor 3. After the rescue, Falcomon and the babies remain in File Town. Falcomon inherits the friendship-count reward service, and the Cliff Camp giver is disabled. Claimed reward progress remains intact; rewards use released family treasures.
- HP Restraint Chip C (the former HP Thorn) is unavailable. SP Restraint Chip C deals damage and removes up to 10 PP from every occupied move slot, never taking PP below zero.
- Family boxes draw uniformly from unique released items within their star tier, globally across families. Family size and local enemy duplication no longer multiply an item's weight. Three-star treasures remain exchange-only; original PMDO bag effects remain intact.
- Disabled legacy items are removed from dungeon pools, placed items, and shops. HP/PP recovery item weights are tripled and status-cure weights halved, rounded up. A persisted tuning marker prevents repeated installation from multiplying these weights again.
- Developer-room tours and post-clear surprise battle detours are removed. Normal camp progression and reward rooms remain.

## Deliberate choices

The seven converted Digi-Egg/Spirit unlock items remain available even though their internal IDs begin with `evo_`. They are real Digimon progression requirements, not leftover Pokémon stones.

Global equal odds per unique family item was the stated default while the optional box-distribution question remained unanswered. Equal odds do not prevent duplicates in a short random sample.

Existing saved dungeon floors are not regenerated in place. Leave the expedition and enter again to use revised generation and loot tables. Player save files are not edited.

## Main implementation locations

- `DumpAsset/Data/Script/origin/digimon/`: `evolution_preview.lua`, `progression.lua`, `terminal.lua`, `story_missions.lua`, `story_npcs.lua`, and `recruitment_rewards.lua`.
- `DumpAsset/Data/Script/origin/event_mapgen.lua`, `event_battle.lua`, affected ground/service callbacks, and dungeon exit scripts.
- `DataAsset/Digimon/story_npcs.json` and its generated runtime catalog.
- `Scripts/digimon_unmatched_items.py`, `Scripts/digimon_family_items.py`, `DataGenerator/DigimonDungeonRules.cs`, and the zone generators.
- `PMDC/PMDC/LevelGen/Spawning/SpeciesItemSpawner.cs`: the shared native box selection fix. No submodule pins or `.gitmodules` edits are required.
- Python/Lua regression suites and `DataGenerator/DigimonRuntimeChecks.cs` / `DigimonNpcChecks.cs`.

## Review findings and playtest focus

Astra required corrections for the training map's script hook/context, Clockmon's native service dispatch, empty repeat-visit boxes, fixed/procedural floor-step contexts, and emptied enemy-held-item pools. The instructor migration also needed to preserve the containing dungeon segments. Native checks now reject generation errors even when they occur identically in test and live dungeon scenes, and verify the affected routes retain their full primary segments.

For manual playtesting, try cancelling each Tree menu level, restoring a Digimon, evolving and de-evolving a reserve member, then speaking to Clockmon after Nursery Courier. Visit the training entry floor and Falcomon's friendship service. Re-enter an expedition to generate fresh floors and loot.

The full evolution cutscene still needs visual confirmation during ordinary gameplay. The preview itself was rendered with native UI components and its Confirm, Cancel, Menu/Escape and page inputs exercised in a native harness; this is not a claim that an entire live expedition or cutscene was played manually.

## Validation

- `dotnet build PMDOData.sln --no-restore`: passed, zero errors; existing upstream warnings remain.
- The six targeted Python suites passed all 38 tests. These include Lua 5.4 runtime scenarios for menu cancellation, restoration, all 1,812 transition records, Clockmon handoff, rescue interactions, camp access, resident/service state, repeat-visit rewards, loot availability and tuning, and family boxes.
- Final native validation passed with 341 forms, 138 converted items, 40 released zones, 567 seeded floors and 146 generated boxes containing family treasures. Live transitions matched initial actor placement with zero generation errors. It also verified 13 reachable training instructors, actual rescue actors, native PP drain, family-box pools, and character save round trips.
- Windows self-contained publish succeeded. All 3,129 published script, zone and item files match the source payload by SHA-256.

The broad legacy test discovery is not entirely green: its old camp/dungeon-level expectations and assumption that every Nifty box contains the complete TM pool need a separate update for the current dungeon design. Two sprite-source tests also require the ignored raw `SpritePackages/Packages` directory, absent here; compiled game art is available and checked natively. These are distinct from the 38 passing targeted tests.

The playable executable is `PMDC/publish/win-x64/PMDC/PMDC.exe`. No generated build/publish output was committed, and no submodule pins were changed.
