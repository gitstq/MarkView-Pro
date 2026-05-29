<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Zero_Dependencies-✓-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Tests-87_Passed-brightgreen.svg" alt="87 Tests Passed">
  <img src="https://img.shields.io/badge/GFM-Compatible-orange.svg" alt="GFM Compatible">
</p>

<h1 align="center">🎨 MarkView-Pro</h1>

<p align="center">
  <b>轻量级终端 Markdown 实时预览与智能格式化引擎</b><br>
  <i>Lightweight Terminal Markdown Live Preview & Intelligent Formatting Engine</i>
</p>

<p align="center">
  <a href="#-项目介绍">简体中文</a> ·
  <a href="#-簡介">繁體中文</a> ·
  <a href="#-introduction">English</a>
</p>

---

<a name="-项目介绍"></a>

## 🎉 项目介绍

**MarkView-Pro** 是一款专为开发者打造的轻量级终端 Markdown 工具集。它将 **实时预览、智能格式化、质量评分、多格式导出、语法高亮** 五大核心能力融为一体，帮助你在终端中高效地阅读、编写和优化 Markdown 文档。

### 💡 解决的痛点

- ❌ 终端中无法直观预览 Markdown 渲染效果
- ❌ Markdown 文档格式混乱、风格不统一
- ❌ 缺乏对文档质量的量化评估手段
- ❌ 现有工具依赖繁重，安装配置复杂

### 🌟 自研差异化亮点

- **真正零依赖** —— 仅使用 Python 标准库，`pip install` 即可使用，无需安装任何第三方包
- **GFM 全兼容** —— 完整支持 GitHub Flavored Markdown 扩展语法（表格、任务列表、删除线等）
- **三维质量评分** —— 从结构完整性、可读性、规范度三个维度量化评估文档质量
- **13+ 语言语法高亮** —— 基于纯正则实现的轻量级代码着色，覆盖主流编程语言
- **TUI 交互式仪表盘** —— 基于 curses 构建的终端内交互界面，支持实时浏览和操作

### 🔍 灵感来源

受 GitHub Trending 热门项目 `microsoft/markitdown`（128k+ Stars）启发，聚焦于 Markdown 生态中**终端预览与格式优化**这一细分场景，打造一款真正轻量、零依赖的终端原生工具。

---

<a name="-核心特性"></a>

## ✨ 核心特性

### 📝 实时预览
- 终端内直接渲染 Markdown，**ANSI 彩色输出**
- 标题层级自动着色（H1 加粗下划线、H2 加粗等）
- 代码块带边框渲染，表格自动对齐
- 引用块用竖线标识，链接显示为 `文本(URL)` 格式
- **自适应终端宽度**，自动换行

### 🎨 智能格式化
- 标题前后空行规范化
- 列表缩进统一（2/4 空格可选）
- 代码块语言标识自动补全
- 行尾空白清理、连续空行合并
- **中英文之间自动添加空格**（可选）
- 表格对齐优化

### 📊 质量评分
- **结构完整性**：标题层级、段落、列表、代码块、链接、表格、引用
- **可读性**：段落长度、行长度、标题密度、空行使用、格式丰富度
- **规范度**：行尾空白、空行规范、标题格式、列表格式、代码块规范
- 综合评分 **0-100 分**，分等级输出（S/A/B/C/D）

### 🔄 文件监听
- 轮询式文件变更检测（无需 watchdog 依赖）
- 可配置轮询间隔（默认 1 秒）
- 文件变更自动刷新预览
- 支持 Ctrl+C 优雅退出

### 📤 多格式导出
- **HTML** —— 生成带内联 CSS 的完整 HTML 文档
- **JSON AST** —— 输出完整的解析抽象语法树
- **纯文本** —— 去除所有 Markdown 语法的干净文本

### 🌈 语法高亮
- 支持 **13+ 种编程语言**：Python、JavaScript/TypeScript、Java、C/C++、Go、Rust、HTML、CSS、JSON、YAML、Bash/Shell、SQL、Markdown
- 关键字、字符串、注释、数字等元素分色显示
- 支持自定义颜色主题

