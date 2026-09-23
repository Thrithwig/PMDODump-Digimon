# Test Camp visual pilot runbook

This is a lab-only visual playtest fixture. Do not copy its generated data or
profiles into the primary playtest tree without an approved copy-back review.

## Build and generate

Run these commands from the `digimon-agent-lab` root:

```powershell
$labRoot = (Get-Location).Path
$publishedAsset = Join-Path $labRoot 'PMDC\publish\win-x64\PMDC'
$generatorRoot = Join-Path $labRoot 'DataGenerator\bin\Debug\net8.0'
$generatorAsset = [IO.Path]::GetRelativePath($generatorRoot, $publishedAsset) + '\'
dotnet build DataGenerator\DataGenerator.csproj --no-restore
dotnet build PMDC\PMDC\PMDC.csproj --no-restore
dotnet publish -c Release -r win-x64 PMDC\PMDC\PMDC.csproj --no-restore
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset $generatorAsset -test-camp
```

`$publishedAsset` is the same published PMDC asset directory used by the launch
command below. The generator resolves `-asset` from its own executable folder,
so `$generatorAsset` converts that lab-root path to the required relative form.

`-test-camp` regenerates Test Camp's map, ground map, optional power status,
and the unreleased `test_camp_fixture` zone in the **lab publish** data. The
fixture contains only `base_camp` and `test_camp`; it is not a story route,
does not appear as released content, and does not alter normal zone generation.

## Run a fresh pilot

Use a new child directory for each session. `-playtest` requires both `-dev`
and an explicit `-appdata`, and the session must be beneath that app-data root.

```powershell
$labRoot = (Get-Location).Path
$labAppData = Join-Path $labRoot 'work\playtest-profiles'
$labSession = Join-Path $labAppData 'test-camp-YYYYMMDD-HHMMSS'
New-Item -ItemType Directory -Force -Path $labSession | Out-Null
$exe = Join-Path $labRoot 'PMDC\publish\win-x64\PMDC\PMDC.exe'
$asset = Join-Path $labRoot 'PMDC\publish\win-x64\PMDC'
& $exe -dev -asset $asset -appdata $labAppData -playtest $labSession -playtest-test-camp
```

The fresh-profile fixture initializes its language to `en`, waits for a settled
TitleScene, enters Test Camp through the normal fixture-zone path, captures the
ground scene, then sends a bounded Down input through the ordinary FrameInput
queue. It never calls the exit Lua function directly.

### Unattended CI-style pilot

For a bounded unattended lab run, add `-playtest-exit-on-complete` to the same
command. The flag is rejected unless all of `-dev`, `-playtest`, and
`-playtest-test-camp` are present. It requests the normal game-loop shutdown
only after `state.json`, `checks.json`, and `index.html` have been written,
whether traversal succeeds or a bounded pilot failure is recorded. It has no
effect on ordinary manual `-playtest` sessions.

```powershell
& $exe -dev -asset $asset -appdata $labAppData -playtest $labSession -playtest-test-camp -playtest-exit-on-complete
```

### Single-case wrapper

`Scripts/digimon_visual_checks.py` is a deliberately narrow Milestone B
wrapper, not a broad dungeon runner. It accepts only the source-controlled
`tests/visual/test-camp.json` Test Camp case, starts the published executable
with the flags above, and validates PMDC's engine-rendered artifacts after the
unattended process exits. It does not render tiles or inject operating-system
input. The wrapper writes only its result report beneath `work/visual-checks`;
PMDC's disposable session and rendered artifacts remain beneath
`work/playtest-profiles`.

```powershell
python Scripts/digimon_visual_checks.py tests/visual/test-camp.json `
  --output work/visual-checks/test-camp-YYYYMMDD-HHMMSS
```

`result.json` records the profile artifact path, renderer/traversal checks, and
the required `visual_review: unreviewed` status. It never overwrites a nonempty
output directory.

### Local file-adapter smoke

The adapter smoke is a separate, source-controlled proof that an atomic JSON
request reaches the ordinary game-loop input queue. Its protocol and safety
bounds are in [PLAYTEST_FILE_ADAPTER_PROTOCOL.md](PLAYTEST_FILE_ADAPTER_PROTOCOL.md).
It starts a fresh lab session, waits for Test Camp, requests one live viewport
capture, sends `Down` through the adapter, then observes Base Camp before clean
exit:

```powershell
python Scripts/digimon_playtest_adapter_smoke.py `
  --output work/visual-checks/adapter-smoke-YYYYMMDD-HHMMSS `
  --timeout-seconds 45
