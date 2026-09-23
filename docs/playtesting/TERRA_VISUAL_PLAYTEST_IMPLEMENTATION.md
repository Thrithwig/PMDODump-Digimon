# Terra implementation brief: visual inspection and interactive playtesting

Status: original implementation specification. Many capabilities are now implemented; see [current status](../PROJECT_STATUS.md) for completed scope and remaining work. Historical future-tense statements below describe the original design.
Prepared 2026-09-19 against the local Digimon conversion, including uncommitted work.

## Objective and work location

Build two complementary capabilities, in this order:

1. Option 2: fast, repeatable screenshots of camps and seeded dungeon floors, rendered by the actual PMDO engine and accompanied by geometry/state checks.
2. Option 1: screenshot-guided movement and interaction in a dedicated game session, using existing Windows computer-use support and a small optional developer control adapter for deterministic actions.

The user-facing example is Test Camp: an exit can have a valid Touch callback while appearing inside trees rather than on the visible path. A successful map load or reachable tile is not evidence of correct visual placement.

Work only in the secondary repository:
`C:\Users\arlet\Documents\Codex\2026-09-09\prior-conversation-with-codex-conversation-role\digimon-agent-lab`

The primary/playtest copy is:
`C:\Users\arlet\Documents\Codex\2026-09-09\prior-conversation-with-codex-conversation-role\playtest-digimon-phase1-1ea2e293`

The secondary is a full physical copy, including nested repositories, uncommitted changes, assets and existing artifacts. It is not a linked worktree. Treat the primary as read-only until a tested change bundle is reviewed for transfer. Read `AGENTS.md`, `README_AGENT_LAB.md`, and `COPY_BACK_WORKFLOW.md` first.

Do not change gameplay balance, Phase 4 sprites, ordinary story unlocks, `.gitmodules`, or gitlinks for this work. Focused engine/editor source changes are allowed in the lab. Do not push, publish a public release, or install changes into the primary automatically.

## Verified existing implementation

Paths in this table are relative to the lab root. Recheck signatures before editing.

| Existing implementation | What to reuse / what is missing |
| --- | --- |
| `DataGenerator/Program.cs`, `-digimon-check` branch | Initializes graphics and invokes native checks. Currently does not run a visual inspection session through the normal game loop. |
| `DataGenerator/DigimonRuntimeChecks.cs` | Seeded generation, installed data, stairs, actors, loot and arrival checks. Preserve these as structural checks; they do not visually approve a map. |
| `DataGenerator/DigimonNpcChecks.cs` | Loads Test Camp and checks markers/objects/script bindings. Currently does not walk to its exit or compare its artwork with its trigger. |
| `PMDC/PMDC/Program.cs` | Existing `-dev`, `-asset`, `-appdata`, `-play` parsing. `-play` feeds the existing debug input replay. |
| `PMDC/RogueEssence/RogueEssence/GameBase.cs` | Real FNA initialization, Update/Draw cycle, input collection and debug-replay input branch. A visual runner needs this lifecycle, including actual draws. |
| `PMDC/RogueEssence/RogueEssence/Scene/GameManager.cs` | `SetFrameInput`, `SetMetaInput`, Update, scene outcomes, pause/frame stepping, `GameScreen` render target. `ForceReady()` advances a large amount of simulation time; do not use it as a generic visual settling shortcut. |
| `PMDC/RogueEssence/RogueEssence/FrameInput.cs`, `InputManager.cs` | Existing gameplay input semantics and press/release/repeat behavior. Reuse instead of calling movement/quest scripts directly. |
| `PMDC/RogueEssence/RogueEssence/Ground/BaseGroundScene.cs` | `Screenshot`, `BeginScreenshot`, `ProcessScreenshot` render a whole ground map. Capture only after actual drawing, then restore camera/render state. |
| `PMDC/RogueEssence/RogueEssence/Dungeon/BaseDungeonScene.cs` | Corresponding whole-dungeon screenshot path. |
| `PMDC/RogueEssence/RogueEssence/Content/GraphicsManager.cs` | `SaveScreenshot(Texture2D)` currently chooses timestamped files under `SCREENSHOT/`. Extend minimally for explicit output paths and completion notification. Preserve normal screenshots. |
| `PMDC/RogueEssence/RogueEssence/Dev/GroundEditScene.cs`, `DungeonEditScene.cs` | Existing debug drawing for terrain/collision/object bounds. Reuse drawing primitives without switching a live test into an editable scene. |
| `PMDC/RogueEssence/RogueEssence.Editor.Avalonia/ViewModels/DevForm/DevTabTravelViewModel.cs` | Existing zone/segment/floor selection, `DebugWarp`, `TestWarp`, reload behavior. Add explicit seed selection rather than using random seed generation for repeatable tests. |
| `.../ViewModels/DevForm/DevTabScriptViewModel.cs` | Existing Lua console for developer use. Do not expose arbitrary Lua evaluation through the new automation adapter. |
| `.../Views/DevForm/DevForm.axaml.cs` | Existing editor synchronization helpers. `ExecuteOrPend` executes immediately on Windows; it is not a safe general-purpose worker-to-game-thread dispatcher. |
| `DataGenerator/Data/Zones/MapInfo.cs`, Test Camp branches | Test Camp reuses Forest Camp map data and adds its power terminal. Verify the installed assets against this generator; do not infer visual correctness from the reused name. |
| `DumpAsset/Data/Script/origin/ground/test_camp/init.lua` | Assembly menu, power toggle, and `South_Exit_Touch` return to Base Camp. |

