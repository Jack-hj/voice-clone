# Quick Start

This guide explains how to run the local Voicebox voice cloning and narration workflow.

## 1. Understand The Package

This repository contains the lightweight source and skill files:

- local Web UI
- Python gateway
- PowerShell startup helpers
- Codex/OpenClaw skill metadata

It does not include the heavy or private runtime:

- `voicebox/`
- `models/`
- `python-runtime/`
- `voicebox-data/`
- `outputs/`
- personal voice samples
- generated private audio

## 2. Prepare The Runtime Layout

A complete local runtime should look like this:

```text
voicebox-local-synthesis-no-env-deps/
  scripts/
    start.ps1
  skill/
    voicebox-local-synthesis/
  voicebox/
  models/
  python-runtime/        optional
  voicebox-data/         created automatically
  outputs/               created automatically
```

## 3. Start The Local Page

From the package root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Open:

```text
http://127.0.0.1:3847/voicebox-clone
```

## 4. Use The Skill Helper

If an agent or user starts from the skill directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\skill\voicebox-local-synthesis\scripts\open_voicebox_page.ps1
```

If the package root is not detected automatically:

```powershell
$env:VOICEBOX_PACKAGE_ROOT = "D:\path\to\voicebox-local-synthesis-no-env-deps"
```

## 5. Generate Narration Audio

General flow:

```text
create or select voice profile
  -> paste final narration script
  -> generate WAV audio
  -> save audio to outputs/
  -> pass WAV path to the video workflow
```

## 6. Environment Variables

Optional variables:

```text
VOICEBOX_PACKAGE_ROOT
VOICEBOX_GATEWAY_HOST
VOICEBOX_GATEWAY_PORT
VOICEBOX_API_URL
VOICEBOX_DATA_DIR
VOICEBOX_OUTPUT_DIR
```

Defaults:

```text
VOICEBOX_GATEWAY_HOST = 127.0.0.1
VOICEBOX_GATEWAY_PORT = 3847
VOICEBOX_API_URL      = http://127.0.0.1:17493
```

## 7. For AI Agents

AI agents should:

1. Read `skill/voicebox-local-synthesis/SKILL.md`.
2. Confirm the runtime package root.
3. Start `scripts/start.ps1` or the skill helper.
4. Use the local page or gateway to select a voice profile and generate WAV audio.
5. Never assume private voice samples, generated audio, models, or cookies are included.

