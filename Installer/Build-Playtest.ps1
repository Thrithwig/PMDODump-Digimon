param(
    [Parameter(Mandatory=$true)][string]$Compiler,
    [string]$Version = '2026.09.11',
    [switch]$SkipPublish
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$published = Join-Path $repo 'PMDC/publish/win-x64/PMDC'
$artifactRoot = Join-Path $repo 'publish/playtest'
$stage = Join-Path $artifactRoot ('stage-' + [guid]::NewGuid().ToString('N'))
$payload = Join-Path $stage 'game'
New-Item -ItemType Directory -Force $payload | Out-Null
Push-Location $repo
try {
    if (!$SkipPublish) {
        & dotnet publish PMDC/PMDC/PMDC.csproj -c Release -r win-x64 --self-contained true -v:q
        if ($LASTEXITCODE -ne 0) { throw 'Game publish failed' }
    }
    foreach ($directory in @('Content','Data','Strings','Licenses','Controls','Base','CONVERSION')) {
        $source = Join-Path $published $directory
        if (Test-Path -LiteralPath $source) { Copy-Item -LiteralPath $source -Destination $payload -Recurse }
    }
    foreach ($file in @('PMDC.exe','PMDO.png','README.txt','spritebot_credits.txt')) {
        Copy-Item -LiteralPath (Join-Path $published $file) -Destination $payload
    }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'PLAYTEST.txt') -Destination $payload
    $forbidden = @(Get-ChildItem -LiteralPath $payload -Recurse -File | Where-Object { $_.Extension -in @('.rssv','.rsrec','.log','.pdb') -or $_.Name -eq 'config.xml' })
    if ($forbidden.Count) { throw "Personal/debug files in installer: $($forbidden.FullName -join ', ')" }
    $revisions = [ordered]@{}
    foreach ($path in @('.', 'PMDC', 'PMDC/RogueEssence', 'DumpAsset', 'RawAsset')) {
        $revisions[$path] = (& git -C $path rev-parse HEAD).Trim()
    }
    [ordered]@{ version=$Version; source=$revisions; runtime='win-x64 self-contained'; createdUtc=[DateTime]::UtcNow.ToString('o') } | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $payload 'BUILD.json')
    & $Compiler "/DPayloadDir=$payload" "/DOutputDir=$artifactRoot" "/DBuildVersion=$Version" (Join-Path $PSScriptRoot 'DigimonPlaytest.iss')
    if ($LASTEXITCODE -ne 0) { throw 'Installer compilation failed' }
    $installer = Join-Path $artifactRoot "PMDODump-Digimon-Playtest-$Version-Setup.exe"
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $installer).Hash.ToLowerInvariant()
    "$hash  $([IO.Path]::GetFileName($installer))" | Set-Content "$installer.sha256"
    Write-Output "Installer: $installer"
    Write-Output "Staged game: $payload"
} finally { Pop-Location }
