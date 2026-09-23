# Visual coverage plan

This is a lab-only execution plan for the visual playtest controller. It does
not add a broad runner, alter dungeon content, or approve any screenshot. Each
future case must use a disposable lab profile and retain `viewport.png`,
`map.png`, `overlay.png`, `state.json`, and `checks.json` as specified in the
[implementation brief](TERRA_VISUAL_PLAYTEST_IMPLEMENTATION.md).

All IDs below are source-verified. `identifier discovery required` means the
storyboard names a future hub or an existing fixed map has not yet been mapped
to a loadable runtime ground-map ID; it must be resolved before a case is added.

## Order of execution

1. Keep the completed Test Camp pilot as the controller baseline. Its
   fixture-zone capture and generic entity-label evidence remain
   [unreviewed](../../work/playtest-profiles/test-camp-entity-overlay/artifacts/test-camp-pilot/overlay.png).
2. Execute early and progressed **arrival** cases for every loadable camp. A
   progressed fixture must have only the quest flags needed to place its
   intended NPC arrangement. Capture entrances, the Assembly/terminal, route
   selectors, changed NPCs, and each active exit.
3. Execute **layout** cases for the seven run-up/lair pairs. For each zone,
   use seeds `"42"`, `"20260919"`, and a reported failing seed when one exists;
   capture the listed visual-band floors plus the lair's fixed arena/reward
   floors. Arrival cases are separate and must establish the normal unlock
   state.
4. Cover fixed boss and reward maps, then sample ordinary seeded floors across
   early, mid, and late routes. A generated floor is not evidence for a fixed
   map, and a fixed-map capture is not evidence for procedural generation.

## Camps and hubs

| Order | Runtime ground-map ID | Storyboard display name | Required fixture states | Focus |
| --- | --- | --- | --- | --- |
| C01 | `base_camp` | File Town | fresh; post-main-quest | Clockmon, Assembly, route visibility, return markers |
| C02 | `forest_camp` | Native Forest Camp | after `tropical_path`; progressed | survivor/NPC movement, outgoing paths |
| C03 | `cliff_camp` | Panorama Camp | after `faded_trail`; progressed | Falcomon reward role, routes, return marker |
| C04 | `canyon_camp` | Great Canyon Camp | after `flyaway_cliffs`; progressed | quarry routes and NPC state |
| C05 | `rest_stop` | Misty Shelter | after `thunderstruck_pass`; progressed | ridge/path routes and NPC state |
| C06 | `final_stop` | Freezeland Camp | after `veiled_ridge`; progressed | snowbound routes and NPC state |
| C07 | `guildmaster_summit` | Infinity Summit Relay | after `champions_road`; endgame | Guildmaster Trail/lair return handling |
| C08 | identifier discovery required | Dragon Eye Dock | after `copper_quarry` | map allocation and dock-route presentation |
| C09 | identifier discovery required | Stormwatch Relay | after `depleted_basin` | map allocation and pass-route presentation |
| C10 | identifier discovery required | Dino Survey Post | after `snowbound_path` | map allocation and approach-route presentation |

`base_camp_2`, `guild_path`, `guild_hut`, `luminous_spring`, and `post_office`
are verified generated map IDs, but their storyboard role/entry markers have
not yet been verified for this plan. Add them only after identifier discovery
records their intended use; do not treat a generated-map list as a route map.

### Existing camp layout POI crop coverage

The fixed seven-case layout fixture additionally captures live runtime
MapObject/marker POIs using `runtime-map-object-and-marker-v1`. It has a static
16-crop cap and preserves `layout`/`unreviewed`; it is not an arrival, story,
or interaction check. The 2026-09-19 evidence is
`work/visual-checks/camps-layout-poi-crops-20260919-1250/result.json`.

