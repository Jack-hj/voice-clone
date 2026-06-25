# Voicebox Runtime Notes

This repository contains only the lightweight skill, gateway, Web UI, and helper scripts. A complete runnable setup also needs the Voicebox backend runtime and model cache.

The helper script `setup-voicebox-runtime.ps1` prepares the missing runtime pieces.

## What The Setup Script Does

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-voicebox-runtime.ps1 -PackageRoot "D:\path\to\voicebox-local-synthesis-no-env-deps"
```

It will:

- create `models/huggingface/hub/`
- clone the official Voicebox backend into `voicebox/`
- check for Python 3.12+
- create `voicebox/.venv/`
- install backend Python dependencies
- install `chatterbox-tts`
- keep the local startup command as `scripts/start.ps1`

The backend source used by the script is:

```text
https://github.com/jamiepine/voicebox
```

Official project pages:

```text
https://github.com/jamiepine/voicebox
https://voicebox.sh
https://docs.voicebox.sh
```

## Model Download Behavior

This repository does not include model files.

The Voicebox backend and its TTS dependencies may download models into the Hugging Face cache during first use. In this package, the cache is configured as:

```text
models/huggingface/hub/
```

The exact model files depend on the selected backend engine and upstream Voicebox/TTS configuration. Check the official Voicebox documentation if you need a specific engine or model family.

## Recommended First Run

1. Install Git.
2. Install Python 3.12+.
3. Make sure you have enough disk space for model downloads.
4. Run setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-voicebox-runtime.ps1 -PackageRoot "D:\path\to\voicebox-local-synthesis-no-env-deps"
```

If Python 3.12 is not installed, you can let the script try `winget`:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-voicebox-runtime.ps1 `
  -PackageRoot "D:\path\to\voicebox-local-synthesis-no-env-deps" `
  -InstallPython312
```

Then start:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Open:

```text
http://127.0.0.1:3847/voicebox-clone
```

## Hardware Notes

Voice cloning and TTS can run slowly on CPU. GPU memory needs depend on the selected model and engine. Start with smaller models or default settings before trying larger engines.

## Safety And Privacy

Only clone voices you own or have permission to use. Do not publish personal voice samples, generated private audio, cookies, API keys, or local profile data in a public repository.