```

This smoke is deliberately narrower than a dungeon runner. Its report and
capture remain **unreviewed** even when the process exits successfully.

`tests/test_playtest_adapter_safety.py` statically verifies that normal launches
cannot configure the controller: `-playtest` requires `-dev`, explicit
`-appdata`, and a contained session directory, while capture pilots without
`-playtest` are rejected. It also verifies that DungeonScene POI selection is
limited to the fixed P01/P02--P07 and exact 27-case early-route tables.

### Base Camp arrival-fixture foundation

`tests/visual/camp-arrival-fixture-base-new-save.json` names the sole initial
arrival case, `base-new-save`. In a new disposable app-data child, record it
with `-playtest-camp-arrival-fixture base-new-save` and then use
`-playtest-camp-arrival-resume base-new-save` with the same profile to exercise
the title save loader. Both commands require `-dev`, explicit `-appdata`,
`-playtest`, and may use `-playtest-exit-on-complete`.

The recorder follows the title flow's new-save destination through the normal
ground lifecycle and serializes `SAVE/SAVE.rssv`; the resume mode follows the
ordinary title main-save loader. After that restored arrival is stable, the
existing native capture service writes one viewport and one full-map image.
It writes a profile-local `fixture.json` and session
`artifacts/camp-arrival/base-new-save/record-provenance.json`,
`resume-provenance.json`, `resume-state.json`, and `resume-checks.json`.
The images and metadata remain **unreviewed** debug-placement/layout evidence;
they do not capture later camps or claim route traversal.

## Existing camp layout captures

`tests/visual/camps-layout.json` is the bounded layout-only camp set. The IDs
were verified from `DataGenerator/Data/Zones/MapInfo.cs` and the authored
published ground data:

| Display role | Stable ground map ID |
| --- | --- |
| Base Camp | `base_camp` |
| Forest Camp | `forest_camp` |
| Cliff Camp | `cliff_camp` |
| Ravine Camp | `canyon_camp` |
| Cave Shelter | `rest_stop` |
| Blizzard Camp | `final_stop` |
| Guildmaster Summit | `guildmaster_summit` |

Generate the additional lab-only fixture after publishing:

```powershell
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll `
  -asset $generatorAsset -camp-layout-fixture
```

The fixture contains only those already-authored ground maps. A capture starts
one fresh PMDC process per map and enters it through the normal ground-scene
lifecycle with declared `fixture-zone-debug-placement`. This is intentionally
**not** story access, quest validation, route traversal, or an NPC-state
review. It never changes a map, story flag, or regular zone.

```powershell
python Scripts/digimon_camp_layout_checks.py tests/visual/camps-layout.json `
  --output work/visual-checks/camps-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 30
```

Each session produces `viewport.png`, `map.png`, `overlay.png`, `state.json`,
`checks.json`, and an individual HTML sheet beneath
`work/playtest-profiles/<session>/artifacts/camp-layout/<map-id>/`. The wrapper
adds an aggregate contact-sheet index beside its result JSON. Every result must
remain `mode: layout` and `visual_review: unreviewed`; use a separate arrival
case before treating a camp route as playable.

### Runtime camp POI crops

The seven fixed camp cases also use the source-controlled
`poi_crop_selector` in `tests/visual/camps-layout.json`. It enumerates the
loaded map's enabled, named runtime `GroundObject` and `GroundMarker` entities
in stable kind/name order. It does not supply coordinates or a per-camp entity
list. Each selected entity receives a clean native 1:1 crop and matching
engine-overlay crop under `crops/`, with runtime bounds, requested bounds,
clamped bounds, source texture, and paths recorded in both `state.json` and
`checks.json`.

The cap is 16 POIs per camp with 64 pixels of context. `poi_crop_selection`
records the eligible count, selected count, and `truncated` flag. A map with no
eligible runtime object or marker remains a valid layout capture and records
`no-crop-eligible-runtime-pois`; the runner never invents a crop point. The
wrapper validates every emitted clean PNG against the matching `map.png`
rectangle pixel-for-pixel and checks the overlay artifact separately.

These artifacts are fixture-zone debug placement only. They remain `layout`
and `unreviewed`, and do not establish story access, NPC arrangements,
traversal, progression, or interactions.

## P01 Barbamon dungeon layout captures

The only dungeon layout runner currently implemented is the fixed P01 pair:
Copper Quarry and Barbamon's Clockwork Vault. It accepts only
`tests/visual/p01-barbamon-layout.json`, starts a fresh process for each case,
and uses `DebugWarp` solely as declared layout placement. It does not simulate
route entry, quest flags, battle completion, or reward collection.

```powershell
python Scripts/digimon_p01_dungeon_layout_checks.py `
  tests/visual/p01-barbamon-layout.json `
  --output work/visual-checks/p01-barbamon-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