### 🖥️ TUI 交互式仪表盘
- 基于 `curses` 构建的终端内交互界面
- 左侧文件预览 + 右侧信息面板
- 快捷键操作：`q` 退出、`r` 刷新、`f` 格式化、`s` 评分

---

<a name="-快速开始"></a>

## 🚀 快速开始

### 环境要求

- **Python** 3.8 或更高版本
- **操作系统**：Windows / macOS / Linux
- **终端**：支持 ANSI 转义码的现代终端

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/MarkView-Pro.git
cd MarkView-Pro

# 安装（零外部依赖）
pip install -e .
```

### 验证安装

```bash
markview --version
# 输出: MarkView-Pro 1.0.0
```

### 基本使用

```bash
# 📝 实时预览 Markdown 文件
markview preview README.md

# 🔄 预览并监听文件变化
markview preview README.md --watch

# 🎨 智能格式化（输出到新文件）
markview format README.md --output README_formatted.md

# 🎨 智能格式化（原地修改）
markview format README.md --in-place

# 🎨 格式化并自动添加中英文空格
markview format README.md --in-place --cjk-spaces

# 📊 质量评分
markview score README.md

# 📊 质量评分（JSON 格式输出）
markview score README.md --json

# 📤 导出为 HTML
markview export README.md --format html --output output.html

# 📤 导出为 JSON AST
markview export README.md --format json --output output.json

# 📤 导出为纯文本
markview export README.md --format text --output output.txt

# 🖥️ 启动 TUI 交互式仪表盘
markview serve README.md
```

---

<a name="-详细使用指南"></a>

## 📖 详细使用指南

### 预览命令详解

```bash
markview preview <file> [选项]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--watch` | 启用文件监听模式 | 关闭 |
| `--no-color` | 禁用 ANSI 彩色输出 | 关闭 |
| `--interval` | 文件监听轮询间隔（秒） | 1 |

### 格式化命令详解

```bash
markview format <file> [选项]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--in-place` | 原地修改文件 | 关闭 |
| `--output` | 输出到指定文件 | 标准输出 |
| `--cjk-spaces` | 中英文之间自动添加空格 | 关闭 |
| `--indent` | 列表缩进空格数 | 2 |

### 评分命令详解

```bash
markview score <file> [选项]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--json` | 以 JSON 格式输出评分结果 | 关闭 |

### 评分等级说明

| 等级 | 分数范围 | 说明 |
|------|----------|------|
| **S** | 90-100 | 卓越，文档质量极高 |
| **A** | 80-89 | 优秀，文档质量良好 |
| **B** | 60-79 | 良好，有改进空间 |
| **C** | 40-59 | 一般，需要较多改进 |
| **D** | 0-39 | 较差，需要大幅改进 |

### 典型使用场景

**场景一：写作时实时预览**
```bash
# 在一个终端窗口中监听文件变化
markview preview my-article.md --watch
# 在编辑器中编辑 my-article.md，保存后终端自动刷新预览
```

**场景二：批量格式化 Markdown 文件**
```bash
# 格式化当前目录下所有 .md 文件
for f in *.md; do markview format "$f" --in-place --cjk-spaces; done
```

**场景三：CI/CD 中集成质量检查**
```bash
# 在 CI 中检查文档质量，低于 60 分则失败
SCORE=$(markview score README.md --json | python3 -c "import sys,json; print(json.load(sys.stdin)['overall'])")
if [ "$SCORE" -lt 60 ]; then echo "文档质量不合格: $SCORE"; exit 1; fi
```

---

<a name="-设计思路与迭代规划"></a>

## 💡 设计思路与迭代规划

### 设计理念

MarkView-Pro 遵循 **「极简但不简陋」** 的设计哲学：

1. **零依赖优先** —— 核心功能完全基于 Python 标准库实现，降低用户安装门槛
2. **模块化架构** —— 解析器、渲染器、格式化器、评分器各自独立，可单独使用
3. **终端原生** —— 所有功能都在终端内完成，无需切换到浏览器或其他应用
4. **渐进增强** —— 从基础的预览功能出发，逐步叠加格式化、评分、导出等能力

### 技术选型原因

| 技术 | 选型理由 |
|------|----------|
| Python | 开发者生态最广泛、标准库最丰富、跨平台兼容性最佳 |
| argparse | 标准库 CLI 框架，零依赖且功能完善 |
| curses | 标准库 TUI 框架，原生终端交互能力 |
| re（正则） | 标准库正则引擎，足以实现轻量级语法高亮 |

### 后续迭代计划

- [ ] 📡 支持 WebSocket 实时协作预览
- [ ] 🎨 添加更多颜色主题（暗色/亮色/自定义）
- [ ] 📐 支持 Mermaid 图表渲染
- [ ] 🔌 插件系统（自定义格式化规则、评分维度）
- [ ] 📦 PyPI 发布，支持 `pip install markview-pro`
- [ ] 🌐 支持更多语言版本（日语、韩语等）

---

<a name="-打包与部署指南"></a>

## 📦 打包与部署指南

### 本地开发安装

```bash
git clone https://github.com/gitstq/MarkView-Pro.git
cd MarkView-Pro
pip install -e .
```

### 运行测试

```bash
cd MarkView-Pro
python -m unittest discover tests/ -v
```

### 卸载

```bash
pip uninstall markview-pro
```

---

<a name="-贡献指南"></a>

## 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！无论是提交 Bug、改进文档，还是贡献新功能。

### 提交 PR 规范

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: 添加某功能"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

### Commit Message 规范

遵循 Angular 提交规范：

| 前缀 | 说明 |
|------|------|
| `feat:` | 新增功能 |
| `fix:` | 修复问题 |
| `docs:` | 文档更新 |
| `refactor:` | 代码重构 |
| `test:` | 测试相关 |
| `chore:` | 构建/工具链相关 |

### Issue 反馈

提交 Issue 时请包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 运行环境（Python 版本、操作系统）

---

<a name="-开源协议"></a>

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

```
MIT License