| Map ID | Eligible runtime POIs | Emitted crops | Truncated |
| --- | ---: | ---: | --- |
| `base_camp` | 11 | 11 | no |
| `forest_camp` | 24 | 16 | yes |
| `cliff_camp` | 19 | 16 | yes |
| `canyon_camp` | 54 | 16 | yes |
| `rest_stop` | 7 | 7 | no |
| `final_stop` | 7 | 7 | no |
| `guildmaster_summit` | 3 | 3 | no |

No map in this fixed set lacked crop-eligible live data. If one does in a later
fresh run, report its `no-crop-eligible-runtime-pois` metadata as evidence;
do not add a fabricated coordinate.

## Run-up and lair coverage

The pair IDs, names, and floor bands are verified in
`docs/phase3/storyboard_routes.json` and
`docs/phase3/DIGIMON_TILESET_ACCEPTANCE.csv`. Lair floor IDs are zero-based:
`6` is the fixed boss arena and `7` the generated reward floor.

| Pair | Run-up ID: rendered floor samples | Lair ID: rendered floor samples | Targeted visual checks |
| --- | --- | --- | --- |
| P01 Barbamon | `copper_quarry`: 1, 5, 9, 12 | `barbamon_lair`: 1, 4, 7, 8 | quarry depth shift; Clockwork Vault arena/reward readability |
| P02 Leviamon | `depleted_basin`: 1, 4, 8, 10 | `leviamon_lair`: 1, 4, 7, 8 | walkable floor versus water; Depths arena/reward |
| P03 Daemon | `thunderstruck_pass`: 1, 5, 9, 13 | `daemon_lair`: 1, 4, 7, 8 | rain/status contrast; Storm Crown arena/reward |
| P04 Lilithmon | `veiled_ridge`: 1, 5, 9, 13 | `lilithmon_lair`: 1, 4, 7, 8 | fog readability; Veil Palace arena/reward |
| P05 Belphemon | `snowbound_path`: 1, 5, 9, 13 | `sleeping_caldera`: 1, 3, 5, 7, 8 | cold-to-hot transition; arena/reward |
| P06 Lucemon | `champions_road`: 1, 5, 9, 13 | `lucemon_lair`: 1, 4, 7, 8 | pale-sprite/stair contrast; Observatory arena/reward |
| P07 Beelzemon | `guildmaster_trail`: 1, 5, 9, 13 | `beelzemon_lair`: 1, 4, 7, 8 | ascent-band readability; Citadel arena/reward |

The floor labels above are player-facing. The runner must resolve and record
the corresponding zero-based IDs from the generated segment before loading a
case; it must not assume display labels are identifiers.

### P01 resolved layout slice

The first bounded dungeon slice is complete and is limited to P01. Source
inspection and the engine results resolve these stable targets:

| Zone | Segment | Zero-based floor ID | Runtime map type | Seeds captured |
| --- | --- | --- | --- | --- |
| `copper_quarry` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `copper_quarry` | `0` | `11` | fixed exit (`end_copper_quarry`) | `"42"` |
| `barbamon_lair` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `barbamon_lair` | `0` | `6` | fixed arena (`end_treacherous_mountain`) | `"42"` |
| `barbamon_lair` | `0` | `7` | generated reward | `"42"`, `"20260919"` |

The source-controlled manifest is `tests/visual/p01-barbamon-layout.json`.
It records `debug-warp-layout-placement`; this proves renderer loading only,
not story access, combat, boss completion, rewards, or traversal. The first
run initially treated Copper Quarry floor `11` as seed-varying, but the live
map asset showed it is fixed; the final manifest captures it once.

The companion `tests/visual/p01-dungeon-poi-crops.json` covers only Copper
floor `11` and Barbamon floors `6` and `7` (seed `"42"` for the generated
reward floor). Its generic live categories are effect-tile exits/stairs, floor
items, and non-player actors; it does not hardcode species or map UI behavior.
The fresh run emitted 3, 5, and 7 POIs respectively without truncation. A
semantic boss or reward role is not exposed by the runtime map state, so the
evidence records only generic actor/item metadata and does not claim either
role. Every clean crop pixel-matched its full-map rectangle; overlay crops and
one inspected crop per selected map remain **unreviewed** layout evidence.

