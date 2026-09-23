# Final lab validation — 2026-09-19

Status: lab-only validation record. No source, content, primary-tree,
copy-back, commit, push, or gitlink action occurred.

## Full solution build

Command, from the lab root:

```powershell
dotnet build PMDOData.sln --no-restore
```

Outcome: **passed** with process exit code `0`, `0 Error(s)`, and `32 Warning(s)`.
The warnings are inherited build context: .NET 6 end-of-support warnings for
`WaypointServer` and `PMDOSetup`; a newer-SDK analyzer-package version notice;
existing bitwise/sign-extension and unused-variable warnings; and existing
`MapGenTest` Windows-registry platform warnings. No warning was changed or
suppressed in this validation.

## Native Digimon check against the published lab asset path

The `DataGenerator` argument parser resolves `-asset` relative to its own
`DataGenerator/bin/Debug/net8.0` executable path, while `-gen` is resolved
from the process working directory. The verified lab-root spelling is:

```powershell
dotnet DataGenerator/bin/Debug/net8.0/DataGenerator.dll `
  -asset ../../../../PMDC/publish/win-x64/PMDC/ `
  -gen DataAsset/ `
  -digimon-check
```

Outcome: **passed** with process exit code `0`, zero stderr bytes, and zero
runtime errors. The final output confirmed live floor transitions across 567
floors with identical initial actors and zero generation errors, then reported
that Digimon runtime checks passed: 341 forms; 138 converted items; 40
released zones and 567 seeded floors; 146 treasure boxes holding family items;
and character save round trips. The command also completed the planned Lua,
matchup, move, dash, resident, Test Camp/nursery, encounter, deterministic
family-pool, rotating catalog, lair-repair, inventory/reward, and SP checks.
No source or generated data was changed.

Earlier argument spellings established the parser constraint: an absolute
`-asset` was concatenated to the executable path, a relative asset path without
a trailing separator produced `PMDCBase`, and `-gen ../../../../DataAsset/`
was resolved from the lab-root working directory outside the lab. Those
attempts did not change the lab and are superseded by the successful command
above.

## Counts and follow-up boundary

| Check | Process errors | Outcome |
| --- | ---: | --- |
| `dotnet build PMDOData.sln --no-restore` | 0 | Pass; 32 inherited warnings |
| Final `-digimon-check` invocation | 0 | Pass; zero stderr bytes, 341 forms, 40 released zones, and 567 seeded floors |

No further validation command was launched after the successful native process
ended. This final command corrects only the invocation; no implementation
change is indicated by this record.