Each P01 artifact records zone ID, segment `0`, zero-based floor ID,
decimal-string seed, map type, observed zone/map asset, tile position, capture
results, `mode: layout`, and `visual_review: unreviewed`. The source-resolved
floor/asset table is in [VISUAL_COVERAGE_PLAN.md](VISUAL_COVERAGE_PLAN.md).
No other dungeon IDs or arbitrary manifests are accepted by this runner.

### P01 fixed-map dungeon POI crops

`tests/visual/p01-dungeon-poi-crops.json` is a second, source-controlled
contract consumed by the existing P01 wrapper. It opts in only the verified
Copper Quarry fixed exit (`copper-f11-s42`) and Barbamon Lair fixed arena and
reward (`barbamon-f6-s42`, `barbamon-f7-s42`). It does not add a command-line
selector or an arbitrary dungeon runner.

After `BaseDungeonScene` writes the engine-rendered `map.png`, it snapshots
that live native full-map texture on the graphics-owning draw thread and makes
clamped 1:1 clean and overlay crops beneath `crops/`. Runtime POIs are sorted
by category, runtime ID, and tile position; the selector has a 16-crop cap and
64 pixels of context. It recognizes only live effect-tile stairs/exits, floor
items, and non-player actors. DungeonScene does not expose a semantic
boss/reward role, so those labels are not inferred and no callback is invoked.
`state.json` and `checks.json` retain the category metadata, native bounds,
requested/clamped bounds, selection count, truncation/no-eligible state, and
source links. The wrapper pixel-compares every clean crop with the recorded
`map.png` rectangle and checks the overlay independently.

Fresh layout-only evidence is
`work/visual-checks/p01-dungeon-poi-crops-20260919-1905/result.json`.
Copper's fixed exit emitted two items and one `stairs_go_up`; the fixed arena
emitted five actors; the reward floor on seed `"42"` emitted six items and one
`stairs_go_up`. One overlay crop from each map was opened. All results remain
`debug-placement`, `layout`, and **unreviewed**; they do not establish access,
combat, boss identity, reward collection, or traversal.

### P02--P07 fixed-context dungeon POI crops

`tests/visual/p02-p07-fixed-dungeon-poi-crops.json` and
`Scripts/digimon_p02_p07_dungeon_poi_crops.py` extend the same generic
DungeonScene crop facility through one static P02--P07 selector table. P01 is
not included or rerun. One fresh lab PMDC session is started for each of the
16 declared contexts:

```powershell
python Scripts/digimon_p02_p07_dungeon_poi_crops.py `
  tests/visual/p02-p07-fixed-dungeon-poi-crops.json `
  --output work/visual-checks/p02-p07-dungeon-poi-crops-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

The manifest includes Depleted Basin floor `8` as its documented generated
rescue-layout context and floor `9` as its fixed `end_depleted_basin` reward
map; it does not claim that a rescue NPC is present. It includes the fixed
run-up terminals on Veiled Ridge floor `12` (`end_veiled_ridge`) and Champions
Road floor `12` (`end_champions_road`). Thunderstruck Pass, Snowbound Path,
and Guildmaster Trail have generated run-up terminal bands in the documented
source, so the manifest records those omissions rather than fabricating fixed
cases. Every lair includes floor `6` fixed-arena and floor `7`
generated-reward context exactly once.

The selector remains limited to live effect-tile exits/stairs, floor items,
and non-player actors, with deterministic category/generic-ID/tile ordering,
a 16-crop cap, and 64 pixels of context. It does not select by species or
infer boss, rescue, or reward semantics. For each emitted crop the wrapper
checks the reported clamped rectangle, native 1:1 clean and overlay dimensions,
and an exact clean-pixel comparison with the engine's `map.png`. Empty live
category results remain `no-crop-eligible-runtime-pois`; they are reported,
not replaced with guessed coordinates. All reports and images are
`debug-placement`, `layout`, and **unreviewed**.

## P02 Leviamon dungeon layout captures

The second bounded dungeon layout runner accepts only the fixed P02 pair:
Depleted Basin and Leviamon Lair. It starts a fresh process for each declared
case and uses `DebugWarp` only for the explicitly recorded layout placement.
It does not validate normal route entry, quest state, rescue NPC spawning,
battle completion, or reward collection.

```powershell
python Scripts/digimon_p02_dungeon_layout_checks.py `
  tests/visual/p02-leviamon-layout.json `
  --output work/visual-checks/p02-leviamon-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

