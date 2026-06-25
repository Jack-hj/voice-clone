# Voice Clone Local Synthesis

Lightweight local Voicebox skill and gateway for voice cloning and narration audio generation.

This repository is the source/skill version. It includes the local Web UI, gateway script, startup helpers, and documentation. It does not include model files, the Voicebox backend runtime, personal voice samples, generated audio, cookies, or private account data.

## What This Repository Includes

```text
.
  scripts/
    start.ps1
    install-skill.ps1
  skill/
    voicebox-local-synthesis/
      SKILL.md
      agents/openai.yaml
      assets/web/index.html
      scripts/open_voicebox_page.ps1
      scripts/voicebox_gateway.py
  setup-voicebox-runtime.ps1
  voicebox-runtime-notes.md
  QUICKSTART.md
```

## What Is Not Included

```text
voicebox/
models/
python-runtime/
voicebox-data/
outputs/
personal voice samples
generated private narration audio
cookies
API keys
```

Use a release archive or private delivery package if you need to distribute a full runnable runtime bundle.

## Expected Runtime Layout

For a complete local package, place runtime folders beside this repository content:

```text
voicebox-local-synthesis-no-env-deps/
  scripts/
  skill/
  voicebox/
  models/
  python-runtime/        optional
  voicebox-data/         created automatically
  outputs/               created automatically
```

## Quick Start

Read:

```text
QUICKSTART.md
```

Short version:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Default local page:

```text
http://127.0.0.1:3847/voicebox-clone
```

## Agent Usage

The skill entry point is:

```text
skill/voicebox-local-synthesis/SKILL.md
```

The helper script is:

```powershell
powershell -ExecutionPolicy Bypass -File .\skill\voicebox-local-synthesis\scripts\open_voicebox_page.ps1
```

## Relationship To AI Video Workflow

This package can provide the voice synthesis step for a video workflow:

```text
final script -> Voicebox Local Synthesis -> narration WAV -> video composer
```

## License

No open-source license has been selected yet. Add a `LICENSE` file before public distribution if you want others to copy, modify, or reuse this project under specific terms.

---

# 中文说明

这是一个本地 Voicebox 声音克隆和口播配音工作流的轻量源码/skill 仓库。它适合放到 GitHub 上展示结构和源码，但不应该包含模型、运行时、个人声音样本、生成音频、Cookie 或账号数据。

## 包含内容

```text
scripts/                         启动和安装辅助脚本
skill/voicebox-local-synthesis/  Codex/OpenClaw skill、网页和 gateway
setup-voicebox-runtime.ps1       运行时准备脚本
voicebox-runtime-notes.md        运行时说明
QUICKSTART.md                    下载后使用说明
```

## 不包含内容

```text
voicebox/
models/
python-runtime/
voicebox-data/
outputs/
个人声音样本
生成的私人口播音频
Cookie、密钥、账号登录态
```

如果要做完整可运行包，建议用 Release 或私有压缩包分发，不要把大模型和私人声音数据直接提交到 Git 仓库。

