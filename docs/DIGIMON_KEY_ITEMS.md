# Inventory expansion and reusable evolution rewards

The File Town supply shop (the original Kecleon shop) always offers **Inventory Expansion Key — 10,000 Bits** until purchased. It is a shop service, separate from the rotating physical stock. Purchase adds ten permanent inventory slots, consumes no bag slot, and cannot be repeated. Insufficient money and cancellation leave the save unchanged. Explicit dungeon bag restrictions still apply.

`ExplorerTeam.InventoryBonusSlots` is serialized with the team, copied in team snapshots, and included when rank changes recalculate capacity. Existing saves default to zero; no reset is needed. The purchase condition reads that saved field directly. The only engine change is this small field/copy/rank adjustment in `RogueEssence/Dungeon/Team.cs`; shop behavior lives in `origin/digimon/inventory_upgrade.lua`.

## Digi-Eggs and Spirits

These seven reusable items are actively required by **18** Digivolution edges. Their requirements and non-consumption behavior are unchanged. They stay released and usable, but no longer occur in dungeon loot, hidden-box contents, enemy inventories or dungeon shops. New rewards come from Clockmon's main-quest debriefs:

| Completed main quest's dungeon | Reward | Unlocks |
| --- | --- | --- |
| Native Forest Trail | Digi-Egg of Courage | Flamedramon |
| Drill Tunnel | Human Spirit of Flame | Agunimon |
| Signpost Forest | Human Spirit of Light | Lobomon |
| Gear Savanna | Beast Spirit of Flame | BurningGreymon |
| Panorama Cliffs | Beast Spirit of Light | KendoGarurumon |
| Factorial Quarry | Digi-Egg of Destiny | Rapidmon (Armor) |
| Dragon Eye Basin | Digi-Egg of Miracles | Magnamon |

All other level/stat/ABI requirements still apply. Evolution requires the item in the bag or equipped, just as before. Gifts use the existing native reward flow, which sends them to storage if the bag is full.

`DataAsset/Digimon/story_item_rewards.json` is the reward assignment source. `Scripts/digimon_story_rewards.py` validates complete coverage, generates the runtime table, updates descriptions and removes random loot entries. Native zone regeneration and the unmatched-item installer enforce the same quest-only rule. Definitions are not disabled or deleted.

One-time claims are saved in `SV.Digimon.StoryMissions.item_rewards`. Clockmon checks completed quests on existing saves too. A legacy copy in the bag, storage, or equipped by an active/reserve member counts as already claimed, preventing duplicate rewards. Existing inventory and saved dungeon floors are not rewritten; leave and re-enter an expedition for new loot tables.

Quest 2 reward fix (September 17): `COMMON.GiftItem` expects the camp's `GroundChar`, whose `GetDisplayName()` takes no arguments. Passing the party's dungeon `Character` raised an NLua overload error before delivery and stopped the next dispatch. Rewards now pass `CH('PLAYER')`. If a save already archived the quest before this error, Clockmon delivers the pending reward and resumes the next eligible primary dispatch on the next interaction, without repeating the route or its unlocks. Native checks exercise the real gift helper with a real ground character, both bag and full-bag storage delivery, and repeated claims. Lua regression scenarios cover interrupted debrief recovery with the next route available and with Forest Camp still pending.

## Nifty TM boxes

The audit found no box offering the full TM pool. All 12 installed Nifty-box spawners now draw one of the **138 common, single-use Digimon TMs**, with equal weights and no supply/training fillers. Signature skills are not TMs and remain excluded. Other box categories are unchanged.

`python Scripts/digimon_attachment_skills.py --chests-only` installs the Nifty pool without rebuilding moves, learnsets or other loot. Native zone generation applies the same pool from `DataAsset/Digimon/attachment_skills.json` in `DigimonDungeonRules`. Rebuild the Zone and Item indexes after installation. Sealed boxes already acquired retain their saved contents; the new pool applies to newly generated boxes.

## Rotating family exchanges

The old random catalog still referenced disabled Pokémon family items, so no rotating Digimon offers appeared. `origin/digimon/family_exchange.lua` now builds the pool from the installed, released `digixcl_` items. The current 132-item pool gives four distinct offers per expedition using the original catalog-size schedule. Every family treasure, including three-star treasures, can appear. The 33 fixed three-star recipes remain available.

All fixed and rotating exchanges cost **10,000 Bits**. Rotating one/two/three-star rewards require **2/4/6 different treasure IDs** from any family, preserving the original wildcard tribute rules. The native menus accept bag, active-team held and storage items. All 132 released `MaterialState` items are Digimon family treasures; unrelated supplies cannot be offered. Original bag effects are unchanged.

Stock lives in `SV.base_trades` and refreshes through the existing `COMMON.EndDayCycle`. The saved `SV.digimon_exchange_version` migrates old stock once when opening the shop. Opening repeatedly or buying every offer does not restock it. Purchases remove the exact rotating row rather than relying on catalog indices, which can shift when disabled legacy recipes are filtered out. Canceling consumes neither money nor tribute. Native delivery still sends the received treasure to storage.

## Validation

Python/Lua tests cover cancellation, insufficient funds, repeat purchase prevention, one-time/catch-up quest rewards, existing copies, and absence of quest keys from every zone payload. Native checks exercise purchase against a real team, save/reload, team cloning, rank recalculation and restricted-dungeon capacity. The full solution and Windows playtest build are rebuilt with the new team field.

The targeted suite also checks the complete and equally weighted TM pools, native tribute eligibility, rotating-stock migration/depletion, canceled transactions, and successful fixed and wildcard trades. Native checks exercise the real Lua item index and deserialize regenerated Nifty spawners.

Final validation: 34 targeted Python tests passed, including the Lua scenarios. `dotnet build PMDOData.sln --no-restore` passed with zero errors and the existing five upstream warnings. Native checks passed all 341 forms, 40 released zones and 567 seeded floors with zero generation errors, plus 146 family-treasure boxes and save round trips. Windows self-contained publish succeeded; all 3,145 published script/zone/item files matched the source payload by SHA-256. These are automated checks; the shop screens still need player testing.
