# Digimon dungeon loot tuning

The conversion removes legacy Apricorns, unused Evolutionary Stones, retired
Pokémon items, and the HP Restraint Chip C (`ammo_stick`) from dungeon pools,
shops, fixed placements, enemy inventories, and generated zone data. The seven
Digimon-themed evolution unlocks keep their stable item IDs and remain usable,
but are now [main-quest rewards only](DIGIMON_KEY_ITEMS.md), excluded from random
loot: Beast Spirit Light/Flame, Human Spirit Flame/Light, Digi-Egg of Destiny,
Digi-Egg of Miracles, and Digi-Egg of Courage.

Floor `ItemSpawnZoneStep` weights are deliberately simple:

| Supply | Weight after conversion |
| --- | --- |
| HP recovery (Oran, Sitrus, Reviver) | original weight × 3 |
| PP recovery (Leppa) | original weight × 3 |
| Status recovery (Aspear, Cheri, Chesto, Lum, Pecha, Persim, Rawst) | original weight ÷ 2, rounded up |
| Other approved supplies and reward rooms | unchanged |

Only ordinary floor item pools are retuned. Fixed reward rooms and treasure
boxes retain their authored rewards. Both the installed-data script and the
native zone generator write `[digimon-loot-v1]` into the internal zone comment
after tuning, so rerunning either repair does not compound the rates.

Family treasure boxes choose uniformly among unique released `digixcl_` items
in the requested star tier. One- and two-star items can appear in boxes; all
three-star items remain Base Camp exchanges.

## Drill Tunnel green chests

The three green-chest theme variants in `faultline_ridge` now draw their former
Heart Scale slots from Heart Scales, all currently installed Dainty Box rewards,
Dynamite, Cookies, and Large Cookies (33 item IDs, equal weight per ID).
Existing reward counts, extra themed supplies, chest placement, and ambush
settings are preserved. Other dungeons and sealed box tables are unchanged.

`Scripts/digimon_drill_chests.py` derives the pool from installed Dainty boxes,
checks every reward is released, writes `DataAsset/Digimon/drill_chest_rewards.json`,
and installs the three pools. `DigimonDungeonRules` reapplies that payload when
regenerating Drill Tunnel. Rebuild the Zone index after installation. The updated
pool applies to newly generated floors; saved chest contents are unchanged.

These slots use the existing `ItemThemeRange` selector, restricted to the chest's
special-item pool. The native floor check exposed an upstream `ItemThemeDirect`
bug: it reads weights by index from the unrelated special-item list, which can
crash when the direct list is longer. Using the supported range selector avoids
that path without an engine change. The added rewards are also available to the
chest's existing extra-item themes.
