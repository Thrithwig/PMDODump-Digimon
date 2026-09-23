# Camp arrival fixture design

Status: design and feasibility review only.  This document does not add a
fixture, modify a save, or change a map, story, script, engine, or test runner.
It covers the existing loadable camp maps in the remaining C01--C07 portion of
[the visual coverage plan](VISUAL_COVERAGE_PLAN.md): `base_camp`,
`forest_camp`, `cliff_camp`, `canyon_camp`, `rest_stop`, `final_stop`, and
`guildmaster_summit`.

## Conclusion

Normal-arrival coverage is feasible for all seven existing map IDs, but it is
**not executable with the current camp-layout runner**.  That runner uses
`DebugWarp` into `camp_layout_fixture`; it deliberately reports
`fixture-zone-debug-placement` and breaks active Lua scripts before placement.
It proves renderer layout only.

An arrival runner needs a separate, source-controlled saved-state fixture and
must enter `guildmaster_island` through the ordinary scene transition after
that state is loaded.  The engine will then create the player at the requested
entry point, run the map's `Init`, then `Enter`, and draw the settled result.
It must not call a camp Lua callback, a destination-menu callback, or an NPC
callback directly.  `rest_stop` is the important exception: its initial entry
is intentionally an ambush that transfers to a boss map, so its settled camp
capture can only follow the ordinary boss-return state.

The source has no existing generic "write this fixture state" or
"load camp-arrival case" command.  Adding that narrow capability is the first
implementation blocker, not an excuse to relabel the existing debug-placement
captures as arrival evidence.

## Findings from current source

### Save and entry model

`DumpAsset/Data/Script/origin/scriptvars.lua` creates `SV` once for a new
save.  It includes the legacy camp tables (`SV.base_camp`,
`SV.forest_camp`, and so on) and a Digimon ledger at `SV.Digimon`.  The latter
contains `StoryMissions.records`, whose records have `accepted`,
`objective_met`, `cleared`, and `debriefed` fields.  `story_missions.lua`
marks a route debriefed only after the objective and a successful route clear;
it also keeps a native mission record in `SV.missions.Missions` while the
request is live.  `phase3_progression.lua` stores later camp availability as
`SV.Digimon.UnlockedCamps`, rather than writing one shared camp flag.

This has three consequences for fixtures:

1. A native dungeon `Completed` unlock is not interchangeable with a Digimon
   story debrief.  `dungeon_access.lua` uses both, depending on the route.
2. A new save already has every default `SV` table, but the current normal map
   scripts also read many unrelated legacy team/cycle/mission fields.  An
   arrival fixture must begin from a real fresh save serialization; it must not
   manufacture a partial `SV` table.
3. Script variables persist in `GameProgress.ScriptVars`.  The engine's
   `LuaEngine.LoadSavedData(GameProgress)` reconstructs `SV` from that saved
   table, while `LuaEngine.SaveData(GameProgress)` serializes it.  A fixture
   writer should therefore operate through this supported save model, not by
   issuing Lua at runtime.

The ground lifecycle is also explicit.  `GroundScene.InitGround` calls a
ground's `OnInit`; `GroundScene.BeginGround` calls `OnEnter`.  `GameManager`
enters an indexed ground through `moveToZoneInit`, and `MoveToGround` resolves
a named marker to an entry index before doing the same work.  This is the
required arrival path.

The existing camp layout fixture is a different mechanism:

| Existing component | What it actually does | Evidence category |
| --- | --- | --- |
| `DataGenerator/Data/Zones/ZoneInfoPlaytesting.cs` | Creates unreleased `camp_layout_fixture` with the seven ground maps. | Fixture data only |
| `PlaytestController.BeginCampLayoutCapture` | Calls `DebugWarp` to the selected fixture-map index after `LuaEngine.BreakScripts()`. | Debug placement |
| `tests/visual/camps-layout.json` and `Scripts/digimon_camp_layout_checks.py` | Accept only that seven-case map list and require `fixture-zone-debug-placement`. | Layout, unreviewed |

Those captures remain useful for static map/POI inspection.  They cannot
establish a normal entry marker, first-visit cutscene, story visibility, route
menu access, or a returned NPC arrangement.

### Verified normal arrival destinations

