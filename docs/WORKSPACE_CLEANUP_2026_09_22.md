# Workspace cleanup — 2026-09-22

## Active locations

The project now has two active full copies under `Documents/Codex/2026-09-09/prior-conversation-with-codex-conversation-role/`:

- `digimon-agent-lab`: implementation and automated testing.
- `playtest-digimon-phase1-1ea2e293`: the user's primary playtest copy; code and saves were preserved.

`Documents/Codex/Digimon` is now a README pointing to these copies. The old staging repository `outputs/PMDODump-Digimon-consolidated` has been retired. Recovery archives live in `outputs/cleanup-20260922/` under the workspace root.

## Verified consolidation

| Retired duplicate | Preserved content | Original bytes | Archive bytes |
|---|---|---:|---:|
| Older Documents/Codex/Digimon tree | 34,124 files, including Git history and edited storyboard | 3,907,831,143 | 2,833,472,739 |
| Older consolidated staging tree | 17,285 files, including Git history | 1,882,672,271 | 1,525,088,033 |
| Lab root publish/ installer staging | 40,725 identical files retained in primary publish/ | 4,194,487,367 | No extra archive required |

Each archived file was read back and SHA-256 checked against the original; sources were rechecked for changes before removal. The duplicate installer staging was SHA-256 compared to the retained primary files. About **5.63 GB (5.24 GiB)** of duplicate storage was reclaimed after accounting for recovery archives, excluding the small inventory/report overhead.

Archive manifests preserve relative paths, byte sizes, hashes, and source modification times. They also identify 76 source/note differences in the older Digimon tree and 52 in the staging tree. These are preserved historical versions, not automatically merged over the newer lab.

Source `PMDC/PMDC` and installed asset `PMDC/publish/win-x64/PMDC` directories have different purposes. Their repeated name is part of the existing build layout. The active lab executable, primary executable, original assets, saves, baseline and visual evidence were preserved.

## Condensed notes

Use [the documentation index](README.md) and [current status](PROJECT_STATUS.md). Five overlapping handoff/audit/changelog documents were condensed into PROJECT_STATUS, retaining pointer files at their original locations. Their exact 80,021 original bytes are preserved in `superseded-playtesting-notes.zip` with a verified hash manifest. The detailed runbook, protocol, coverage, arrival design and transfer procedure remain available.

Stale root/lab guidance claiming the extension had not been implemented was corrected. Disposable lab `work/` output is now ignored by Git. Historical notes never override the current source model or authorize blanket transfer.

## GitHub publication scope

The publication for this cleanup is a documentation-only branch, `docs/project-consolidation-20260922`, based on the current remote Phase 1 commit. It adds missing documentation and a `PROJECT_NOTES.md` entry point. Existing remote files, gameplay source, submodule pins and the primary playtest tree are not overwritten. Uncommitted engine/gameplay work still requires the documented source review before publication.

## Validation

- Two recovery archives verified file by file; live sources rechecked before retirement.
- All 40,725 duplicate installer files compared byte-for-byte by SHA-256.
- Documentation links and Git whitespace checks performed for this cleanup.
- No gameplay changes were made, so no new build was necessary. The last full lab build/native validation is recorded in [FINAL_LAB_VALIDATION_2026_09_19.md](playtesting/FINAL_LAB_VALIDATION_2026_09_19.md).

To recover an older copy, extract its ZIP into a **new empty folder**, then consult its manifest. Never extract over the active lab or primary tree. Keep the archives until the inherited dirty source work has been reviewed and safely published.
