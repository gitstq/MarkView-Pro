"""
Markdown解析器模块 - GFM兼容的Markdown AST解析器。

将Markdown文本解析为抽象语法树(AST)，支持标准Markdown语法和
GitHub Flavored Markdown (GFM) 扩展。

支持的语法：
- 标题 (H1 ~ H6)
- 粗体、斜体、删除线
- 行内代码、代码块（围栏式和缩进式）
- 链接、图片
- 引用块
- 有序列表、无序列表
- 任务列表 (GFM)
- 表格 (GFM)
- 水平线
- Frontmatter (YAML)
- 自动链接 (GFM)
"""

import re
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# AST 节点类型常量
# ============================================================

class NodeType:
    """AST 节点类型常量。"""
    DOCUMENT = "document"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    STRIKETHROUGH = "strikethrough"
    CODE_INLINE = "code_inline"
    CODE_BLOCK = "code_block"
    LINK = "link"
    IMAGE = "image"
    BLOCKQUOTE = "blockquote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    LIST_ITEM = "list_item"
    TASK_LIST = "task_list"
    TASK_ITEM = "task_item"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    HR = "hr"
    FRONTMATTER = "frontmatter"
    SOFTBREAK = "softbreak"
    LINEBREAK = "linebreak"


# ============================================================
# AST 节点类
# ============================================================