Each P02 artifact records the requested zone ID, segment `0`, zero-based floor
ID, decimal-string seed, map type, observed zone/map asset, tile position,
renderer capture results, `mode: layout`, and `visual_review: unreviewed`.
The source-resolved floor/asset table is in
[VISUAL_COVERAGE_PLAN.md](VISUAL_COVERAGE_PLAN.md). No arbitrary maps or
additional dungeon pairs are accepted by this runner.

## P06 Lucemon dungeon layout captures

```powershell
python Scripts/digimon_p06_dungeon_layout_checks.py `
  tests/visual/p06-lucemon-layout.json `
  --output work/visual-checks/p06-lucemon-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

This fixed runner accepts only the eight P06 cases. It records debug placement
and renderer output; it does not validate normal route access, quests, bosses,
or rewards. Every result remains `layout` and `unreviewed`.

## P07 Beelzemon dungeon layout captures

```powershell
python Scripts/digimon_p07_dungeon_layout_checks.py `
  tests/visual/p07-beelzemon-layout.json `
  --output work/visual-checks/p07-beelzemon-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

This fixed runner accepts only the nine P07 cases: Guildmaster Trail generated
floors `0` and `12` on seeds `"42"` and `"20260919"`, plus Beelzemon Lair
generated floor `0` and reward floor `7` on both seeds and fixed arena floor
`6` once. It uses declared debug placement only; it does not validate normal
route access, progression, bosses, rewards, or traversal. Every result remains
`layout` and `unreviewed`.

The 2026-09-19 run passed all nine cases. Its aggregate report is
`work/visual-checks/p07-beelzemon-layout-20260919-1500/result.json`; it points
to separate disposable profiles and PMDC-rendered artifacts for each case.
The Guildmaster Trail floor-0 viewport and Beelzemon fixed-arena viewport were
opened during validation and show live DungeonScene terrain, party/UI,
minimap, and entities. They remain **unreviewed** and do not validate route
access, progression, boss or reward behavior, or traversal.

## P05 Belphemon dungeon layout captures

The fixed P05 runner accepts only Freezeland Path and Slumbering Caldera.
It uses declared debug placement only; it does not validate progression,
battles, rewards, or routes.

```powershell
python Scripts/digimon_p05_dungeon_layout_checks.py `
  tests/visual/p05-belphemon-layout.json `
  --output work/visual-checks/p05-belphemon-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

Artifacts record the requested IDs, seed, map type, observed map, captures,
`mode: layout`, and `visual_review: unreviewed`. The verified floor table is
in [VISUAL_COVERAGE_PLAN.md](VISUAL_COVERAGE_PLAN.md).

## P04 Lilithmon dungeon layout captures

The fourth bounded dungeon layout runner accepts only P04: Veiled Ridge and
Lilithmon Lair. It starts a fresh process for each declared case and uses
`DebugWarp` only for the explicitly recorded layout placement. Veiled Ridge
floor `12` loads its source-authored terminal map `end_veiled_ridge`.

```powershell
python Scripts/digimon_p04_dungeon_layout_checks.py `
  tests/visual/p04-lilithmon-layout.json `
  --output work/visual-checks/p04-lilithmon-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

Each P04 artifact records the requested zone ID, segment `0`, zero-based floor
ID, decimal-string seed, map type, observed zone/map asset, tile position,
renderer capture results, `mode: layout`, and `visual_review: unreviewed`.
The source-resolved floor/asset table is in
[VISUAL_COVERAGE_PLAN.md](VISUAL_COVERAGE_PLAN.md). No arbitrary maps or
additional dungeon pairs are accepted by this runner.

## P03 Daemon dungeon layout captures

The third bounded dungeon layout runner accepts only P03: Thunderstruck Pass
and Daemon Lair. It starts a fresh process for each declared case and uses
`DebugWarp` only for the explicitly recorded layout placement. Thunderstruck
Pass has no source-authored fixed terminal map, so the fixed case in this pair
is Daemon Lair's shared arena only.

