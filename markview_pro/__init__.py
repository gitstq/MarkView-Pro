"""
MarkView-Pro - 轻量级终端Markdown实时预览与智能格式化引擎
Lightweight Terminal Markdown Live Preview & Intelligent Formatting Engine

零外部依赖，仅使用Python标准库，Python 3.8+ 兼容。
"""

__version__ = "1.0.0"
__author__ = "MarkView-Pro Team"
__license__ = "MIT"
__description__ = "轻量级终端Markdown实时预览与智能格式化引擎"

# 核心模块公开接口
from markview_pro.parser import MarkdownParser
from markview_pro.renderer import TerminalRenderer
from markview_pro.formatter import MarkdownFormatter
from markview_pro.scorer import MarkdownScorer
from markview_pro.exporter import MarkdownExporter
from markview_pro.highlighter import SyntaxHighlighter
from markview_pro.watcher import FileWatcher

__all__ = [
    "MarkdownParser",
    "TerminalRenderer",
    "MarkdownFormatter",
    "MarkdownScorer",
    "MarkdownExporter",
    "SyntaxHighlighter",
    "FileWatcher",
]