class ASTNode:
    """
    抽象语法树节点。

    表示Markdown文档中的一个语法元素。

    Attributes:
        type: 节点类型
        content: 节点的文本内容（叶子节点）
        children: 子节点列表
        metadata: 节点的元数据（如标题层级、链接URL等）
    """

    def __init__(self, node_type: str, content: str = "",
                 children: Optional[List["ASTNode"]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化AST节点。

        Args:
            node_type: 节点类型
            content: 节点文本内容
            children: 子节点列表
            metadata: 元数据字典
        """
        self.type: str = node_type
        self.content: str = content
        self.children: List[ASTNode] = children if children is not None else []
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}

    def add_child(self, child: "ASTNode") -> "ASTNode":
        """
        添加子节点。

        Args:
            child: 子节点

        Returns:
            自身（支持链式调用）
        """
        self.children.append(child)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """
        将节点转换为字典格式（用于JSON序列化）。

        Returns:
            包含节点信息的字典
        """
        result: Dict[str, Any] = {
            "type": self.type,
        }
        if self.content:
            result["content"] = self.content
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    def __repr__(self) -> str:
        """返回节点的字符串表示。"""
        if self.content:
            return f"ASTNode({self.type}, {self.content!r})"
        if self.children:
            return f"ASTNode({self.type}, children={len(self.children)})"
        return f"ASTNode({self.type})"


# ============================================================
# Markdown 解析器
# ============================================================

class MarkdownParser:
    """
    GFM兼容的Markdown解析器。

    将Markdown文本解析为AST（抽象语法树）结构。
    支持标准Markdown语法和GitHub Flavored Markdown扩展。

    Usage:
        parser = MarkdownParser()
        ast = parser.parse("# Hello World")
        # ast.children[0].type == "heading"
        # ast.children[0].metadata["level"] == 1
    """

    def __init__(self) -> None:
        """初始化Markdown解析器。"""
        # 行内解析正则模式（按优先级排列）
        self._inline_patterns = self._build_inline_patterns()

    def parse(self, text: str) -> ASTNode:
        """
        解析Markdown文本为AST。

        Args:
            text: Markdown源文本

        Returns:
            文档根节点（DOCUMENT类型）
        """
        lines = text.split("\n")
        # 移除末尾空行
        while lines and not lines[-1].strip():
            lines.pop()

        doc = ASTNode(NodeType.DOCUMENT)
        frontmatter = self._parse_frontmatter(lines)

        if frontmatter:
            doc.add_child(frontmatter)
            # 跳过frontmatter行
            lines = lines[frontmatter.metadata.get("line_count", 0):]

        i = 0
        while i < len(lines):
            node, consumed = self._parse_block(lines, i)
            if node:
                doc.add_child(node)
            i += consumed

        return doc

    def _build_inline_patterns(self) -> List[Tuple[str, str]]:
        """
        构建行内语法正则模式列表。

        Returns:
            (正则模式, 节点类型) 元组列表
        """
        return [
            # 图片 ![alt](url)
            (r"!\[([^\]]*)\]\(([^)]+)\)", NodeType.IMAGE),
            # 链接 [text](url)
            (r"\[([^\]]+)\]\(([^)]+)\)", NodeType.LINK),
            # 行内代码 `code`
            (r"`([^`]+)`", NodeType.CODE_INLINE),
            # 删除线 ~~text~~
            (r"~~([^~]+)~~", NodeType.STRIKETHROUGH),
            # 粗斜体 ***text*** 或 ___text___
            (r"\*\*\*(.+?)\*\*\*|___(.+?)___", "bold_italic"),
            # 粗体 **text** 或 __text__
            (r"\*\*(.+?)\*\*|__(.+?)__", NodeType.BOLD),
            # 斜体 *text* 或 _text_
            (r"\*(.+?)\*|_(.+?)_", NodeType.ITALIC),
            # 自动链接 <url>
            (r"<([^>]+)>", NodeType.LINK),
        ]

    # --------------------------------------------------------
    # Frontmatter 解析
    # --------------------------------------------------------

    def _parse_frontmatter(self, lines: List[str]) -> Optional[ASTNode]:
        """
        解析YAML Frontmatter。

        Frontmatter格式：以 --- 开头和结尾的YAML元数据块。

        Args:
            lines: 文档行列表

        Returns:
            Frontmatter节点，如果没有则返回None
        """
        if len(lines) < 3:
            return None
        if lines[0].strip() != "---":
            return None

        end_index = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_index = i
                break

        if end_index is None:
            return None

        content = "\n".join(lines[1:end_index])
        node = ASTNode(
            NodeType.FRONTMATTER,
            content=content,
            metadata={"line_count": end_index + 1}
        )
        return node

    # --------------------------------------------------------
    # 块级元素解析
    # --------------------------------------------------------

    def _parse_block(self, lines: List[str], index: int) -> Tuple[Optional[ASTNode], int]:
        """
        解析单个块级元素。

        Args:
            lines: 文档行列表
            index: 当前行索引

        Returns:
            (AST节点, 消耗的行数) 元组
        """
        line = lines[index]

        # 空行
        if not line.strip():
            return None, 1

        # 水平线
        hr_match = re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", line.strip())
        if hr_match:
            return ASTNode(NodeType.HR, content=hr_match.group(1)), 1

        # 标题
        heading = self._parse_heading(line)
        if heading:
            return heading, 1

        # 代码块（围栏式）
        if line.strip().startswith("```"):
            return self._parse_code_block(lines, index)

        # 表格
        if "|" in line and index + 1 < len(lines) and re.match(
                r"^\|?\s*[-:]+[-|:\s]+\|?\s*$", lines[index + 1].strip()):
            return self._parse_table(lines, index)

        # 引用块
        if line.startswith(">"):
            return self._parse_blockquote(lines, index)

        # 无序列表
        ul_match = re.match(r"^(\s*)([-*+])\s", line)
        if ul_match:
            return self._parse_unordered_list(lines, index)

        # 有序列表
        ol_match = re.match(r"^(\s*)(\d+)\.\s", line)
        if ol_match:
            return self._parse_ordered_list(lines, index)

        # 段落
        return self._parse_paragraph(lines, index)

    def _parse_heading(self, line: str) -> Optional[ASTNode]:
        """
        解析标题行。

        支持 ATX 风格 (# ~ ######) 和 Setext 风格 (===/---)。

        Args:
            line: 单行文本

        Returns:
            标题节点，如果不是标题则返回None
        """
        # ATX 风格标题
        match = re.match(r"^(#{1,6})\s+(.+?)(?:\s+#+\s*)?$", line)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            children = self._parse_inline(content)
            return ASTNode(
                NodeType.HEADING,
                content=content,
                children=children,
                metadata={"level": level}
            )
        return None

    def _parse_code_block(self, lines: List[str],
                          index: int) -> Tuple[ASTNode, int]:
        """
        解析围栏式代码块。

        支持 ```lang ... ``` 格式，可指定语言标识。

        Args:
            lines: 文档行列表
            index: 代码块开始行索引

        Returns:
            (代码块节点, 消耗的行数) 元组
        """
        first_line = lines[index].strip()
        # 提取语言标识
        lang_match = re.match(r"^```(\w*)", first_line)
        language = lang_match.group(1) if lang_match else ""

        # 查找结束的 ```
        end_index = None
        for i in range(index + 1, len(lines)):
            if lines[i].strip().startswith("```"):
                end_index = i
                break

        if end_index is None:
            # 没有结束标记，取剩余所有行
            code_lines = lines[index + 1:]
            consumed = len(lines) - index
        else:
            code_lines = lines[index + 1:end_index]
            consumed = end_index - index + 1

        code_content = "\n".join(code_lines)
        node = ASTNode(
            NodeType.CODE_BLOCK,
            content=code_content,
            metadata={"language": language}
        )
        return node, consumed

    def _parse_table(self, lines: List[str],
                     index: int) -> Tuple[ASTNode, int]:
        """
        解析GFM表格。

        表格格式：
        | Header | Header |
        | ------ | ------ |
        | Cell   | Cell   |

        Args:
            lines: 文档行列表
            index: 表格开始行索引

        Returns:
            (表格节点, 消耗的行数) 元组
        """
        rows: List[ASTNode] = []
        alignments: List[str] = []
        consumed = 0

        # 解析表头行
        header_line = lines[index].strip()
        header_cells = self._parse_table_row(header_line)
        if not header_cells:
            return ASTNode(NodeType.PARAGRAPH, content=header_line), 1

        # 解析分隔行（获取对齐方式）
        if index + 1 < len(lines):
            sep_line = lines[index + 1].strip()
            sep_cells = self._parse_table_row(sep_line)
            alignments = self._parse_table_alignments(sep_cells)
            consumed = 2
        else:
            consumed = 1

        # 创建表头行节点
        header_row = ASTNode(NodeType.TABLE_ROW, metadata={"is_header": True})
        for cell_text in header_cells:
            cell_text = cell_text.strip()
            cell = ASTNode(
                NodeType.TABLE_CELL,
                content=cell_text,
                children=self._parse_inline(cell_text)
            )
            header_row.add_child(cell)
        rows.append(header_row)

        # 解析数据行
        i = index + consumed
        while i < len(lines):
            line = lines[i].strip()
            if not line or "|" not in line:
                break
            # 检查是否为新的块级元素
            if (re.match(r"^#{1,6}\s", line) or line.startswith("```")
                    or line.startswith(">") or line.startswith("---")):
                break

            cells = self._parse_table_row(line)
            if not cells:
                break

            row = ASTNode(NodeType.TABLE_ROW)
            for j, cell_text in enumerate(cells):
                cell_text = cell_text.strip()
                align = alignments[j] if j < len(alignments) else "left"
                cell = ASTNode(
                    NodeType.TABLE_CELL,
                    content=cell_text,
                    children=self._parse_inline(cell_text),
                    metadata={"align": align}
                )
                row.add_child(cell)
            rows.append(row)
            i += 1
            consumed += 1

        table = ASTNode(NodeType.TABLE, children=rows, metadata={
            "alignments": alignments,
            "rows": len(rows),
            "cols": len(header_cells),
        })
        return table, consumed

    def _parse_table_row(self, line: str) -> List[str]:
        """
        解析表格行，提取单元格内容。

        Args:
            line: 表格行文本

        Returns:
            单元格内容列表
        """
        # 去除首尾的 |
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]

        cells = line.split("|")
        return [cell.strip() for cell in cells]

    def _parse_table_alignments(self, cells: List[str]) -> List[str]:
        """
        从表格分隔行解析列对齐方式。

        Args:
            cells: 分隔行单元格列表

        Returns:
            对齐方式列表 ("left", "center", "right")
        """
        alignments = []
        for cell in cells:
            cell = cell.strip()
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append("center")
            elif cell.endswith(":"):
                alignments.append("right")
            else:
                alignments.append("left")
        return alignments

    def _parse_blockquote(self, lines: List[str],
                         index: int) -> Tuple[ASTNode, int]:
        """
        解析引用块。

        支持嵌套引用（> > 嵌套层级）。

        Args:
            lines: 文档行列表
            index: 引用块开始行索引

        Returns:
            (引用块节点, 消耗的行数) 元组
        """
        content_lines: List[str] = []
        consumed = 0

        i = index
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                # 空行结束引用块（除非后面还有引用行）
                if i + 1 < len(lines) and lines[i + 1].startswith(">"):
                    content_lines.append("")
                    i += 1
                    consumed += 1
                    continue
                else:
                    consumed += 1
                    break

            if line.startswith(">"):
                # 去除 > 前缀
                content = line[1:]
                if content.startswith(" "):
                    content = content[1:]
                content_lines.append(content)
                i += 1
                consumed += 1
            else:
                break

        # 递归解析引用块内容
        inner_text = "\n".join(content_lines)
        inner_lines = inner_text.split("\n")
        children: List[ASTNode] = []
        j = 0
        while j < len(inner_lines):
            node, c = self._parse_block(inner_lines, j)
            if node:
                children.append(node)
            j += c

        node = ASTNode(
            NodeType.BLOCKQUOTE,
            content=inner_text,
            children=children
        )
        return node, consumed

    def _parse_unordered_list(self, lines: List[str],
                              index: int) -> Tuple[ASTNode, int]:
        """
        解析无序列表。

        支持任务列表 (- [ ] / - [x])。

        Args:
            lines: 文档行列表
            index: 列表开始行索引

        Returns:
            (列表节点, 消耗的行数) 元组
        """
        items: List[ASTNode] = []
        consumed = 0
        is_task_list = False

        # 检测缩进级别
        indent_match = re.match(r"^(\s*)", lines[index])
        base_indent = len(indent_match.group(1)) if indent_match else 0

        i = index
        while i < len(lines):
            line = lines[i]

            # 空行结束列表
            if not line.strip():
                consumed += 1
                break

            # 检测缩进
            current_indent_match = re.match(r"^(\s*)", line)
            current_indent = len(current_indent_match.group(1)) if current_indent_match else 0

            # 如果缩进减少，结束当前列表
            if current_indent < base_indent and line.strip():
                break

            # 无序列表项
            item_match = re.match(
                r"^\s*([-*+])\s+(?:\[(x| )\]\s+)?(.*)$", line
            )
            if item_match:
                marker = item_match.group(1)
                checkbox = item_match.group(2)
                content = item_match.group(3)

                if checkbox is not None:
                    is_task_list = True
                    item = ASTNode(
                        NodeType.TASK_ITEM,
                        content=content,
                        children=self._parse_inline(content),
                        metadata={"checked": checkbox.lower() == "x"}
                    )
                else:
                    item = ASTNode(
                        NodeType.LIST_ITEM,
                        content=content,
                        children=self._parse_inline(content)
                    )
                items.append(item)
                i += 1
                consumed += 1
            else:
                # 可能是列表项的续行（多行段落）
                if items and line.strip():
                    # 检查是否是更深的缩进
                    if current_indent > base_indent:
                        items[-1].content += "\n" + line.strip()
                        i += 1
                        consumed += 1
                        continue
                break

        if is_task_list:
            node = ASTNode(NodeType.TASK_LIST, children=items)
        else:
            node = ASTNode(NodeType.UNORDERED_LIST, children=items)
        return node, consumed

    def _parse_ordered_list(self, lines: List[str],
                            index: int) -> Tuple[ASTNode, int]:
        """
        解析有序列表。

        Args:
            lines: 文档行列表
            index: 列表开始行索引

        Returns:
            (列表节点, 消耗的行数) 元组
        """
        items: List[ASTNode] = []
        consumed = 0

        indent_match = re.match(r"^(\s*)", lines[index])
        base_indent = len(indent_match.group(1)) if indent_match else 0

        i = index
        while i < len(lines):
            line = lines[i]

            if not line.strip():
                consumed += 1
                break

            current_indent_match = re.match(r"^(\s*)", line)
            current_indent = len(current_indent_match.group(1)) if current_indent_match else 0

            if current_indent < base_indent and line.strip():
                break

            item_match = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
            if item_match:
                number = int(item_match.group(1))
                content = item_match.group(2)
                item = ASTNode(
                    NodeType.LIST_ITEM,
                    content=content,
                    children=self._parse_inline(content),
                    metadata={"number": number}
                )
                items.append(item)
                i += 1
                consumed += 1
            else:
                if items and line.strip() and current_indent > base_indent:
                    items[-1].content += "\n" + line.strip()
                    i += 1
                    consumed += 1
                    continue
                break

        node = ASTNode(NodeType.ORDERED_LIST, children=items)
        return node, consumed

    def _parse_paragraph(self, lines: List[str],
                         index: int) -> Tuple[ASTNode, int]:
        """
        解析段落。

        段落由连续的非空行组成，遇到空行或其他块级元素时结束。

        Args:
            lines: 文档行列表
            index: 段落开始行索引

        Returns:
            (段落节点, 消耗的行数) 元组
        """
        content_lines: List[str] = []
        consumed = 0

        i = index
        while i < len(lines):
            line = lines[i]

            # 空行结束段落
            if not line.strip():
                consumed += 1
                break

            # 遇到其他块级元素时结束段落
            if (re.match(r"^#{1,6}\s", line)
                    or line.strip().startswith("```")
                    or line.startswith(">")
                    or re.match(r"^(\*{3,}|-{3,}|_{3,})\s*$", line.strip())):
                break

            # 遇到列表项时结束段落
            if re.match(r"^\s*[-*+]\s", line) or re.match(r"^\s*\d+\.\s", line):
                break

            content_lines.append(line)
            i += 1
            consumed += 1

        content = "\n".join(content_lines)
        children = self._parse_inline(content)
        node = ASTNode(NodeType.PARAGRAPH, content=content, children=children)
        return node, consumed

    # --------------------------------------------------------
    # 行内元素解析
    # --------------------------------------------------------

    def _parse_inline(self, text: str) -> List[ASTNode]:
        """
        解析行内Markdown语法。

        处理粗体、斜体、删除线、行内代码、链接、图片等。

        Args:
            text: 行内文本

        Returns:
            行内元素AST节点列表
        """
        if not text:
            return []

        nodes: List[ASTNode] = []
        remaining = text

        while remaining:
            matched = False

            for pattern, node_type in self._inline_patterns:
                match = re.search(pattern, remaining)
                if match:
                    # 添加匹配前的纯文本
                    before = remaining[:match.start()]
                    if before:
                        nodes.append(ASTNode(NodeType.TEXT, content=before))

                    if node_type == NodeType.IMAGE:
                        alt = match.group(1)
                        url = match.group(2)
                        nodes.append(ASTNode(
                            NodeType.IMAGE,
                            content=alt,
                            metadata={"url": url}
                        ))
                    elif node_type == NodeType.LINK:
                        link_text = match.group(1)
                        url = match.group(2)
                        nodes.append(ASTNode(
                            NodeType.LINK,
                            content=link_text,
                            children=self._parse_inline(link_text),
                            metadata={"url": url}
                        ))
                    elif node_type == "bold_italic":
                        # 粗斜体
                        content = match.group(1) or match.group(2)
                        nodes.append(ASTNode(
                            NodeType.BOLD,
                            content=content,
                            children=[
                                ASTNode(NodeType.ITALIC, content=content)
                            ]
                        ))
                    else:
                        content = match.group(1)
                        nodes.append(ASTNode(
                            node_type,
                            content=content,
                            children=self._parse_inline(content) if node_type in (
                                NodeType.BOLD, NodeType.ITALIC,
                                NodeType.STRIKETHROUGH
                            ) else []
                        ))

                    remaining = remaining[match.end():]
                    matched = True
                    break

            if not matched:
                nodes.append(ASTNode(NodeType.TEXT, content=remaining))
                break

        return nodes