```powershell
python Scripts/digimon_p03_dungeon_layout_checks.py `
  tests/visual/p03-daemon-layout.json `
  --output work/visual-checks/p03-daemon-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

Each P03 artifact records the requested zone ID, segment `0`, zero-based floor
ID, decimal-string seed, map type, observed zone/map asset, tile position,
renderer capture results, `mode: layout`, and `visual_review: unreviewed`.
The source-resolved floor/asset table is in
[VISUAL_COVERAGE_PLAN.md](VISUAL_COVERAGE_PLAN.md). No arbitrary maps or
additional dungeon pairs are accepted by this runner.

## Intermediate run-up visual-band captures

`tests/visual/runup-visual-bands-layout.json` and
`Scripts/digimon_runup_visual_band_checks.py` close only the documented
intermediate run-up bands. The wrapper rejects every other manifest and starts
one fresh PMDC process per case. It does not cover lairs, endpoints, terminal
maps, arenas, rewards, traversal, combat, or progression.

```powershell
python Scripts/digimon_runup_visual_band_checks.py `
  tests/visual/runup-visual-bands-layout.json `
  --output work/visual-checks/runup-visual-bands-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

The fixed 14-case table uses segment `0`, the exact source-verified zero-based
middle floors (`4`/`8` except Depleted Basin `3`/`7`), and the decimal string
seed `"42"`. Each artifact root contains engine-rendered `viewport.png`,
`map.png`, `overlay.png`, `state.json`, `checks.json`, and `index.html`.
`state.json` and `checks.json` record `debug_placement: "debug-placement"`,
`mode: "layout"`, and `unreviewed`; this is debug placement evidence only.

The historical 2026-09-19 report
`work/visual-checks/runup-visual-bands-layout-20260919-1700/result.json` is
preserved but superseded for seed-validity use: it predates DebugWarp seed
preservation and did not carry logical-layout fingerprints. Use the refreshed
report instead:
`work/visual-checks/runup-visual-bands-layout-20260919-seed42-fingerprint-refresh-r2/result.json`.
It passed all 14 fresh, compact-profile sessions with nonempty standard
artifacts, state/check `debug-placement`, `layout`, `unreviewed`, and valid
logical-layout fingerprints. Intermediate-band cases intentionally emit no
POI crops, recorded as an empty crop selection in every state/check report.

## Intermediate run-up visual-band second seed

`tests/visual/runup-visual-bands-seed-20260919-layout.json` and
`Scripts/digimon_runup_visual_band_seed_20260919_checks.py` provide a separate
fixed 14-case pass for the same intermediate generated bands on decimal-string
seed `"20260919"`. The original seed-42 manifest, selector, runner, and
evidence remain unchanged. The wrapper accepts only this second-seed manifest,
uses the separate `-playtest-runup-band-seed-20260919-layout` static selector,
and starts one fresh lab PMDC process per case.

```powershell
python Scripts/digimon_runup_visual_band_seed_20260919_checks.py `
  tests/visual/runup-visual-bands-seed-20260919-layout.json `
  --output work/visual-checks/runup-visual-bands-seed-20260919-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

The selection remains only segment `0` and the source-verified zero-based
intermediate IDs (`4`/`8`, except Depleted Basin `3`/`7`). It contains no
floor-zero, terminal, fixed arena, fixed reward, endpoint, or lair case. Each
artifact remains debug-placement, layout-only, and **unreviewed**.

The fresh second-seed pass is
`work/visual-checks/runup-visual-bands-seed-20260919-layout-20260919-seed2-evidence/result.json`.
All 14 cases exited 0 and recorded the required nonempty engine artifacts.
Copper Quarry floor `4`, Veiled Ridge floor `8`, and Guildmaster Trail floor
`4` viewport PNGs were opened. They show live DungeonScene terrain, party/UI,
minimap, and entities, but no visual approval, traversal, access, progression,
combat, or reward claim is made.

### Seed fingerprint comparison

Run this after the refreshed seed-42 pass and the final seed-20260919 report
exist. It compares only state metadata for exact zone/segment/floor matches;
it never opens, hashes, or pixel-diffs PNG files.

```powershell
python Scripts/digimon_runup_seed_fingerprint_comparison.py `
  --seed42-report work/visual-checks/<refreshed-seed42>/result.json `
  --seed20260919-report work/visual-checks/runup-visual-bands-seed-20260919-layout-20260919-seed2-evidence/result.json `
  --output work/visual-checks/runup-visual-bands-seed-fingerprint-comparison-YYYYMMDD-HHMMSS
```

The 2026-09-19 refresh report observed 0 equal, 14 different, and 0
unsupported fingerprints in
`work/visual-checks/runup-visual-bands-seed-fingerprint-comparison-20260919-refresh/result.json`.
It makes no visual-review or image-comparison claim. The historical seed-42
`1700` report remains available as evidence but is superseded only for
seed-validity comparisons.

