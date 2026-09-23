# Terra visual-playtest transfer review manifest

Status: **review-only; no copy-back is authorized.** This manifest records the
complete candidate source set for the Terra visual-playtest implementation. It
does not approve a file transfer, a commit, a push, a gitlink update, or an
automatic merge into `../playtest-digimon-phase1-1ea2e293`.

Use this together with [COPY_BACK_WORKFLOW.md](COPY_BACK_WORKFLOW.md), the
[implementation brief](TERRA_VISUAL_PLAYTEST_IMPLEMENTATION.md), and the
[visual changelog](TERRA_VISUAL_PLAYTEST_CHANGELOG.md). The copy baseline is
`../outputs/agent-lab-setup/baseline-files.jsonl`, relative to the lab root.

## Baseline interpretation

The lab was copied from already-dirty outer, PMDC, and RogueEssence trees.
Git status and Git HEAD are therefore not a transfer boundary. The baseline
contains the pre-lab SHA-256 values for existing paths. Candidate files absent
from it are additions after the copy. Candidate files present in it but now
different are marked **modified/hunk review**: reviewers must isolate the
visual-playtest hunks against the recorded baseline before any replacement.
The baseline alone cannot attribute individual hunks in an already-dirty file
to Terra versus other post-copy work.

No candidate below changes tiles, game content, story/progression, combat, or
engine behavior outside the opt-in visual-playtest/developer path. That scope
statement still needs source review.

## Candidate source-controlled files

### Outer lab repository

**Modified/hunk review (present in baseline):**

| Path | Candidate purpose |
| --- | --- |
| `DataGenerator/DataGenerator.csproj` | Includes the explicit playtest fixture source. |
| `DataGenerator/Program.cs` | Adds `-test-camp` and `-camp-layout-fixture` generation paths. |

**Added after the copy (not present in baseline):**

| Path(s) | Candidate purpose |
| --- | --- |
| `DataGenerator/Data/Zones/ZoneInfoPlaytesting.cs` | Lab-only Test Camp and camp-layout fixture source. |
| `Scripts/digimon_visual_checks.py`, `Scripts/digimon_playtest_adapter_smoke.py`, `Scripts/digimon_playtest_adapter_negative_smoke.py`, `Scripts/digimon_test_camp_interactions_smoke.py` | Bounded Test Camp, adapter, and interaction wrappers. |
| `Scripts/digimon_camp_layout_checks.py`, `Scripts/digimon_p01_dungeon_layout_checks.py`, `Scripts/digimon_p02_dungeon_layout_checks.py`, `Scripts/digimon_p03_dungeon_layout_checks.py`, `Scripts/digimon_p04_dungeon_layout_checks.py`, `Scripts/digimon_p05_dungeon_layout_checks.py`, `Scripts/digimon_p06_dungeon_layout_checks.py`, `Scripts/digimon_p07_dungeon_layout_checks.py`, `Scripts/digimon_p02_p07_dungeon_poi_crops.py` | Fixed layout and native POI-crop wrappers. |
| `Scripts/digimon_runup_visual_band_checks.py`, `Scripts/digimon_runup_visual_band_seed_20260919_checks.py`, `Scripts/digimon_runup_visual_band_seed_424242_checks.py`, `Scripts/digimon_runup_seed_fingerprint_comparison.py`, `Scripts/digimon_early_seeded_routes_visual_checks.py`, `Scripts/digimon_early_seeded_routes_dungeon_poi_crops.py`, `Scripts/digimon_lair_generated_floor_seed_refresh.py`, `Scripts/digimon_layout_determinism_check.py` | Declared-seed layout, generic runtime POI-crop, and metadata-fingerprint wrappers. |
| `Scripts/digimon_dungeon_input_smoke.py`, `Scripts/digimon_visual_catalog.py` | Fixed queued-input smoke and local evidence catalog. |
| `tests/test_playtest_adapter_safety.py`, `tests/test_visual_catalog.py` | Wrapper/catalog regression tests. |
| `tests/visual/test-camp.json`, `tests/visual/test-camp-interactions.json`, `tests/visual/camps-layout.json`, `tests/visual/dungeon-input-smoke.json` | Test Camp, camp, and fixed input contracts. |
| `tests/visual/p01-barbamon-layout.json`, `tests/visual/p01-dungeon-poi-crops.json`, `tests/visual/p02-leviamon-layout.json`, `tests/visual/p02-p07-fixed-dungeon-poi-crops.json`, `tests/visual/p03-daemon-layout.json`, `tests/visual/p04-lilithmon-layout.json`, `tests/visual/p05-belphemon-layout.json`, `tests/visual/p06-lucemon-layout.json`, `tests/visual/p07-beelzemon-layout.json` | Fixed P01–P07 layout and crop contracts. |
| `tests/visual/runup-visual-bands-layout.json`, `tests/visual/runup-visual-bands-seed-20260919-layout.json`, `tests/visual/runup-visual-bands-seed-424242-layout.json`, `tests/visual/early-seeded-routes-layout.json`, `tests/visual/early-seeded-routes-dungeon-poi-crops.json`, `tests/visual/lair-generated-floor-seed-refresh.json` | Fixed declared-seed layout and generic runtime POI-crop contracts. |
| `docs/playtesting/TEST_CAMP_PILOT_RUNBOOK.md`, `docs/playtesting/PLAYTEST_FILE_ADAPTER_PROTOCOL.md`, `docs/playtesting/VISUAL_COVERAGE_PLAN.md`, `docs/playtesting/TERRA_VISUAL_PLAYTEST_CHANGELOG.md`, `docs/playtesting/TRANSFER_REVIEW_MANIFEST.md` | Runbook, protocol, coverage, evidence inventory, and this review manifest. |

