# Reserve training (first slice)

Benched Digimon improve while the active party explores, in the spirit of the
Cyber Sleuth DigiFarm. This slice covers the regimen menu, the floor tick, stat
gains and level catch-up. Farm Goods, Development and Investigation are later
slices.

## What the player sees

The Base Camp assembly signpost gains a **Training** entry next to Scan Data and
Restore Digimon. It lists every Digimon in the party and reserves with its current
regimen (or "Resting"). Picking one offers HP, Attack, Defense, M.Attack,
M.Defense, Speed, SP, ABI, Bond, Rest or Back. A regimen only accrues while the
Digimon sits in reserve; assigning it to a party member is allowed so the player
can set it up before benching.

In a dungeon, each new floor logs one line per reserve that changed, for example
`Agumon (reserve): Lv.12, Attack +1`.

## Clock

One tick is one new dungeon floor entered by the active party, detected by the
same floor identity the Scan Data ledger uses, so reloading a floor never ticks.
There is no wall-clock timer, in keeping with the "no fake running timers" rule
already in `item_effects.lua`. Ground maps do not tick.

## Stat regimens

| Regimen | Field | Cap |
| --- | --- | --- |
| HP, Attack, Defense, M.Attack, M.Defense, Speed | native stat bonus | 256 |
| SP | `sp_bonus` | 256 |
| ABI | `abi` | 200 |
| Bond | `bond` | 100 |

A point is gained every 3 floors, or every 2 floors when the regimen matches the
personality's favored stat (Durable HP, Lively M.Defense, Fighter Attack,
Defender Defense, Brainy M.Attack, Nimble Speed). Builder and Searcher have no
favored stat. These are the same fields and caps the training foods use, and in
the Digimon stat model one bonus point is one stat point, so a ten-floor run on
one regimen is worth about three levels of that stat.

Changing regimen resets the floor counter, so switching every visit is never
better than committing.

## Level catch-up

Every reserve below the target level gains whole levels each tick. The target is
the strongest active member's level minus 5, capped at the engine maximum, so the
bench trails the party and never leads it. Levels per tick are the remaining gap
divided by 5, rounded up, at least 1; a 24-level gap closes in 11 floors and a
small gap closes one level per floor. EXP toward the next level is kept because
the requirement never shrinks with level. HP is refilled when a level is gained.

This matters more than in Cyber Sleuth because every digivolution resets the
Digimon to level 1. Levels earned in reserve count toward ABI through the usual
peak-level bookkeeping, exactly as dungeon levels do.

Skills unlocked by reserve levels are not prompted mid-dungeon. The lowest level
since the last check is stored, and the Training menu calls the native learn
prompt for that Digimon the next time it is selected.

The engine's own assembly EXP handout does not reach reserves: `PrepAdventureStates`
marks every assembly member absent at dungeon start and the handout skips absentees.
That path is left untouched.

## State

Everything lives in the per-character row under `SV.Digimon.characters`, keyed by
`RewardIdentity`, as plain Lua: `regimen`, `training_floors`, `trained_total` and
`skill_check_level`. Old saves without `SV.Digimon` get the existing "fresh save"
message and keep the Adventuring Team action.

## Tuning knobs

All in `origin/digimon/farm.lua`: `floors_per_gain`, `favored_floors_per_gain`,
`level_margin`, `catch_up_divisor`. A failure inside the tick is caught and logged
so it can never block floor entry.

## Tests

`tests/lua/test_digimon_runtime.lua` covers gain cadence, favored speed, every
cap, catch-up pacing and ceiling, skipping party members, non-Digimon and dead
reserves, save round trip, and the once-per-floor service hook. The terminal
scenarios cover assigning, resting, the skill prompt on selection, backing out
without changes, and refusal on old saves.
