# Dungeon pair tileset review — proposals only

## Scope and evidence

Reviewed all 185 `RawAsset/TileDtef/*/tileset_0.png` images visually on twelve numbered contact sheets at native sheet scale or below. Each folder has an individual visual description in the [catalogue](tileset_review/CATALOGUE.md) and a full-size source link in the [searchable image gallery](tileset_review/catalogue.html). This is an art-selection review, not an implementation or an in-engine visual playtest.

Restored the missing TileDtef directory from the existing RawAsset commit `03c80dad937911572f8fb19903771a47956fc696`, without changing HEAD, gitlinks, or the index. All **4,884 tracked files** are present and byte-identical to their Git blobs; all **185 folders** contain `tileset_0.png`. The existing staged deletions in RawAsset have deliberately not been staged away: the filesystem is restored, but a future commit must not accidentally commit that pre-existing deletion state. No other missing RawAsset directories were restored.

All 185 folders also have a same-named `.tile` file under `DumpAsset/Content/Tile`. That is evidence the corresponding compiled files exist, not proof that every animation, layer combination, or autotile ID works in play. The earlier missing raw checkout did not establish a need for Test Dungeon artwork. The installed library and this visual review provide usable candidates for every pair.

The catalogue inventories animation-frame files, but only the requested base sheets were visually reviewed. It does not claim animation playback has been tested. Names such as `UnusedSteamCave` describe source folders, not verified lack of usage in the game. No unused-assets claim is made without a separate runtime reference audit.

## Recommended visual identities

Folder names below identify the reviewed source sheets, not guessed runtime texture IDs. Whole sets should be used together by default. Change palettes between floor bands; avoid arbitrary mixing of banks and floors within one floor until seams have been checked. Floors are proposals based on the current run-up lengths. For every lair: floors 1–6 are challenge floors, floor 7 remains the separately authorized temporary MountainPeak arena, and floor 8 uses the proposed reward-room palette. Boss-art replacement remains a separate art task.

| Pair | Run-up progression | Lair progression | Reserved visual identity |
|---|---|---|---|
| Factorial Quarry / Clockwork Vault — Barbamon | F1–4 `RockMaze`; F5–8 `DeepBoulderQuarry`; F9–12 `RockAegisCave` | F1–3 `BuriedRelic3`; F4–6 `BuriedRelic1`; F8 `GoldenChamber` | Earthy excavation becoming gold masonry and a concentrated hoard |
| Dragon Eye Basin / Dragon Eye Depths — Leviamon | F1–3 `SidePath`; F4–7 `CraggyCoast`; F8–10 `LowerBrineCave` | F1–3 `BrineCave`; F4–6 `DeepSealedRuin`; F8 `MiracleSea` | Shoreline sand becoming dark teal, blue and purple sea caves |
| Thunder Pass / Storm Crown — Daemon | F1–4 `FarAmpPlains`; F5–8 `AmpPlains`; F9–13 `MtThunder` | F1–3 `MtThunderPeak`; F4–6 `ElectricMaze`; F8 `ElectricMaze` | Exposed pale crags becoming a cream-and-blue signal installation |
| Misty Ridge / Veil Palace — Lilithmon | F1–4 `MystifyingForest`; F5–8 `FoggyForest`; F9–13 `MurkyForest` | F1–3 `WesternCave1`; F4–6 `WesternCave2`; F8 `WesternCave1` | Misty woodland becoming deceptively inviting pink-flowered architecture |
| Freezeland Path / Slumbering Caldera — Belphemon | F1–4 `FrostyForest`; F5–8 `MtFreeze`; F9–13 `DarkIceMountain` | F1–2 `SteamCave`; F3–4 `MagmaCavern2`; F5–6 `DeepDarkCrater`; F8 `SteamCave` | Drained white-blue cold outside; stolen orange heat accumulating below |
| Infinity Approach / False Dawn Observatory — Lucemon | F1–4 `NorthernRange1`; F5–8 `NorthernRange2`; F9–13 `SkyTower` | F1–3 `SkyTower`; F4–6 `WishCave1`; F8 `SkyTower` | Pale high-altitude ascent becoming pristine white/cobalt controlled architecture |
| Infinity Mountain / Return Protocol Citadel — Beelzemon | F1–4 `ZeroIsleSouth2`; F5–8 `SkyPeakSummitPass`; F9–13 `SpacialCliffs` | F1–3 `SteelAegisCave`; F4–6 `FutureTemporalTower`; F8 `FutureTemporalTower` | Grey mountain becoming charcoal, steel-blue and ordered machine-like ruins |

These primary selections share no source folder between different pairs. Visual separation also comes from material and value, not only hue: gold excavation, marine sediment, open storm crags, flowering forest, cold-to-hot volcanic descent, luminous sky masonry, and dark machine geometry.

## Pair-by-pair reasoning and limitations

### Barbamon: resources taken from earth into a hoard

`RockMaze` has readable grey boulders, brown banks and gravel. `DeepBoulderQuarry` deepens the excavation to red-purple rock. `RockAegisCave` introduces carved, greened stone before `BuriedRelic3` turns the route into constructed sandstone. `BuriedRelic1` visibly concentrates gold; `GoldenChamber` should be reserved for the reward floor so its bright gold does not make every challenge floor exhausting to read.

This supports greed and appropriation using existing art. It does not supply literal gears, ore carts, broken supports, gold piles, or machinery. Those require props or later bespoke art. `DarknightRelic` is a credible alternative for timber storage rooms, but its walls look like crates rather than a metal factory. Do not call it machinery based on its name. CopperQuarry's original floor/secondary components can remain an alternate industrial-green accent, but they are incomplete sets and need a matched wall.