## Intermediate run-up visual-band third seed

Run the deterministic seed `"424242"` suite after publishing PMDC:

```powershell
python Scripts/digimon_runup_visual_band_seed_424242_checks.py `
  tests/visual/runup-visual-bands-seed-424242-layout.json `
  --output work/visual-checks/runup-visual-bands-seed-424242-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

The wrapper accepts only the fixed 14 cases in its manifest and starts a fresh
lab-owned PMDC session per case. It retains source-verified segment `0` IDs
`4`/`8` for Copper Quarry, Thunderstruck Pass, Veiled Ridge, Snowbound Path,
Champions Road, and Guildmaster Trail, plus `3`/`7` for Depleted Basin. They
are the coverage plan's middle and late-middle generated bands, preserving the
documented transition without adding endpoints, fixed terminal/reward maps,
arenas, lairs, or floor-zero cases.

`424242` is a selected deterministic sample, not a failure label. Required
artifacts are nonempty engine-native `viewport.png`, `map.png`, `overlay.png`,
`state.json`, `checks.json`, and `index.html`; each result also validates a
`logical-layout-v1` SHA-256 fingerprint. All evidence remains
`debug-placement`, `layout`, and **unreviewed**. It does not establish normal
access, progression, traversal, combat, rewards, or visual approval.

The fresh run is
`work/visual-checks/runup-visual-bands-seed-424242-layout-20260919-third-seed-complete/result.json`.
It passed all 14 fresh sessions. Copper Quarry floor ID `4` and Guildmaster
Trail floor ID `8` viewport PNGs were opened; each is a live DungeonScene
capture with terrain, party/UI, minimap, and entities, and remains
**unreviewed**. Its local one-report catalog is
`work/visual-checks/runup-visual-bands-seed-424242-layout-catalog-20260919-third-seed-complete/`.

## Early seeded route layout suite

Run this one fixed source-controlled suite after publishing PMDC:

```powershell
& C:/Users/arlet/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe `
  Scripts/digimon_early_seeded_routes_visual_checks.py `
  tests/visual/early-seeded-routes-layout.json `
  --output work/visual-checks/early-seeded-routes-layout-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

The wrapper rejects every other manifest and starts one fresh disposable lab
session per static case. Its engine selector accepts only Tropical Path,
Faded Trail, and Faultline Ridge primary segment `0`: respectively source
floor IDs `0/2/3`, `0/3/6`, and `0/5/9` for first/middle/last. These are
zero-based engine IDs, not display floor labels. For the even-length Tropical
and Faultline segments, middle is the upper central ID (`floor_count / 2`).

The matrix has exactly 27 cases: three routes × three selected floors × the
decimal-string seeds `"42"`, `"20260919"`, and `"424242"`. `424242` is the
documented deterministic third selection; it is not a failing-seed label.
Every source floor is `GridFloorGen`, so each seed gets its own fresh capture.
Each artifact directory must contain nonempty engine-native `viewport.png`,
`map.png`, `overlay.png`, `state.json`, `checks.json`, and `index.html`, with
`logical-layout-v1` SHA-256 fingerprint metadata. State/check metadata must
remain `debug-placement`, `layout`, and `unreviewed`.

The original layout-only pass keeps its empty crop metadata. A separate,
source-controlled crop pass is run only with:

```powershell
& C:/Users/arlet/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe `
  Scripts/digimon_early_seeded_routes_dungeon_poi_crops.py `
  tests/visual/early-seeded-routes-dungeon-poi-crops.json `
  --output work/visual-checks/early-seeded-routes-dungeon-poi-crops-YYYYMMDD-HHMMSS `
  --timeout-seconds 35