Copyright (c) 2025 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>

---

<a name="-簡介"></a>

## 🎉 簡介

**MarkView-Pro** 是一款專為開發者打造的輕量級終端 Markdown 工具集。它將 **實時預覽、智慧格式化、質量評分、多格式匯出、語法高亮** 五大核心能力融為一體，幫助你在終端中高效地閱讀、撰寫和優化 Markdown 文件。

### 💡 解決的痛點

- ❌ 終端中無法直觀預覽 Markdown 渲染效果
- ❌ Markdown 文件格式混亂、風格不統一
- ❌ 缺乏對文件質量的量化評估手段
- ❌ 現有工具依賴繁重，安裝配置複雜

### 🌟 自研差異化亮點

- **真正零依賴** —— 僅使用 Python 標準庫，`pip install` 即可使用，無需安裝任何第三方套件
- **GFM 全相容** —— 完整支援 GitHub Flavored Markdown 擴展語法（表格、任務清單、刪除線等）
- **三維質量評分** —— 從結構完整性、可讀性、規範度三個維度量化評估文件質量
- **13+ 語言語法高亮** —— 基於純正則實現的輕量級代碼著色，覆蓋主流程式語言
- **TUI 互動式儀表板** —— 基於 curses 建構的終端內互動介面，支援即時瀏覽和操作

---

<a name="-核心特性-1"></a>

## ✨ 核心特性

### 📝 即時預覽
- 終端內直接渲染 Markdown，**ANSI 彩色輸出**
- 標題層級自動著色（H1 粗體底線、H2 粗體等）
- 代碼塊帶邊框渲染，表格自動對齊
- 引用塊用豎線標識，連結顯示為 `文字(URL)` 格式
- **自適應終端寬度**，自動換行

### 🎨 智慧格式化
- 標題前後空行規範化
- 清單縮排統一（2/4 空格可選）
- 代碼塊語言標識自動補全
- 行尾空白清理、連續空行合併
- **中英文之間自動新增空格**（可選）
- 表格對齊優化