The map IDs are in `DataGenerator/Data/Zones/MapInfo.cs`.  In the normal
`guildmaster_island` zone, map IDs match the `MapInfo.MapNames` indices:
`base_camp` is 1, `forest_camp` 3, `cliff_camp` 4, `canyon_camp` 5,
`rest_stop` 6, `final_stop` 7, and `guildmaster_summit` 8.  The source route
returns below use those numeric IDs and entry indices; the marker names for
those indices have not been enumerated in this review and must be recorded by
the future loader rather than invented in a manifest.

| Camp | Verified source transition | What it establishes |
| --- | --- | --- |
| File Town / `base_camp` | New-save `SV.checkpoint` is `guildmaster_island`, map 1, entry 0.  Test Camp's separate proof enters by the named `entrance_center` marker. | A new-save/checkpoint base state is source-backed; this review did not verify the title/new-game bootstrap destination. |
| Native Forest / `forest_camp` | `tropical_path.ExitSegment` sends a cleared segment 0 or 1 to map 3, entry 0. | The normal Tropical return reaches Forest Camp. |
| Panorama / `cliff_camp` | `faded_trail.ExitSegment` sends cleared segment 0 to map 4, entry 0. | The normal Faded Trail return reaches Cliff Camp. |
| Great Canyon / `canyon_camp` | `flyaway_cliffs.ExitSegment` sends cleared segment 0 to map 5, entry 0. | The normal Flyaway Cliffs return reaches Canyon Camp. |
| Misty Shelter / `rest_stop` | `thunderstruck_pass.ExitSegment` and `veiled_ridge.ExitSegment` send cleared segment 0 to map 6, entry 2. | Those normal returns reach Rest Stop, subject to its `BossPhase` branch. |
| Freezeland / `final_stop` | `snowbound_path.ExitSegment` sends cleared segment 0 to map 7, entry 0.  The later Digimon access layer can also expose map 7 after the Veiled Ridge debrief. | The storyboard says Veiled Ridge opens Freezeland, but the inspected direct route return is Snowbound Path, not Veiled Ridge. |
| Infinity Summit / `guildmaster_summit` | `champions_road.ExitSegment` sends cleared segment 0 to map 8, entry 0; on a Digimon save it uses `GAME:EnterZone`. | The camp script sees `SV.Digimon` and takes its resident/fade branch rather than the legacy summit battle. |

The route matrix in `docs/phase3/storyboard_routes.json` is planning context,
not a replacement for these runtime calls.  It calls the three unimplemented
dispatch hubs `dragon_eye_dispatch`, `stormwatch_dispatch`, and
`dino_survey_dispatch`; they are not camp-map IDs and are outside this seven
map fixture set.

## Per-camp state requirements

The table separates exact entry control flow from the smallest useful staged
state.  "Fixture prerequisite" is a proposed capture definition, not a claim
that the game has a fixture implementation today.  All story-record names are
current source identifiers.

