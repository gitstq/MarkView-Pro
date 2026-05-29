"""
多格式导出模块 - 将Markdown导出为HTML、JSON AST、纯文本等格式。

支持的导出格式：
- HTML：生成带内联CSS的完整HTML文档
- JSON AST：输出完整的解析AST树
- 纯文本：去除所有Markdown语法的纯文本
"""

import html as html_module
import json
import re
from typing import Any, Dict, List, Optional

from markview_pro.parser import MarkdownParser, ASTNode, NodeType
from markview_pro.highlighter import SyntaxHighlighter


class MarkdownExporter:
    """
    Markdown多格式导出器。

    将Markdown文档导出为不同格式。

    Usage:
        exporter = MarkdownExporter()
        html = exporter.export_to_html("# Hello")
        ast_json = exporter.export_to_json("# Hello")
        text = exporter.export_to_text("# Hello")
    """

    def __init__(self) -> None:
        """初始化导出器。"""
        self.parser = MarkdownParser()
        self.highlighter = SyntaxHighlighter(no_color=True)

    def export(self, text: str, fmt: str) -> str:
        """
        导出Markdown到指定格式。

        Args:
            text: Markdown源文本
            fmt: 导出格式 ("html", "json", "text")

        Returns:
            导出后的文本

        Raises:
            ValueError: 不支持的导出格式
        """
        exporters = {
            "html": self.export_to_html,
            "json": self.export_to_json,
            "text": self.export_to_text,
        }

        exporter = exporters.get(fmt.lower())
        if exporter is None:
            raise ValueError(
                f"不支持的导出格式: {fmt}，"
                f"支持的格式: {', '.join(exporters.keys())}"
            )

        return exporter(text)

    # --------------------------------------------------------
    # HTML 导出
    # --------------------------------------------------------

    def export_to_html(self, text: str, title: Optional[str] = None) -> str:
        """
        导出为HTML文档。

        生成带内联CSS的完整HTML文档，支持代码高亮和表格样式。

        Args:
            text: Markdown源文本
            title: HTML文档标题，若为None则自动从H1提取

        Returns:
            完整的HTML文档字符串
        """
        ast = self.parser.parse(text)

        # 自动提取标题
        if title is None:
            for child in ast.children:
                if child.type == NodeType.HEADING and child.metadata.get("level") == 1:
                    title = child.content
                    break
        if title is None:
            title = "Markdown Document"

        # 生成HTML body
        body_parts: List[str] = []
        for child in ast.children:
            body_parts.append(self._render_html_node(child))

        body = "\n".join(body_parts)

        # 生成完整HTML
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_module.escape(title)}</title>
    <style>
{self._get_html_css()}
    </style>
</head>
<body>
    <div class="markdown-body">
{body}
    </div>
