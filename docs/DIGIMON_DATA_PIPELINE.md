# Digimon data import and initial roster

This is a data preparation milestone, not a playable Phase 1 release. The C# data
generator and runtime do not yet consume these manifests. No submodule source or
gitlinks are changed by the import.

The next data milestone is also implemented: the separate stat/progression overlay
and compiler. See `docs/DIGIMON_PHASE1_BALANCE.md` for rules, generation commands,
starter comparisons, and numerical reachability results. Runtime integration and
skill combat conversion remain pending.

## Reproduce

Use Python 3.10 or newer from the repository root. The importer and its tests use
only the standard library. Input is the five user-supplied Cyber Sleuth CSV files.

```sh
python Scripts/digimon_dataset.py --input DataAsset/Digimon/Source --output DataAsset/Monster/digimon_manifest.json
python Scripts/digimon_dataset.py --input DataAsset/Digimon/Source --roster DataAsset/Digimon/phase1_roster.json --output DataAsset/Digimon/phase1_manifest.json
python -m unittest discover -s tests -v
dotnet build PMDOData.sln --no-restore
```

The full manifest contains 341 species, 494 skill-name groups, and 910 forward
links. Its reverse links are derived from those forward links. The roster manifest
contains 44 unique forms and 115 unambiguous skill groups. Source graph edges that
are not on the eight selected paths remain in the full manifest only.

## Selected lines

| Choice | Initial line (source names) |
| --- | --- |
| Agumon | Botamon → Koromon → Agumon → Greymon → MetalGreymon → WarGreymon |
| Gabumon | Punimon → Tsunomon → Gabumon → Garurumon → WereGarurumon → MetalGarurumon |
| Biyomon | Pabumon → Yokomon → Biyomon → Birdramon → Garudamon → Hououmon |
| Tentomon | Pabumon → Motimon → Tentomon → Kabuterimon → MegaKabuterimon → HerculesKabuterimon |
| Palmon | Pabumon → Tanemon → Palmon → Togemon → Lillymon → Rosemon |
| Gomamon | Poyomon → Bukamon → Gomamon → Ikkakumon → Zudomon → Vikemon |
| Patamon | Poyomon → Tokomon → Patamon → Angemon → MagnaAngemon → Seraphimon |
| Gatomon | Punimon → Nyaromon → Salamon → Gatomon → Angewomon → Ophanimon |

Gatomon remains a Champion in source data; selecting it does not silently relabel
its stage or decide starter balance. Baby forms shared by multiple lines appear
once in the manifest and retain the union of selected edges. Each chosen lead has
one forward path; additional branches are deferred. This selection does not yet
assign NPC roles, encounters, combat balance, or release status in the game.

## Schema 2 and source fidelity

- `source.files` records SHA-256 checksums and nonblank row counts. CSV bytes are
  preserved, including line endings, using `.gitattributes`. The publisher version
  and original download date are unknown (`null`); hashes identify this snapshot.
- `source` rows retain source facts as strings. `stats_by_level` preserves all six
  stats at 1, 50, and 99 without inventing a growth formula. `stats` supports older
  unsuffixed fixture tables and is empty for the real level-specific input.
- `requirements` preserve the dataset conditions, including ABI, CAM, and textual
  special conditions. These are not yet executable PMDO rules.
- Exactly one audited spelling correction maps learnset `Commet Hammer II` to
  `Comet Hammer II`. The original learnset value and correction record are retained.
  Whitespace/punctuation normalization resolves `ChronoBreaker`/`Chrono Breaker`.
- 86 `N/A` evolution destinations are terminal markers, not species IDs; two blank
  rows are skipped. Other unknown references fail validation.
- All 505 skill rows survive in 494 name groups. Identical definitions are merged
  with their source row numbers retained. Ten groups have distinct variants.
  Variant IDs include a hash of their source definition; they never depend on row
  ordering. A changed definition gets a new variant ID on refresh.
- An ambiguous learnset keeps `variant: null`, and the full manifest lists an issue.
  Roster generation rejects ambiguous assignments instead of guessing. None of
  the 44 selected forms has such an assignment. A future overlay must explicitly
  resolve variants before adding affected species.
- Selection validates every path against the full source graph and filters both
  graph directions and skill definitions to produce a closed slice.

Do not use Wikimon to fill gameplay gaps. Future intentional PMDO interpretations
belong in a separate overlay; the normalized source manifest remains authoritative.

## Images

`DataAsset/Digimon/Images` contains one PNG per selected form. `image_sources.json`
maps dataset IDs to the explicitly selected Japanese names and original image URLs
from https://wikimon.net/Visual_List_of_Digimon. `image_provenance.json` records file
pages, URLs, retrieval times, dimensions, original/PNG checksums, and processing.

The selected originals are JPEG. Only encoding is changed to PNG; no resizing,
cropping, background removal, or synthetic art is applied. White backgrounds remain.
A static-image runtime adapter now supplies dungeon sprites and portraits. Attribution does not establish
redistribution permission; that status is recorded explicitly with each image.

Optional re-download requires Pillow and network access:

```sh
python Scripts/digimon_images.py
```

Existing files with matching provenance hashes are skipped. Tests verify all 44
image files and their checksums without network access. No audio conversion,
temporary battle digivolution, or save migration is introduced.

## Runtime generation and checks

```sh
python Scripts/digimon_runtime_assets.py
dotnet build PMDOData.sln --no-restore
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../DumpAsset/ -index Monster Skill Zone Tile GrowthGroup
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../DumpAsset/ -digimon-check
python -m unittest discover -s tests -v
dotnet publish -c Release -r win-x64 PMDC/PMDC/PMDC.csproj --no-restore
```

The trailing slash in `-asset` is required by the upstream path resolver. Native
checks do not write a player save: they validate 44 installed forms and learnsets,
round-trip characters through the engine serializer, and generate all regular and
secret-room floors for three seeds (including the user's crash seed). They reject
dangling stair destinations, missing guardians, and non-Digimon enemies.
Generated native content and indices are runtime assets; `bin`, `obj`, and publish
folders remain build output and must not be committed.

EXP tuning lives in `Scripts/digimon_progression_tuning.py`. Runtime generation
writes six stage growth curves, BaseEXP, and the Tropical Path EXP rate, then
removes Apricorn-only entries from dungeon drop/shop pools. Regression tests model
200 intro runs, verify low-level farming suppression, and check all zone tables
and shared shop stock for remaining Apricorn entries.
