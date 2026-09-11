#ifndef PayloadDir
  #error PayloadDir must point to the clean staged game
#endif
#ifndef OutputDir
  #error OutputDir must be specified
#endif
#ifndef BuildVersion
  #define BuildVersion "2026.09.11"
#endif
[Setup]
AppId={{9270BB87-72A2-4D0C-9582-9A38E6057532}
AppName=PMDODump Digimon Playtest
AppVersion={#BuildVersion}
AppPublisher=Thrithwig
AppPublisherURL=https://github.com/Thrithwig/PMDODump-Digimon
DefaultDirName={localappdata}\Programs\PMDODump-Digimon-Playtest
DefaultGroupName=PMDODump Digimon Playtest
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir={#OutputDir}
OutputBaseFilename=PMDODump-Digimon-Playtest-{#BuildVersion}-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\PMDC.exe
SetupLogging=yes
CloseApplications=yes
RestartApplications=no
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked
[Dirs]
Name: "{app}\SAVE"; Flags: uninsneveruninstall
Name: "{app}\CONFIG"; Flags: uninsneveruninstall
Name: "{app}\LOG"
Name: "{app}\REPLAY"; Flags: uninsneveruninstall
Name: "{app}\RESCUE"; Flags: uninsneveruninstall
Name: "{app}\MODS"
[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Play Digimon"; Filename: "{app}\PMDC.exe"; WorkingDir: "{app}"
Name: "{group}\Playtest notes"; Filename: "{app}\PLAYTEST.txt"
Name: "{autodesktop}\PMDODump Digimon Playtest"; Filename: "{app}\PMDC.exe"; WorkingDir: "{app}"; Tasks: desktopicon
[Run]
Filename: "{app}\PMDC.exe"; WorkingDir: "{app}"; Description: "Launch Digimon playtest"; Flags: nowait postinstall skipifsilent
