# Initial Phase 1 stat and progression overlay

The Phase 1 runtime consumes the authored overlay and its compiled level curves.
The Cyber Sleuth source CSVs remain unchanged. `phase1_skill_adaptations.json`
records combat approximations: source secondary effects and penetration mechanics
are not yet reproduced exactly. This is a playable initial balance, not full combat parity.

## Generate and verify

From the repository root, with Python 3.10 or later:

```sh
python Scripts/digimon_balance.py --manifest DataAsset/Digimon/phase1_manifest.json --overlay DataAsset/Digimon/phase1_overlay.json --output DataAsset/Digimon/phase1_gameplay.json
python -m unittest discover -s tests -v
dotnet build PMDOData.sln --no-restore
```

The catalog contains 44 forms, 4,356 level rows, eight starter previews, and 80
directed transitions (40 forward, 40 reverse). Canonical JSON input hashes identify
the exact manifest and overlay. Generation refuses unsupported source conditions,
broken graph references, invalid policy values, unresolved skill variants, and
numerically unreachable selected forward transitions. It validates before writing
and refuses to overwrite either source input.

## Authored PMDO decisions

These are initial design choices, not additional Cyber Sleuth facts or playtested
balance. They are centralized in the overlay for review and later adjustment.

| Area | Initial rule |
| --- | --- |
| Level | Start/restoration at 5; maximum 99; forward changes preserve level; reverse changes reset to 1 |
| HP | Source HP / 10 + 20 |
| Attack/defense/speed | Corresponding source stat / 2 + 5 |
| Magic attack and defense | Both derive from source INT / 2 + 5 |
| SP | Retained unscaled as `source_sp` for progression gates; not a new combat resource |
| Intermediate levels | Piecewise linear interpolation between source levels 1, 50, 99, followed by scaling and round-half-up |
| CAM | Bond: initially 10, capped at 100; +1 per eligible defeat for each active living party member |
| ABI | Training: initially 0, capped at 100; +1 per newly attained highest level in the current training cycle |
| Forward transition | All target source conditions must pass; permanent, free, hub-only |
| Reverse transition | Corresponding selected parent; free and hub-only, resets level/EXP; no forward requirement reapplied |
| Scan | 25 points per eligible defeat; restoration threshold 100; cap 100 newly earned points per species per floor |
| Stored scans | Total scan points are uncapped; no conversion to Bits. The per-species per-floor earning cap remains 100. |
| Restoration | Requires the species DigiCode and roster confirmation at a hub terminal; direct joining remains prohibited |

The compiler emits all these values, but reward eligibility, caps, overflow,
restoration, and highest-level tracking must still be enforced by the runtime.
Training must follow persistent highest level, not current level, so revisiting a
form or a previously reached level cannot generate training. No level reset or
temporary battle form is introduced. Summons, illusions, friendlies, neutral actors,
PvP ghosts, and scripted defeats are excluded from ordinary scan/bond rewards.

Target HP/ATK/etc. requirements use the same conversion as the relevant stat curve.
CAM percentages and ABI values become bond and training thresholds. Original field
names and values remain alongside every compiled requirement. The source label
`Starter digimon` is accepted only on root forms; arbitrary textual conditions fail.

The preview function is pure: it reports each current/required value and a combined
eligibility result without changing any state. It checks numerical requirements
only. A runtime caller must additionally check location, actor identity, equipment,
save version, and transactional preconditions.

## Starter comparison at level 5

| Choice | HP | ATK | DEF | Magic ATK/DEF | Speed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Agumon | 70 | 42 | 30 | 14 | 26 |
| Gabumon | 69 | 30 | 23 | 22 | 26 |
| Biyomon | 54 | 25 | 22 | 25 | 26 |
| Tentomon | 50 | 24 | 31 | 27 | 24 |
| Palmon | 76 | 32 | 26 | 23 | 24 |
| Gomamon | 78 | 27 | 27 | 23 | 24 |
| Patamon | 59 | 22 | 20 | 29 | 26 |
| Gatomon | 48 | 22 | 24 | 48 | 40 |

Gatomon remains a Champion. Its low HP and higher magic/speed profile are visible
instead of being flattened to Rookie stats. Starter selection is an explicit
fresh-save grant, not a bypass that can be used by ordinary restoration.

## Reachability results

The compiler checks each forward gate using the current form's stats. Tests then
walk each complete line while preserving level, and return through every reverse
edge. Training is bounded by levels gained since the initial level; bond requires
eligible encounters. No bonus-stat training is assumed.