Developer input presently includes F2 pause, F3 frame advance, and F11 screenshot (F11 is gated by developer mode). Actual debug input must still reach the selected game window.

## Architecture and delivery sequence

Use one small engine-side playtest controller with two clients: batch visual cases and an optional Avalonia Playtest panel/local agent adapter. Both clients must call the same capture/state/input services. Do not create a second renderer, a separate movement simulator, or per-dungeon UI classes.

Proposed modules (these files do not yet exist):

- `DataGenerator/DigimonVisualChecks.cs`: case validation and structural assertions, sharing helpers with existing runtime checks where useful.
- `PMDC/RogueEssence/RogueEssence/Dev/Playtesting/PlaytestController.cs`: bounded queued commands executed at a documented main-loop point.
- `.../PlaytestCapture.cs`: viewport/full-map/overlay export and capture acknowledgements.
- `.../PlaytestState.cs`: immutable snapshots with map, position, input/menu readiness and pending action information.
- `.../PlaytestInput.cs`: typed gameplay actions through the normal input path.
- `.../DevForm/DevTabPlaytestViewModel.cs` plus matching Avalonia view: developer panel, with stable accessible names.
- `Scripts/digimon_visual_checks.py`: launcher/report aggregation; no tile rendering or OS input injection.
- `tests/visual/`: small JSON case manifests, fixtures and expectations.

Keep changes to existing update/draw code limited to explicit opt-in hooks. Start with a small Test Camp capture proof before generalizing.

### Milestone A: one real engine capture

1. Launch the lab build using absolute lab asset and app-data paths. Require developer mode and a separate opt-in playtest argument for automation features.
2. Use a fresh disposable fixture under `lab/work/playtest-profiles/<session>/`; never use the copied production SAVE/REPLAY folders. Set the party/story state deterministically before map entry.
3. Load Test Camp with its actual scripts and arrival sequence; let the normal engine update and draw it.
4. Save a player-view PNG from the completed `GameScreen` target and a full-map PNG through the scene screenshot path. Await a capture-complete response after file close, not after setting a Screenshotting flag.
5. Open and visually inspect those images. Confirm they are rendered game content, correctly sized, not a splash screen, empty black frame, editor grid only, or old screenshot.
6. Verify the player-view capture retains menus/UI and the full-map capture uses the same map artwork/layer ordering as the game.

Do not mark this milestone complete based solely on a PNG existing.

### Milestone B: repeatable Option 2 visual cases

Add a separate visual-check entry point so current quick structural checks keep their present behavior. Proposed CLI, not currently available:

`DataGenerator ... -digimon-visual-check <manifest.json> -visual-output <directory>`

