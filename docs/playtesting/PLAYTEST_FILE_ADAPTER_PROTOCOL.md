# Local file adapter protocol

The local file adapter is an opt-in, lab-only bridge for a running PMDC
session started with `-dev -playtest <session>`. It is not a network service,
an MCP plugin, a general dungeon runner, or an operating-system input tool.
The game consumes JSON only on its existing game-loop hook and uses the same
queued `FrameInput` path as the Test Camp pilot.

## Session layout

After PMDC configures a disposable session, it atomically creates:

```text
work/playtest-profiles/<session>/playtest-control/
  session.json
  requests/
  processing/
  completed/
  responses/
```

`session.json` provides the per-process `session_id`. Every request must use
that exact token. The adapter accepts only files ending in `.json` under the
active session's `requests` directory, moves each accepted request into
`processing`, and writes one final response atomically under `responses`.
Requests are never accepted from arbitrary paths, and capture names become
paths beneath the session's `artifacts/adapter/<request-id>/` directory.

Write a request by writing a temporary file in `requests/` and atomically
renaming it to `<request-id>.json`. Read only a final response file; the
adapter never writes a partially populated response at the final path.
Submitting a completed request ID again cannot repeat its action.

## Request schema

```json
{
  "schema_version": 1,
  "session_id": "read-from-session-json",
  "request_id": "down-to-exit-001",
  "command": "input",
  "arguments": {
    "direction": "Down",
    "buttons": [],
    "press_frames": 30,
    "release_frames": 1
  },
  "wall_timeout_seconds": 10
}
```

`request_id` contains only letters, digits, `_`, and `-`, with at most 64
characters. The wall timeout is required and must be 1–60 seconds. At most one
input/capture/step/wait request is active. `get_state` and `cancel` remain
responsive while a command is active. The shared controller keeps at most eight
waiting input commands; an over-capacity adapter input receives a failed response
that explicitly says the bounded queue is full.

| Command | Arguments | Result |
| --- | --- | --- |
| `get_state` | `{}` | Immutable scene/map/player snapshot. Ground coordinates are pixels; dungeon coordinates are tiles. `quest` is currently `not-exposed`. |
| `capture` | `mode`: `viewport`, `full_map`, or `overlay`; simple `.png` `file_name` | Uses the live PMDC renderer and returns a session-relative artifact path plus SHA-256. |
| `input` | `direction`, whitelisted gameplay `buttons`, `press_frames` 1–60, `release_frames` 1–8 | Uses queued normal `FrameInput`, then sends a neutral release frame before completing. Debug/engine-control buttons are rejected. |
| `step` | `frames` 1–60 | Advances exactly those game ticks only while the existing game is paused. It rejects an unpaused session. |
| `wait_for` | `player_ready`, `menu_open`, `capture_complete`, `map_id_equals` with `map_id`, or fixed-smoke-only `dungeon_turn_settled` | Returns an observed state when true or `timeout` after the request deadline. |
| `cancel` | target `request_id` | Cancels a matching active command, removes its queued input, and emits one neutral automation frame before physical input resumes. It does not unwind arbitrary game/Lua coroutines. |

Every final response contains `schema_version`, `session_id`, `request_id`,
`status`, decimal-string `state_sequence`, a state snapshot, result/error, and
`visual_review: "unreviewed"`. Valid statuses are `completed`, `cancelled`,
`timeout`, and `failed`.

## Test Camp smoke flow

The source-controlled smoke script starts the special lab fixture mode with
`-playtest-adapter-smoke`; it does not start the auto-pilot capture flow. It
uses three normal adapter requests in sequence:

1. wait for `test_camp`;
2. capture one renderer viewport; and
3. queue `Down` for 30 frames, then wait for `base_camp`.

The fixture requests clean game-loop exit after the final wait response is
written. The script proves a file-adapter input reaches the existing
`South_Exit` trigger; it never calls the Lua callback directly.

## Fixed dungeon input smoke

`Scripts/digimon_dungeon_input_smoke.py` is a separate, source-controlled
smoke for the ground-versus-dungeon input proof. It accepts only
`tests/visual/dungeon-input-smoke.json`, which declares Copper Quarry segment
`0`, zero-based floor `4` (displayed F5), and decimal-string seed `"42"`.
PMDC's `-playtest-dungeon-input-smoke` flag uses the existing debug-warp
layout-placement lifecycle solely to put that fixed generated map into a live
`DungeonScene`; it does not call movement callbacks, teleport the player, or
load an arbitrary file-adapter case.

After `player_ready`, the adapter's dungeon state reports the four cardinal
neighbors in stable `Up`, `Right`, `Down`, `Left` order. Each report comes from
the live `Map` and includes target tile, terrain passability, character
occupancy, full collision passability, and final `passable`. The wrapper
selects the first `passable: true` direction, sends exactly one normal
`input` request (`8` press frames and `1` neutral release frame), waits for
the fixed-smoke-only `dungeon_turn_settled` predicate, and captures before and
after viewports. Dungeon state records tile positions and the corresponding
live pixel position.

If every live cardinal is blocked, the wrapper writes `status: "blocked"` with
the collision report and issues no bypass movement. If a queued direction does
not move because an enemy, effect, or other runtime action intervenes, the
after-state, settled response, and `checks.json` retain that actual result.
The smoke proves only one bounded queued dungeon direction reaches the normal
engine turn loop. It does not prove combat, multi-tile traversal, story access,
rewards, or visual approval; all captures remain `unreviewed`.

Use only a disposable lab session. A normal `-dev -playtest` session remains
open after adapter commands. The smoke-only flag is bounded cleanup for the
source-controlled test and rejects combination with the auto-pilot exit flag.

## Logical layout fingerprint

Opt-in fixture evidence carries `logical-layout-v1`, a SHA-256 digest built on
the game loop from the map object actually loaded by the engine. Ground layout
reports place it at `state.json.logical_layout_fingerprint`; the Test Camp
pilot retains the pre-traversal value at
`state.json.loaded_logical_layout_fingerprint` because its final report is
written after reaching Base Camp.

The canonical input includes the declared decimal-string seed, fixture/load
mode, map identity and dimensions. Ground maps additionally include their tile
layers/autotile geometry and named object/marker/spawner bounds/triggers. Dungeon maps include
their zone/floor/type and terrain/effect-tile/autotile geometry. It excludes
rendered image pixels, runtime item/actor spawn state, weather/map status,
frame/animation phase, camera/UI/draw scale, and session/profile/output paths.

`Scripts/digimon_layout_determinism_check.py` is the only runner for this
comparison. It starts two new Test Camp fixture sessions and two new P01 Copper
Quarry F5 sessions (zero-based floor `4`, seed `"42"`), compares matching
ground/dungeon pairs, and requires their two fingerprints to differ from each
other. It preserves normal viewport/full-map/overlay artifacts but does not
hash, diff, or claim equality of those images.

This proves repeatability of the stated logical layout inputs for these two
engine-loaded fixtures. It does not prove story access, combat, traversal,
rewards, runtime spawns, or pixel determinism.

## Limits

The adapter polls from the game loop. If the engine stops updating entirely,
it cannot itself issue a timeout response; the external harness must report
that stalled process separately. Rendering, route correctness, and screenshot
review remain distinct: all automated responses remain **unreviewed**.