### P02--P07 fixed-context POI crop slice

`tests/visual/p02-p07-fixed-dungeon-poi-crops.json` is the single fixed
P02--P07 POI-crop manifest. Its generic selector applies only to documented
run-up terminal/rescue-reward contexts and lair arena/reward contexts; P01
remains separately controlled by its existing manifest. The static selection
table has 16 fresh-session cases: Depleted Basin floors `8` (generated rescue
layout) and `9` (fixed `end_depleted_basin` reward), Leviamon/Daemon/Lilithmon/
Caldera/Lucemon/Beelzemon lair floors `6` and `7`, plus Veiled Ridge and
Champions Road fixed terminal floors `12`.

Thunderstruck Pass, Snowbound Path, and Guildmaster Trail do not expose a
documented fixed terminal map: their terminal bands are generated, so no
synthetic fixed case is selected. This source reality is recorded directly in
the manifest. Floor `8` does not assert a spawned rescue NPC, and every lair
floor `7` remains a generated reward context; names describe the fixed
selection context rather than a semantic runtime POI role. The emitted POIs
remain generic effect-tile exits/stairs, floor items, and non-player actors.
All captures use debug placement and start as **unreviewed** layout evidence.
The final fresh-session report is
`work/visual-checks/p02-p07-dungeon-poi-crops-20260919-2204/result.json`;
its 16 cases passed native rectangle/pixel checks and its P02, P04, and P06
overlay crops were opened. This remains layout-only, **unreviewed** evidence.

### P02 resolved layout slice

The second bounded dungeon slice covers only P02: Depleted Basin and
Leviamon Lair. Source inspection and the engine results resolve these stable
targets:

| Zone | Segment | Zero-based floor ID | Runtime map type | Seeds captured |
| --- | --- | --- | --- | --- |
| `depleted_basin` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `depleted_basin` | `0` | `8` | generated rescue layout | `"42"`, `"20260919"` |
| `depleted_basin` | `0` | `9` | fixed reward (`end_depleted_basin`) | `"42"` |
| `leviamon_lair` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `leviamon_lair` | `0` | `6` | fixed arena (`end_treacherous_mountain`) | `"42"` |
| `leviamon_lair` | `0` | `7` | generated reward | `"42"`, `"20260919"` |

The source-controlled manifest is `tests/visual/p02-leviamon-layout.json`.
Floor `8` deliberately records only the generated rescue **layout**; direct
debug placement does not claim the quest NPC was spawned or that the rescue
was completable. As with P01, every capture records
`debug-warp-layout-placement`, and proves renderer loading only—not normal
access, combat, boss completion, reward logic, or traversal.

### P03 resolved layout slice

The third bounded dungeon slice covers only P03: Thunderstruck Pass and Daemon
Lair. Source inspection confirms that Thunderstruck Pass has thirteen authored
procedural floors (`0` through `12`) and no `LoadGen` terminal map. Its late
visual band is therefore captured as seeded generated layout rather than
inventing a fixed exit case.

| Zone | Segment | Zero-based floor ID | Runtime map type | Seeds captured |
| --- | --- | --- | --- | --- |
| `thunderstruck_pass` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `thunderstruck_pass` | `0` | `12` | generated late | `"42"`, `"20260919"` |
| `daemon_lair` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `daemon_lair` | `0` | `6` | fixed arena (`end_treacherous_mountain`) | `"42"` |
| `daemon_lair` | `0` | `7` | generated reward | `"42"`, `"20260919"` |

The source-controlled manifest is `tests/visual/p03-daemon-layout.json`.
Every capture records `debug-warp-layout-placement`, and proves renderer
loading only—not normal access, combat, boss completion, reward logic, or
traversal.

### P06 resolved layout slice

