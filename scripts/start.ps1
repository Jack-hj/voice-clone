param(
    [switch] $NoBrowser
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
$VoiceboxRoot = Join-Path $Root "voicebox"
$DataDir = Join-Path $Root "voicebox-data"
$OutputsDir = Join-Path $Root "outputs"
$ModelHubDir = Join-Path $Root "models\huggingface\hub"
$PythonRuntime = Join-Path $Root "python-runtime\python.exe"
$VenvPython = Join-Path $VoiceboxRoot ".venv\Scripts\python.exe"
$VenvConfig = Join-Path $VoiceboxRoot ".venv\pyvenv.cfg"
$SitePackages = Join-Path $VoiceboxRoot ".venv\Lib\site-packages"
$GatewayScript = Join-Path $Root "skill\voicebox-local-synthesis\scripts\voicebox_gateway.py"
$VoiceboxPort = 17493
$GatewayPort = 3847

if (-not (Test-Path $VoiceboxRoot)) {
    throw "Missing runtime folder: $VoiceboxRoot. Download or copy the Voicebox backend runtime before starting."
}

if (-not (Test-Path $ModelHubDir)) {
    throw "Missing model cache: $ModelHubDir. Download the required model files before starting."
}

New-Item -ItemType Directory -Force -Path $DataDir, $OutputsDir | Out-Null

if ((Test-Path $PythonRuntime) -and (Test-Path $VenvPython)) {
    $RuntimeRoot = Split-Path -Parent $PythonRuntime
    $RuntimeVersion = (& $PythonRuntime -c "import sys; print('.'.join(map(str, sys.version_info[:3])))").Trim()
    $ConfigLines = @(
        "home = $RuntimeRoot",
        "include-system-site-packages = false",
        "version = $RuntimeVersion",
        "executable = $PythonRuntime",
        "command = $PythonRuntime -m venv $VoiceboxRoot\.venv"
    )
    [System.IO.File]::WriteAllLines(
        $VenvConfig,
        $ConfigLines,
        [System.Text.UTF8Encoding]::new($false)
    )
}

if (Test-Path $VenvPython) {
    $Python = $VenvPython
} elseif (Test-Path $PythonRuntime) {
    $Python = $PythonRuntime
} else {
    $Python = "python"
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:VOICEBOX_PACKAGE_ROOT = $Root
$env:VOICEBOX_DATA_DIR = $DataDir
$env:VOICEBOX_OUTPUT_DIR = $OutputsDir
$env:VOICEBOX_MODELS_DIR = $ModelHubDir
$env:HF_HOME = Join-Path $Root "models\huggingface"
$env:HF_HUB_CACHE = $ModelHubDir
$env:VOICEBOX_API_URL = "http://127.0.0.1:$VoiceboxPort"
if (Test-Path $SitePackages) {
    $env:PYTHONPATH = "$SitePackages;$VoiceboxRoot"
} else {
    $env:PYTHONPATH = $VoiceboxRoot
}

function Test-HttpOk($Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
    } catch {
        return $false
    }
}

if (-not (Test-HttpOk "http://127.0.0.1:$VoiceboxPort/health")) {
    Start-Process -FilePath $Python `
        -ArgumentList @("-m", "backend.main", "--host", "127.0.0.1", "--port", "$VoiceboxPort", "--data-dir", "$DataDir") `
        -WorkingDirectory $VoiceboxRoot `
        -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 6
}

if (-not (Test-HttpOk "http://127.0.0.1:$GatewayPort/api/voicebox/status")) {
    Start-Process -FilePath $Python `
        -ArgumentList @("$GatewayScript") `
        -WorkingDirectory $Root `
        -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 2
}

$Url = "http://127.0.0.1:$GatewayPort/voicebox-clone"
if (-not $NoBrowser) {
    Start-Process $Url | Out-Null
}
Write-Host "Voicebox local page: $Url"
Write-Host "Data directory: $DataDir"
Write-Host "Output directory: $OutputsDir"
