# Phase 4 efficiency commands

Run these from the lab root with `venv/Scripts/python.exe Scripts/phase4_sprite_pipeline.py` (Windows). All outputs belong under a new `work/phase4/pipeline-efficiency/<run>` directory. The reviewed Agumon package and its frame cache are protected.

## Bounded auditions and comparison

`audition <species-config.json> <jobs.json> <model.glb> <output-root>` accepts 1–16 requests. Each job has a native `clip`, `time` in seconds, `azimuth` in degrees, and optional `note`. It writes a labeled contact sheet, per-frame attestations, and `audition.json`. A warm rerun uses verified frames without starting Chrome. Auditions are unreviewed pose evidence, not a package.

`benchmark <species-config.json> <jobs.json> <model.glb> <output-root> --baseline-renderer <frozen-renderer-dir>` compares the old single-frame route with one persistent worker. It writes `old/`, `new/`, and `benchmark.json` with decoded-pixel/full-geometry parity and elapsed times. The baseline directory must contain the original `render.html`, `capture.mjs`, and matching Three.js dependencies.

## Actions

`build-actions <fresh-output-root> --config <species-config.json> --actions-config <actions.json> --workers 2` renders only missing verified frames, assembles into staging, then publishes a complete unreviewed candidate. `--cache-root <prior-intermediate-dir>` shares exact attested renders across revisions. `--assemble-only` requires every render frame to match its recorded inputs. A successful candidate output root is immutable; use a new root for a revision. If rendering fails, `summary.json` says `failed-resumable`, the verified intermediate frames remain, and no candidate package is published.

Omitting both configs retains the Agumon CLI default. `--only Hurt` creates a diagnostic partial package containing Idle and Hurt; it is not a full action-set revision. For a complete revision, omit `--only` and use a fresh output root plus a shared cache root. `validate-actions` and `previews` accept the same `--config` and `--actions-config` flags. The existing `build` command remains the route for generating an initial Idle; action building requires a complete approved Idle baseline and does not approve one itself.

An action manifest specifies `species` matching the render config, `model_path`, `approved_idle`, `palette_policy` (`approved-idle` or `quantized`), `mouth_palette`, and nonempty `actions`. Optional `installed_idle` pins an installed comparison; `mouth_colors` and `open_mouth_actions` define species-specific palette checks. Each action needs a PMDO registry `name`, native `clip`, declared `seconds`, positive tick `durations`, and `ground_policy` (`per-frame` or `fixed`); optional `sample_phases`, `turn_degrees`, `repeat_cycles`, `events`, and `closed_eyes` control sampling and conversion. Species config supplies PMDO ID, frame/render size, direction azimuths, renderer and anatomical bone settings, and placement. Production actions require four explicit offset bone mappings. The approved Idle PNGs and Idle XML element are preserved; changed candidate output remains pending visual review and native engine checks.

Render records hash the model GLB (including embedded materials/textures), renderer HTML, batch capture code, render-side Python code, Three.js lockfile, exact clip/time/azimuth/direction, size, and settings. Image and geometry hashes are checked before reuse. Conversion, palette, duration ticks, and XML events are downstream inputs; changing only those can reuse render frames when sample times stay identical.