P06 covers only `champions_road` and `lucemon_lair`: Champions Road generated
floor `0` on seeds `"42"` and `"20260919"`, fixed terminal floor `12`
(`end_champions_road`), Lucemon Lair generated floor `0` on both seeds, fixed
arena floor `6` (`end_treacherous_mountain`), and generated reward floor `7`
on both seeds. The fixed source manifest is
`tests/visual/p06-lucemon-layout.json`; all cases are
`debug-warp-layout-placement`, layout-only, and **unreviewed**.

### P07 resolved layout slice

P07 covers only `guildmaster_trail` and `beelzemon_lair`. Source inspection
confirms Guildmaster Trail floors `0` and `12` are generated, so both retain
the declared decimal seeds. Beelzemon Lair floor `6` is the shared fixed arena
(`end_treacherous_mountain`), while floors `0` and `7` are generated.

| Zone | Segment | Zero-based floor ID | Runtime map type | Seeds captured |
| --- | --- | --- | --- | --- |
| `guildmaster_trail` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `guildmaster_trail` | `0` | `12` | generated late | `"42"`, `"20260919"` |
| `beelzemon_lair` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `beelzemon_lair` | `0` | `6` | fixed arena (`end_treacherous_mountain`) | `"42"` |
| `beelzemon_lair` | `0` | `7` | generated reward | `"42"`, `"20260919"` |

The source-controlled manifest is `tests/visual/p07-beelzemon-layout.json`.
Every capture records `debug-warp-layout-placement`, and proves renderer
loading only—not normal access, progression, boss completion, reward logic, or
traversal. All visual review remains **unreviewed**.

The fresh P07 suite passed on 2026-09-19. Each of the nine cases produced
nonempty viewport, full-map, overlay, state, checks, and HTML artifacts with
`renderer_capture: true`; the report is
`work/visual-checks/p07-beelzemon-layout-20260919-1500/result.json`. The
Guildmaster Trail early viewport and Beelzemon Lair arena viewport were opened
and show live DungeonScene terrain, party/UI, minimap, and entities. This is
engine-rendered layout evidence only; it does not change the unreviewed status
or establish progression, boss, reward, or traversal behavior.

### P05 resolved layout slice

P05 covers only Freezeland Path and Slumbering Caldera. Source inspection
confirms `snowbound_path` floors `0` through `12` are generated, so its early
and late layout samples both use the declared decimal seeds. The Caldera uses
the shared fixed arena on floor `6` and generated reward floor `7`.

| Zone | Segment | Zero-based floor ID | Runtime map type | Seeds captured |
| --- | --- | --- | --- | --- |
| `snowbound_path` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `snowbound_path` | `0` | `12` | generated late | `"42"`, `"20260919"` |
| `sleeping_caldera` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `sleeping_caldera` | `0` | `6` | fixed arena (`end_treacherous_mountain`) | `"42"` |
| `sleeping_caldera` | `0` | `7` | generated reward | `"42"`, `"20260919"` |

The fixed source manifest is `tests/visual/p05-belphemon-layout.json`.
Every capture is `debug-warp-layout-placement`, layout-only, and unreviewed.

### P04 resolved layout slice

The fourth bounded dungeon slice covers only P04: Veiled Ridge and Lilithmon
Lair. Source inspection confirms twelve generated Veiled Ridge floors (`0`
through `11`) followed by the fixed terminal `LoadGen` map on floor `12`.

| Zone | Segment | Zero-based floor ID | Runtime map type | Seeds captured |
| --- | --- | --- | --- | --- |
| `veiled_ridge` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `veiled_ridge` | `0` | `12` | fixed exit (`end_veiled_ridge`) | `"42"` |
| `lilithmon_lair` | `0` | `0` | generated early | `"42"`, `"20260919"` |
| `lilithmon_lair` | `0` | `6` | fixed arena (`end_treacherous_mountain`) | `"42"` |
| `lilithmon_lair` | `0` | `7` | generated reward | `"42"`, `"20260919"` |

The source-controlled manifest is `tests/visual/p04-lilithmon-layout.json`.
Every capture records `debug-warp-layout-placement`, and proves renderer
loading only—not normal access, combat, boss completion, reward logic, or
traversal.

