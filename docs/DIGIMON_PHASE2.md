# Phase 2 Part 1

The full Cyber Sleuth roster is installed: 341 native species records, original-size PNG assets, 506 runtime skill records and 1,812 directed transitions covering all 910 source forward edges. The eight starting choices, Tropical Path encounters, secret room, guardian and scoped town cast remain unchanged.

336 species are connected to the starter graph. The five NX forms retain the source's no-evolution rule and remain restoration-only. Their encounter/scan distribution is not added in this step; no free scans are granted. NX illustrations currently share the corresponding normal form's art. MagnaGarurumon SV also shares its regular illustration. These substitutions are explicit in image provenance.

## Evolution rules

- Story completion gates are removed. Numerical level, stat, CAM and ABI requirements remain sourced from the CSVs.
- Full-roster ABI caps at 200 because the source contains requirements above 100. Repeated dedigivolution/training remains necessary for some evolutions. Stat bonuses still cap at 256.
- Both fusion partners, including the actual character being changed, must be in the active party at the required level. Reserves and an underlevel partner do not qualify. The second partner remains in the party, and no substitute item or duplicate character is created. Requirements are checked again on confirmation.
- Item gates accept the corresponding item in the bag or equipped by an active party member. They are reusable unlock items, not consumed. Seven existing evolution-item IDs now represent the four Spirits and three Digi-Eggs, preserving their existing drop/shop references.
- Every digivolution, dedigivolution and permanent mode change resets the Digimon to level 1 and zero EXP. Learned skills and permanent training progress remain attached to the character.
- Digivolution is available at the Tree of Life. Choosing a target opens a confirmation screen with both illustrations, the target stage and level, and each requirement's current pass/fail state.
- Armor EXP uses Champion scaling (1x), Ultra uses Mega scaling (0.5x). The source's stage-less Shoutmon and OmniShoutmon use Rookie (1.5x) and Mega (0.5x) respectively.

The ten ambiguous source skill names are resolved with explicit per-learner assignments in `phase2_decisions.json`. These are documented adaptations: the dataset does not associate variant rows with individual learners. Both normalized source variants remain intact. The existing skill-effect adaptation limitations still apply; this step does not claim an exact recreation of every Cyber Sleuth skill.

## Artwork

`phase2_image_provenance.json` records every source URL, original dimensions, hashes and actual alpha-channel transparency. All 341 PNG files retain source resolution without resizing. 27 selected originals have transparent pixels; 314 retain an opaque source background. Matching transparent PNG originals were preferred over opaque art. Background removal, replacing shared variant illustrations and improving the engine's small sprite rendering remain Phase 4 work. Source: https://wikimon.net/Visual_List_of_Digimon . Existing rights attribution is retained; fetching images does not establish redistribution permission.

## Items

The original user-supplied item files are copied into `DataAsset/Digimon/Source`. Every native item ID is accounted for. The first 49 direct equivalents remain byte-for-byte stable, and the supplied unmatched-item decisions are applied separately:

- 49 equivalents are installed. `item_mapping.json` records source descriptions, actual runtime descriptions and adaptation decisions.
- Unreleased, Apricorn, evolution-item, herb, medicine, wand, XCL and move-disc entries are unavailable and removed from shops and dungeon loot. Blast Seed is Dynamite; other seeds are unavailable.
- Released ammo is converted to C-tier Restraint Chips, food uses digital food names, Gummis become personality-favored training foods, and held items become Cyber Sleuth-style equipment. Boxes, loot and dungeon machines remain available.
- Five Brave Point items award exactly 2,500, 5,000, 10,000, 20,000 or 40,000 EXP.
- Elemental Guard DX equipment now reduces the corresponding element's damage by 20%. Full Revival Spray replaces automatic Reviver Seed behavior with manual full-party revival.
- Consumables otherwise use explicitly described dungeon quantities/ranges. PP recovery is the dungeon analogue of SP. Equipment and buffs retain native percentage/stage effects rather than claiming source fixed-stat effects. Training foods remain usable before the farm minigame. Cure items remove dungeon bad statuses but do not yet add the source's 100 HP healing.
- Attachment Skills are now 138 single-use TMs, selected strictly from CSV `Inheritable = Yes`. Every Digimon can learn every common TM. There are no character-identity, prior-learning reward or first-acquisition checks. The normal learn/replace/cancel menu remains. Native successful-use consumption removes the disc; cancelling keeps it. Signature skills (`Inheritable = No`) receive no TMs.
- Nifty Boxes, the original PMDO TM chest category, now roll the complete common-skill pool. All 13 existing Nifty Box spawners are populated, including those in Tiny Tunnel. Chest placement and drop frequency remain those of the original dungeons.
- Exclusive items should begin as reusable lineage memories keyed to broad families such as Greymon, Garurumon, Angel, Machine and Insect. This keeps equipment useful across a line without creating thousands of species-locked records. Stage-changing crests and achievement chips are reasonable later variants.