| Camp / capture | Entry-control fields read by `Enter` | Source-backed normal precondition | Proposed minimal disposable state |
| --- | --- | --- | --- |
| `base_camp` fresh | `SV.base_camp.IntroComplete`, `ExpositionComplete`; reward branch also reads `SV.guildmaster_trail.FloorsCleared` and `Rewarded`. | Fresh default checkpoint has map 1 / entry 0. | A real new-save serialization, retained before its first base-map entry. Capture the intentional first-visit state; `PrepareFirstTimeVisit` hides Assembly, Storage, and `North_Exit`. |
| `base_camp` progressed | Same fields; `SetupNpcs` also reads family/team fields and `SV.guildmaster_summit.GameComplete`. | No single source-defined "post-main-quest" state exists. | Split rather than inventing one broad state: `base-return-after-tropical` and a separately named endgame state only if needed. Both must be captured from normal play and retain exact observed story/native-dungeon records. |
| `forest_camp` fresh arrival | `SV.forest_camp.ExpositionComplete`; exceptional branches read `SnorlaxPhase`. | Cleared Tropical segment returns to map 3 / entry 0. | Replay/retain a save immediately before that route's ordinary return. First arrival runs `SetupNpcs`, `BeginExposition`, then writes `ExpositionComplete=true`. |
| `forest_camp` progressed | `ExpositionComplete`; `SnorlaxPhase` 2 or 3 runs a fail/success branch. | The coverage plan calls this "after `tropical_path`". | A settled post-first-arrival state must use `ExpositionComplete=true` and avoid phase 2/3 unless the capture intentionally covers the boss-return event. For story residents, add only the specific debrief records that the declared view needs. |
| `cliff_camp` fresh arrival | `SV.cliff_camp.ExpositionComplete`. | Cleared Faded Trail segment 0 returns to map 4 / entry 0. | Retain just before normal route return; first entry plays `BeginExposition` and unlocks `flyaway_cliffs` and `fertile_valley`. |
| `cliff_camp` progressed | `ExpositionComplete`; `SetupNpcs` reads legacy team/family/supply fields. | The plan labels it after `faded_trail`. | Settled state is `ExpositionComplete=true`; the route record `DigimonStory_FadedTrail.debriefed=true` belongs only if the case asserts the Digimon post-debrief arrangement. |
| `canyon_camp` fresh arrival | `SV.canyon_camp.ExpositionComplete`; exception reads `SV.rest_stop.BossPhase==2`. | Cleared Flyaway Cliffs segment 0 returns to map 5 / entry 0. | Retain the ordinary first arrival; it plays `BeginExposition` and directly unlocks `copper_quarry` and `depleted_basin`. |
| `canyon_camp` progressed | `ExpositionComplete`; `SetupNpcs` conditionally reads `SV.rest_stop.ExpositionComplete` plus team/quest states. | The coverage plan labels it after `flyaway_cliffs`. | Settled map requires `ExpositionComplete=true`; use `DigimonStory_FlyawayCliffs.debriefed=true` only when the case specifically asserts that transition. Do not set Rest Stop state merely to make its extra NPCs appear. |
| `rest_stop` arrival event | `SV.rest_stop.BossPhase`: 0/1 calls `BeginExposition`; 3 calls `Steelix_Success`, changes it to 4, and sets `ExpositionComplete=true`. | Thunderstruck/Veiled return goes to map 6 / entry 2. | A distinct **arrival-event** case is feasible from an authentic pre-entry save with `BossPhase=0`; its expected result is transfer to `guildmaster_island` dungeon map 6, not a stable camp screenshot. |
| `rest_stop` progressed | `BossPhase>=4` reaches `SetupNpcs`/fade; update also reads `ExpositionComplete` and `SV.secret.Wish`. | The plan says after `thunderstruck_pass`; only a normal boss completion reaches the settled first camp branch. | Capture only a save produced after the ordinary boss return has observed `BossPhase=4` and `ExpositionComplete=true`. Do not synthesize this by invoking `Steelix_Success`. |
| `final_stop` fresh arrival | `SV.final_stop.ExpositionComplete`; exceptional branches read `SV.guildmaster_summit.BossPhase` and `SV.final_stop.DragonPhase`. | Normal source return from Snowbound Path uses map 7 / entry 0. | Retain a genuine pre-entry state. A Veiled-debrief travel-menu case is also valid, but must be named separately because it is a different arrival provenance. |
| `final_stop` progressed | `ExpositionComplete=true`; avoid DragonPhase 2/3 unless testing failure/success. | `phase3_progression.resolve_route('veiled_ridge')` writes `SV.Digimon.UnlockedCamps.final_stop=true`; `dungeon_access.grounds` can make the ground destination available. | For the first normal travel-menu arrival: exact Veiled record must be debriefed and `UnlockedCamps.final_stop=true`, with base state still `ExpositionComplete=false`. For its settled successor: `ExpositionComplete=true`. |
| `guildmaster_summit` arrival | First branch is simply `if SV.Digimon`, then `SetupNpcs` and fade. | Champions Road source sends map 8 / entry 0. | A valid Digimon-save serialized state plus normal Champions Road return. It must retain `SV.Digimon`; removing it routes into the legacy battle flow. |
| `guildmaster_summit` progressed | On a Digimon save, no `GameComplete` branch is evaluated.  NPC setup reads `SV.team_rivals.Status` and `SV.supply_corps` cycle fields. | The plan says after `champions_road`; the source transition is compatible with that. | Use `DigimonStory_ChampionsRoad.debriefed=true` and `SV.Digimon.UnlockedCamps.guildmaster_summit=true` only for a case asserting the unlocked dispatch. Do not use `GameComplete=true`: that is a legacy/non-Digimon branch and a different state. |