</body>
</html>"""
        return html_template

    def _get_html_css(self) -> str:
        """
        获取HTML内联CSS样式。

        Returns:
            CSS样式字符串
        """
        return """        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: #24292e;
            background-color: #ffffff;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
        }
        .markdown-body h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; margin: 24px 0 16px; font-weight: 600; }
        .markdown-body h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; margin: 24px 0 16px; font-weight: 600; }
        .markdown-body h3 { font-size: 1.25em; margin: 24px 0 16px; font-weight: 600; }
        .markdown-body h4 { font-size: 1em; margin: 24px 0 16px; font-weight: 600; }
        .markdown-body h5 { font-size: 0.875em; margin: 24px 0 16px; font-weight: 600; }
        .markdown-body h6 { font-size: 0.85em; margin: 24px 0 16px; font-weight: 600; color: #6a737d; }
        .markdown-body p { margin-bottom: 16px; }
        .markdown-body a { color: #0366d6; text-decoration: none; }
        .markdown-body a:hover { text-decoration: underline; }
        .markdown-body strong { font-weight: 600; }
        .markdown-body em { font-style: italic; }
        .markdown-body del { text-decoration: line-through; color: #6a737d; }
        .markdown-body code {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 85%;
        }
        .markdown-body pre {
            background-color: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin-bottom: 16px;
        }
        .markdown-body pre code {
            background-color: transparent;
            padding: 0;
            font-size: 100%;
            border-radius: 0;
        }
        .markdown-body blockquote {
            border-left: 4px solid #dfe2e5;
            padding: 0 16px;
            color: #6a737d;
            margin-bottom: 16px;
        }
        .markdown-body ul, .markdown-body ol { padding-left: 2em; margin-bottom: 16px; }
        .markdown-body li { margin-bottom: 4px; }
        .markdown-body table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
        .markdown-body th, .markdown-body td { border: 1px solid #dfe2e5; padding: 6px 13px; }
        .markdown-body th { font-weight: 600; background-color: #f6f8fa; }
        .markdown-body tr:nth-child(even) { background-color: #f6f8fa; }
        .markdown-body hr { border: 0; border-top: 1px solid #e1e4e8; margin: 24px 0; }
        .markdown-body img { max-width: 100%; }
        .markdown-body .task-list-item { list-style-type: none; margin-left: -1.5em; }
        .markdown-body .task-list-item input { margin-right: 8px; }
        /* 代码高亮 */
        .hl-keyword { color: #d73a49; }
        .hl-string { color: #22863a; }
        .hl-comment { color: #6a737d; font-style: italic; }
        .hl-number { color: #005cc5; }
        .hl-function { color: #6f42c1; }
        .hl-type { color: #005cc5; }
        .hl-operator { color: #d73a49; }
        .hl-builtin { color: #005cc5; }
        .hl-decorator { color: #e36209; }"""

    def _render_html_node(self, node: ASTNode) -> str:
        """
        将AST节点渲染为HTML。

        Args:
            node: AST节点

        Returns:
            HTML字符串
        """
        if node.type == NodeType.HEADING:
            level = node.metadata.get("level", 1)
            content = self._render_html_inline(node)
            return f"<h{level}>{content}</h{level}>"

        elif node.type == NodeType.PARAGRAPH:
            content = self._render_html_inline(node)
            return f"<p>{content}</p>"

        elif node.type == NodeType.CODE_BLOCK:
            language = node.metadata.get("language", "")
            code = html_module.escape(node.content)

            # 简单的语法高亮（基于正则）
            if language:
                highlighted = self._highlight_html(code, language)
            else:
                highlighted = code

            lang_attr = f' class="language-{language}"' if language else ""
            return f"<pre><code{lang_attr}>{highlighted}</code></pre>"

        elif node.type == NodeType.BLOCKQUOTE:
            content = self._render_html_children(node)
            return f"<blockquote>{content}</blockquote>"

        elif node.type == NodeType.UNORDERED_LIST:
            items = []
            for child in node.children:
                content = self._render_html_inline(child)
                items.append(f"<li>{content}</li>")
            return f"<ul>{''.join(items)}</ul>"

        elif node.type == NodeType.ORDERED_LIST:
            items = []
            for child in node.children:
                content = self._render_html_inline(child)
                items.append(f"<li>{content}</li>")
            return f"<ol>{''.join(items)}</ol>"

        elif node.type == NodeType.TASK_LIST:
            items = []
            for child in node.children:
                checked = child.metadata.get("checked", False)
                checkbox = "checked" if checked else ""
                content = self._render_html_inline(child)
                items.append(
                    f'<li class="task-list-item">'
                    f'<input type="checkbox" {checkbox} disabled>'
                    f'{content}</li>'
                )
            return f"<ul>{''.join(items)}</ul>"

        elif node.type == NodeType.TABLE:
            return self._render_html_table(node)

        elif node.type == NodeType.HR:
            return "<hr>"

        elif node.type == NodeType.FRONTMATTER:
            return ""  # Frontmatter不导出到HTML

        else:
            return node.content or ""

    def _render_html_children(self, node: ASTNode) -> str:
        """
        渲染节点的所有子节点为HTML。

        Args:
            node: AST节点

        Returns:
            HTML字符串
        """
        parts: List[str] = []
        for child in node.children:
            parts.append(self._render_html_node(child))
        return "\n".join(parts)

    def _render_html_inline(self, node: ASTNode) -> str:
        """
        渲染节点的行内子元素为HTML。

        Args:
            node: AST节点

        Returns:
            HTML字符串
        """
        if not node.children:
            return html_module.escape(node.content or "")

        parts: List[str] = []
        for child in node.children:
            parts.append(self._render_html_inline_node(child))
        return "".join(parts)

    def _render_html_inline_node(self, node: ASTNode) -> str:
        """
        渲染单个行内节点为HTML。

        Args:
            node: 行内AST节点

        Returns:
            HTML字符串
        """
        if node.type == NodeType.TEXT:
            return html_module.escape(node.content)

        elif node.type == NodeType.BOLD:
            content = self._render_html_inline(node)
            return f"<strong>{content}</strong>"

        elif node.type == NodeType.ITALIC:
            content = self._render_html_inline(node)
            return f"<em>{content}</em>"

        elif node.type == NodeType.STRIKETHROUGH:
            content = self._render_html_inline(node)
            return f"<del>{content}</del>"

        elif node.type == NodeType.CODE_INLINE:
            return f"<code>{html_module.escape(node.content)}</code>"

        elif node.type == NodeType.LINK:
            text = self._render_html_inline(node)
            url = html_module.escape(node.metadata.get("url", ""))
            return f'<a href="{url}">{text}</a>'

        elif node.type == NodeType.IMAGE:
            alt = html_module.escape(node.content)
            url = html_module.escape(node.metadata.get("url", ""))
            return f'<img src="{url}" alt="{alt}">'

        else:
            return html_module.escape(node.content or "")

    def _render_html_table(self, node: ASTNode) -> str:
        """
        渲染表格为HTML。

        Args:
            node: 表格AST节点

        Returns:
            HTML表格字符串
        """
        thead_html: List[str] = []
        tbody_html: List[str] = []

        for row_node in node.children:
            is_header = row_node.metadata.get("is_header", False)

            cells_html: List[str] = []
            for cell in row_node.children:
                cell_tag = "th" if is_header else "td"
                content = self._render_html_inline(cell)
                cells_html.append(f"<{cell_tag}>{content}</{cell_tag}>")

            row_html = f"<tr>{''.join(cells_html)}</tr>"

            if is_header:
                thead_html.append(row_html)
            else:
                tbody_html.append(row_html)

        parts: List[str] = []
        if thead_html:
            parts.append(f"<thead>{''.join(thead_html)}</thead>")
        if tbody_html:
            parts.append(f"<tbody>{''.join(tbody_html)}</tbody>")

        return f"<table>{''.join(parts)}</table>"

    def _highlight_html(self, code: str, language: str) -> str:
        """
        为HTML输出进行简单的语法高亮。

        使用正则替换实现基本的语法着色。

        Args:
            code: 已转义的HTML代码文本
            code: 编程语言标识

        Returns:
            带HTML span标签的高亮代码
        """
        # 注释
        code = re.sub(
            r"(#[^\n]*)",
            r'<span class="hl-comment">\1</span>',
            code
        )
        # 字符串（双引号）
        code = re.sub(
            r'(&quot;[^&]*?&quot;)',
            r'<span class="hl-string">\1</span>',
            code
        )
        # 数字
        code = re.sub(
            r"\b(\d+\.?\d*)\b",
            r'<span class="hl-number">\1</span>',
            code
        )
        # 关键字（常见）
        keywords = (
            r"\b(def|class|if|else|elif|for|while|return|import|from|"
            r"try|except|finally|with|as|in|not|and|or|is|lambda|yield|"
            r"pass|break|continue|raise|async|await|function|var|let|const|"
            r"new|this|true|false|null|undefined|public|private|protected|"
            r"static|void|int|float|double|char|boolean|string)\b"
        )
        code = re.sub(
            keywords,
            r'<span class="hl-keyword">\1</span>',
            code
        )

        return code

    # --------------------------------------------------------
    # JSON AST 导出
    # --------------------------------------------------------

    def export_to_json(self, text: str) -> str:
        """
        导出为JSON格式的AST。

        Args:
            text: Markdown源文本

        Returns:
            JSON格式字符串
        """
        ast = self.parser.parse(text)
        return json.dumps(ast.to_dict(), ensure_ascii=False, indent=2)

    # --------------------------------------------------------
    # 纯文本导出
    # --------------------------------------------------------

    def export_to_text(self, text: str) -> str:
        """
        导出为纯文本。

        去除所有Markdown语法标记，保留纯文本内容。

        Args:
            text: Markdown源文本

        Returns:
            纯文本字符串
        """
        ast = self.parser.parse(text)
        lines: List[str] = []
        self._render_text_node(ast, lines)
        result = "\n".join(lines)
        return result.strip() + "\n"

    def _render_text_node(self, node: ASTNode, lines: List[str]) -> None:
        """
        将AST节点渲染为纯文本。

        Args:
            node: AST节点
            lines: 输出行列表
        """
        if node.type == NodeType.DOCUMENT:
            for child in node.children:
                self._render_text_node(child, lines)

        elif node.type == NodeType.HEADING:
            level = node.metadata.get("level", 1)
            prefix = "#" * level
            lines.append(f"{prefix} {self._render_text_inline(node)}")
            lines.append("")

        elif node.type == NodeType.PARAGRAPH:
            lines.append(self._render_text_inline(node))
            lines.append("")

        elif node.type == NodeType.CODE_BLOCK:
            for code_line in node.content.split("\n"):
                lines.append(f"    {code_line}")
            lines.append("")

        elif node.type == NodeType.BLOCKQUOTE:
            for child in node.children:
                self._render_text_node(child, lines)

        elif node.type in (NodeType.UNORDERED_LIST, NodeType.ORDERED_LIST,
                           NodeType.TASK_LIST):
            for i, child in enumerate(node.children, 1):
                if node.type == NodeType.ORDERED_LIST:
                    lines.append(f"  {i}. {self._render_text_inline(child)}")
                elif node.type == NodeType.TASK_LIST:
                    checked = child.metadata.get("checked", False)
                    mark = "[x]" if checked else "[ ]"
                    lines.append(f"  {mark} {self._render_text_inline(child)}")
                else:
                    lines.append(f"  - {self._render_text_inline(child)}")
            lines.append("")

        elif node.type == NodeType.TABLE:
            for row_node in node.children:
                cells = [cell.content for cell in row_node.children]
                lines.append(" | ".join(cells))
            lines.append("")

        elif node.type == NodeType.HR:
            lines.append("---")
            lines.append("")

        elif node.type == NodeType.FRONTMATTER:
            pass  # 跳过frontmatter

        else:
            if node.content:
                lines.append(node.content)

    def _render_text_inline(self, node: ASTNode) -> str:
        """
        渲染行内节点为纯文本。

        Args:
            node: AST节点

        Returns:
            纯文本字符串
        """
        if not node.children:
            return node.content or ""

        parts: List[str] = []
        for child in node.children:
            if child.type == NodeType.LINK:
                parts.append(self._render_text_inline(child))
            elif child.type == NodeType.IMAGE:
                parts.append(child.content)
            elif child.type in (NodeType.BOLD, NodeType.ITALIC,
                                NodeType.STRIKETHROUGH):
                parts.append(self._render_text_inline(child))
            else:
                parts.append(child.content or "")
        return "".join(parts)
