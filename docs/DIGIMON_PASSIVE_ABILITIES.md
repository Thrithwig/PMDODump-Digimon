# Digimon passive abilities: playtest rules

Every one of the 341 Digimon has a released current-form innate ability. The editable authority is `DataAsset/Digimon/passive_abilities.json`; `Scripts/digimon_passive_abilities.py` materializes the catalog into native PMDO Intrinsic assets and assigns them to monster forms and explicitly configured dungeon spawns.

These are dungeon adaptations inspired by Cyber Sleuth support skills, not a claim that all mechanics match the source game. Earlier draft concepts remain in `revised_from` for review. Only `effects` and the matching current `description` describe implemented behavior. Source Vaccine/Virus/Data/Free classifications, elemental attributes and stages remain unchanged.

## What the current passives do

Each ability combines a species-specific learned-move modifier with one complementary effect. The 341 combinations are distinct at the native event level, even where individual components repeat. This makes the forms distinct without requiring 341 unrelated engine systems.

- Named-move modifiers increase formula damage or accuracy by 10%. Accuracy is multiplicative and remains subject to the engine's accuracy/evasion rules; it is not ten percentage points or a guaranteed hit.
- Secondary effects improve an element's damage, reduce category/element damage, improve HP restoration, support nearby allies, or restore PP.
- Nearby effects use native proximity radius 2, affect other active allies and exclude the owner. They do not affect distant party members or storage.
- Native multiplicative stacking applies with no custom aggregate cap. Integer rounding can hide small gains on very small damage/healing values. Fixed-damage attacks ignore damage multipliers, including defensive and elemental modifiers.
- Floor-entry PP recovery restores one use to each equipped move up to its maximum. Defeat-triggered recovery additionally requires an enemy target, actual direct damage and a defeated target; friendly fire and indirect poison defeats do not qualify.

EXP rewards, Scan Data, evolution retention and permanent stats are unaffected by this system.

## Existing saves and evolution

The runtime synchronization helper upgrades party and assembly members through the native `LearnIntrinsic` API. Repeated synchronization does not relearn an already-correct ability. Non-Digimon remain unchanged. Changing form uses that form's innate ability rather than permanently retaining a previous form's passive.

Existing learned moves remain under player control. A named-move modifier only operates while its listed move is equipped and used; the generic secondary component continues to function without it. The low-stage starter moves remain a separate 20-power/20-PP system.

## Independent review corrections

Review against native events found and corrected eleven partially inert named-move assignments:

- Tokomon, Starmon, Raptordramon, Pandamon, Mamemon, Monzaemon and WereGarurumon (Black) now receive a damage bonus on their listed formula attacks instead of an accuracy bonus that included an always-hit move.
- Clockmon, Gatomon, Devimon and Apocalymon no longer claim a damage bonus on Chrono Breaker, Lightning Paw, Death Claw or Darkness Zone respectively. Their modifier targets their other listed formula attack. Native `FixedDamageEvent` bypasses damage multipliers.

All 341 descriptions were revised for grammatical subject agreement and possession. No engine or generator behavior was changed by this review.

## Validation and regeneration

`tests/test_digimon_passive_catalog.py` verifies all 341 species, unique native event combinations, unchanged source attributes, monster assignments, generated-record agreement, functional named-move anchors and enemy-only PP wrappers. `tests/test_digimon_passive_sync.py` executes the actual synchronization Lua module with focused party/assembly migration mocks. Main-agent native checks and gameplay tests cover runtime execution separately.

```powershell
python Scripts/digimon_passive_abilities.py
python -m unittest discover -s tests -p 'test_digimon_passive_*.py' -v
```

After regeneration, rebuild the Intrinsic and Monster indexes (and Zone when explicit spawn assignments change). The full phase-2 runtime generator also reapplies the passive catalog after writing monster forms.