### NPC and quest dependencies that matter to case selection

Every camp calls `require('origin.digimon.story_npcs').install(...)`.
`story_npcs.lua` evaluates residents from the current saved `SV.Digimon`
records: `mission` completion means `records[id].debriefed == true`, and
`zone_mission` searches a debriefed record with that `zone`.  It also applies
the native map's own visibility first for `native` and `native_or_after`
bindings.  Therefore a visual fixture needs both the serialized story record
and the relevant legacy native status when a binding has the latter presence
mode.

The full per-entity mapping is source data in
`DumpAsset/Data/Script/origin/digimon/story_npc_catalog.lua` and
`docs/phase3/DIGIMON_NPC_BINDINGS.csv`.  The minimal fixture should not set
every row.  It should use the following source-defined state families only
when its acceptance assertions name the affected characters:

| Camp | State families read by its current setup | Digimon resident records with a direct camp-level effect |
| --- | --- | --- |
| `base_camp` | `family`, `team_catch`, `team_kidnapped`, `team_steel`, `missions`, `guildmaster_summit.GameComplete` | Tropical record affects Clockmon/Guardromon presentation. The source has no generic base "all mains completed" switch. |
| `forest_camp` | `town_elder`, `forest_child`, `team_catch`, `team_kidnapped`, `team_retreat`, `team_solo`, `supply_corps`, `missions` | `DigimonStory_FadedTrail` can make the Lopmon/Terriermon-related bindings visible; added residents depend on their own completed zone missions. |
| `cliff_camp` | `family`, `team_hunter`, `team_catch`, `team_rivals`, `team_kidnapped`, `team_retreat`, `team_meditate`, `team_solo`, `team_firecracker`, `supply_corps`, `missions`, `Experimental` | `DigimonStory_FlyawayCliffs` is the meaningful route record for its Hawkmon-related binding; optional residents have their own record dependencies. |
| `canyon_camp` | `rest_stop.ExpositionComplete`, `team_rivals`, `team_meditate`, `team_steel`, `team_solo`, `team_psychic`, `team_dragon`, `team_firecracker`, `supply_corps`, `missions` | `DigimonStory_CopperQuarry` controls the Mamemon/Chip/Tally-related returned states. |
| `rest_stop` | `team_rivals`, `team_dark`, `team_dragon`, `team_firecracker`, `supply_corps`, `rest_stop.DaysSinceBoss`, `BossSolved`, `missions`, `secret.Wish` | `DigimonStory_ThunderstruckPass`, `DigimonStory_VeiledRidge`, and optional zone records control only the corresponding selected story residents. |
| `final_stop` | `family`, `team_rivals`, `team_dragon`, `team_firecracker`, `supply_corps`, `missions`, `DragonPhase` | `DigimonStory_SnowboundPath` controls the Hearth/Brine-related returned states; Champions Road affects Cairn. |
| `guildmaster_summit` | `team_rivals`, `supply_corps` cycle fields; no map-local quest table is read by `SetupNpcs`. | Guildmaster Trail records control Unimon/Relay profiles, but the requested Champions Road arrival should not assert them unless that later record is present. |

This is intentionally a dependency inventory, not a proposal to make every
legacy side quest complete.  In particular, the many `SV.team_*` status values
and native `SV.missions.Missions` records change visuals independently of the
Digimon progression.  A case should either retain their values from the
recorded normal playthrough or assert an explicitly documented native state;
it must not guess numeric status values from a desired screenshot.

## Proposed fixture shape and loading contract

### Disposable fixture files

Use one fresh profile per case below
`work/playtest-profiles/<run>/<case-id>/`.  A fixture should contain:

```text
fixture.json                 # declarative identity and expected state fingerprint
SAVE/                        # ordinary engine save data, created in the disposable profile
provenance.json              # source route, result, destination map/index, entry index,
                             # captured before/after state fingerprints
```

`fixture.json` should carry only stable identifiers and explicit expectations:
`case_id`, `mode: "arrival"`, `source_route` or `source_travel`,
`expected_zone_id: "guildmaster_island"`, `expected_map_id`, expected entry
index/marker **after discovery**, `state_stage`, required debrief record IDs,
and the normal artifact contract.  Do not include direct Lua source text,
arbitrary table assignments, arbitrary map IDs, or a claimed marker name that
has not been inspected.