### Resolved run-up visual-band slice

The P01–P07 endpoint/layout captures already retain each run-up's floor-zero
entry and terminal/fixed-map evidence. The remaining player-facing visual-band
gap is therefore a single narrow layout-only suite: two intermediate bands per
run-up, each launched with the decimal-string seed `"42"`. The source-controlled
manifest is `tests/visual/runup-visual-bands-layout.json`; the wrapper accepts
only that manifest and its static 14-case table.

| Pair | Zone | Displayed bands | Zero-based IDs | Source map type |
| --- | --- | --- | --- | --- |
| P01 | `copper_quarry` | 5F, 9F | `4`, `8` | generated; floor `11` remains the separately covered fixed exit |
| P02 | `depleted_basin` | 4F, 8F | `3`, `7` | generated; floor `9` remains the separately covered fixed reward |
| P03 | `thunderstruck_pass` | 5F, 9F | `4`, `8` | generated; all authored primary floors are procedural |
| P04 | `veiled_ridge` | 5F, 9F | `4`, `8` | generated; floor `12` remains the separately covered fixed exit |
| P05 | `snowbound_path` | 5F, 9F | `4`, `8` | generated |
| P06 | `champions_road` | 5F, 9F | `4`, `8` | generated; floor `12` remains the separately covered fixed exit |
| P07 | `guildmaster_trail` | 5F, 9F | `4`, `8` | generated |

No lair, floor-zero endpoint, terminal, arena, or reward case is duplicated by
this suite. Every artifact records the requested zone, segment `0`, zero-based
floor ID, seed, `debug_placement: "debug-placement"`, `mode: "layout"`, and
`unreviewed` review status. It is renderer layout evidence only and makes no
claim about access, progression, combat, rewards, or traversal.

The historical 2026-09-19 seed-42 report at
`work/visual-checks/runup-visual-bands-layout-20260919-1700/result.json` is
preserved, but is superseded for seed-validity use because it predates
DebugWarp seed preservation and logical-layout fingerprint reporting. The
refreshed seed-42 report is
`work/visual-checks/runup-visual-bands-layout-20260919-seed42-fingerprint-refresh-r2/result.json`:
all 14 cases have complete artifacts/state, `debug-placement`, `layout`,
`unreviewed`, and logical-layout fingerprints. This intermediate suite emits
no POI crops; each state/check record reports an empty crop selection.

### Intermediate run-up second seed selection

The same fixed intermediate-only selection has a separate second-seed evidence
pass at decimal-string seed `"20260919"`:
`tests/visual/runup-visual-bands-seed-20260919-layout.json`. It retains the
same seven zones, segment `0`, and zero-based IDs in the table above; it does
not add endpoints, floor-zero cases, terminals, arenas, rewards, or lairs.
The distinct static selector and wrapper preserve seed-42 evidence rather than
superseding it. Both evidence sets are selected in the catalog only as
unreviewed debug-placement layout records.

The fresh report is
`work/visual-checks/runup-visual-bands-seed-20260919-layout-20260919-seed2-evidence/result.json`.
All 14 cases passed engine artifact/state checks. The opened Copper Quarry
floor `4`, Veiled Ridge floor `8`, and Guildmaster Trail floor `4` viewports
are live engine captures; their review status remains **unreviewed**.

The metadata-only comparison at
`work/visual-checks/runup-visual-bands-seed-fingerprint-comparison-20260919-refresh/result.json`
matches exact zone/segment/floor records from the refreshed seed-42 report and
this final seed-20260919 report. It observed 0 equal, 14 different, and 0
unsupported logical-layout fingerprints. It does not compare screenshots or
approve any image. The refreshed 28-case selection catalog is
`work/visual-checks/runup-visual-bands-seed-validity-catalog-20260919-refresh/`;
all entries remain **unreviewed**.

### Intermediate run-up third seed selection