It may launch a PMDC visual-runner session internally. Do not make DataGenerator's current empty `CheckScene.Draw` pretend to be a rendering test. A dedicated short-lived game process per case is acceptable initially and provides clean global/Lua state isolation; optimize batching only after correctness is proven.

A visual case specifies stable zone/map IDs, map kind, segment and zero-based floor ID, seed as a decimal STRING, fixture, capture mode and assertions. Displayed floor numbers are labels, not identifiers. Use real floor IDs from dictionary segments, especially Green Gym's entry ID 4. Include fixed reward rooms and boss maps, not just random GridFloorGen maps.

Two execution modes are required:

- `layout`: inspect map generation/artwork with a declared fixture and controlled camera/visibility. Does not prove story access or player traversal.
- `arrival`: execute normal map entry, NPC/quest service hooks, fades and scripts, then capture the actual player state. Does not bypass prerequisites unless the fixture explicitly establishes a valid prerequisite history.

For each case export:

- `viewport.png`: actual player view, preserving fog and current UI.
- `map.png`: full map in native pixel resolution, clearly labeled if fog is revealed.
- `overlay.png`: separate diagnostic image with collision cells, entrances, exit trigger bounds, object/NPC bounds and IDs.
- Focused native-resolution crops around exits, entrances, terminals, rescue NPCs, bosses and reward chests.
- `state.json`: zone/map/seed, asset/build fingerprints, fixture, actor/object/trigger coordinates, camera, draw scale, collision grid dimensions, scene and command sequence.
- `checks.json`: structural results and observed interaction results.
- A local HTML contact sheet with links to the original PNGs and metadata. Keep visual review status `unreviewed` until an agent/human inspects it.

Capture implementation rules:

- Export on the graphics-owning thread after Draw. Never access/dispose GPU render targets from a watcher/MCP thread.
- Preserve camera, viewport, zoom, visibility, debug flags, render targets and game state, restoring temporary capture settings in `finally` on success or failure.
- Full-map capture must handle the existing drawScale/matrixScale behavior explicitly. Test at multiple zoom levels so zoom does not crop or stretch the map.
- Use point sampling and lossless PNG. Do not rescale source tiles to construct the result outside the engine.
- Oversized maps must be captured in bounded camera chunks and optionally stitched, with coordinate metadata and overlap checks. Respect GPU texture and memory limits; a thumbnail is not the only retained artifact.
- For static comparisons use a controlled render tick/weather phase and the same seed, fixture and build. Keep at least one normal-weather capture. Rain and sprite animation must not produce endless `wait until image stops changing` loops.
- Include both the clean image and the overlay. A collision overlay alone cannot establish that a path looks like a path.
- Fingerprint relevant source/assets, including uncommitted file content. HEAD alone is insufficient in this project. Compute fingerprints once per run, not per frame.

Extend assertions for entrance/exit existence, reachable approach cells, trigger overlap, objects blocking corridors, rescue/loot placement and transition destinations. Ground scenes use continuous pixel movement and a finer collision grid; dungeon scenes use tiles. Obtain sizes and transformations from the engine. Test with the player's actual collision footprint and permitted movement, not a point flood fill that can squeeze through an impossible gap. Trigger rectangles can legally sit at the map edge; assess reachable overlap instead of rejecting every out-of-map bound.

### Milestone C: Option 1 screenshot-guided interaction

First use the existing Windows computer-use plugin rather than build another desktop controller. In this environment `@oai/sky` initialized and `list_windows` worked; actual PMDC key input was not verified because there was no selected game window. The supported setup is the computer-use skill and `mcp__node_repl__js`; do not confuse it with browser-only CUA.

Use a dedicated lab session. Find the exact returned PMDC window, observe, send one bounded action, observe again. Verify movement and menu behavior before chaining scenarios. Do not guess window handles or reuse old screenshot coordinates. Do not control another PMDC installation with the same title.

Make the developer Playtest panel expose:

