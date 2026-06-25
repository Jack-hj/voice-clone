# Voicebox 轻量包补齐说明

我检查过你给的 `voicebox-local-synthesis-no-env-deps.zip`。它缺的是运行环境，不是页面代码。

## 这个脚本补什么

`setup-voicebox-runtime.ps1` 会做这些事：

- 在已解压的轻量包目录里创建 `models/huggingface/hub/`
- 把官方 Voicebox 仓库克隆到 `voicebox/`
- 检查 Python 3.12+
- 在 `voicebox/.venv/` 创建虚拟环境
- 安装官方后端依赖
- 保持原包的 `scripts/start.ps1` 启动方式不变

## 你电脑当前缺什么

- 已有：Git
- 已有：Python 3.11.9
- 已有：ffmpeg
- 缺少：Python 3.12+
- 缺少：Voicebox 后端依赖
- 缺少：模型缓存

官方后端要求 Python `>=3.12`，所以 Python 3.11 不建议硬跑。

## 推荐操作

先把原 zip 解压到一个固定目录，例如：

```powershell
C:\Users\wang\Documents\voicebox-local-synthesis-no-env-deps
```

然后运行：

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\wang\Documents\Codex\2026-06-04\new-chat-2\outputs\setup-voicebox-runtime.ps1" -PackageRoot "C:\Users\wang\Documents\voicebox-local-synthesis-no-env-deps" -InstallPython312
```

如果你已经自己装好了 Python 3.12，可以不用 `-InstallPython312`：

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\wang\Documents\Codex\2026-06-04\new-chat-2\outputs\setup-voicebox-runtime.ps1" -PackageRoot "C:\Users\wang\Documents\voicebox-local-synthesis-no-env-deps"
```

补齐后启动：

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\wang\Documents\voicebox-local-synthesis-no-env-deps\scripts\start.ps1"
```

页面地址：

```text
http://127.0.0.1:3847/voicebox-clone
```

## 注意

第一次生成语音时，模型可能会从 HuggingFace 下载，体积可能较大。你的 GTX 1650 是 4GB 显存，适合先试 `0.6B` 小模型；如果显存不够，可能会退到 CPU 或报错，速度也会慢。

只用于合成你本人声音或你有授权的声音。