The remaining declared deterministic sample is decimal-string seed `"424242"`.
It is an ordinary selected seed, not a reported failing seed. Its isolated,
source-controlled manifest is
`tests/visual/runup-visual-bands-seed-424242-layout.json`; the matching
controller selector and narrow wrapper accept only this 14-case table.

Source inspection and the endpoint coverage above retain the same primary
segment (`0`) intermediate generated slice: Copper Quarry, Thunderstruck Pass,
Veiled Ridge, Snowbound Path, Champions Road, and Guildmaster Trail use IDs
`4` and `8`; Depleted Basin uses `3` and `7`. Those are the two documented
intermediate visual bands for every route. They retain the coverage-plan
middle-to-late-middle transition while excluding floor zero, fixed
exits/rewards, lairs, arenas, and endpoints.

Every case records standard engine artifacts, `logical-layout-v1` SHA-256
metadata, `debug-placement`, `layout`, and `unreviewed`. This is engine
renderer layout evidence only; it does not prove access, progression, combat,
reward behavior, traversal, or visual approval.

The fresh third-seed run is
`work/visual-checks/runup-visual-bands-seed-424242-layout-20260919-third-seed-complete/result.json`:
all 14 cases exited `0` with the standard nonempty engine artifacts and valid
logical fingerprints. Copper Quarry ID `4` and Guildmaster Trail ID `8`
viewports were opened as mid- and late-route live engine checks. They remain
**unreviewed**. The one-report review catalog is
`work/visual-checks/runup-visual-bands-seed-424242-layout-catalog-20260919-third-seed-complete/`.

### Early seeded routes resolved layout suite

The documented early seeded sample is one static, source-controlled 27-case
layout suite: `tests/visual/early-seeded-routes-layout.json`. The controller
and its narrow wrapper accept only that case table. It selects the primary
playable segment (`0`) from the installed source definitions under
`DumpAsset/Data/Zone/`; it does not use player-facing floor labels as IDs.

| Zone | Primary segment source floor IDs | First / middle / last selected IDs | Map source kind |
| --- | --- | --- | --- |
| `tropical_path` | `0`–`3` | `0` / `2` / `3` | `GridFloorGen` |
| `faded_trail` | `0`–`6` | `0` / `3` / `6` | `GridFloorGen` |
| `faultline_ridge` | `0`–`9` | `0` / `5` / `9` | `GridFloorGen` |

For even-length primary segments, **middle** is `floor_count / 2`, the upper
central zero-based floor. The three declared decimal-string seeds are `"42"`,
`"20260919"`, and `"424242"`; `424242` is the selected deterministic third
seed, not a reported failing seed. All 27 cases are generated source maps, so
every declared seed is retained rather than collapsed to a fixed-map capture.

This suite records debug placement (`debug-placement`), `layout`, and
**unreviewed** only. Its preserved original report has no crop selector. The
separate `early-seeded-routes-dungeon-poi-crops` manifest reruns the exact same
27 cases with the opt-in generic runtime selector (`exit`, `stairs`, `item`,
`actor`), a 16-crop cap, native clean/overlay crops, and selection/truncation
metadata. It does not infer route, species, boss, rescue, reward, or
progression semantics. The evidence does not establish normal access,
progression, combat, reward behavior, or traversal.

The fresh 2026-09-19 pass is
`work/visual-checks/early-seeded-routes-layout-20260919-fresh/result.json`.
All 27 fresh sessions produced nonempty standard artifacts and valid
`logical-layout-v1` fingerprints. Tropical Path floor `0` (`"42"`), Faded
Trail floor `3` (`"20260919"`), and Faultline Ridge floor `9` (`"424242"`)
viewports were opened and show live DungeonScene terrain, party UI, minimap,
and entities. Their review state remains **unreviewed**. The local 27-entry
catalog is `work/visual-checks/early-seeded-routes-layout-catalog-20260919-fresh/`.

## Fixed-map and seeded-floor cases

