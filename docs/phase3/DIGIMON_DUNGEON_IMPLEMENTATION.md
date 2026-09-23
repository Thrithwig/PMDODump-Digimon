# Phase 3 dungeon implementation matrix

The generator now emits seven stable lair IDs: `barbamon_lair`, `leviamon_lair`, `daemon_lair`, `lilithmon_lair`, `sleeping_caldera`, `lucemon_lair`, and `beelzemon_lair`. Each lair has six procedural challenge floors, a fixed seventh `LoadGen` arena using the existing `end_treacherous_mountain` map backed by `MountainPeak.png`, and a procedural reward floor. Challenge and reward floors use compiled themed autotiles; the arena remains intentionally unchanged. The arena map is rethemed at map start with the lair boss and support guard; the reward callback is idempotent and grants a first-clear box plus a repeat-clear TM.

| Route | Level | Floors | Unlock result |
|---|---:|---:|---|
| Factorial Quarry | 25 | 12 | Clockwork Vault, Canyon Camp, Dragon Eye Basin |
| Dragon Eye Basin | 25 | 10 | Dragon Eye Depths, Stormwatch, Thunder Pass |
| Thunder Pass | 30 | 13 | Storm Crown, Misty Shelter, Misty Ridge |
| Misty Ridge | 35 | 13 | Veil Palace, Freezeland, Freezeland Path |
| Freezeland Path | 40 | 13 | Slumbering Caldera, Dino Survey, Infinity Approach |
| Infinity Approach | 50 | 13 | False Dawn Observatory, Infinity Summit, Guildmaster Trail |
| Guildmaster Trail | 65 | 13 | Return Protocol Citadel after six lair flags |
| Lairs 1–6 | 60 | 8 | Completion flag only |
| Return Protocol Citadel | 70 | 8 | Finale completion flag |

`story_missions.lua` owns the live primary-request flow for each run-up: acceptance, target rescue, successful-clear recording and one-time debrief. The early chain (Tropical Path, Faultline Ridge, Faded Trail, Trickster Woods, Fertile Valley, and Flyaway Cliffs) must be debriefed before Factorial Quarry can be accepted. The attached zone callbacks call the successful-clear hook, while failure and escape return without mutating the request. `phase3_progression.lua` makes the debrief unlock explicit and idempotent: each run-up exposes its own lair, next camp and next run-up; lairs do not gate later run-ups. A generic clear never writes a lair flag. Floor-7 scripts use `phase3_lair.lua` to record boss defeat and the separate rescue/recovery objective before `clear_lair` can write a key. The first six lair records exclusively gate Guildmaster clearance, and the Guildmaster debrief exposes the final Citadel.

Temporary arena art needs six distinct replacements: machine vault, submerged basin, storm peak, mist palace, false-dawn observatory, and corrupted citadel. Each needs a boss platform, objective/rescue tile, clear entry, reward exit, themed hazards, elevation, lighting and animated environmental detail. Existing MountainPeak remains unmodified.

The generator keeps the eighteen storyboard optional maps and releases them as playable routes. `story_missions.lua` adds one deterministic rescue or problem request for each optional map; requests are offered by Clockmon after the primary chain, use the native mission spawner, require a successful clear after the objective, and can be repeated as renewable surveys. Their entry levels remain within five levels of the unlocking main route (for example, Overgrown Wilds 15, Lava Floe Island 25, Moonlit Courtyard 30, Sickly Hollow 35, Relic Tower 30, Cave of Whispers 35, and Prism Isles 45). Postgame requests, secret rooms, hidden stairs, and postgame reward redesigns remain deferred as directed by the implementation prompt.

Validation source coverage: `tests/lua/test_digimon_phase3_progression.lua` exercises failed exits, retry, objective-before-clear rejection, one-time run-up debrief, boss-and-objective lair completion, duplicate-clear rejection, and the six-key gate. The generator emits the released optional maps, seven lairs, and rebuilds `Data/Zone/index.idx`. Shared encounter/item sanitation maps legacy species references to the installed Digimon forms, removes unreleased and Apricorn loot, and supplies safe Digimon encounters and supplies for empty optional segments. The native runtime check validates the generated floor structure, deterministic Tropical Path guardian, Digimon encounter rules, usable loot and stairs: 341 forms, 49 converted items, 40 released zones and 566 seeded floors all pass. Secret rooms, hidden stairs and postgame reward redesigns remain deferred as directed by the implementation prompt.

