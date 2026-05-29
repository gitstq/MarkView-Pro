# MarkView-Pro

轻量级终端Markdown实时预览与智能格式化引擎 | Lightweight Terminal Markdown Live Preview & Intelligent Formatting Engine

## Features

- Zero external dependencies (Python standard library only)
- GFM compatible Markdown parser
- Terminal rendering with ANSI colors
- Intelligent formatting engine
- File watching with auto-refresh
- Markdown quality scoring
- Multi-format export (HTML/JSON/Text)
- Code syntax highlighting (13+ languages)
- TUI interactive dashboard

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Preview Markdown file
markview preview README.md

# Preview with file watching
markview preview README.md --watch

# Format Markdown file
markview format README.md --in-place

# Score Markdown quality
markview score README.md

# Export to HTML
markview export README.md --format html --output output.html

# Export to JSON AST
markview export README.md --format json

# Export to plain text
markview export README.md --format text

# Interactive TUI dashboard
markview serve README.md
```

## License

MIT