### 📊 質量評分
- **結構完整性**：標題層級、段落、清單、代碼塊、連結、表格、引用
- **可讀性**：段落長度、行長度、標題密度、空行使用、格式豐富度
- **規範度**：行尾空白、空行規範、標題格式、清單格式、代碼塊規範
- 綜合評分 **0-100 分**，分等級輸出（S/A/B/C/D）

### 📤 多格式匯出
- **HTML** —— 生成帶內嵌 CSS 的完整 HTML 文件
- **JSON AST** —— 輸出完整的解析抽象語法樹
- **純文字** —— 去除所有 Markdown 語法的乾淨文字

### 🌈 語法高亮
- 支援 **13+ 種程式語言**：Python、JavaScript/TypeScript、Java、C/C++、Go、Rust、HTML、CSS、JSON、YAML、Bash/Shell、SQL、Markdown
- 關鍵字、字串、註釋、數字等元素分色顯示
- 支援自訂顏色主題

---

<a name="-快速開始-1"></a>

## 🚀 快速開始

### 環境要求

- **Python** 3.8 或更高版本
- **作業系統**：Windows / macOS / Linux
- **終端**：支援 ANSI 跳脫碼的現代終端

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/MarkView-Pro.git
cd MarkView-Pro

# 安裝（零外部依賴）
pip install -e .
```

### 驗證安裝

```bash
markview --version
# 輸出: MarkView-Pro 1.0.0
```

### 基本使用

```bash
# 📝 即時預覽 Markdown 文件
markview preview README.md

# 🔄 預覽並監聽文件變化
markview preview README.md --watch

# 🎨 智慧格式化（原地修改）
markview format README.md --in-place

# 📊 質量評分
markview score README.md

# 📤 匯出為 HTML
markview export README.md --format html --output output.html

