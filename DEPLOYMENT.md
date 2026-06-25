# Deployment Guide

This guide explains how to turn the lightweight `voice-clone` repository into a working local Voicebox package.

## 1. What You Need

Required:

- Windows 10/11
- PowerShell
- Git
- Python 3.12+
- Internet access for first-time backend and model downloads
- Enough disk space for Python dependencies and model cache

Optional:

- NVIDIA GPU for faster generation
- a private voice sample that you have permission to use

## 2. What This Repository Provides

This repository provides:

- local Voicebox gateway
- local Web page
- Codex/OpenClaw skill metadata
- startup helper scripts
- setup helper script

This repository does not provide:

- official Voicebox backend runtime
- model files
- Python virtual environment
- personal voice samples
- generated audio history

## 3. Prepare The Package Folder

Use a folder such as:

```text
D:\voicebox-local-synthesis-no-env-deps
```

The final layout should become:

```text
voicebox-local-synthesis-no-env-deps/
  scripts/
  skill/
  voicebox/             created by setup script
  models/               created by setup script or first model download
  voicebox-data/        created during use
  outputs/              created during use
```

## 4. Install Runtime Dependencies

From this repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-voicebox-runtime.ps1 `
  -PackageRoot "D:\voicebox-local-synthesis-no-env-deps"
```

If Python 3.12 is missing:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-voicebox-runtime.ps1 `
  -PackageRoot "D:\voicebox-local-synthesis-no-env-deps" `
  -InstallPython312
```

The script clones:

```text
https://github.com/jamiepine/voicebox
```

into:

```text
voicebox/
```

and prepares:

```text
voicebox/.venv/
models/huggingface/hub/
```

## 5. Where Models Come From

Models are not included in this repository.

The backend and its TTS dependencies may download model files during first generation. The local Hugging Face cache is:

```text
models/huggingface/hub/
```

For the latest model and engine details, use the official Voicebox project and docs:

```text
https://github.com/jamiepine/voicebox
https://voicebox.sh
https://docs.voicebox.sh
```

Do not hard-code private model paths or commit downloaded model files to Git.

## 6. Start The Local App

From the package root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Open:

```text
http://127.0.0.1:3847/voicebox-clone
```

## 7. Generate Voice Audio

Basic flow:

```text
start app
  -> create or select voice profile
  -> paste final narration text
  -> generate WAV audio
  -> save to outputs/
```

Generated audio should stay local unless you intentionally publish it.

## 8. Agent Skill Usage

Skill file:

```text
skill/voicebox-local-synthesis/SKILL.md
```

Open helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\skill\voicebox-local-synthesis\scripts\open_voicebox_page.ps1
```

If the helper cannot find the package root:

```powershell
$env:VOICEBOX_PACKAGE_ROOT = "D:\voicebox-local-synthesis-no-env-deps"
```

## 9. Troubleshooting

If `scripts/start.ps1` says the runtime folder is missing:

```text
Missing runtime folder: ...\voicebox
```

Run `setup-voicebox-runtime.ps1`.

If it says model cache is missing:

```text
Missing model cache: ...\models\huggingface\hub
```

Create the folder or run the setup script. The actual model files may still download during first use.

If Python is missing or too old, install Python 3.12+ or run setup with `-InstallPython312`.

## 10. Do Not Commit

Keep these out of public Git repositories:

```text
voicebox/
models/
python-runtime/
voicebox-data/
outputs/
personal voice samples
generated private audio
cookies
API keys
```