- Session/build/asset/profile paths and a prominent LAB label.
- Map kind, stable ID, segment, floor ID, decimal-string seed, fixture and load mode.
- Capture viewport / full map / overlay / point-of-interest crops.
- Pause, bounded frame advance, reset fixture, cancel command and read state.
- A command status/progress display and links to artifacts.
- Read-only coordinates, trigger IDs, selected object bounds and active quest objective.

Use existing Avalonia conventions and accessibility names, e.g. `PlaytestCaptureViewport`, rather than pixel-only buttons. The panel supplements normal play; walking to an exit must still activate the real trigger and transition.

### Milestone D: deterministic local agent adapter, if needed

The user requested UI support for moving about. Native computer use may be sufficient for manual-style checks; add a thin local control adapter for repeatable bounded input if focus/hold timing is unreliable. This adapter is part of the agreed design, but do not implement it before the first successful capture and input proof.

A file-based request/response directory under the session profile is sufficient for the first version. Publish JSON requests atomically, consume only explicit completed files, and return response IDs and artifact paths. A local MCP plugin can wrap this protocol later; it must not contain a second implementation of the game actions. No remote service or network-exposed control port is needed.

Require both `-dev` and the opt-in automation flag. Refuse a profile/output path outside the lab's session tree. Commands must be queued from transport to the main game loop; do not wait synchronously on that queue from the UI/game thread. Use request IDs, one in-flight mutation, session tokens/IDs, bounded queues and deadlines. Duplicate request IDs return the original result; they must not repeat movement or reward interactions.

Minimum commands:

| Command | Behavior |
| --- | --- |
| `get_state` | Immutable scene/map/player/menu/quest/command snapshot; explicit coordinate units. |
| `capture` | Next completed draw to viewport/full-map/overlay PNG; correlate the artifact with its state sequence. |
| `load_case` | Load a named fixture/case with stable seed through the scene lifecycle. Explicitly distinguish debug placement from natural travel. |
| `input` | A whitelisted direction/button, bounded press duration, then a neutral release frame through the normal FrameInput/InputManager path. |
| `step` | Bounded simulation ticks with correct update/draw scheduling; honor pause state. |
| `wait_for` | Bounded predicates such as player-ready, menu-open, map-ID-changed, or capture-complete. |
| `cancel` | Cancel the current automation request and release held inputs; do not claim to unwind arbitrary gameplay coroutines. |
| `reset_fixture` | Reset only the disposable session after recording failure evidence. |

FrameInput currently has private setters/indexer writes; add one narrow internal factory/provider if needed rather than mutating it through reflection in production. Inject at the GameBase input selection point so physical input does not overwrite the scripted frame. Decide and document precedence among physical input, automation and replay. Clear automation on cancellation, loss of session, timeout and window closure. Log the chosen input source. Preserve ordinary input behavior when automation is off.

For ground movement, press for a capped number of ticks and verify the resulting pixel position/collision. For dungeon movement, observe player readiness, issue one action and wait until that action/turn settles. An enemy hit, menu or blocked step may prevent movement; return the actual result, not an assumed one-tile delta. Teleporting is acceptable for fixture setup but never counts as a traversal test. Never invoke `South_Exit_Touch` or a rescue callback directly to claim an interaction passed.

Suggested wrapper tool names are `digimon_playtest_state`, `digimon_playtest_capture`, `digimon_playtest_input`, `digimon_playtest_load_case` and `digimon_playtest_wait`. They are PROPOSED names, not currently installed tools. If packaged as a Codex plugin, follow the plugin-creator skill and use a small skill explaining lab isolation, observation/action loops and artifact review. Verify plugin discovery and schemas before claiming agent control works. No installation into the user's environment is part of this write-up.

On timeout, produce the last screenshot, map/position, pending command, elapsed ticks, relevant logs, scene/coroutine summary if available, and seed. Report `timeout` distinctly from a failed assertion. Do not forcibly finish a battle coroutine or modify a save to make a test pass. The previous animated-rain/dash softlock is a useful negative test: rendering can advance while the player is never ready.

## Test Camp pilot and broader coverage

The first end-to-end case is Test Camp, before any general sweep:

