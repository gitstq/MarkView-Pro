"""
智能格式化引擎模块 - 自动规范化和优化Markdown文档格式。

提供多种格式化规则，用于清理和规范化Markdown文档。

格式化规则：
- 标题前后空行规范化
- 列表缩进统一
- 代码块语言标识补全
- 行尾空白清理
- 连续空行合并
- 表格对齐优化
- 链接引用格式统一
- 中英文之间自动添加空格（可选）
"""

import re
from typing import Dict, List, Optional, Tuple


class MarkdownFormatter:
    """
    Markdown智能格式化引擎。

    对Markdown文本进行自动规范化和优化处理。

    Attributes:
        indent_size: 列表缩进空格数
        add_cjk_spaces: 是否在中英文之间添加空格
        trailing_newline: 是否确保文件末尾有换行符
    """

    def __init__(self, indent_size: int = 2,
                 add_cjk_spaces: bool = False,
                 trailing_newline: bool = True) -> None:
        """
        初始化格式化引擎。

        Args:
            indent_size: 列表缩进空格数（2或4）
            add_cjk_spaces: 是否在中英文之间添加空格
            trailing_newline: 是否确保文件末尾有换行符
        """
        self.indent_size: int = indent_size
        self.add_cjk_spaces: bool = add_cjk_spaces
        self.trailing_newline: bool = trailing_newline

    def format(self, text: str) -> str:
        """
        格式化Markdown文本。

        按顺序应用所有格式化规则。

        Args:
            text: Markdown源文本

        Returns:
            格式化后的Markdown文本
        """
        lines = text.split("\n")

        # 步骤1：清理行尾空白
        lines = self._clean_trailing_whitespace(lines)

        # 步骤2：合并连续空行
        lines = self._merge_blank_lines(lines)

        # 步骤3：规范化标题空行
        lines = self._normalize_heading_spacing(lines)

        # 步骤4：统一列表缩进
        lines = self._normalize_list_indent(lines)

        # 步骤5：代码块语言标识补全
        lines = self._normalize_code_blocks(lines)

        # 步骤6：表格对齐优化
        lines = self._optimize_tables(lines)

        # 步骤7：链接格式统一
        lines = self._normalize_links(lines)

        # 步骤8：中英文空格（可选）
        if self.add_cjk_spaces:
            lines = self._add_cjk_spaces(lines)

        # 步骤9：规范化水平线
        lines = self._normalize_hr(lines)

        result = "\n".join(lines)

        # 确保末尾换行
        if self.trailing_newline and result and not result.endswith("\n"):
            result += "\n"

        return result

    # --------------------------------------------------------
    # 格式化规则实现
    # --------------------------------------------------------

    def _clean_trailing_whitespace(self, lines: List[str]) -> List[str]:
        """
        清理行尾空白字符。

        移除每行末尾的空格和制表符。

        Args:
            lines: 文档行列表

        Returns:
            清理后的行列表
        """
        return [line.rstrip() for line in lines]

    def _merge_blank_lines(self, lines: List[str]) -> List[str]:
        """
        合并连续空行，最多保留一个空行。

        Args:
            lines: 文档行列表

        Returns:
            合并后的行列表
        """
        result: List[str] = []
        prev_blank = False

        for line in lines:
            is_blank = not line.strip()
            if is_blank and prev_blank:
                continue
            result.append(line)
            prev_blank = is_blank

        return result

    def _normalize_heading_spacing(self, lines: List[str]) -> List[str]:
        """
        规范化标题前后的空行。

        标题前必须有一个空行（除非是文档第一行），
        标题后必须有一个空行。

        Args:
            lines: 文档行列表

        Returns:
            规范化后的行列表
        """
        result: List[str] = []
        n = len(lines)

        for i, line in enumerate(lines):
            # 检测标题行
            is_heading = bool(re.match(r"^#{1,6}\s", line))

            if is_heading:
                # 标题前添加空行（如果不是第一行且前一行不是空行）
                if result and result[-1].strip():
                    result.append("")

                result.append(line)

                # 标题后添加空行（如果下一行不是空行）
                if i + 1 < n and lines[i + 1].strip():
                    result.append("")
            else:
                result.append(line)

        return result

    def _normalize_list_indent(self, lines: List[str]) -> List[str]:
        """
        统一列表缩进。

        将列表项的缩进统一为指定的空格数。

        Args:
            lines: 文档行列表

        Returns:
            缩进统一后的行列表
        """
        result: List[str] = []
        in_list = False
        list_indent = 0

        for line in lines:
            # 检测列表项开始
            list_match = re.match(r"^(\s*)([-*+]|\d+\.)\s", line)
            if list_match:
                current_indent = len(list_match.group(1))
                if not in_list:
                    in_list = True
                    list_indent = current_indent
                # 规范化缩进
                marker = list_match.group(2)
                rest = line[list_match.end():]
                new_indent = " " * list_indent
                result.append(f"{new_indent}{marker} {rest}")
            elif in_list:
                # 检查是否仍在列表中（缩进的续行或空行）
                stripped = line.lstrip()
                if not stripped:
                    result.append(line)
                elif line.startswith(" " * (list_indent + 2)):
                    # 列表项的续行，保持相对缩进
                    result.append(line)
                elif re.match(r"^#{1,6}\s", line) or line.strip().startswith("```"):
                    in_list = False
                    result.append(line)
                else:
                    in_list = False
                    result.append(line)
            else:
                result.append(line)

        return result

    def _normalize_code_blocks(self, lines: List[str]) -> List[str]:
        """
        规范化代码块。

        检测无语言标识的围栏式代码块，尝试根据内容推断语言。

        Args:
            lines: 文档行列表

        Returns:
            规范化后的行列表
        """
        result: List[str] = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            # 检测围栏式代码块开始
            if line.strip().startswith("```"):
                fence = line.strip()
                lang_match = re.match(r"^```(\w*)", fence)

                if lang_match and not lang_match.group(1):
                    # 无语言标识，尝试推断
                    code_lines: List[str] = []
                    j = i + 1
                    while j < n and not lines[j].strip().startswith("```"):
                        code_lines.append(lines[j])
                        j += 1

                    lang = self._detect_language(code_lines)
                    if lang:
                        result.append(f"```{lang}")
                    else:
                        result.append("```")

                    result.extend(code_lines)
                    if j < n:
                        result.append(lines[j])
                    i = j + 1
                    continue
                else:
                    result.append(line)
                    i += 1
                    continue
            else:
                result.append(line)
                i += 1

        return result

    def _detect_language(self, code_lines: List[str]) -> Optional[str]:
        """
        根据代码内容推断编程语言。

        使用简单的启发式规则进行语言检测。

        Args:
            code_lines: 代码行列表

        Returns:
            推断出的语言标识，无法推断则返回None
        """
        if not code_lines:
            return None

        content = "\n".join(code_lines)

        # Python 特征
        python_patterns = [
            r"^\s*def\s+\w+\s*\(",
            r"^\s*class\s+\w+",
            r"^\s*import\s+\w+",
            r"^\s*from\s+\w+\s+import",
            r"^\s*if\s+__name__\s*==\s*['\"]__main__['\"]",
            r"^\s*print\s*\(",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in python_patterns):
            return "python"

        # JavaScript/TypeScript 特征
        js_patterns = [
            r"^\s*(const|let|var)\s+\w+",
            r"^\s*function\s+\w+",
            r"^\s*console\.\w+\(",
            r"^\s*=>\s*\{",
            r"require\s*\(",
            r"module\.exports",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in js_patterns):
            return "javascript"

        # HTML 特征
        if re.search(r"<(!DOCTYPE|html|head|body|div|span)", content, re.IGNORECASE):
            return "html"

        # CSS 特征
        css_patterns = [
            r"^\s*[\.\#\@]\w+.*\{",
            r"^\s*\w+\s*:\s*\w+",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in css_patterns):
            return "css"

        # JSON 特征
        if re.match(r"^\s*[\{\[]", content) and re.match(r".*[\}\]]\s*$", content):
            try:
                import json
                json.loads(content)
                return "json"
            except (ValueError, ImportError):
                pass

        # SQL 特征
        sql_patterns = [
            r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s",
            r"^\s*(FROM|WHERE|JOIN|GROUP BY|ORDER BY)\s",
        ]
        if any(re.search(p, content, re.IGNORECASE | re.MULTILINE) for p in sql_patterns):
            return "sql"

        # Bash 特征
        bash_patterns = [
            r"^#!/bin/(ba)?sh",
            r"^\s*echo\s+",
            r"^\s*export\s+\w+=",
            r"^\s*if\s+\[",
            r"^\s*fi\s*$",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in bash_patterns):
            return "bash"

        # YAML 特征
        yaml_patterns = [
            r"^\w+:\s+\w+",
            r"^\w+:\s*$",
            r"^\s+-\s+\w+",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in yaml_patterns):
            return "yaml"

        # Go 特征
        go_patterns = [
            r"^\s*package\s+\w+",
            r"^\s*func\s+\w+",
            r"^\s*import\s*\(",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in go_patterns):
            return "go"

        # Rust 特征
        rust_patterns = [
            r"^\s*fn\s+\w+",
            r"^\s*let\s+mut\s+",
            r"^\s*impl\s+",
            r"^\s*use\s+\w+::",
            r"#\[derive\(",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in rust_patterns):
            return "rust"

        # Java 特征
        java_patterns = [
            r"^\s*public\s+(class|interface|enum)\s+",
            r"^\s*private\s+\w+\s+\w+\(",
            r"System\.out\.print",
        ]
        if any(re.search(p, content, re.MULTILINE) for p in java_patterns):
            return "java"

        return None

    def _optimize_tables(self, lines: List[str]) -> List[str]:
        """
        优化表格对齐。

        确保表格单元格内容对齐，列宽一致。

        Args:
            lines: 文档行列表

        Returns:
            优化后的行列表
        """
        result: List[str] = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            # 检测表格行
            if "|" in line:
                # 收集连续的表格行
                table_lines: List[str] = []
                while i < n and "|" in lines[i]:
                    table_lines.append(lines[i])
                    i += 1

                # 优化表格
                optimized = self._align_table(table_lines)
                result.extend(optimized)
            else:
                result.append(line)
                i += 1

        return result

    def _align_table(self, table_lines: List[str]) -> List[str]:
        """
        对齐表格行。

        解析表格内容，计算列宽，重新对齐。

        Args:
            table_lines: 表格行列表

        Returns:
            对齐后的表格行列表
        """
        # 解析每行的单元格
        rows: List[List[str]] = []
        for line in table_lines:
            cells = self._parse_table_cells(line)
            rows.append(cells)

        if not rows:
            return table_lines

        # 计算每列最大宽度
        num_cols = max(len(row) for row in rows)
        col_widths: List[int] = [0] * num_cols

        for row in rows:
            for j, cell in enumerate(row):
                if j < num_cols and len(cell) > col_widths[j]:
                    col_widths[j] = len(cell)

        # 重新格式化每行
        result: List[str] = []
        for row in rows:
            cells = []
            for j in range(num_cols):
                cell = row[j] if j < len(row) else ""
                cells.append(cell.ljust(col_widths[j]))
            result.append("| " + " | ".join(cells) + " |")

        return result

    @staticmethod
    def _parse_table_cells(line: str) -> List[str]:
        """
        解析表格行的单元格。

        Args:
            line: 表格行文本

        Returns:
            单元格内容列表
        """
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [cell.strip() for cell in line.split("|")]

    def _normalize_links(self, lines: List[str]) -> List[str]:
        """
        统一链接格式。

        确保链接格式为 [text](url) 标准格式。

        Args:
            lines: 文档行列表

        Returns:
            规范化后的行列表
        """
        result: List[str] = []
        for line in lines:
            # 统一链接格式：确保URL前后没有多余空格
            line = re.sub(
                r"\[\s*([^\]]+?)\s*\]\(\s*([^)]+?)\s*\)",
                r"[\1](\2)",
                line
            )
            # 统一图片格式
            line = re.sub(
                r"!\[\s*([^\]]*?)\s*\]\(\s*([^)]+?)\s*\)",
                r"![\1](\2)",
                line
            )
            result.append(line)
        return result

    def _add_cjk_spaces(self, lines: List[str]) -> List[str]:
        """
        在中文与英文/数字之间自动添加空格。

        规则：
        - 中文后面紧跟英文字母/数字时，中间添加空格
        - 英文字母/数字后面紧跟中文时，中间添加空格
        - 不影响已有的空格
        - 不影响行内代码和链接中的内容

        Args:
            lines: 文档行列表

        Returns:
            添加空格后的行列表
        """
        result: List[str] = []
        for line in lines:
            # 跳过代码块标记行
            if line.strip().startswith("```"):
                result.append(line)
                continue

            # 跳过行内代码中的内容
            parts = self._split_by_inline_code(line)
            processed_parts = []
            for part_type, part_text in parts:
                if part_type == "code":
                    processed_parts.append(part_text)
                else:
                    processed_parts.append(self._insert_cjk_spaces(part_text))

            result.append("".join(processed_parts))
        return result

    def _split_by_inline_code(self, line: str) -> List[Tuple[str, str]]:
        """
        将行按行内代码分割。

        Args:
            line: 输入行

        Returns:
            (类型, 文本) 元组列表，类型为 "code" 或 "text"
        """
        parts: List[Tuple[str, str]] = []
        i = 0
        n = len(line)

        while i < n:
            if line[i] == '`':
                # 找到行内代码的结束
                j = line.find("`", i + 1)
                if j != -1:
                    parts.append(("code", line[i:j + 1]))
                    i = j + 1
                else:
                    parts.append(("text", line[i]))
                    i += 1
            else:
                # 收集普通文本
                j = i
                while j < n and line[j] != '`':
                    j += 1
                parts.append(("text", line[i:j]))
                i = j

        return parts

    @staticmethod
    def _insert_cjk_spaces(text: str) -> str:
        """
        在中文与英文/数字之间插入空格。

        Args:
            text: 输入文本

        Returns:
            处理后的文本
        """
        # 中文后跟英文/数字
        text = re.sub(
            r"([\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef])"
            r"([a-zA-Z0-9])",
            r"\1 \2",
            text
        )
        # 英文/数字后跟中文
        text = re.sub(
            r"([a-zA-Z0-9])"
            r"([\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef])",
            r"\1 \2",
            text
        )
        return text

    def _normalize_hr(self, lines: List[str]) -> List[str]:
        """
        规范化水平线格式。

        将各种水平线格式统一为 ---。

        Args:
            lines: 文档行列表

        Returns:
            规范化后的行列表
        """
        result: List[str] = []
        for line in lines:
            stripped = line.strip()
            if re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", stripped):
                result.append("---")
            else:
                result.append(line)
        return result
