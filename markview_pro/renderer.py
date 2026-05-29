"""
终端渲染引擎模块 - 将Markdown AST渲染为终端友好的ANSI着色文本。

将解析器生成的AST渲染为适合终端显示的纯文本格式，
使用ANSI转义码进行语法着色。

功能特性：
- 标题层级用不同颜色和样式区分
- 代码块带边框渲染，支持语法高亮
- 引用块用灰色竖线标识
- 列表缩进对齐
- 表格自动计算列宽并渲染
- 链接显示为 文本(URL) 格式
- 支持无颜色模式（纯文本）
- 支持终端宽度自适应
"""

from typing import Any, Dict, List, Optional

from markview_pro.parser import ASTNode, NodeType
from markview_pro.highlighter import SyntaxHighlighter
from markview_pro.utils import (
    ANSIStyle, DEFAULT_THEME, colorize, strip_ansi,
    ansi_len, get_terminal_width, pad_text,
)


class TerminalRenderer:
    """
    终端渲染引擎。

    将Markdown AST渲染为终端友好的纯文本，使用ANSI转义码着色。

    Attributes:
        no_color: 是否禁用颜色输出
        term_width: 终端宽度
        theme: 颜色主题
        highlighter: 语法高亮器
    """

    def __init__(self, no_color: bool = False,
                 term_width: Optional[int] = None,
                 theme: Optional[Dict[str, str]] = None) -> None:
        """
        初始化终端渲染引擎。

        Args:
            no_color: 是否禁用颜色输出
            term_width: 终端宽度，若为None则自动检测
            theme: 自定义颜色主题
        """
        self.no_color: bool = no_color
        self.term_width: int = term_width or get_terminal_width(80)
        self.theme: Dict[str, str] = theme or DEFAULT_THEME
        self.highlighter: SyntaxHighlighter = SyntaxHighlighter(
            theme=self.theme, no_color=self.no_color
        )

    def render(self, ast: ASTNode) -> str:
        """
        渲染AST为终端文本。

        Args:
            ast: 文档AST根节点

        Returns:
            渲染后的终端文本
        """
        lines: List[str] = []
        self._render_node(ast, lines, indent=0)
        result = "\n".join(lines)
        # 移除末尾多余的空行
        return result.rstrip("\n") + "\n"

    def render_text(self, markdown_text: str) -> str:
        """
        直接渲染Markdown文本为终端文本。

        便捷方法，内部调用解析器解析后再渲染。

        Args:
            markdown_text: Markdown源文本

        Returns:
            渲染后的终端文本
        """
        from markview_pro.parser import MarkdownParser
        parser = MarkdownParser()
        ast = parser.parse(markdown_text)
        return self.render(ast)

    def _render_node(self, node: ASTNode, lines: List[str],
                     indent: int = 0) -> None:
        """
        递归渲染AST节点。

        Args:
            node: 当前AST节点
            lines: 输出行列表
            indent: 缩进级别
        """
        if node.type == NodeType.DOCUMENT:
            for child in node.children:
                self._render_node(child, lines, indent)

        elif node.type == NodeType.FRONTMATTER:
            self._render_frontmatter(node, lines)

        elif node.type == NodeType.HEADING:
            self._render_heading(node, lines)

        elif node.type == NodeType.PARAGRAPH:
            self._render_paragraph(node, lines, indent)

        elif node.type == NodeType.CODE_BLOCK:
            self._render_code_block(node, lines)

        elif node.type == NodeType.BLOCKQUOTE:
            self._render_blockquote(node, lines, indent)

        elif node.type == NodeType.UNORDERED_LIST:
            self._render_unordered_list(node, lines, indent)

        elif node.type == NodeType.ORDERED_LIST:
            self._render_ordered_list(node, lines, indent)

        elif node.type == NodeType.TASK_LIST:
            self._render_task_list(node, lines, indent)

        elif node.type == NodeType.TABLE:
            self._render_table(node, lines)

        elif node.type == NodeType.HR:
            self._render_hr(lines)

        else:
            # 未知节点类型，渲染为纯文本
            if node.content:
                lines.append(node.content)

    def _c(self, text: str, style_name: str) -> str:
        """
        应用主题颜色到文本。

        Args:
            text: 文本
            style_name: 主题中的样式名称

        Returns:
            着色后的文本
        """
        style = self.theme.get(style_name, "")
        return colorize(text, style, self.no_color)

    # --------------------------------------------------------
    # 各元素渲染方法
    # --------------------------------------------------------

    def _render_frontmatter(self, node: ASTNode, lines: List[str]) -> None:
        """
        渲染Frontmatter。

        Args:
            node: Frontmatter节点
            lines: 输出行列表
        """
        lines.append(self._c("---", "frontmatter"))
        for line in node.content.split("\n"):
            lines.append(self._c(line, "frontmatter"))
        lines.append(self._c("---", "frontmatter"))

    def _render_heading(self, node: ASTNode, lines: List[str]) -> None:
        """
        渲染标题。

        根据标题层级使用不同颜色和样式。

        Args:
            node: 标题节点
            lines: 输出行列表
        """
        level = node.metadata.get("level", 1)
        prefix = "#" * level
        content = self._render_inline_children(node)

        style_name = f"h{level}"
        styled_prefix = self._c(prefix, style_name)
        styled_content = self._c(content, style_name)

        line = f"{styled_prefix} {styled_content}"
        lines.append(line)

        # H1 下面加下划线
        if level == 1 and not self.no_color:
            underline = self._c("=" * min(ansi_len(content) + 2, self.term_width), style_name)
            lines.append(underline)

    def _render_paragraph(self, node: ASTNode, lines: List[str],
                         indent: int = 0) -> None:
        """
        渲染段落。

        自动换行以适应终端宽度。

        Args:
            node: 段落节点
            lines: 输出行列表
            indent: 缩进级别
        """
        content = self._render_inline_children(node)
        if not content.strip():
            return

        # 自动换行
        prefix = "  " * indent
        max_width = self.term_width - len(prefix)
        wrapped = self._word_wrap(content, max_width)

        for line in wrapped.split("\n"):
            lines.append(prefix + line)

        lines.append("")  # 段落后空行

    def _render_code_block(self, node: ASTNode, lines: List[str]) -> None:
        """
        渲染代码块。

        带边框渲染，支持语法高亮。

        Args:
            node: 代码块节点
            lines: 输出行列表
        """
        language = node.metadata.get("language", "")
        code = node.content

        # 应用语法高亮
        if language:
            highlighted = self.highlighter.highlight(code, language)
        else:
            highlighted = code

        # 计算边框宽度
        border_char = self._c("│", "table_border")
        corner_tl = self._c("┌", "table_border")
        corner_tr = self._c("┐", "table_border")
        corner_bl = self._c("└", "table_border")
        corner_br = self._c("┘", "table_border")

        # 找出最长行（考虑ANSI码）
        max_line_width = 0
        for line in highlighted.split("\n"):
            line_width = ansi_len(line)
            if line_width > max_line_width:
                max_line_width = line_width

        top_border = f"{corner_tl}{'─' * (max_line_width + 2)}{corner_tr}"
        bottom_border = f"{corner_bl}{'─' * (max_line_width + 2)}{corner_br}"

        # 语言标签
        if language:
            lang_label = self._c(f" {language} ", "code_inline")
            label_len = ansi_len(lang_label)
            top_border = (
                f"{corner_tl}{lang_label}"
                f"{'─' * (max_line_width + 2 - label_len)}{corner_tr}"
            )

        lines.append(top_border)
        for line in highlighted.split("\n"):
            padded = pad_text(line, max_line_width)
            lines.append(f"{border_char} {padded} {border_char}")
        lines.append(bottom_border)
        lines.append("")

    def _render_blockquote(self, node: ASTNode, lines: List[str],
                           indent: int = 0) -> None:
        """
        渲染引用块。

        使用灰色竖线标识引用内容。

        Args:
            node: 引用块节点
            lines: 输出行列表
            indent: 缩进级别
        """
        prefix = "  " * indent
        border = self._c("│", "blockquote_border")

        if node.children:
            # 递归渲染子节点
            inner_lines: List[str] = []
            for child in node.children:
                self._render_node(child, inner_lines, 0)

            for line in inner_lines:
                if line:
                    lines.append(f"{prefix}{border} {self._c(line, 'blockquote')}")
                else:
                    lines.append(f"{prefix}{border}")
        elif node.content:
            for line in node.content.split("\n"):
                if line:
                    lines.append(f"{prefix}{border} {self._c(line, 'blockquote')}")
                else:
                    lines.append(f"{prefix}{border}")

        lines.append("")

    def _render_unordered_list(self, node: ASTNode, lines: List[str],
                               indent: int = 0) -> None:
        """
        渲染无序列表。

        Args:
            node: 列表节点
            lines: 输出行列表
            indent: 缩进级别
        """
        prefix = "  " * indent
        bullet = self._c("●", "list_bullet")

        for item in node.children:
            content = self._render_inline_children(item)
            lines.append(f"{prefix}  {bullet} {content}")

        lines.append("")

    def _render_ordered_list(self, node: ASTNode, lines: List[str],
                             indent: int = 0) -> None:
        """
        渲染有序列表。

        Args:
            node: 列表节点
            lines: 输出行列表
            indent: 缩进级别
        """
        prefix = "  " * indent

        for i, item in enumerate(node.children, 1):
            number = item.metadata.get("number", i)
            num_str = self._c(f"{number}.", "list_number")
            content = self._render_inline_children(item)
            lines.append(f"{prefix}  {num_str} {content}")

        lines.append("")

    def _render_task_list(self, node: ASTNode, lines: List[str],
                          indent: int = 0) -> None:
        """
        渲染任务列表。

        Args:
            node: 任务列表节点
            lines: 输出行列表
            indent: 缩进级别
        """
        prefix = "  " * indent

        for item in node.children:
            checked = item.metadata.get("checked", False)
            if checked:
                checkbox = self._c("[x]", "task_done")
            else:
                checkbox = self._c("[ ]", "task_pending")
            content = self._render_inline_children(item)
            lines.append(f"{prefix}  {checkbox} {content}")

        lines.append("")

    def _render_table(self, node: ASTNode, lines: List[str]) -> None:
        """
        渲染表格。

        自动计算列宽，支持对齐方式。

        Args:
            node: 表格节点
            lines: 输出行列表
        """
        # 收集所有行数据
        rows_data: List[List[str]] = []
        alignments = node.metadata.get("alignments", [])

        for row_node in node.children:
            row: List[str] = []
            for cell in row_node.children:
                row.append(cell.content)
            rows_data.append(row)

        if not rows_data:
            return

        # 计算列数和每列最大宽度
        num_cols = max(len(row) for row in rows_data)
        col_widths: List[int] = [0] * num_cols

        for row in rows_data:
            for j, cell_text in enumerate(row):
                if j < num_cols:
                    # 使用显示宽度
                    width = len(strip_ansi(cell_text))
                    if width > col_widths[j]:
                        col_widths[j] = width

        # 限制列宽不超过终端宽度
        total_min_width = num_cols + 1  # | 和空格
        available = self.term_width - total_min_width
        for j in range(num_cols):
            if col_widths[j] > available // num_cols:
                col_widths[j] = available // num_cols

        # 渲染表格
        border = self._c("|", "table_border")
        sep_char = self._c("-", "table_border")

        def render_row(row_data: List[str], is_header: bool = False) -> str:
            """渲染单行表格。"""
            cells = []
            for j in range(num_cols):
                cell_text = row_data[j] if j < len(row_data) else ""
                align = alignments[j] if j < len(alignments) else "left"
                padded = pad_text(cell_text, col_widths[j], align=align)
                if is_header:
                    padded = self._c(padded, "table_header")
                cells.append(f" {padded} ")
            return f"{border}{border.join(cells)}{border}"

        # 渲染分隔行
        def render_separator() -> str:
            """渲染表格分隔行。"""
            cells = []
            for j in range(num_cols):
                align = alignments[j] if j < len(alignments) else "left"
                if align == "center":
                    cell = f":{sep_char * (col_widths[j] - 1)}:"
                elif align == "right":
                    cell = f"{sep_char * (col_widths[j] - 1)}:"
                else:
                    cell = sep_char * col_widths[j]
                cells.append(cell)
            return f"{border}{border.join(cells)}{border}"

        # 输出表格
        for i, row in enumerate(rows_data):
            is_header = (i == 0 and node.children[0].metadata.get("is_header", False))
            lines.append(render_row(row, is_header=is_header))
            if i == 0:
                lines.append(render_separator())

        lines.append("")

    def _render_hr(self, lines: List[str]) -> None:
        """
        渲染水平线。

        Args:
            lines: 输出行列表
        """
        hr_char = self._c("─", "hr")
        hr_line = hr_char * self.term_width
        lines.append(hr_line)
        lines.append("")

    # --------------------------------------------------------
    # 行内元素渲染
    # --------------------------------------------------------

    def _render_inline_children(self, node: ASTNode) -> str:
        """
        渲染节点的行内子元素。

        Args:
            node: 包含行内子元素的节点

        Returns:
            渲染后的行内文本
        """
        if not node.children:
            return node.content or ""

        parts: List[str] = []
        for child in node.children:
            parts.append(self._render_inline_node(child))
        return "".join(parts)

    def _render_inline_node(self, node: ASTNode) -> str:
        """
        渲染单个行内节点。

        Args:
            node: 行内AST节点

        Returns:
            渲染后的文本
        """
        if node.type == NodeType.TEXT:
            return node.content

        elif node.type == NodeType.BOLD:
            content = self._render_inline_children(node)
            return self._c(content, "bold")

        elif node.type == NodeType.ITALIC:
            content = self._render_inline_children(node)
            return self._c(content, "italic")

        elif node.type == NodeType.STRIKETHROUGH:
            content = self._render_inline_children(node)
            return self._c(content, "strikethrough")

        elif node.type == NodeType.CODE_INLINE:
            return self._c(node.content, "code_inline")

        elif node.type == NodeType.LINK:
            text = self._render_inline_children(node)
            url = node.metadata.get("url", "")
            return f"{self._c(text, 'link_text')}({self._c(url, 'link_url')})"

        elif node.type == NodeType.IMAGE:
            alt = node.content
            url = node.metadata.get("url", "")
            return f"{self._c(f'[{alt}]', 'image')}({self._c(url, 'link_url')})"

        elif node.type == NodeType.SOFTBREAK:
            return "\n"

        elif node.type == NodeType.LINEBREAK:
            return "  \n"

        else:
            return node.content or ""

    # --------------------------------------------------------
    # 文本处理工具
    # --------------------------------------------------------

    def _word_wrap(self, text: str, max_width: int) -> str:
        """
        自动换行文本到指定宽度。

        考虑CJK字符的显示宽度（全角字符占2列）。

        Args:
            text: 输入文本
            max_width: 最大行宽

        Returns:
            换行后的文本
        """
        if max_width <= 0:
            return text

        # 去除ANSI码进行换行计算
        clean_text = strip_ansi(text)
        if len(clean_text) <= max_width:
            return text

        result_lines: List[str] = []
        current_line = ""
        current_width = 0

        i = 0
        while i < len(text):
            char = text[i]

            # 跳过ANSI转义序列
            if char == "\033":
                j = text.find("m", i)
                if j != -1:
                    current_line += text[i:j + 1]
                    i = j + 1
                    continue

            # 计算字符宽度
            char_width = self._char_width(char)

            if current_width + char_width > max_width and current_line:
                result_lines.append(current_line)
                current_line = ""
                current_width = 0

            current_line += char
            current_width += char_width
            i += 1

        if current_line:
            result_lines.append(current_line)

        return "\n".join(result_lines)

    @staticmethod
    def _char_width(char: str) -> int:
        """
        计算单个字符的显示宽度。

        CJK全角字符占2列，其他字符占1列。

        Args:
            char: 单个字符

        Returns:
            显示宽度
        """
        cp = ord(char)
        if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF
                or 0xFF00 <= cp <= 0xFFEF or 0x3000 <= cp <= 0x303F):
            return 2
        return 1