| Case group | Verified target | Required evidence |
| --- | --- | --- |
| Lair arena | each P01–P07 lair, floor ID `6` | boss object/team bounds, entrance/stairs, collision approach, normal arrival state |
| Lair reward | each P01–P07 lair, floor ID `7` | reward object bounds, exits, loot placement, normal post-boss state |
| Dragon Eye rescue/reward | `depleted_basin`, segment `0`, floor IDs `8` and `9` | rescue NPC only on floor `8`; reward-map presentation and no rescue NPC on floor `9` |
| Other fixed boss/reward maps | identifier discovery required | enumerate `LoadGen`/fixed-map references, then add stable map ID, segment/floor ID, source event, and unlock fixture |
| Early seeded sample | `tropical_path`, `faded_trail`, `faultline_ridge` | static 27-case first/middle/last primary-segment layout suite for all three declared seeds |
| Mid seeded sample | `copper_quarry`, `depleted_basin`, `thunderstruck_pass`, `veiled_ridge` | one floor from each visual band for all three declared seeds |
| Late seeded sample | `snowbound_path`, `champions_road`, `guildmaster_trail` | one floor from each visual band for all three declared seeds |

For every captured exit, the overlay must identify the target object/marker and
the case must record a reachable player-footprint approach. A structural pass,
render capture, visual review, and normal traversal are separate outcomes. All
new cases begin with `visual_review: unreviewed` until an actual reviewer has
inspected the native PNGs.

## Lair generated-floor declared-seed refresh

The seven historical P01--P07 layout reports remain preserved as records of
their original captures:

| Pair | Historical report | Generated-floor evidence superseded for declared-seed use |
| --- | --- | --- |
| P01 | p01-barbamon-layout-20260919-1110 | barbamon_lair floors 0 and 7 on "42" and "20260919" |
| P02 | p02-leviamon-layout-20260919-1200 | leviamon_lair floors 0 and 7 on "42" and "20260919" |
| P03 | p03-daemon-layout-20260919-1230 | daemon_lair floors 0 and 7 on "42" and "20260919" |
| P04 | p04-lilithmon-layout-20260919-1300 | lilithmon_lair floors 0 and 7 on "42" and "20260919" |
| P05 | p05-belphemon-layout-20260919-1330 | sleeping_caldera floors 0 and 7 on "42" and "20260919" |
| P06 | p06-lucemon-layout-20260919-1400 | lucemon_lair floors 0 and 7 on "42" and "20260919" |
| P07 | p07-beelzemon-layout-20260919-1500 | beelzemon_lair floors 0 and 7 on "42" and "20260919" |

Those historical results predate the DebugWarp seed-preservation correction
and do not provide fresh logical-layout fingerprint evidence for declared-seed
use. They are not deleted and their non-generated cases, including every fixed
arena floor 6, remain historical evidence only.
The fixed refresh manifest is tests/visual/lair-generated-floor-seed-refresh.json.
Source verification in DataGenerator/Data/Zones/ZoneInfoPhase3.cs shows segment 0 appends generated GridFloorGen floors 0 through 5, one fixed LoadGen arena at floor 6, and the generated reward GridFloorGen at floor 7.
The refresh contains exactly 28 fresh sessions: P01--P07, each lair floors 0 and 7, each on decimal-string seeds "42" and "20260919". It selects no run-up map and does not rerun the fixed arena.
Every case retains standard native artifacts and reports logical-layout-v1, debug-placement, layout, and unreviewed. The per-lair/floor cross-seed summary compares only logical-layout fingerprints with image_comparison: not-performed; it does not claim visual approval, normal access, progression, combat, reward behavior, or traversal.
The fresh report is work/visual-checks/lair-generated-floor-seed-refresh-20260919/result.json: all 28 cases passed and its metadata-only summary found 0 equal and 14 different fingerprints. The 28-entry unreviewed catalog is work/visual-checks/lair-generated-floor-seed-refresh-catalog-20260919/; Barbamon and Slumbering Caldera entry/reward viewports were opened.
