# Dungeon spawns and camp progression

This supersedes the earlier Phase 1 blanket unlock and Base Camp return shortcut.
Camp grouping follows the supplied screenshot and the
[PMDO dungeon reference](https://wiki.pmdo.pmdcollab.org/Dungeon).

## Travel

- Base Camp junction: Guildmaster Trail, Tropical Path, Faultline Ridge only.
  Guildmaster Trail remains the long endgame challenge available from the junction.
  Tropical Path completion leads to Forest Camp. Faultline Ridge becomes available
  after reaching Forest Camp or recording a Tropical Path clear. Clearing it
  unlocks Trickster Woods at Forest Camp.
- Forest Camp: Faded Trail, Bramble Woods, Trickster Woods, Overgrown Wilds,
  Moonlit Courtyard, Ambush Forest, Tiny Tunnel, Sickly Hollow, Secret Garden.
- Cliff Camp: Fertile Valley, Flyaway Cliffs, Wayward Wetlands, Geode Crevice.
- Ravine Camp (`canyon_camp`): Copper Quarry, Depleted Basin, Forsaken Desert,
  Relic Tower, Sleeping Caldera.
- Cave Shelter (`rest_stop`): Thunderstruck Pass, Veiled Ridge, Snowbound Path,
  Treacherous Mountain. Cave of Whispers retains its existing Cave Shelter entrance
  as an extra dungeon outside the screenshot's main campaign list.
- Blizzard Camp (`final_stop`): Champion's Road.

Secret branches remain inside their parent dungeons; they are not global menu
entries. Normal quest unlocks still apply. The global menu no longer injects or
unlocks every early dungeon, including on return paths and secret exits.
Base Camp's ferry no longer adds dungeon destinations, following the explicit
request to restrict Base Camp to the three junction routes.

Existing save completion and quest records are preserved. The two main story
gates are enforced even if an older slice save already unlocked those destinations.
A recorded Tropical Path clear exposes the Forest Camp travel destination without
skipping that camp's first-visit scene.

## Spawns and loot

`Scripts/digimon_dungeon_audit.py` reviews all 35 released zones, converts their
serialized encounters to Digimon, and fills empty procedural enemy/loot tables.
Existing floor layouts, encounter placement, quest callbacks and special rewards
are retained. Empty fixed treasure rooms and noncombat maps are not given random
enemy tables.

Repairs cover Cave of Whispers, Eon Island, Labyrinth of the Lost, Prism Isles,
The Neverending Tale, Champion's Road's second segment, Depleted Basin's second
segment, and Lava Floe Island's second segment. The last two needed loot only.
Current Cave of Whispers data has 16 procedural floors; every one now has both
enemy and item table coverage. The tables use existing converted item IDs.

The native runtime check now verifies actual generated floors, initial enemies,
respawn tables, loot tables, placed loot, valid item references and absolute stairs.
Relative stairs may intentionally exit a segment. Fixed-map enemies run through
the same Digimon conversion callback as the playable game before validation.

## Enemy stage tiers (2026-09-12 playtest retuning)

The first slice picked enemy stages from the zone's starting level, one full stage
ahead of what the player could reach: level-10 zones were about 60% Champions and
Trickster Woods (level 20, solo) was 52% Ultimates, while Rookie-to-Champion needs
level 12-20 and Champion-to-Ultimate needs level 26-40 in the source requirements.
In this stat model a stage step is worth 10-20 stat points and a level about one,
so that mismatch, not enemy level, made the third story dungeon unwinnable.

Enemy stage now follows each spawn's own level, and the upper stage's share rises
across the tier. Enemy levels themselves are unchanged from upstream.

| Enemy level | Stages | Upper-stage share |
| --- | --- | --- |
| 1-7 | Baby, In-Training | 50% |
| 8-13 | In-Training, Rookie | 60% |
| 14-27 | Rookie, Champion | 20% rising to 50% |
| 28-54 | Champion, Ultimate | 20% rising to 50% |
| 55+ | Ultimate, Mega | 20% rising to 50% |

The pick is a deterministic function of zone, spawn path and level, so reruns are
stable. Tropical Path, the Koromon guardian and Monzaemon are exempt. Spawns whose
upstream level is far from the zone's starting level (rare high-level encounters and
low-level fodder) now receive matching stages rather than the zone's average stage.
Trickster Woods keeps its upstream solo team size. The target is that a story
dungeon falls in two or three attempts; side dungeons may run slightly harder.

## Camp NPCs

The seven camp maps (including Base Camp's alternate map) convert static NPCs and
scripted spawners to Champion-stage-or-lower Digimon. Party assembly spawners are
excluded. Post Office, Guild Hut and the summit use the same conversion.
Conversion runs after initialization and after entry scripts, covering dynamically
replaced NPCs such as the Ravine Camp tutor.

The Forest Camp sleeper is explicitly Monzaemon. Its internal `Snorlax` entity
name and quest variables are retained so the fight and building-unlock sequence
continue working. Snorlax encounter conversion also selects Monzaemon.

## Rebuild

```powershell
python Scripts/digimon_dungeon_audit.py
python Scripts/digimon_early_zones.py
dotnet build PMDOData.sln --no-restore
```

From `DataGenerator/bin/Debug/net8.0`:

```powershell
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -index Zone
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-check
```

Then run the Python tests and publish the Windows build. Native verification uses
an isolated save; it does not edit the player's save.

## Validation completed

All 51 regression tests pass, including camp routing and seven-camp NPC conversion.
The native runtime check passes for all 35 released zones across 568 seeded floors
(seed 42; infinite segments sample their entry floor), as well as 341 Digimon forms
and 49 converted items. The full solution builds with zero errors and existing
upstream warnings.

The audit also removes six invalid generation steps from Wayward Wetlands and
restores vault item, trap and enemy placement settings from upstream data. Both
item-cleanup functions now preserve intentionally empty spawn placeholders, which
previously caused vault generation to fail and fall back to an empty map.