## Tileset v2 acceptance matrix

The complete acceptance matrix, including stable dungeon IDs, legacy references, each resolved wall/floor/secondary ID, status configuration, generated scans, evidence paths, and Astra’s review state is maintained in [`DIGIMON_TILESET_ACCEPTANCE.csv`](DIGIMON_TILESET_ACCEPTANCE.csv). The source and generated-data checks are passing for all fourteen dungeons. Astra’s required rendered-map review remains pending because the native game window could not be exposed to the capture tooling; the raw-sheet catalogue is documented separately and is not being counted as rendered evidence.

Runtime IDs below were resolved from the compiled-tile registry in `ZoneInfoBase.cs`, which invokes each exact wall/floor/secondary triple in its tile test map. They were not constructed from the raw DTEF folder names.

| Dungeon | Floor bands | Runtime triples (wall/floor/secondary) | Status | Generated scan | Render evidence |
|---|---|---|---|---|---|
| Factorial Quarry | 1–4 RockMaze; 5–8 DeepBoulderQuarry; 9–12 RockAegisCave | `rock_maze`; `deep_boulder_quarry`; `rock_aegis_cave` | sandstorm | generated and scanned | [manifest](tileset_review/RENDER_MANIFEST.md) |
| Clockwork Vault | 1–3 BuriedRelic3; 4–6 BuriedRelic1; 7 MountainPeak; 8 GoldenChamber | `buried_relic_3`; `buried_relic_1`; `golden_chamber` | sandstorm | generated and scanned | manifest |
| Dragon Eye Basin | 1–3 SidePath; 4–7 CraggyCoast; 8–10 LowerBrineCave | `side_path`; `craggy_coast`; `lower_brine_cave` | rain | generated and scanned | manifest |
| Dragon Eye Depths | 1–3 BrineCave; 4–6 DeepSealedRuin; 7 MountainPeak; 8 MiracleSea | `brine_cave`; `deep_sealed_ruin`; `miracle_sea` | rain | generated and scanned | manifest |
| Thunder Pass | 1–4 FarAmpPlains; 5–8 AmpPlains; 9–13 MtThunder | `far_amp_plains`; `amp_plains`; `mt_thunder` | rain | generated and scanned | manifest |
| Storm Crown | 1–3 MtThunderPeak; 4–6 ElectricMaze; 7 MountainPeak; 8 ElectricMaze | `mt_thunder_peak`; `electric_maze` | rain | generated and scanned | manifest |
| Misty Ridge | 1–4 MystifyingForest; 5–8 FoggyForest; 9–13 MurkyForest | `mystifying_forest`; `foggy_forest`; `murky_forest` | misty_terrain | generated and scanned | manifest |
| Veil Palace | 1–3 WesternCave1; 4–6 WesternCave2; 7 MountainPeak; 8 WesternCave1 | `western_cave_1`; `western_cave_2` | misty_terrain | generated and scanned | manifest |
| Freezeland Path | 1–4 FrostyForest; 5–8 MtFreeze; 9–13 DarkIceMountain | `frosty_forest`; `mt_freeze`; `dark_ice_mountain` | snow | generated and scanned | manifest |
| Slumbering Caldera | 1–2 SteamCave; 3–4 MagmaCavern2; 5–6 DeepDarkCrater; 7 MountainPeak; 8 SteamCave | `steam_cave`; `magma_cavern_2`; `deep_dark_crater` | snow F1–2; sunny F3–6 | generated and scanned | manifest |
| Infinity Approach | 1–4 NorthernRange1; 5–8 NorthernRange2; 9–13 SkyTower | `northern_range_1`; `northern_range_2`; `sky_tower` | cloudy | generated and scanned | manifest |
| False Dawn Observatory | 1–3 SkyTower; 4–6 WishCave1; 7 MountainPeak; 8 SkyTower | `sky_tower`; `wish_cave_1` | cloudy | generated and scanned | manifest |
| Guildmaster Trail | 1–4 ZeroIsleSouth2; 5–8 SkyPeakSummitPass; 9–13 SpacialCliffs | `zero_isle_south_2`; `sky_peak_summit_pass`; `spacial_cliffs` | cloudy | generated and scanned | manifest |
| Return Protocol Citadel | 1–3 SteelAegisCave; 4–6 FutureTemporalTower; 7 MountainPeak; 8 FutureTemporalTower | `steel_aegis_cave`; `future_temporal_tower` | cloudy | generated and scanned | manifest |
