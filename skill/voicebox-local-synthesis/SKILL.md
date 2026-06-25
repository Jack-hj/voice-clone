---
name: voicebox-local-synthesis
description: >
  Local Voicebox workflow for voice cloning and narration audio generation.
  Use this skill when the user wants to open a local Voicebox page, create or
  select a voice profile, generate WAV narration from text, save generated
  audio, or concatenate multiple generated voice segments.
version: 1.0.0-public
allowed-tools: Read,Write,Bash
---

# Voicebox Local Synthesis

This skill provides a lightweight local interface for voice cloning and
script-to-speech narration. It is designed to be paired with a separate local
Voicebox runtime package.

## What This Skill Contains

```text
voicebox-local-synthesis/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ assets/
│  └─ web/
│     └─ index.html
└─ scripts/
   ├─ open_voicebox_page.ps1
   └─ voicebox_gateway.py
```

Included:

- Codex/OpenClaw skill metadata.
- A local browser UI.
- A small Python gateway server.
- A PowerShell helper for opening the local page.

Not included:

- Voicebox model files.
- Python runtime.
- Python virtual environment.
- Backend dependencies.
- Personal voice samples.
- Generated audio history.
- Login state, cookies, secrets, or private profile data.

## Expected Runtime Layout

Place this skill inside a runtime package that has this shape:

```text
voicebox-local-synthesis-no-env-deps/
├─ scripts/
│  └─ start.ps1
├─ skill/
│  └─ voicebox-local-synthesis/
├─ voicebox/
├─ models/
├─ python-runtime/        optional
├─ voicebox-data/         created automatically
└─ outputs/               created automatically
```

The `voicebox/` and `models/` folders belong to the local runtime. They should
not be committed to a public source repository unless you explicitly intend to
publish a full runtime bundle.

## Quick Start

From the package root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

The local page opens at:

```text
http://127.0.0.1:3847/voicebox-clone
```

You can also run the skill helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\skill\voicebox-local-synthesis\scripts\open_voicebox_page.ps1
```

If the helper cannot find the package root, set:

```powershell
$env:VOICEBOX_PACKAGE_ROOT = "D:\path\to\voicebox-local-synthesis-no-env-deps"
```

## Environment Variables

The gateway supports these optional environment variables:

```text
VOICEBOX_GATEWAY_HOST    default: 127.0.0.1
VOICEBOX_GATEWAY_PORT    default: 3847
VOICEBOX_PACKAGE_ROOT    runtime package root
VOICEBOX_API_URL         default: http://127.0.0.1:17493
VOICEBOX_DATA_DIR        default: <package-root>/voicebox-data
VOICEBOX_OUTPUT_DIR      default: <package-root>/outputs
```

## Main Capabilities

- Check whether the local Voicebox backend is running.
- List available voice profiles that have at least one sample.
- Select and remember an active voice profile.
- Generate narration audio through the local Voicebox backend.
- Save generated WAV audio to the output folder or a user-selected path.
- Copy generated audio to another location.
- Concatenate multiple WAV files into one narration file.
- Serve generated audio back through local HTTP endpoints.

## Local Endpoints

The gateway runs on `http://127.0.0.1:3847` by default.

Common endpoints:

```text
GET  /voicebox-clone
GET  /api/voicebox/status
POST /api/voicebox/select
POST /api/voicebox/save-audio
POST /api/voicebox/copy-audio
POST /api/voicebox/concat-audio
GET  /api/voicebox/saved-audio/{filename}
```

Requests under `/api/voicebox/` that are not handled by the gateway are proxied
to the configured Voicebox backend.

## Suggested Public Repository Policy

For source repositories, include this skill and documentation only.

Do not commit:

```text
voicebox/
models/
python-runtime/
voicebox-data/
outputs/
.venv/
*.wav generated from private voices
personal voice samples
API keys or cookies
```

If you need to distribute a full runnable package, use a release archive or a
separate private delivery channel.

## Workflow Handoff

This skill can be used by a video workflow as the voice generation step:

```text
final script -> Voicebox Local Synthesis -> narration WAV -> video composer
```

The video workflow should pass final narration text into the Voicebox runtime,
save the resulting WAV file, and then provide that file path to the video
composition step.

