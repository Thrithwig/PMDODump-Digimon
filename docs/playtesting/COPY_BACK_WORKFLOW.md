# Transfer verified lab changes to the primary copy

## Baseline and responsibilities

Lab: `../../` relative to this file.
Primary: sibling `playtest-digimon-phase1-1ea2e293`.
Full-copy baseline: sibling `../outputs/agent-lab-setup/baseline-files.jsonl` relative to the lab root. `verification.json` records copy integrity and independent Git repositories.

The user authorized creating this lab and writing an implementation brief. Do not interpret that as approval to transfer an unfinished or unreviewed implementation. The intended flow is lab implementation -> tests and visual evidence -> concrete change bundle -> user review -> transfer.

The primary and lab both began with extensive uncommitted work. Git HEAD is not the baseline. Use the per-file SHA256 snapshot to identify what changed since the copy.

## Prepare a small, reviewable bundle

1. Record the lab root, primary root, baseline ID/date, engine and data repository HEADs, changed-file hashes, build command and test evidence.
2. Enumerate new/changed/deleted files relative to the copy baseline. Classify source, generated game asset, docs, or local-only artifact. Explain every file to be transferred; exclude unrelated existing dirty changes.
3. Include generator and generated source-controlled assets together where required, plus any necessary index file. List cross-repository changes separately (parent, DumpAsset, PMDC, RogueEssence, RawAsset). No `.git` directory or gitlink replacement belongs in a file-transfer bundle.
4. Exclude every bin/obj/publish/installer output, runtime profile, save/replay/log, screenshot cache, heap dump, copied local tool and lab-only AGENTS/README/config file. Visual evidence may be reviewed separately without being installed as game data.
5. Produce a manifest with `relative_path`, `operation` (add/replace/delete), `repository`, `baseline_sha256`, `lab_sha256`, reason, and required rebuild/regeneration step. A new file has no baseline hash. A deletion must be explicit; do not express it through `/MIR`.
6. The review should include before/after viewport and overlay captures for visual changes, actual traversal evidence, and test limitations. Passing a screenshot export is not visual approval.

## Preflight after approval

- Check the primary file still matches its baseline hash. If it differs, stop transferring that file and prepare a three-way merge using the copied baseline/current-primary/current-lab versions. Never overwrite newer primary work, including changes from the user's friend.
- For a new file, verify the primary target does not already exist. For a deletion, verify its baseline hash and the explicitly approved deletion.
- Resolve all destination paths beneath the intended primary repository. Reject absolute paths, `..` escapes, reparse-point escapes, and destinations in SAVE/REPLAY/LOG or Git metadata.
- Back up only the primary files being replaced to a dated local backup outside its runtime data directories. Preserve the manifest with the backup.
- Close only the applicable playtest process when replacing a locked executable or runtime file; do not kill unrelated game installations or interrupt a live user session silently.

## Apply and verify

Copy the approved source/assets with explicit relative paths. Rebuild and republish in the primary from those sources instead of installing the lab's bin/obj/publish directories. Run relevant structural, visual and traversal checks against the primary build using another isolated profile. Hash-check transferred files and record results.

If a transfer or rebuild fails, report the exact partial state and restore only the affected files from the dated backup when appropriate. Never reset the primary repository to HEAD.

No push or commit is implied. Source changes inside nested repositories need their own eventual commits and published references, coordinated separately with the user. Do not advance gitlinks until explicitly carrying out that Git workflow.

## Suggested manifest shape (proposal)

```json
{
  "schema_version": 1,
  "baseline": "agent-lab-copy-2026-09-19",
  "status": "awaiting-review",
  "files": [
    {
      "relative_path": "path/verified-file.cs",
      "repository": "parent-or-submodule-path",
      "operation": "replace",
      "baseline_sha256": "fill-from-baseline",
      "lab_sha256": "fill-from-tested-file",
      "reason": "specific reviewed change"
    }
  ],
  "validation": {
    "build": "actual command and result",
    "structural": "actual coverage",
    "visual": "reviewed case IDs and artifact paths",
    "traversal": "actual transition results"
  }
}
```
