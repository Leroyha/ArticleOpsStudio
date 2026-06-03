# ArticleOps Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](pyproject.toml)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](frontend/package.json)

**中文** | [English](#english)

ArticleOps Studio 是一个本地 Web 工作台，用于生成 OpenClaw 通用定时发文任务模板，并记录产品计划使用历史。它适合需要批量安排文章发布时间、复制结构化提示词、追踪产品发文密度的本地运营流程。

## 功能

- 生成 OpenClaw 通用定时发文任务模板。
- 支持随机时间和手动时间，两种排程方式都按最小间隔校验。
- 支持任意数量任务，不强制固定为 5 篇。
- 保存批次到 SQLite，并统计产品计划使用次数。
- 提供控制面板：数据库查看、受保护 CRUD、主题/语言设置、内置文档阅读。
- 运行期数据集中写入 `articleops-runtime/`，便于备份、清理和打包分发。

## 技术栈

- Backend: FastAPI, Uvicorn, SQLite, Pydantic
- Frontend: React, Vite, GSAP
- Packaging: PyInstaller onedir
- Tooling: UV, pytest

## 快速开始

```powershell
cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio
uv sync
cd frontend
npm install
npm run build
cd ..
.\start.bat
```

打开：

```text
http://127.0.0.1:8000
```

`start.bat` 会把运行期数据、日志、缓存和临时文件指向项目内的 `articleops-runtime/`。

## 后端测试

```powershell
cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio
$env:ARTICLEOPS_RUNTIME_DIR = Join-Path (Get-Location) "articleops-runtime"
$env:TEMP = Join-Path $env:ARTICLEOPS_RUNTIME_DIR "temp"
$env:TMP = $env:TEMP
$env:TMPDIR = $env:TEMP
$env:XDG_CACHE_HOME = Join-Path $env:ARTICLEOPS_RUNTIME_DIR "cache"
$env:UV_CACHE_DIR = Join-Path $env:XDG_CACHE_HOME "uv"
$env:PYTHONPYCACHEPREFIX = Join-Path $env:XDG_CACHE_HOME "pycache"
uv run pytest -p no:cacheprovider
```

## Windows 打包

先构建前端：

```powershell
cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio\frontend
npm run build
```

再打包：

```powershell
cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio
uv run pyinstaller --noconfirm --clean ArticleOpsStudio.spec
```

产物位于：

```text
dist/ArticleOpsStudio/
```

当前 spec 已启用：

```text
console=False
icon=assets/logo/articleops-logo.ico
version=packaging/windows_version_info.txt
```

### EXE 图标

如果 exe 图标未显示，替换并重新生成：

```text
assets/logo/articleops-logo.ico
```

推荐源图规格：

```text
1024x1024 PNG
32-bit RGBA
square
transparent or solid background
```

推荐 `.ico` 内含尺寸：

```text
16x16
32x32
48x48
64x64
128x128
256x256
```

## 项目结构

```text
src/articleops_studio/       FastAPI app, scheduling, templates, SQLite, runtime
frontend/                    React + Vite frontend
assets/logo/                 Logo and icon assets
docs/                        Project documentation
tests/                       Backend tests
packaging/                   PyInstaller entrypoint and Windows metadata
articleops-runtime/          Runtime data, logs, cache, temp files, backups
```

## 文档

- [API](docs/API.md)
- [Database](docs/DATABASE.md)
- [Runtime and packaging](docs/RUNTIME.md)
- [Template maintenance](docs/TEMPLATE.md)
- [UI and resources](docs/UI.md)
- [GitHub publishing notes](docs/GITHUB.md)

## License

ArticleOps Studio is released under the [MIT License](LICENSE).

---

## English

ArticleOps Studio is a local web workbench for generating generic scheduled publishing prompts for OpenClaw and tracking planned product usage. It is designed for local operations workflows that need repeatable article scheduling, structured prompt generation, and lightweight SQLite-backed history.

### Features

- Generate generic OpenClaw scheduled article publishing prompts.
- Support random schedules and manual time slots with minimum-interval validation.
- Support any task count instead of forcing a fixed batch size.
- Save generated batches to SQLite and track planned product usage.
- Provide a control panel for database inspection, protected CRUD, settings, and built-in docs.
- Keep runtime files under `articleops-runtime/` for easier backup, cleanup, and packaging.

### Quick Start

```powershell
cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio
uv sync
cd frontend
npm install
npm run build
cd ..
.\start.bat
```

Open:

```text
http://127.0.0.1:8000
```

### Test

```powershell
cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio
uv run pytest -p no:cacheprovider
```

### Package

```powershell
cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio\frontend
npm run build

cd /d H:\0_DevWorkshop-Leroy\24_ArticleOpsStudio
uv run pyinstaller --noconfirm --clean ArticleOpsStudio.spec
```