# 🖥️ 啟動 TUI 互動式儀表板
markview serve README.md
```

---

<a name="-設計思路與迭代規劃-1"></a>

## 💡 設計思路與迭代規劃

### 設計理念

MarkView-Pro 遵循 **「極簡但不簡陋」** 的設計哲學：

1. **零依賴優先** —— 核心功能完全基於 Python 標準庫實現，降低使用者安裝門檻
2. **模組化架構** —— 解析器、渲染器、格式化器、評分器各自獨立，可單獨使用
3. **終端原生** —— 所有功能都在終端內完成，無需切換到瀏覽器或其他應用
4. **漸進增強** —— 從基礎的預覽功能出發，逐步疊加格式化、評分、匯出等能力

### 後續迭代計畫

- [ ] 📡 支援 WebSocket 即時協作預覽
- [ ] 🎨 新增更多顏色主題（暗色/亮色/自訂）
- [ ] 📐 支援 Mermaid 圖表渲染
- [ ] 🔌 外掛系統（自訂格式化規則、評分維度）
- [ ] 📦 PyPI 發布，支援 `pip install markview-pro`

---

<a name="-貢獻指南-1"></a>

## 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！無論是提交 Bug、改進文件，還是貢獻新功能。

### Commit Message 規範

| 前綴 | 說明 |
|------|------|
| `feat:` | 新增功能 |
| `fix:` | 修復問題 |
| `docs:` | 文件更新 |
| `refactor:` | 代碼重構 |
| `test:` | 測試相關 |
| `chore:` | 建構/工具鏈相關 |

---

<a name="-開源協議-1"></a>

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>

---

<a name="-introduction"></a>

## 🎉 Introduction

**MarkView-Pro** is a lightweight terminal Markdown toolkit designed for developers. It integrates **live preview, intelligent formatting, quality scoring, multi-format export, and syntax highlighting** into a single zero-dependency CLI tool, helping you read, write, and optimize Markdown documents efficiently right from your terminal.

### 💡 Problems Solved

- ❌ No intuitive way to preview rendered Markdown in the terminal
- ❌ Markdown documents with inconsistent formatting and messy styles
- ❌ Lack of quantitative assessment for document quality
- ❌ Existing tools are heavy with complex installation and configuration

### 🌟 Differentiation Highlights

- **Truly Zero Dependencies** — Built entirely with Python standard library, `pip install` and you're ready
- **Full GFM Compatibility** — Complete support for GitHub Flavored Markdown extensions (tables, task lists, strikethrough, etc.)
- **3D Quality Scoring** — Quantitative assessment from three dimensions: structural completeness, readability, and standardization
- **13+ Language Syntax Highlighting** — Lightweight regex-based code coloring covering mainstream programming languages
- **TUI Interactive Dashboard** — curses-based terminal interactive interface with real-time browsing and operations

### 🔍 Inspiration

Inspired by the GitHub Trending project `microsoft/markitdown` (128k+ Stars), focusing on the niche of **terminal preview and format optimization** within the Markdown ecosystem, building a truly lightweight, zero-dependency native terminal tool.

---

<a name="-core-features"></a>

## ✨ Core Features

### 📝 Live Preview
- Render Markdown directly in the terminal with **ANSI colored output**
- Automatic heading level coloring (H1 bold+underline, H2 bold, etc.)
- Code blocks with border rendering, auto-aligned tables
- Blockquotes with vertical line indicators, links displayed as `text(URL)`
- **Adaptive terminal width** with automatic line wrapping

### 🎨 Intelligent Formatting
- Heading spacing normalization
- Unified list indentation (2/4 spaces configurable)
- Auto-detection and completion of code block language identifiers
- Trailing whitespace cleanup, consecutive blank line merging
- **Auto-spacing between CJK and Latin characters** (optional)
- Table alignment optimization

### 📊 Quality Scoring
- **Structural Completeness**: Heading hierarchy, paragraphs, lists, code blocks, links, tables, blockquotes
- **Readability**: Paragraph length, line length, heading density, blank line usage, format richness
- **Standardization**: Trailing whitespace, blank line norms, heading format, list format, code block norms
- Overall score **0-100** with grade output (S/A/B/C/D)

### 🔄 File Watching
- Polling-based file change detection (no watchdog dependency)
- Configurable polling interval (default: 1 second)
- Auto-refresh preview on file changes
- Graceful exit with Ctrl+C

### 📤 Multi-Format Export
- **HTML** — Full HTML document with inline CSS styling
- **JSON AST** — Complete parsed abstract syntax tree
- **Plain Text** — Clean text with all Markdown syntax stripped

### 🌈 Syntax Highlighting
- Supports **13+ programming languages**: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust, HTML, CSS, JSON, YAML, Bash/Shell, SQL, Markdown
- Keywords, strings, comments, numbers displayed in different colors
- Custom color theme support

### 🖥️ TUI Interactive Dashboard
- curses-based terminal interactive interface
- Left panel: file preview + Right panel: info dashboard
- Keyboard shortcuts: `q` quit, `r` refresh, `f` format, `s` score

---

<a name="-quick-start"></a>

## 🚀 Quick Start

### Requirements

- **Python** 3.8 or higher
- **OS**: Windows / macOS / Linux
- **Terminal**: Modern terminal with ANSI escape code support

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/MarkView-Pro.git
cd MarkView-Pro

# Install (zero external dependencies)
pip install -e .
```

### Verify Installation

```bash
markview --version
# Output: MarkView-Pro 1.0.0
```

### Basic Usage

```bash
# 📝 Preview a Markdown file
markview preview README.md

# 🔄 Preview with file watching
markview preview README.md --watch

# 🎨 Format in-place
markview format README.md --in-place

# 🎨 Format with CJK-Latin auto-spacing
markview format README.md --in-place --cjk-spaces

# 📊 Quality scoring
markview score README.md

# 📊 Quality scoring (JSON output)
markview score README.md --json

# 📤 Export to HTML
markview export README.md --format html --output output.html

# 📤 Export to JSON AST
markview export README.md --format json --output output.json

# 📤 Export to plain text
markview export README.md --format text --output output.txt

# 🖥️ Launch TUI interactive dashboard
markview serve README.md
```

---

<a name="-detailed-usage-guide"></a>

## 📖 Detailed Usage Guide