| Line | Earliest numerically reachable Mega level with sufficient bond |
| --- | ---: |
| Agumon → WarGreymon | 64 |
| Gabumon → MetalGarurumon | 84 |
| Biyomon → Hououmon | 55 |
| Tentomon → HerculesKabuterimon | 62 |
| Palmon → Rosemon | 55 |
| Gomamon → Vikemon | 65 |
| Patamon → Seraphimon | 60 |
| Gatomon → Ophanimon | 78 |

The late gates follow from source stat requirements, not just the listed required
level. The output records every edge's earliest level and required bond encounters.
For example, CAM 80% requires 70 eligible defeats from initial bond 10. These are
numeric feasibility checks, not proof that the future dungeon provides the needed
XP, encounters, hub access, or appropriate pacing. Phase 1's dungeon should exercise
an early transition and reversal; completing all Mega paths is not yet a pacing claim.

## Runtime and training policy

Dedigivolution resets level to 1 and EXP to 0. Levels earned since the cycle began
(initially level 5, then level 1 after a reset) award one permanent bonus to each
mapped stat and source SP per 10 levels, plus one ABI per 5 levels. Stat bonuses
cap at 256 and ABI at 100. Bond, identity, nickname, equipment, learned skills and
existing bonuses remain. Forward changes preserve level. Immediate reversals earn
no additional bonuses; another training cycle requires leveling again. The table
above describes baseline reachability without these earned bonuses.

The signpost offers team management, ledger, restoration, and evolution in the two
Base Camp maps. Generated Tropical Path encounters are the 12 Baby/In-Training
forms; a level-8 Koromon guardian with +20 HP guards the final regular floor's
normal and secret exits. Its own secret room is retained; unrelated mystery
segments are not part of the slice. Clearing either route returns to Base Camp.

Source image pixels remain unchanged. The runtime currently fits them into static
32px creature tiles and portrait tiles, retaining source white backgrounds. Image
clarity and transparency are explicitly deferred to Phase 4 after user playtesting.

No audio conversion, migration compatibility, or temporary battle digivolution is included.

## EXP and consumable scans: playtest tuning (2026-09-10)

The initial slice reused PMDO's Medium Fast growth table (cumulative level cubed,
except its zero starting entry), `max(10, Memory * 8)` BaseEXP, the upstream relative
EXP formula, and Tropical Path's 75% EXP setting. That was placeholder tuning.

Now each Digimon uses a separate stage growth table. Every original per-level
requirement is multiplied by the stage factor and rounded up: Baby/In-Training
2, Rookie 1.5, Champion 1, Ultimate 0.75, Mega 0.5. Evolution preserves the fraction
of progress toward the next level; dedigivolution still resets level and EXP.

BaseEXP is now source Memory * 24 (48 for Baby, 72 for In-Training). Rewards use
`floor(BaseEXP * (defeatedLevel - 1) / 10) + BaseEXP`. Tropical Path awards 100%.
A recipient up to five levels above the defeated enemy receives the full award.
Beyond that, halve the award once per extra level, rounding down; at 15 levels
above the enemy it is zero. The rule applies to active and reserve Digimon EXP.
Pokemon enemy rewards retain the upstream formula.

A deterministic 200-seed model assumes 16 normal kills (four per regular floor)
plus the level-8 guardian and the existing secret reward room. Starting at level
5, average finishing levels are Baby/In-Training 8.83, Rookie 9.04, Champion 10,
Ultimate 10.59, Mega 11.05. Those differences follow the requested stage costs.
Level-20 parties receive negligible or zero EXP; level 30 receives none. This is
an initial pacing model, not a guaranteed number of levels regardless of kills.
Faster dungeon routing or more respawn farming changes the result.

Restoration spends ALL stored Scan Data for that species only after the reserve
has been added successfully. At 100-199 points it starts at level 5; 200-299 gives
level 10; 300-399 gives level 15. Each complete extra 100 adds five levels, capped
at 99. Partial hundreds are also spent, and the confirmation states the total
cost and resulting level. Cancellation or failure preserves all points. Repeated
restorations require earning more scans and may create another of an owned species.
Bonus starting levels do not grant free ABI or dedigivolution training bonuses.

Apricorn entries, including boxed and fake item spawns, have been removed from
all dungeon loot/shop tables and shared shop stock. Other items and story gift
scripts are unchanged. This targeted global removal is the user's exception to
the original one-dungeon geography limit.
