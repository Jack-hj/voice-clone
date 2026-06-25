$ErrorActionPreference = "Stop"

$SkillScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillDir = Split-Path -Parent $SkillScriptDir
$PackageRoot = $env:VOICEBOX_PACKAGE_ROOT

if (-not $PackageRoot) {
    $SkillParent = Split-Path -Parent $SkillDir
    $PackageRoot = Split-Path -Parent $SkillParent
}

$StartScript = Join-Path $PackageRoot "scripts\start.ps1"

if (-not (Test-Path $StartScript)) {
    throw "Voicebox startup script not found. Set VOICEBOX_PACKAGE_ROOT or run scripts\start.ps1 from the package root."
}

& powershell -ExecutionPolicy Bypass -File $StartScript
