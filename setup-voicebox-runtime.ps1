param(
    [string]$PackageRoot = "",
    [string]$PythonExe = "",
    [switch]$InstallPython312,
    [switch]$SkipDependencyInstall,
    [switch]$ForceReclone
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Resolve-FullPath($Path) {
    if (-not $Path) { return "" }
    return [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path)
}

function Get-PythonVersion($Exe) {
    try {
        $output = & $Exe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
        return [version]($output.Trim())
    } catch {
        return $null
    }
}

function Find-Python312 {
    param([string]$Preferred)

    $candidates = @()
    if ($Preferred) { $candidates += $Preferred }
    $candidates += @(
        "python",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python313\python.exe"
    )

    foreach ($candidate in $candidates) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        $exe = $cmd.Source
        $version = Get-PythonVersion $exe
        if ($version -and $version.Major -eq 3 -and $version.Minor -ge 12) {
            return $exe
        }
    }
    return $null
}

if (-not $PackageRoot) {
    $PackageRoot = Read-Host "Enter the extracted voicebox-local-synthesis-no-env-deps directory path"
}

$PackageRoot = Resolve-FullPath $PackageRoot
$StartScript = Join-Path $PackageRoot "scripts\start.ps1"
if (-not (Test-Path -LiteralPath $StartScript)) {
    throw "scripts\start.ps1 was not found. Make sure PackageRoot points to the extracted voicebox-local-synthesis-no-env-deps directory."
}

$VoiceboxRoot = Join-Path $PackageRoot "voicebox"
$ModelsHub = Join-Path $PackageRoot "models\huggingface\hub"
$VenvPython = Join-Path $VoiceboxRoot ".venv\Scripts\python.exe"

Write-Step "Preparing directories"
New-Item -ItemType Directory -Force -Path $ModelsHub | Out-Null

if ($ForceReclone -and (Test-Path -LiteralPath $VoiceboxRoot)) {
    Remove-Item -LiteralPath $VoiceboxRoot -Recurse -Force
}

if (-not (Test-Path -LiteralPath $VoiceboxRoot)) {
    Write-Step "Cloning the official Voicebox backend"
    git clone --depth 1 https://github.com/jamiepine/voicebox.git $VoiceboxRoot
} else {
    Write-Host "Backend directory already exists: $VoiceboxRoot"
}

$python = Find-Python312 -Preferred $PythonExe
if (-not $python -and $InstallPython312) {
    Write-Step "Trying to install Python 3.12 with winget"
    winget install --id Python.Python.3.12 --source winget --scope user --accept-package-agreements --accept-source-agreements
    $python = Find-Python312 -Preferred $PythonExe
}

if (-not $python) {
    throw "Python 3.12+ was not found. Install Python 3.12 and run this script again, or add -InstallPython312 to let the script try winget."
}

Write-Host "Using Python: $python"
Write-Host "Python version: $(Get-PythonVersion $python)"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Step "Creating virtual environment"
    & $python -m venv (Join-Path $VoiceboxRoot ".venv")
}

if (-not $SkipDependencyInstall) {
    Write-Step "Installing Python dependencies. This can be slow and may download large files."
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r (Join-Path $VoiceboxRoot "backend\requirements.txt")
    & $VenvPython -m pip install --no-deps chatterbox-tts
} else {
    Write-Host "Dependency installation was skipped. Re-run without -SkipDependencyInstall later."
}

Write-Step "Done"
Write-Host "Package root: $PackageRoot"
Write-Host "Backend directory: $VoiceboxRoot"
Write-Host "Model cache: $ModelsHub"
Write-Host ""
Write-Host "Start command:"
Write-Host "powershell -ExecutionPolicy Bypass -File `"$StartScript`""
Write-Host ""
Write-Host "Open after startup:"
Write-Host "http://127.0.0.1:3847/voicebox-clone"
