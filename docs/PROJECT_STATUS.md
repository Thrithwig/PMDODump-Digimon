# Digimon conversion — current project status

Updated 2026-09-22. This is the current continuation note. Detailed domain specifications remain authoritative for their subjects; historical progress reports are not instructions to redo completed work.

## Working copies

- `digimon-agent-lab`: current development code, including inherited uncommitted conversion work and the visual-playtest extension.
- `../playtest-digimon-phase1-1ea2e293`: primary user playtest copy. Preserve newer changes and saves; transfer reviewed source selectively.
- `../outputs/agent-lab-setup/baseline-files.jsonl`: original dirty-tree file baseline. Git HEAD does not represent the starting state.
- `../outputs/cleanup-20260922/`: local cleanup inventory, recovery manifests and archived notes. These are not release assets.

## Implemented visual playtesting

The opt-in engine controller, developer panel, atomic local file adapter, native viewport/full-map/overlay capture and bounded input are implemented in the lab. There is no installed custom Codex plugin.

Static cases cover camps, P01–P07 run-up/lair layouts, three seeds for intermediate run-up bands and early routes, and native crops around stairs, items and actors. The 27 early-route POI cases passed with 290 crops verified against the original rendered pixels. Test Camp input reached Base Camp, opened/cancelled Assembly, and toggled test power on and off. One dungeon input smoke verified a single settled step.

The developer DebugWarp path now preserves the requested seed. Repeated Test Camp and Copper Quarry cases matched logical-layout fingerprints. Logical fingerprints exclude time-dependent weather/UI and dynamic actors/items.

The `base-new-save` fixture records a native fresh save and resumes through the normal title loader. It reached `guildmaster_island` / `base_camp` at X244/Y250 and captured a 640×480 viewport and 504×576 map. This is the only completed normal-arrival fixture.

## Evidence and validation

Latest aggregate: `work/visual-checks/aggregate-visual-catalog-20260919-base-new-save-capture-final-r2/index.html` relative to the lab. It has 26 reports, 232 displayed entries, 1,773 PNG references and 5,796 validated HTML targets.

Images remain **unreviewed**. Debug-placement captures establish layout rendering, not normal quest access, battle correctness or traversal. Test Camp's south exit visually appears in a narrow forest opening instead of a drawn path; the map has not been changed.

Last full solution build: exit 0, zero errors, 32 inherited warnings. Final native validation: 341 forms, 138 converted items, 40 zones, 567 seeded floors/transitions, 146 family-item boxes, save round trips, zero runtime/generation errors. See [the validation record](playtesting/FINAL_LAB_VALIDATION_2026_09_19.md).

Run from lab root:

```powershell
dotnet build PMDOData.sln --no-restore
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll -asset ../../../../PMDC/publish/win-x64/PMDC/ -gen DataAsset/ -digimon-check
```

Focused tests covered adapter gates/queue/cancellation, fixture serialization and visual catalog links. Ordinary launch requires no automation and does not activate the controller.

## Next implementation

1. Review the rendered Test Camp exit and decide a source map correction, retaining before/after evidence.
2. Add the next normal-arrival case: Forest Camp after Tropical Path. See [arrival fixture design](playtesting/CAMP_ARRIVAL_FIXTURE_DESIGN.md). A prepared-state fixture can validate the Forest entry lifecycle; proof of an actual Tropical clear requires an authentic pre-return save or a separate bounded route-clear runner.
3. Forest's pre-debrief Tropical record has accepted/objective_met/cleared true and debriefed false. Cleared segment 0 or 1 returns to `guildmaster_island`, ground map 3, entry 0. First Forest entry sets ExpositionComplete. Do not assert a fabricated traversal.
4. Review source hunks before transferring to the primary. The [transfer manifest](playtesting/TRANSFER_REVIEW_MANIFEST.md) and [copy-back workflow](playtesting/COPY_BACK_WORKFLOW.md) remain the procedure. Preserve user saves and newer primary changes.

## Source safety and remaining limits

The 2026-09-19 audit identified 12 baseline-present source candidates requiring three-way hunk review and subsequently recorded hashes for 52 added source/test/manifest files. Exact historical hashes and audits are preserved in `../outputs/cleanup-20260922/superseded-playtesting-notes.zip` relative to the lab root. Refresh that inventory before transfer; counts are historical, not a live guarantee.

No lab implementation has been copied back or published by the visual-playtest task. The 2026-09-22 request authorizes cleanup and conditional GitHub publication, but does not justify blanket source replacement. Saves, diagnostic dumps, logs, build output, and disposable profiles must not enter source commits.

The adapter remains local and opt-in. It does not defend against a malicious same-user filesystem junction race. Wrappers enforce disposable lab profiles; native desktop window control and an installed Codex plugin remain unverified/unimplemented.
