# Transparent Digimon sprite packages

44/44 Digimon in the original eight evolution lines have transparent artwork and
PMDO packages. Expanded collection: 338/341 forms.

`Sources/` retains the downloaded artwork's original resolution and alpha, encoded
losslessly as PNG. `Records/` records the source/page URLs and SHA-256 hashes.
The artwork is sourced from Wikimon; its original creators retain their rights.

`Packages/<species>/` and its adjacent ZIP are equivalent PMDO imports:

- `AnimData.xml`: one-frame Idle; every configured PMDO action copies Idle.
- `Idle-Anim.png`: eight 96×96 frames in one column.
- `Idle-Offsets.png`: coincident body/hand/head effect anchors at frame center.
- `Idle-Shadow.png`: one white shadow anchor per row; smallest shadow size.

Sheet rows are Down, DownRight, Right, UpRight, Up, UpLeft, Left, DownLeft.
Rows 5–7 (zero-based) mirror the entire original frame. PMDO converts these
clockwise rows into its counterclockwise Dir8 order on import.
Images fit within 92×92 pixels with transparent padding and retain aspect ratio.
Small sources are never enlarged. Original source images remain available for
larger packages. This is static art, not a newly animated sprite set.

The playable build now uses **40-pixel runtime packages** under
`DumpAsset/Content/DigimonSprite/<IndexNum>/`. The sprite loader prefers these
eight-direction packages over the original static image. Portraits use the
transparent source images; the three unresolved forms keep their existing art.
The 96-pixel source packages remain unchanged for art review. No upstream
RawAsset files were replaced. `installed.json` maps species to runtime indices.

## Remaining art work

`all_report.json` lists three unresolved forms: Arcadiamon Rookie, Champion and
Mega. Their checked Wikimon model renders are opaque. Transparent illustrations
were not found; no package substitutes an incorrect evolution stage.

Durandamon, Zubamon and ZubaEagermon use native transparent Digimon Unlimited
pixel art pending larger cutouts. Some other forms use game-model renders, and
some illustrations retain attack effects. The Sistermon Hacker's Memory models
have faint source alpha and need better art. `review_*.jpg` and
`initial_preview.jpg` provide contact sheets for further visual review.
NX forms retain the previously selected base-form artwork.

## Rebuild and verify

From the repository root, with Python/Pillow installed:

```powershell
python Scripts/digimon_sprite_packages.py --roster initial
python Scripts/digimon_sprite_packages.py --roster all
python Scripts/digimon_sprite_packages.py --roster initial --offline --size 96
python Scripts/digimon_install_sprites.py
python -m unittest discover -s tests -q
dotnet build PMDOData.sln --no-restore
```

The download pass resumes from source hashes. Missing art is recorded in the
report; it never deletes existing game assets. Offline mode requires previously
downloaded sources. An all-roster offline pass will report the unresolved forms.

Native import verification (after building), from `DataGenerator/bin/Debug/net8.0`:

```powershell
dotnet DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-sprite-check C:/Users/arlet/PMDODump-Digimon/DataAsset/Digimon/SpritePackages/Packages
```

This runs the real CharSheet importer, saves each imported sheet to an in-memory
binary stream, and reloads it. It does not write runtime assets or player saves.
