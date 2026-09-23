# Dash softlock repair — 2026-09-17

## Evidence
The live merchant encounter dump identified level-100 Garudamon using `digi_shadow_wing`. Its static sprite gave rush, hit, return and total animation times of 8 frames. The character had already switched to EmptyCharAction while the dash coroutine waited on an AttachedCircleHitbox with three pending tiles, time 0, and delay 10. Rendering continued but the turn could never finish.

## Shared engine repair
- DashAction now prevents idle retirement until hitbox release/processing finishes. An empty hitbox list before release no longer means the dash is finished.
- Animation readiness (ActionDone) retains its previous meaning, so a hit reaction waiting for the attacker can still proceed without deadlocking the hit-processing coroutine.
- Character exposes an identity check for the current action. Dash queue processing cancels remaining hits if the attacker dies or another action replaces the dash.
- This applies to the shared DashAction, not individual moves or species. Sprite images/timings, damage, and move definitions were not changed. Submodule pins were not changed.

## Checks
`DigimonDashChecks` runs through the existing `-digimon-check` native harness. It covers 150 combinations of frame increments (1/2/4/16/64), zero/one/three target tiles, zero/nonzero dash travel time, uninterrupted execution, death, action replacement, death during a hit, and a hit reaction waiting for ActionDone. It uses native dash and hit queue code with controlled collision results; it is not a live interactive combat playtest.

Build: `dotnet build PMDOData.sln --no-restore`.
Publish: `dotnet publish -c Release -r win-x64 PMDC/PMDC/PMDC.csproj --no-restore`.
Logs are local under `work/dash-*.log`. The earlier heap snapshot is diagnostic-only and must not be published or committed.

Source changes: RogueEssence `Dungeon/Characters/CharAction.cs`, `Dungeon/Characters/Character.cs`, `Dungeon/DSceneAction.cs`; DataGenerator `DigimonDashChecks.cs`, `DigimonRuntimeChecks.cs`, `DataGenerator.csproj`.

Final validation: all 150 dash scenarios passed; the full native runtime check passed (see work/dash-runtime-final.log). Solution build succeeded with zero errors; win-x64 publish succeeded. Published EXE SHA256: 15DC0DD2F95BD762ED31A53D45FFB44ECDC8CB509822488B6E0D575DC39FFCD6. Interactive merchant combat has not been replayed after the fix.
