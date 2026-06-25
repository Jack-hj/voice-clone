$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
$SkillSource = Join-Path $Root "skill\voicebox-local-synthesis"
$SkillTarget = Join-Path $env:USERPROFILE ".codex\skills\voicebox-local-synthesis"

if (-not (Test-Path $SkillSource)) {
    throw "Skill source not found: $SkillSource"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $SkillTarget) | Out-Null
if (Test-Path $SkillTarget) {
    Remove-Item -LiteralPath $SkillTarget -Recurse -Force
}
Copy-Item -LiteralPath $SkillSource -Destination $SkillTarget -Recurse -Force

Write-Host "Installed skill to: $SkillTarget"
Write-Host "Set VOICEBOX_PACKAGE_ROOT to this package root when using the installed skill:"
Write-Host $Root
