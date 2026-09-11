# Sharing and building a playtest

Source lives on `digimon-phase1` in Thrithwig/PMDODump-Digimon. The PMDC,
RogueEssence and DumpAsset submodules use the matching Thrithwig Digimon forks;
RawAsset and the remaining dependencies retain their upstream URLs.

Clone with `git clone --recurse-submodules --branch digimon-phase1
https://github.com/Thrithwig/PMDODump-Digimon.git` (one line).
Install .NET SDK 8, then run `dotnet restore PMDOData.sln` and
`dotnet build PMDOData.sln --no-restore`.

Install [Inno Setup 6](https://jrsoftware.org/isdl.php), then run:

```powershell
./Installer/Build-Playtest.ps1 -Compiler 'C:/Program Files (x86)/Inno Setup 6/ISCC.exe'
```

The installer and SHA-256 checksum are written under `publish/playtest` and are
ignored by Git. Send the `*-Setup.exe` to the tester. It installs for the current
Windows user without administrator rights, creates Start menu shortcuts, and
includes .NET. It is not code signed. Windows may show an unknown-publisher prompt.

The package includes no personal saves, replays, logs, contacts, settings or debug
symbols. It does not bundle optional upstream gameplay mods. It retains upstream
license/credit files. Existing player-generated save/config files are not removed
by an update or uninstall. Testers should start a new game for this conversion.

Build-Playtest uses a new staging directory on each run rather than clearing an
existing install. BUILD.json records source commits for bug reports. Staging,
compiled binaries and installers must never be committed to Git.