### Preview Command

```bash
markview preview <file> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--watch` | Enable file watching mode | Off |
| `--no-color` | Disable ANSI colored output | Off |
| `--interval` | File watch polling interval (seconds) | 1 |

### Format Command

```bash
markview format <file> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--in-place` | Modify file in-place | Off |
| `--output` | Output to specified file | stdout |
| `--cjk-spaces` | Auto-add spaces between CJK and Latin | Off |
| `--indent` | List indentation spaces | 2 |

### Score Command

```bash
markview score <file> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--json` | Output score results in JSON format | Off |

### Scoring Grades

| Grade | Score Range | Description |
|-------|-------------|-------------|
| **S** | 90-100 | Excellent, outstanding document quality |
| **A** | 80-89 | Good, solid document quality |
| **B** | 60-79 | Fair, room for improvement |
| **C** | 40-59 | Below average, significant improvements needed |
| **D** | 0-39 | Poor, major overhaul required |

### Typical Use Cases

**Use Case 1: Live Preview While Writing**
```bash
# Watch for changes in one terminal
markview preview my-article.md --watch
# Edit my-article.md in your editor — terminal auto-refreshes on save
```

**Use Case 2: Batch Format Markdown Files**
```bash
# Format all .md files in the current directory
for f in *.md; do markview format "$f" --in-place --cjk-spaces; done
```

**Use Case 3: CI/CD Quality Gate**
```bash
# Fail CI if document quality score is below 60
SCORE=$(markview score README.md --json | python3 -c "import sys,json; print(json.load(sys.stdin)['overall'])")
if [ "$SCORE" -lt 60 ]; then echo "Document quality check failed: $SCORE"; exit 1; fi
```

---

<a name="-design-philosophy-and-roadmap"></a>

## 💡 Design Philosophy & Roadmap

### Design Philosophy

MarkView-Pro follows the principle of **"Minimal but Not Minimalist"**:

1. **Zero Dependencies First** — Core features built entirely on Python standard library to minimize installation friction
2. **Modular Architecture** — Parser, renderer, formatter, and scorer are independent and can be used standalone
3. **Terminal Native** — All functionality works within the terminal, no browser or external app needed
4. **Progressive Enhancement** — Start with basic preview, then layer on formatting, scoring, and export capabilities

### Tech Stack Rationale

| Technology | Why |
|------------|-----|
| Python | Widest developer ecosystem, richest standard library, best cross-platform compatibility |
| argparse | Standard library CLI framework, zero-dependency and feature-complete |
| curses | Standard library TUI framework, native terminal interaction |
| re (regex) | Standard library regex engine, sufficient for lightweight syntax highlighting |

### Roadmap

- [ ] 📡 WebSocket-based real-time collaborative preview
- [ ] 🎨 Additional color themes (dark/light/custom)
- [ ] 📐 Mermaid diagram rendering support
- [ ] 🔌 Plugin system (custom formatting rules, scoring dimensions)
- [ ] 📦 PyPI release: `pip install markview-pro`
- [ ] 🌐 Additional language support (Japanese, Korean, etc.)

---

<a name="-build-and-deploy"></a>

## 📦 Build & Deploy

### Local Development Setup

```bash
git clone https://github.com/gitstq/MarkView-Pro.git
cd MarkView-Pro
pip install -e .
```

### Running Tests

```bash
cd MarkView-Pro
python -m unittest discover tests/ -v
```

### Uninstall

```bash
pip uninstall markview-pro
```

---

<a name="-contributing"></a>

## 🤝 Contributing

We welcome and appreciate contributions of all forms! Whether it's filing bugs, improving documentation, or contributing new features.

### PR Submission Guidelines

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add some feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a Pull Request

### Commit Message Convention

Following the Angular commit convention:

| Prefix | Description |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation update |
| `refactor:` | Code refactoring |
| `test:` | Test-related changes |
| `chore:` | Build/tooling changes |

### Issue Reporting

When filing an issue, please include:
- Problem description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Runtime environment (Python version, OS)

---

<a name="-license"></a>

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