`DataGenerator/Data/Zones/ZoneInfoPhase3.cs` is deliberately **not** a visual
candidate. It is referenced only to verify the pre-existing lair floor layout;
its dirty state belongs to other conversion work.

### PMDC nested repository: `PMDC`

**Modified/hunk review (present in baseline):**

| Path | Candidate purpose |
| --- | --- |
| `PMDC/PMDC/Program.cs` | Parses and validates the bounded opt-in playtest flags. |

This is a separate nested repository review. Do not replace `PMDC` as a
directory and do not update the outer repository's `PMDC` gitlink.

### RogueEssence nested repository: `PMDC/RogueEssence`

**Modified/hunk review (present in baseline):**

| Path(s) | Candidate purpose |
| --- | --- |
| `RogueEssence/GameBase.cs`, `RogueEssence/FrameInput.cs`, `RogueEssence/Scene/GameManager.cs` | Opt-in controller update/draw/input path and declared-seed preservation. |
| `RogueEssence/Content/GraphicsManager.cs`, `RogueEssence/Ground/BaseGroundScene.cs`, `RogueEssence/Dungeon/BaseDungeonScene.cs`, `RogueEssence/Ground/GroundScene.cs` | Native capture, map artifact, and enabled-only overlay path. |
| `RogueEssence.Editor.Avalonia/ViewModels/DevForm/DevFormViewModel.cs`, `RogueEssence.Editor.Avalonia/Views/DevForm/DevForm.axaml` | Registers the developer Playtest panel. |

**Added after the copy (not present in baseline):**

| Path(s) | Candidate purpose |
| --- | --- |
| `RogueEssence/Dev/Playtesting/PlaytestController.cs`, `RogueEssence/Dev/Playtesting/PlaytestFileAdapter.cs` | Bounded controller and disposable-session JSON adapter. |
| `RogueEssence.Editor.Avalonia/ViewModels/DevForm/DevTabPlaytestViewModel.cs`, `RogueEssence.Editor.Avalonia/Views/DevForm/DevTabPlaytest.axaml`, `RogueEssence.Editor.Avalonia/Views/DevForm/DevTabPlaytest.axaml.cs` | Developer Playtest panel implementation. |

RogueEssence must be reviewed and eventually committed/published independently
of both `PMDC` and the outer lab. In particular, do not treat the outer
`PMDC` gitlink as carrying RogueEssence source.

## Excluded paths and generated output

These are not transfer candidates and must not be committed or copied back as
implementation payload:

- `work/playtest-profiles/**` and `work/visual-checks/**`: disposable
  profiles, saves, logs, PNGs, state/check JSON, HTML reports, and catalogs.
- `PMDC/publish/**`, `**/bin/**`, `**/obj/**`: build and publish output.
- Generated Test Camp/camp-layout fixture data in the published asset tree:
  regenerate it from the DataGenerator candidate source.
- `.git/**`, all submodule metadata, all gitlinks, runtime caches, screenshots,
  historical saves, and diagnostic dumps.
- All unrelated inherited dirty conversion files, including gameplay data,
  dungeon/story generators, item/move scripts, PMDC spawning changes, and
  RogueEssence character/action files.