### Leviamon: drought at the rim, pressure below

`SidePath` supplies pale sand and orange banks for the drained approach. `CraggyCoast` cools the floor toward the blue-grey shoreline. `LowerBrineCave` and then `BrineCave` produce a clear green-to-navy/purple descent. `DeepSealedRuin` supplies dark submerged-looking masonry for the pressure system. `MiracleSea` provides a lighter aquatic release after the objective.

The blue-green appearance does not make a floor physically underwater. Keep safe walkable ground readable; water depth, pressure and restored flow require existing terrain/event behavior or props. `StormySea1/2` and the `SilverTrench3` components are alternatives for a strongly underwater space, but their similarly saturated blue floor and secondary layers make obstacle readability risky without a rendered map review. They are not the first choice.

### Daemon: storm geography becoming a relay site

`FarAmpPlains` begins with tan rock and olive grass; `AmpPlains` and `MtThunder` bring progressively pale exposed stone and deep blue water. `MtThunderPeak` adds sharp crags and a gold cast. `ElectricMaze` carries that pale gold into regular cream walls and blue masonry. The visual change communicates entry to a built relay complex without borrowing Barbamon's saturated gold hoard.

No base sheet visibly provides a broadcast mast, cables, control panels, or proof of animated electricity. Those remain prop/effect requirements. `LightningField` is an alternate golden outdoor accent, but its trees would weaken the crag-to-installation sequence if overused. Storm conditions should not obscure the route or introduce an elemental party requirement.

### Lilithmon: a pleasant sanctuary with visible unease

`MystifyingForest` establishes a believable woodland. `FoggyForest` visibly includes washed-out haze; `MurkyForest` shifts the journey to dark teal foliage and purple ground. The floral lattice and pale stone of `WesternCave1` make the palace inviting, while `WesternCave2` repeats the same pink flowers over darker stone farther in. Similar structure with darker values supports the false-sanctuary theme better than an unrelated purple crystal cavern.

`PoisonMaze` is an optional small-area accent for contaminated vegetation. Its purple ground and yellow grass are strong enough to overwhelm the pair, so it should not replace the main palace palette. Base-sheet haze is not a substitute for testing fog opacity. Vines that paralyze, spore emitters, evidence stations and rescued scouts need their own visuals; decorative vegetation must not imply unsupported interactions.

### Belphemon: keep the surface cold

This pair deliberately crosses two temperatures. The storyboard's Fire identity comes from heat being stolen into the core, not from a fiery surface. `FrostyForest`, `MtFreeze` and `DarkIceMountain` take travelers from snowy vegetation to bleak exposed ice. The warm rock and cool pools in `SteamCave` bridge into `MagmaCavern2`; `DeepDarkCrater` concentrates the darkest basalt and hottest lava near the core. Return to the quieter steam-cave palette for recovery.

No sheet alone establishes a heat siphon or safe sleeping refuge. Heat pipes, depleted fuel stores and rescue-space props remain required storytelling details. Palette transitions should occur between floors rather than placing incompatible ice and lava bank art side by side. Flame terrain must retain its actual engine meaning.

### Lucemon: beauty and imposed order

`NorthernRange1/2` offer pale natural mountain textures without repeating the snow-heavy Belphemon route. `SkyTower` provides cloud-like white forms and blue negative space for the ascent. Repeating it at the lair entrance links the pair; `WishCave1` then introduces precise pale walls and blue brick floors, visually replacing natural irregularity with controlled order. The reward can return to cloud forms to suggest reopened movement.

`JoyousTower` is an alternate if a stronger magenta accent is wanted, but the pink paving makes the area feel less sterile and closer to Lilithmon's palette. No static tile proves wind, vacuum or restored air currents. Wind effects and observation equipment remain separate needs. White party sprites must be checked against the pale walls and floors in an eventual implementation.

### Beelzemon: physical mountain into a protocol complex

`ZeroIsleSouth2` supplies stony grey cliffs and subdued gravel, followed by the darker `SkyPeakSummitPass` and `SpacialCliffs`. `SteelAegisCave` introduces cold carved structure, and `FutureTemporalTower` resolves it into repeated dark geometric masonry. This keeps the finale darker and heavier than Lucemon's luminous controlled order.

`WorldAbyss2` is a strong optional accent for a single corrupted chamber or threshold, not the default six-floor texture. Its neon tangles and gold marks are visually noisy. `FutureTemporalSpire` is an alternative for a damaged interior with broken paving. Literal terminals, protocol doors, transmission conduits and rescue consoles are not present in these base sheets; do not claim the ruins are a finished machine facility. Reserve the neon corruption for this pair if selected.

## Before any future implementation

1. Resolve the chosen source components to actual in-memory autotile IDs and verify the compiled sheet content. Matching `.tile` filenames alone are not sufficient.
2. Render a representative early/deep floor for each pair, checking floor/wall/secondary seams, stairs, traps, item outlines and dark or white Digimon sprites.
3. Preview animated variants, especially water, lava and patterned channels; the present catalogue does not evaluate their motion.
4. Keep water, lava and void visuals consistent with actual terrain rules. The DTEF importer labels columns Wall/Secondary/Floor; the word Secondary does not itself define gameplay terrain.
5. Keep the temporary floor-7 arena explicitly identified. The proposed six-floor palettes can guide replacement arena art, but this review does not change the LoadGen map.

No dungeon data, assignment, terrain behavior, weather, encounters, quest flags or build output was changed for this review. The only asset operation was restoring the requested raw source subtree; the remaining additions are catalogue material and its reproduction script.
