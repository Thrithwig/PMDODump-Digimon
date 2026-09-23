# Quest completion audit — September 17, 2026

The live playtest log identified the quest 2 blocker in `common.lua:359`: `Invalid arguments to method: Character.GetDisplayName`. `story_rewards.lua` passed the party's dungeon `Character` to `COMMON.GiftItem`, which expects a camp `GroundChar`. The shared call now uses `CH('PLAYER')`, fixing all seven evolution-key rewards.

The error could occur after archiving a request but before clearing the current request and assigning its successor. Clockmon now claims pending rewards and resumes dispatch from that saved state without redoing the dungeon, repeating unlocks, or creating duplicate native mission records. Normal Forest Camp and late-game prerequisites remain enforced.

## Coverage and results

- All **20 primary quests** complete in sequence through the final citadel, including all seven lairs and the six-lair summit gate.
- All **18 optional quests** complete and repeat twice each.
- The complete sequence runs both normally and with an interrupted delivery at each of the **seven evolution-key rewards**, serializing/reloading quest state before recovery.
- Successful completion archives the native mission, reconciles Phase 3 route/lair records, and advances the next eligible primary request. Each key is delivered once.
- Missing objectives, failed runs, missing lair bosses, and premature lair exits do not complete quests.
- Repeat conversations do not duplicate rewards or archives; optional completions reset their objective and clear flags for the next run.
- A native integration check calls the actual `COMMON.GiftItem` helper using a real ground character and real inventory, confirming bag delivery, full-bag storage delivery, and no duplicate claim.
- Full solution build passes with zero errors. The native validation suite passes **341 forms, 40 released zones and 567 seeded floors**, with zero floor-generation errors.

The definition-driven completion audit lives in `tests/lua/test_digimon_all_quest_completions.lua`, invoked by `tests.test_digimon_terminal`. Quest definitions are loaded from the shipped script, rather than maintaining a separate test roster. Dialogue/input are simulated; this is automated validation, not a manual playthrough of every quest. No additional completion blocker was found in these tested flows.

The two corrected Lua scripts are installed in the current playtest build. Restart the game, load the existing save, and speak to Clockmon to collect the pending reward and resume dispatch. Player saves are not edited.