The fixture generator should start from a new disposable profile and reach the
declared state through normal game input/scene transitions.  Once the expected
arrival and `Enter` processing have completed, it serializes through the
engine save path.  Subsequent capture processes load that saved profile and
repeat the real departure/return transition (preferred), or resume at the
recorded destination only when the case metadata labels it
`resume-after-normal-arrival`.  The latter is evidence of state rendering, not of route
traversal; it should not replace the first variant.

No direct `South_Exit_Touch`, `Enter`, `SetupNpcs`, `Story.debrief`,
`Phase3.resolve_route`, or similar Lua invocation is allowed.  Queued normal
`FrameInput` and the existing engine scene outcome APIs are allowed because
they preserve the game lifecycle.  Captures remain queued after completed
draws, as in the current controller.

### Capture matrix

Start with fourteen small cases rather than an unbounded save editor:

| Case family | Case IDs | Required evidence |
| --- | --- | --- |
| First/fresh arrival | `base-new-save`, `forest-after-tropical-return`, `cliff-after-faded-return`, `canyon-after-flyaway-return`, `rest-after-thunderstruck-arrival-event`, `final-after-veiled-travel` or `final-after-snowbound-return` (do not conflate), `summit-after-champions-return` | Before/after map identity, entry position, `Init`/`Enter` completion, relevant cutscene/menu state, and viewport/full-map/overlay. Rest Stop expects the boss transfer. |
| Settled/progressed | One explicitly named successor for each map; `rest-after-boss-return` is mandatory. | Same artifacts plus exact persisted state fingerprint and selected NPC/route-menu observations. |

The two Final Stop options are mutually distinct; pick one source route before
implementation.  Base Camp must likewise replace the plan's ambiguous
"post-main-quest" label with a concrete story point.  These two choices are
blockers for source-controlled manifest names, but do not block the common
fixture infrastructure.

### Next gated case: Forest after Tropical Path

`forest-after-tropical-return` is the next candidate after the completed
`base-new-save` foundation. It has one exact source route: a cleared Tropical
Path segment `0` or `1` calls `StoryMissions.on_zone_exit` and then
`COMMON.EndDungeonDay` for `guildmaster_island`, map `3`, entry `0`
(`zone/tropical_path/init.lua`). Forest Camp is map index `3`
(`DataGenerator/Data/Zones/MapInfo.cs`). Its normal `Enter` records checkpoint
map `3`, entry `1`; with `SV.forest_camp.ExpositionComplete == false`, it runs
the first exposition and then persists that flag as true
(`ground/forest_camp/init.lua`).

The exact first-return story state is intentionally narrower than a generic
"Tropical complete" label: `SV.Digimon.StoryMissions.records`
`["DigimonStory_TropicalPath"]` has `accepted`, `objective_met`, and
`cleared` true, with `debriefed` still false. `story_missions.lua` sets
`cleared` during the valid route exit, while the later Clockmon interaction is
the only path that sets `debriefed`. The normal game-progress completion record
for `tropical_path` is also relevant to Forest Camp travel-menu availability;
it must be observed and fingerprinted, not inferred from the story record.

This case has a strict claim boundary. An **authentic pre-return save** made
after the ordinary Tropical clear and before its normal destination transition
may establish `after-tropical-return` when the title loader follows its saved
destination and Forest Camp completes `Init`/`Enter`. A fixture that starts
from a real new-save serialization and prepares only the listed native and
script-variable state may establish the resulting Forest state and ordinary
map lifecycle, but must be labeled `state-prepared` or
`resume-after-normal-arrival`; it cannot claim that Tropical Path was
traversed. Do not call `tropical_path.ExitSegment`, `Story.debrief`, or a camp
callback directly.

The current base-only controller has no generic typed script-variable preparer
and must not become an arbitrary save or Lua editor. Review is required before
adding a one-case, fixed-schema preparer or recording an authentic pre-return
save. No gameplay data, map, story, or progression data change is required for
either path.

### What stays layout-only

The current `camps-layout.json` seven-map set, its generic object/marker crops,
and its existing `work/visual-checks` reports stay layout-only.  It is safe to
reuse their static map IDs and crop selector in arrival output, but an arrival
case must add its own state/provenance and must never inherit the layout
runner's `fixture-zone-debug-placement` label.