There is no DataGenerator nested repository: it is outer-lab source. There are
no candidate changes to `.gitmodules`, remotes, or gitlinks. No automatic
transfer is safe or authorized.

## Required rebuild, generation, and fixture sequence

Run in the destination only after a file-by-file, three-way review against the
copy baseline and current primary. Use an isolated destination profile and
destination publish directory.

```powershell
dotnet build DataGenerator\DataGenerator.csproj --no-restore -v:q
dotnet build PMDC\PMDC\PMDC.csproj --no-restore -v:q
dotnet publish -c Release -r win-x64 PMDC\PMDC\PMDC.csproj --no-restore -v:q
dotnet DataGenerator\bin\Debug\net8.0\DataGenerator.dll -asset <publish-relative-path> -test-camp
dotnet DataGenerator\bin\Debug\net8.0\DataGenerator.dll -asset <publish-relative-path> -camp-layout-fixture
```

The `-test-camp` and `-camp-layout-fixture` commands generate lab-only fixture
payloads. They must target only the isolated review build; do not install them
in ordinary primary saves or data directories.

## Validation evidence and rerun commands

The lab changelog records successful build/publish and wrapper results. The
reports below are local review evidence, excluded from transfer, and all visual
entries remain `unreviewed`:

- `work/visual-checks/test-camp-wrapper-20260919-1015/result.json`
- `work/visual-checks/test-camp-interactions-20260919-final5/result.json`
- `work/visual-checks/adapter-smoke-safety-audit-20260919/result.json` and
  `work/visual-checks/adapter-negative-safety-audit-20260919/result.json`
- `work/visual-checks/camps-layout-poi-crops-20260919-1250/result.json`
- `work/visual-checks/p01-dungeon-poi-crops-20260919-1905/result.json` and
  `work/visual-checks/p02-p07-dungeon-poi-crops-20260919-2204/result.json`
- `work/visual-checks/layout-determinism-20260919-final2/result.json`,
  `work/visual-checks/dungeon-input-smoke-20260919-fresh2/result.json`, and
  `work/visual-checks/lair-generated-floor-seed-refresh-20260919/result.json`
- `work/visual-checks/early-seeded-routes-layout-20260919-fresh/result.json`
  and the refreshed seed-42, seed-20260919, and seed-424242 run-up reports
  named in [TERRA_VISUAL_PLAYTEST_CHANGELOG.md](TERRA_VISUAL_PLAYTEST_CHANGELOG.md).

At minimum rerun the build/generation commands above, then run:

```powershell
python -m unittest tests/test_playtest_adapter_safety.py tests/test_visual_catalog.py
python Scripts/digimon_visual_checks.py tests/visual/test-camp.json --output work/visual-checks/review-test-camp
python Scripts/digimon_playtest_adapter_smoke.py --output work/visual-checks/review-adapter-smoke --timeout-seconds 45
python Scripts/digimon_test_camp_interactions_smoke.py --output work/visual-checks/review-interactions --timeout-seconds 45
python Scripts/digimon_dungeon_input_smoke.py tests/visual/dungeon-input-smoke.json --output work/visual-checks/review-input --timeout-seconds 35
python Scripts/digimon_layout_determinism_check.py --output work/visual-checks/review-layout-determinism
```

Then rerun every fixed manifest wrapper listed in the source table, inspect the
native viewport/full-map/overlay output, and separately perform normal
non-debug traversal. A passing capture or metadata fingerprint is not visual
approval, normal access, combat, progression, reward, or full traversal proof.

## Safe next-week review order

1. Freeze the current primary hashes for every proposed replacement and compare
   baseline/current-primary/lab. Stop on any newer primary content.
2. Review outer added scripts, manifests, tests, and documentation first; then
   review the two modified DataGenerator files as visual-only hunks.
3. Review `PMDC/PMDC/Program.cs` in the PMDC repository separately. Do not
   advance an outer gitlink.
4. Review all RogueEssence additions and modified hunks in the RogueEssence
   repository separately, including the developer-panel registration. Resolve
   any overlap with existing character/action or other inherited engine work.
5. Build each reviewed source combination, regenerate fixtures only into an
   isolated review publish directory, and rerun structural, capture, input,
   and traversal checks.
6. Inspect representative native images plus every required UI/map context;
   record limitations and keep `unreviewed` until a reviewer accepts them.
7. Only after explicit approval, prepare a small explicit file/hunk bundle with
   backups and destination hash checks. Make nested-repository commits and any
   gitlink update a separate, explicitly authorized Git workflow.