```

It accepts only the same fixed 27-case matrix and launches the existing early
route layout selector once per fresh lab session. The opt-in selector chooses
only live generic `exit`, `stairs`, `item`, and non-player `actor` entities in
deterministic order, capped at 16. The wrapper requires selection,
no-eligible/truncation, requested/clamped bounds, native clean/overlay sizes,
and an exact clean-to-`map.png` pixel comparison for every emitted crop. It
does not prove story access, progression, combat, rewards, traversal, or
visual approval. Open representative clean/overlay crops spanning Tropical,
Faded, and Faultline routes before reporting engine-rendered evidence.

The 2026-09-19 fresh pass is
`work/visual-checks/early-seeded-routes-layout-20260919-fresh/result.json`,
with its local review catalog at
`work/visual-checks/early-seeded-routes-layout-catalog-20260919-fresh/`.
It passed 27/27 fresh sessions. The opened Tropical first, Faded middle, and
Faultline last viewports remain **unreviewed** engine-rendered layout evidence.

### Aggregate review catalog refresh

The current aggregate evidence is
`work/visual-checks/aggregate-visual-catalog-20260919-base-new-save-capture-final-r2/`.
It contains 26 explicitly named validated reports, 232 displayed entries, and
1,773 linked native PNG references, including all three declared run-up seed
reports, the early-route layout and POI-crop r2 reports, the lair
generated-floor seed refresh, and the base-new-save normal-arrival viewport and
full-map capture. All 5,796 HTML href/src targets and every source report
exist. The aggregate preserves `unreviewed` image evidence and retains the two
metadata-only comparison entries as `not-reported`.

## Expected artifacts and results

The pilot writes:

```text
work/playtest-profiles/<session>/artifacts/test-camp-pilot/
  viewport.png
  map.png
  overlay.png
  crops/
    south-exit.png
    south-exit.overlay.png
    assembly.png
    assembly.overlay.png
    test-power.png
    test-power.overlay.png
  state.json
  checks.json
  index.html
```

`state.json` should identify `map_id` as `base_camp` after the traversal and
`traversal` as `reached-base-camp`. It records the decimal-string seed (`"42"`),
`fixture_zone_id`, `load_mode`, Test Camp's `entrance_south` marker and player
position, and Base Camp's `entrance_center` marker and player position.
`checks.json` should report `renderer_capture: true`, per-mode capture results
for viewport/full-map/overlay, the same traversal result, and
`visual_review: unreviewed`.

## Focused native crops

The Test Camp manifest declares exactly three existing runtime **object** IDs:
`South_Exit`, `Assembly`, and `Test_Power`. The controller resolves each ID on
the loaded `GroundMap` and uses its live `Bounds`; it does not infer a tile
position from Test Camp artwork. The generic crop service also accepts marker
IDs, so later source-controlled cases can select either marker or object
entities without adding map-specific renderer branches.

Each clean crop is a 1:1 copy from the completed ground full-map render
target, with 64 pixels of context and bounds clamped to that source texture.
The matching `.overlay.png` is the same crop with live entity labels/bounds.
`state.json` and `checks.json` record the runtime ID, entity bounds, requested
and clamped crop bounds, source texture, full-map link, and clean/overlay paths.
The narrow wrapper performs a pixel-for-pixel Python comparison between each
clean crop and its declared `map.png` rectangle; it does not render or resize
tiles.

On the FNA backend, sampling the bound `RenderTarget2D` into a second target
invalidates its later color readback. The engine therefore exports `map.png`
first, then snapshots those already-rendered native pixels on the graphics
thread before producing crops. This is an engine texture copy, not an external
renderer or tile reconstruction. It keeps the ordinary camera, debug flag,
and render state unchanged after the capture.

The pilot verifies three separate facts:

- **Structural:** Test Camp and Base Camp load in a single, unreleased fixture
  zone, so their existing same-zone travel calls resolve normally.
- **Rendered:** viewport, full-map, and debug-overlay PNGs are created by the
  live PMDC renderer.
- **Traversal:** the queued Down input triggers the live `South_Exit_Touch`
  route and the engine reaches Base Camp.

The screenshot review remains **unreviewed** unless a human reviewer approves
the captured images. Successful generation or traversal does not approve tile,
collision, or presentation quality.

## Generic entity overlay evidence

`overlay.png` is a live renderer capture with the opt-in diagnostic overlay
enabled. It labels visible ground entities by their stable runtime names and
draws their bounds: `MARKER:<name>`, `OBJECT:<name>`, `NPC:<name>`, and
`SPAWNER:<name>`. The renderer discovers those entities from the current
ground map; it has no Test Camp-specific label list. Ordinary play and ordinary
debug rendering do not draw these labels because the overlay is enabled only
for a `-playtest` session.

The latest fixture-zone evidence is
[the Test Camp overlay](../../work/playtest-profiles/test-camp-entity-overlay/artifacts/test-camp-pilot/overlay.png).
It visibly identifies `MARKER:ENTRANCE_SOUTH` and `OBJECT:SOUTH_EXIT`. This
image remains **unreviewed**: it proves the labels are rendered, not that the
map placement is visually approved.

## Current visual finding

The full-map capture shows the Test Camp south entry/exit at a narrow opening on
the forest edge rather than on a visibly drawn path. This confirms the reported
presentation concern and is intentionally only a finding: this pilot does not
modify the map or its tiles. Review `map.png` before deciding on a tile/layout
change.

## Test Camp interaction smoke

The fixed `test-camp-interactions` case uses only queued `FrameInput` movement,
Attack, Confirm, Cancel, and bounded neutral frames. It starts at `X:244 Y:460`,
opens Assembly at `X:160 Y:116` (`DungeonsMenu`, count `1`), and cancels to
count `0`. It then reaches Test_Power at `X:232 Y:116`, captures `Test power is
now ON.`, repeats the interaction, and captures `Test power is now OFF.` with
normal play restored (`menu_count: 0`).

```powershell
python Scripts/digimon_test_camp_interactions_smoke.py `
  tests/visual/test-camp-interactions.json `
  --output work/visual-checks/test-camp-interactions-YYYYMMDD-HHMMSS `
  --timeout-seconds 60
```