An arrival capture can test normal map entry, first-visit or settled script
behavior, source-return placement, and state-dependent NPC visibility.  It
does not prove a dungeon route was traversed unless the fixture-production run
also records and validates the normal route clear.  It does not approve a
visual review merely because the PNG files exist.

## Identifiers safe to use now, and unresolved identifiers

Safe, source-verified identifiers are the seven map IDs above;
`guildmaster_island`; fixed map indices 1/3/4/5/6/7/8; story records named in
the per-camp table; `camp_layout_fixture`; and the existing
`runtime-map-object-and-marker-v1` crop selector.  `test_camp_fixture`,
`test_camp`, `entrance_south`, and `entrance_center` are safe only for the
already-implemented Test Camp pilot, not for this camp suite.

Do not use these as camp-arrival identifiers until source/runtime discovery
has produced evidence:

- named entry markers for the normal numeric entries 0 and 2;
- a single Base Camp "post-main-quest" state;
- whether Final Stop's first arrival is the Veiled travel menu or Snowbound
  route return for the requested coverage row;
- direct normal routes for the storyboard-only Dragon Eye Dock, Stormwatch
  Relay, and Dino Survey Post.  The coverage plan already marks all three as
  identifier discovery required.

## Blockers and staged next-week plan

1. **Freeze exact case meaning.** Choose Base Camp's concrete progressed
   story point and Final Stop's normal-arrival provenance.  Record each
   destination's runtime marker index/name using a one-off observation, not
   a guessed string.
2. **Build a narrow fixture recorder.** Add no generic Lua evaluator and no
   arbitrary state editor.  It must create a new disposable save, drive only
   the selected normal transition, serialize it through `GameProgress`, and
   write provenance/fingerprints below `work/`.
3. **Add a narrow arrival loader.** It should accept only the static camp
   case table, load the disposable profile, and call the ordinary engine
   scene transition.  Capture must wait for normal player readiness and a
   completed draw.  Persist observed zone/map/entry/position, `SV` state
   fingerprint, menu/cutscene state, and capture sequence.
4. **Prove one benign early case.** Use `forest-after-tropical-return` or
   `cliff-after-faded-return` before the boss branches.  Verify source route,
   map ID, entry marker, screenshots, and no direct callback use.
5. **Add the special cases.** Implement Rest Stop's event versus settled
   return as separate cases, then Final Stop and Summit.  Verify the
   Digimon-save Summit branch remains non-battle.
6. **Extend the matrix only after review.** Add selected resident/quest
   arrangements one at a time, preserving native status fields and source
   evidence.  Keep each case unreviewed until a visual reviewer inspects it.

The substantive blockers are the missing fixture recorder/loader, the two
case-definition choices above, and unrecorded marker identities.  There is no
blocker to preserving the existing layout-only captures while that work is
designed and implemented.

## Referenced source paths

- `DataGenerator/Data/Zones/MapInfo.cs`
- `DataGenerator/Data/Zones/ZoneInfoPlaytesting.cs`
- `DumpAsset/Data/Script/origin/scriptvars.lua`
- `DumpAsset/Data/Script/origin/common.lua`
- `DumpAsset/Data/Script/origin/digimon/story_missions.lua`
- `DumpAsset/Data/Script/origin/digimon/phase3_progression.lua`
- `DumpAsset/Data/Script/origin/digimon/dungeon_access.lua`
- `DumpAsset/Data/Script/origin/digimon/story_npcs.lua`
- `DumpAsset/Data/Script/origin/digimon/story_npc_catalog.lua`
- `DumpAsset/Data/Script/origin/ground/{base_camp,forest_camp,cliff_camp,canyon_camp,rest_stop,final_stop,guildmaster_summit}/init.lua`
- `DumpAsset/Data/Script/origin/zone/{tropical_path,faded_trail,flyaway_cliffs,thunderstruck_pass,veiled_ridge,snowbound_path,champions_road}/init.lua`
- `PMDC/RogueEssence/RogueEssence/Ground/GSceneZone.cs`
- `PMDC/RogueEssence/RogueEssence/Lua/LuaEngine.cs`
- `PMDC/RogueEssence/RogueEssence/Scene/GameManager.cs`
- `PMDC/RogueEssence/RogueEssence/Dev/Playtesting/PlaytestController.cs`
