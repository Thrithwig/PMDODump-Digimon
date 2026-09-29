# Phase 4 Part 1 — Agumon 3D-to-PMDO sprite pipeline

Status: Idle-only output is installed for Agumon (10018) in the lab and primary playtest source/runtime asset trees. Latest visual corrections were checked in the live lab game on 2026-09-23.

## Scope

This phase establishes a reproducible path from the local Digimon Story Time Stranger model data to one PMDO Agumon package. It intentionally does not add Walk, Attack, or any other non-Idle motion.

The checked-in entry point is:

```powershell
python Scripts/phase4_sprite_pipeline.py inspect work/phase4/source/agumon.glb
python Scripts/phase4_sprite_pipeline.py build config/phase4/agumon.json work/phase4/source/agumon.glb work/phase4 --repo-root .
python Scripts/phase4_sprite_pipeline.py validate config/phase4/agumon.json work/phase4/output/agumon
```

The build writes `work/phase4/output/agumon/` with `Idle-Anim.png`, `Idle-Offsets.png`, `Idle-Shadow.png`, and `AnimData.xml`, plus a machine-readable `work/phase4/phase4-build-report.json`. The intermediate browser renders are under `work/phase4/intermediate/agumon/idle/`.

## Source and provenance

The legitimate Steam installation was found at:

```text
C:\Program Files (x86)\Steam\steamapps\common\Digimon Story Time Stranger
```

The current `dsts-extractor==0.9.0` tool was installed into the ignored lab virtual environment. Its subset setup was run into `work/phase4/dsts-data`, leaving the Steam installation untouched. The catalog maps Agumon to DSTS `chr050`; the extracted GLB contains the rig, materials, and animation clips. The selected Idle clip is `chr050_bn01`.

The exported GLB is proprietary source material and is intentionally ignored by Git. The report records its SHA-256, extractor version, clip, renderer dimensions, direction order, and offset source so a reviewer can reproduce the run without committing the model.

## Rendering and conversion

The renderer is a local, scripted Three.js page driven by headless Chrome. It uses the GLB’s embedded `chr050_bn01` clip, an orthographic camera, transparent output, deterministic light positions, and eight configured azimuths. Four samples are taken per direction at the times in `config/phase4/agumon.json`.

The converter downsamples 256×256 renders to 40×40 frames, applies binary alpha, quantizes the complete Idle atlas to at most 64 opaque colors, and writes rows in the PMDO order:

```text
Down, DownRight, Right, UpRight, Up, UpLeft, Left, DownLeft
```

No manual repainting or screenshot cropping is part of the build.

## PMDO offsets and shadow

`Idle-Offsets.png` uses PMDO’s marker colors: black head, red left hand, green center, and blue right hand. `Idle-Shadow.png` uses one white shadow marker per frame. The current Part 1 mapping is a checked-in Agumon anatomical template (`template-assisted-agumon-v1`) so every frame has a deterministic valid marker set while the browser bridge is kept separate from the proprietary rig data. The GLB and report preserve the rig and animation provenance; projecting bone positions into each 40×40 frame is the next refinement before installing this package into the game asset tree.

## Validation boundary

### Playtest visual corrections (2026-09-23)

The later facial-detail revision (`work/phase4/face-corrected/`) excludes head/jaw-weighted surfaces from generic crease detection while retaining the body contour rules. A depth-tested diagnostic mask follows the original `chr050a01` mouth seam and nostril texture details, reduced to a continuous single-pixel mouth and small nostril marks. Pupil positions are projected from the anterior side of each animated eye mesh, then constrained to visible eye coverage; highlights no longer paint outside the eye. Run `python -m SpritePipeline.check_face` with `PYTHONPATH=Scripts`, the config, and this build root to check all frames and generate a direction review sheet. Structural checks do not replace a fresh native game capture.

The renderer preserves transparent backgrounds and uses corrected left/right azimuths. Depth and normal passes create one-pixel black silhouette and feature-separation lines. The eye meshes receive black pupils, with a final-resolution pupil pixel preserved for each visible projected eye. Exact black is retained through palette quantization.

Each frame's lowest opaque pixel is aligned to row 32, matching its shadow marker; anatomical offsets move with the sprite. Validation checks this contact alignment in all 32 frames, alongside alpha and palette constraints. The latest verified output is `work/phase4/outlined-pupils/output/agumon/` (63 opaque colors). Native viewport captures were taken after walking the character in TestCamp; front and side views show the updated outline, pupils, and ground contact. Only the four Agumon package files were transferred to the primary playtest; prior files are backed up under `work/phase4/playtest-backup/outlined-pupils-20260923-112828/`.

The validator checks file presence, exact sheet dimensions, Idle XML dimensions and duration count, all four per-frame offset markers, every shadow marker, binary alpha, and the palette limit. This is structural PMDO validation. Engine loading and an in-game visual playtest remain separate acceptance steps and must not be represented as complete by a successful generation run alone.

## References

- [DSTS extractor](https://tangled.org/nuffle.me/dsts-extractor/blob/a139b1fc9b9931c332159301fee2ef540fbafe47/README.md)
- [DSTS viewer](https://nuffle.me/dsts-viewer)
- [PMDO sprite format](https://wiki.pmdo.pmdcollab.org/PMD_Sprite_Format)
