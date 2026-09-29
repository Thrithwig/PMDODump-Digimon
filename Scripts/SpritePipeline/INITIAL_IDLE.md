# Initial Idle candidates

The legacy `build CONFIG GLB OUTPUT` command is unchanged. New species can use:

```powershell
venv/Scripts/python.exe Scripts/phase4_sprite_pipeline.py build-idle config/phase4/baby-kuramon-idle.json work/phase4/baby-production/kuramon-idle-v1 --cache-root work/phase4/baby-production/kuramon-idle-cache --workers 2
venv/Scripts/python.exe Scripts/phase4_sprite_pipeline.py validate-idle config/phase4/baby-kuramon-idle.json work/phase4/baby-production/kuramon-idle-v1/package/10001
```

`build-idle` accepts `--model` to override a config's `model_path`, `--cache-root`, `--workers 1..3`, and `--assemble-only`. Paths for model_path are relative to the lab root. It uses the existing renderer, conversion, registry XML writer, projected offsets and exact action-cache attestation primitives. It does not require an approved Idle or action manifest. No species-specific Python builder is needed.

Config fields follow the existing species schema: species/display_name, pmdo_index, model_path, idle_clip, idle_frames/frame_times, idle_duration_ticks (positive uniform PMDO ticks), frame_size/render_size, palette_size/alpha_cutoff, outline, renderer, offsets, canonical directions, and ground_contact_row or airborne placement. New optional checks are minimum_edge_margin (default2), approved_neutral_height, and neutral_frame (default0 in Down). idle_ground_policy is per-frame by default or fixed to retain vertical motion. Airborne placement uses one shared translation over all frames/directions and a fixed shadow.

Renderer settings must explicitly select eye_mode and fixed_framing or a fixed union framing sample set. Four offset_bones entries must name existing source bones. Each entry can remain a bone name string (unchanged behavior), or be `{ "bone": "J_center", "local_point": [x,y,z] }` for a documented anatomical body attachment transformed by that animated bone. This is a point in bone-local coordinates, not a new bone or a screen-space template. PMDO hand-slot substitutes for limbless species must be explicitly documented and visually reviewed.

The command stages and validates before publishing `package/<pmdo_index>`. Existing candidates cannot be overwritten. Failed renders keep exact verified cache frames and write `failed-resumable` summary; a validation failure publishes no package. Warm `--assemble-only` revisions start no renderer. Cache records include exact model/renderer/capture/dependency hashes, sample time/direction/azimuth, dimensions and render settings, with output hashes. Timing or other downstream conversion-only changes can reuse renders. Unattested files are never upgraded to trusted cache.

Artifacts: summary.json, validation.json, provenance.json, native-sheet.png, labeled contact-sheet.png, projected offset-sheet.png and all-direction idle-playback.gif. Validation checks registry IDs, dimensions, tick durations, explicit CopyOf Idle placeholders, exact marker multiplicity, alpha, palette, edge margins, height target, contact/airborne placement and distinct frames per direction. Initial placeholders are NOT complete additional action sets. Native CharSheet import, parent visual approval and later live-game checks remain separate gates.

Regression fixtures live in `work/phase4/baby-production/kuramon-preparation/test_idle_builder.py` within the authorized task write scope. Existing tests remain unchanged. Botamon's approved Idle is reproduced separately through this entry point for exact package comparison; approved files are never regenerated in place.