The runner launches `-dev -playtest -playtest-adapter-smoke
-playtest-exit-on-complete`. After the restored normal-play snapshot, its
existing `player_ready` wait asks the opt-in adapter-smoke exit path to stop
the game loop; it does not route through South Exit. All captures and profiles
remain under `work/` and visual review remains `unreviewed`.

## Fixed logical-layout repeatability check

Run the source-controlled comparison from the lab root after publishing PMDC:

```powershell
& C:/Users/arlet/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe `
  Scripts/digimon_layout_determinism_check.py `
  --output work/visual-checks/layout-determinism-YYYYMMDD-HHMMSS `
  --timeout-seconds 45
```

It opens four separate disposable engine sessions: Test Camp twice and P01
Copper Quarry F5 (zero-based floor `4`) twice, each with decimal seed `"42"`.
Read `result.json` for `ground_runs_match`, `dungeon_runs_match`, and
`ground_and_dungeon_differ`; it also links each state report and the ordinary
renderer artifacts. Do not substitute a rendered-image hash or a manual image
diff for this check.

The SHA-256 fingerprint is logical state evidence: it covers the declared
fixture/seed and engine-loaded static map geometry/content recorded in the
state report. It excludes time/weather/frame/UI/session artifacts and runtime
items/actors. A pass does not establish normal story access, combat, traversal,
rewards, or pixel determinism. Screenshot review remains `unreviewed`.

## Fixed DungeonScene input smoke

Run this only from the lab root after publishing PMDC. It starts a fresh,
disposable profile and accepts only the static Copper Quarry F5 manifest.

```powershell
python Scripts/digimon_dungeon_input_smoke.py `
  tests/visual/dungeon-input-smoke.json `
  --output work/visual-checks/dungeon-input-smoke-YYYYMMDD-HHMMSS `
  --timeout-seconds 45
```

The engine debug-places Copper Quarry segment `0`, zero-based floor `4`, with
seed `"42"`. That placement is recorded as `debug-placement`; it is not normal
story travel. The wrapper waits for an actual `DungeonScene` player, reads the
live four-cardinal collision/terrain report, then sends exactly one bounded
queued FrameInput direction only when that report says it is passable. It waits
until the player turn has settled and records before/after tile and pixel
positions, raw adapter responses, `result.json`, `checks.json`, and two live
renderer `viewport` PNGs.

Open both PNGs and inspect the state/check reports. A `passed` result means the
observed tile position changed after that one queued direction. A `blocked`
result is evidence of the actual live obstruction or non-moving turn result;
do not route around it or interpret it as combat/traversal proof. The images
remain `unreviewed`, and this one step does not test combat, full traversal,
story progression, rewards, or presentation quality.

## Lair generated-floor declared-seed refresh
Run after publishing PMDC:

    & C:/Users/arlet/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe Scripts/digimon_lair_generated_floor_seed_refresh.py tests/visual/lair-generated-floor-seed-refresh.json --output work/visual-checks/lair-generated-floor-seed-refresh-YYYYMMDD-HHMMSS --timeout-seconds 35

The wrapper accepts only its static 28-case table: each P01--P07 lair's generated entry floor 0 and generated reward floor 7, once on decimal-string seed "42" and once on "20260919". It uses only the existing bounded P01--P07 selectors. It contains no run-up-map case and does not rerun fixed arena floor 6.
Require nonempty viewport.png, map.png, overlay.png, state.json, checks.json, and index.html for every case. State/check evidence must report logical-layout-v1, debug-placement, layout, and unreviewed. result.json.cross_seed_summary is metadata-only and does not hash, diff, or claim equality of screenshots. Create a catalog from that result and inspect representative entry and reward images from at least two different lairs.