## Early playable zones

All 14 zones whose configured starting level is from 5 through 15 are released, unlocked for fresh Digimon saves and listed at Base Camp. Their 2,089 serialized encounter records use Baby through Champion Digimon appropriate to the zone's starting tier. A floor-entry conversion also covers fixed maps and dynamic encounter builders. Runtime validation generates all 169 finite floor definitions, including Tropical Path's secret segment, and checks entries, stairs and generated encounter species.

### Existing-save access and quest gates

Existing Digimon saves receive missing early-dungeon unlocks when a ground map initializes or a destination menu opens. Travel menus include the complete early roster, ordered by starting level, without duplicating existing entries. Completed dungeon records and quest flags are preserved. Training Maze enters at its first defined floor ID 4, rather than the nonexistent floor 0. There are 14 zones total, including Tropical Path, not 14 additional zones.

No quests are required to unlock these zones in the current Digimon slice. The upstream routes were: Tropical Path's secret exit unlocks Tiny Tunnel; Forest Camp exposition unlocks Faded Trail and Bramble Woods; Faded Trail's secret segment unlocks Faultline Ridge; Cliff Camp exposition unlocks Fertile Valley; Forest Camp's hidden gate exit unlocks Secret Garden. The original Tropical Path Digimon exit returns to Base Camp and skips that upstream camp progression, so depending on those quest routes would leave older saves stranded. Direct early access now removes that dependency without marking those quests complete or changing their order. The other early zones likewise require no quest completion. This is an access audit for the selected dungeons, not validation of the full upstream story campaign.

Regression coverage starts from an existing save with only Tropical Path unlocked, invokes the actual destination-menu function for all 14 choices, checks repeated access preserves progress, and confirms non-Digimon saves retain their original unlock behavior. Native generation checks also instantiate the exact menu entry floor for each zone.

## Move presentation and targeting

`digimon_skill_presentation.py` selects original PMDO attack templates by source damage category, element, all-foes targeting and move-name cues. Physical attacks use adjacent single-target strikes, three-tile dashes or two-tile bursts. Special attacks use four-tile enemy-only projectiles, six-tile shots that stop at the first friend or foe, or three-tile enemy-only bursts. All projectiles stop at walls. Skill descriptions state targeting and friendly fire explicitly.

Native PMDO action emitters, hit effects, character actions and sounds supply elemental presentation; damage power, accuracy and existing secondary-effect adaptations are retained. This is a reusable visual vocabulary, not bespoke animation for each signature move. Support skills retain their existing PMDO adaptations.

## Rebuild and verify

Run from the repository root, using Python with Pillow and the installed .NET SDK:

```text
python Scripts/digimon_phase2.py
python Scripts/digimon_full_art.py
python Scripts/digimon_runtime_assets.py --phase2
python Scripts/digimon_items.py
python Scripts/digimon_unmatched_items.py
python Scripts/digimon_early_zones.py
python Scripts/digimon_attachment_skills.py
python -m unittest discover -s tests -v
dotnet build PMDOData.sln --no-restore
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../DumpAsset/ -index Monster Skill Zone Tile GrowthGroup Item
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-check
dotnet publish -c Release -r win-x64 PMDC/PMDC/PMDC.csproj --no-restore
```

Use the Phase 2 generator for the installed runtime; Phase 1 manifests and default generator mode remain historical fixtures. Build/publish outputs are ignored and must not be committed. New source/runtime assets inside submodule working trees must be handled separately when preparing commits; do not silently update parent gitlinks.

Tests cover all source edges, graph connectivity, numeric reachability after training, item gates, fusion party identity and level checks, all sprite hashes/dimensions/transparency, item migration policy, native serialization, character save round trips and generation of every finite floor in all 14 early zones.