1. Load `test_camp` at each legitimate entrance marker. Inspect the existing Forest Camp artwork and installed trigger geometry before deciding the cause of the reported misplaced exit.
2. Capture clean and annotated views of the path, `South_Exit`, Assembly and Test_Power. Confirm readable placement and accessible approach space.
3. Walk along the visible path into the exit. Record the actual transition to Base Camp and return spawn. Walk back through normal travel.
4. Use Assembly, cancel out of the menu, and verify quest-gated dungeon choices in a valid fixture.
5. With a disposable fixture, toggle power once and verify UI/state, then restore it. Do not use the cheat to claim normal dungeon difficulty or combat correctness.
6. If the exit really is misplaced, correct the generator/asset only in the lab, regenerate, repeat the same case and produce before/after evidence. Do not patch only the currently published map.

Next, cover all camps, each run-up/lair visual band boundary, fixed boss/reward maps, and sampled random floors. Use at least a default seed, another fixed seed and a reported failing seed where available. Scenario selection must include early and progressed NPC arrangements and accepted rescue quests. Green Gym is tutorial-only; preserve its 13 teachers and do not restore its retired rescue quest.

Run cheap structural checks broadly and render only requested/changed cases first. A selected-seed visual pass is not proof that every possible random layout is valid. Track coverage explicitly in the report.

## Acceptance and handoff

- Existing solution builds and current structural checks still pass.
- One command produces real rendered Test Camp viewport, full map, overlay, crops, state and report.
- Native keyboard input is verified, or the deterministic adapter demonstrably moves the player through the ordinary input path.
- Exit traversal is verified by normal interaction and destination/return state, with no trigger callback shortcuts.
- Repeating seed/fixture produces the same logical map; image comparison tolerates declared animation differences only.
- Ground collision, dungeon blocking, menu cancel, fixed reward maps, loading/fades, invalid case IDs, timeout and cancellation have regression coverage.
- An intentional misplaced trigger is detected by the review workflow; an intentional inaccessible trigger fails an automatic geometry/traversal check.
- No writes occur in the primary tree or its save directories. No test artifacts enter the transferable source bundle.
- Normal play with the automation flag absent remains unchanged.
- Deliver source changes, test commands, results, selected-case coverage, reviewed screenshots and known limitations. Keep structural pass, visual review and traversal pass separate.

Stop after each milestone long enough to inspect its evidence. Do not report completion merely because all cases generated, the editor opened, or a plugin tool returned successfully.

See `visual-cases.example.json` and `playtest-protocol.examples.json` for the proposed contracts, and `COPY_BACK_WORKFLOW.md` for transferring a verified implementation.
## Build and execution commands for the implementation

Run commands from the lab root; resolve paths once instead of inheriting the working directory of an old shortcut.

```powershell
$labRoot = (Get-Location).Path
# Confirm this is digimon-agent-lab before continuing.
dotnet restore PMDOData.sln --force
dotnet build PMDOData.sln --no-restore
# Existing structural check (already implemented):
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset "$labRoot/DumpAsset" -gen "$labRoot/DataAsset" -digimon-check
```

`DataGenerator.csproj` has `EnableDefaultItems=false`: explicitly add new C# files to its Compile list. New visual-check output must not be written to `DataAsset` or `DumpAsset`.

After Terra implements the proposed arguments, a visual run should look like:

```powershell
# Proposed command; currently unavailable.
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset "$labRoot/DumpAsset" -gen "$labRoot/DataAsset" -digimon-visual-check "$labRoot/tests/visual/test-camp.json" -visual-output "$labRoot/work/visual-checks/test-camp"
```

For a manual developer session, the currently supported launch arguments are:

```powershell
& "$labRoot/PMDC/publish/win-x64/PMDC/PMDC.exe" -dev -asset "$labRoot/PMDC/publish/win-x64/PMDC" -appdata "$labRoot/work/playtest-profiles/manual-review"
```

The copied executable predates any future implementation. Rebuild/publish within the lab after engine changes before testing the published executable. Confirm the window/process asset root and profile in the controller handshake so a stale or primary executable cannot masquerade as a validated lab build. The automation controller must provision its own fixture rather than assuming the manual profile already has a playable save.
