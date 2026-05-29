"""
Markdown解析器测试模块。

测试MarkdownParser的解析功能，包括标题、段落、代码块、
列表、表格、引用等语法元素的解析。
"""

import unittest

from markview_pro.parser import MarkdownParser, ASTNode, NodeType


class TestMarkdownParser(unittest.TestCase):
    """MarkdownParser 测试用例。"""

    def setUp(self) -> None:
        """测试前初始化解析器。"""
        self.parser = MarkdownParser()

    # --------------------------------------------------------
    # 标题解析测试
    # --------------------------------------------------------

    def test_parse_h1(self) -> None:
        """测试H1标题解析。"""
        ast = self.parser.parse("# Hello World")
        self.assertEqual(len(ast.children), 1)
        heading = ast.children[0]
        self.assertEqual(heading.type, NodeType.HEADING)
        self.assertEqual(heading.metadata["level"], 1)
        self.assertEqual(heading.content, "Hello World")

    def test_parse_h2_to_h6(self) -> None:
        """测试H2-H6标题解析。"""
        for level in range(2, 7):
            prefix = "#" * level
            text = f"{prefix} Title {level}"
            ast = self.parser.parse(text)
            heading = ast.children[0]
            self.assertEqual(heading.type, NodeType.HEADING)
            self.assertEqual(heading.metadata["level"], level)

    def test_parse_heading_with_inline_formatting(self) -> None:
        """测试包含行内格式的标题。"""
        ast = self.parser.parse("# **Bold** and *Italic*")
        heading = ast.children[0]
        self.assertEqual(heading.type, NodeType.HEADING)
        self.assertTrue(len(heading.children) > 0)

    # --------------------------------------------------------
    # 段落解析测试
    # --------------------------------------------------------

    def test_parse_paragraph(self) -> None:
        """测试段落解析。"""
        ast = self.parser.parse("This is a paragraph.")
        self.assertEqual(len(ast.children), 1)
        para = ast.children[0]
        self.assertEqual(para.type, NodeType.PARAGRAPH)
        self.assertEqual(para.content, "This is a paragraph.")

    def test_parse_multiple_paragraphs(self) -> None:
        """测试多段落解析。"""
        text = "First paragraph.\n\nSecond paragraph."
        ast = self.parser.parse(text)
        self.assertEqual(len(ast.children), 2)
        self.assertEqual(ast.children[0].type, NodeType.PARAGRAPH)
        self.assertEqual(ast.children[1].type, NodeType.PARAGRAPH)

    def test_parse_inline_bold(self) -> None:
        """测试粗体解析。"""
        ast = self.parser.parse("This is **bold** text.")
        para = ast.children[0]
        self.assertEqual(para.type, NodeType.PARAGRAPH)
        self.assertTrue(any(c.type == NodeType.BOLD for c in para.children))

    def test_parse_inline_italic(self) -> None:
        """测试斜体解析。"""
        ast = self.parser.parse("This is *italic* text.")
        para = ast.children[0]
        self.assertTrue(any(c.type == NodeType.ITALIC for c in para.children))

    def test_parse_inline_code(self) -> None:
        """测试行内代码解析。"""
        ast = self.parser.parse("Use `print()` function.")
        para = ast.children[0]
        self.assertTrue(any(c.type == NodeType.CODE_INLINE for c in para.children))

    # --------------------------------------------------------
    # 代码块解析测试
    # --------------------------------------------------------

    def test_parse_code_block_with_language(self) -> None:
        """测试带语言标识的代码块解析。"""
        text = '```python\nprint("hello")\n```'
        ast = self.parser.parse(text)
        self.assertEqual(len(ast.children), 1)
        code = ast.children[0]
        self.assertEqual(code.type, NodeType.CODE_BLOCK)
        self.assertEqual(code.metadata["language"], "python")
        self.assertEqual(code.content, 'print("hello")')

    def test_parse_code_block_without_language(self) -> None:
        """测试无语言标识的代码块解析。"""
        text = "```\nsome code\n```"
        ast = self.parser.parse(text)
        code = ast.children[0]
        self.assertEqual(code.type, NodeType.CODE_BLOCK)
        self.assertEqual(code.metadata["language"], "")

    def test_parse_code_block_multiline(self) -> None:
        """测试多行代码块解析。"""
        text = "```python\ndef hello():\n    print('hi')\n```"
        ast = self.parser.parse(text)
        code = ast.children[0]
        self.assertIn("def hello():", code.content)
        self.assertIn("    print('hi')", code.content)

    # --------------------------------------------------------
    # 列表解析测试
    # --------------------------------------------------------

    def test_parse_unordered_list(self) -> None:
        """测试无序列表解析。"""
        text = "- item 1\n- item 2\n- item 3"
        ast = self.parser.parse(text)
        self.assertEqual(len(ast.children), 1)
        ul = ast.children[0]
        self.assertEqual(ul.type, NodeType.UNORDERED_LIST)
        self.assertEqual(len(ul.children), 3)

    def test_parse_ordered_list(self) -> None:
        """测试有序列表解析。"""
        text = "1. first\n2. second\n3. third"
        ast = self.parser.parse(text)
        ol = ast.children[0]
        self.assertEqual(ol.type, NodeType.ORDERED_LIST)
        self.assertEqual(len(ol.children), 3)

    def test_parse_task_list(self) -> None:
        """测试任务列表解析。"""
        text = "- [x] done\n- [ ] todo"
        ast = self.parser.parse(text)
        task_list = ast.children[0]
        self.assertEqual(task_list.type, NodeType.TASK_LIST)
        self.assertTrue(task_list.children[0].metadata["checked"])
        self.assertFalse(task_list.children[1].metadata["checked"])

    # --------------------------------------------------------
    # 链接和图片解析测试
    # --------------------------------------------------------

    def test_parse_link(self) -> None:
        """测试链接解析。"""
        ast = self.parser.parse("Visit [Google](https://google.com)")
        para = ast.children[0]
        link = next(c for c in para.children if c.type == NodeType.LINK)
        self.assertEqual(link.content, "Google")
        self.assertEqual(link.metadata["url"], "https://google.com")

    def test_parse_image(self) -> None:
        """测试图片解析。"""
        ast = self.parser.parse("![Alt text](image.png)")
        para = ast.children[0]
        img = next(c for c in para.children if c.type == NodeType.IMAGE)
        self.assertEqual(img.content, "Alt text")
        self.assertEqual(img.metadata["url"], "image.png")

    # --------------------------------------------------------
    # 引用块解析测试
    # --------------------------------------------------------

    def test_parse_blockquote(self) -> None:
        """测试引用块解析。"""
        text = "> This is a quote.\n> Second line."
        ast = self.parser.parse(text)
        bq = ast.children[0]
        self.assertEqual(bq.type, NodeType.BLOCKQUOTE)

    # --------------------------------------------------------
    # 表格解析测试
    # --------------------------------------------------------

    def test_parse_table(self) -> None:
        """测试表格解析。"""
        text = "| Name | Age |\n| --- | --- |\n| Alice | 30 |"
        ast = self.parser.parse(text)
        table = ast.children[0]
        self.assertEqual(table.type, NodeType.TABLE)
        self.assertEqual(len(table.children), 2)  # header + data

    def test_parse_table_with_alignment(self) -> None:
        """测试表格对齐解析。"""
        text = "| Left | Center | Right |\n| :--- | :---: | ---: |"
        ast = self.parser.parse(text)
        table = ast.children[0]
        alignments = table.metadata.get("alignments", [])
        self.assertEqual(alignments[0], "left")
        self.assertEqual(alignments[1], "center")
        self.assertEqual(alignments[2], "right")

    # --------------------------------------------------------
    # 水平线解析测试
    # --------------------------------------------------------

    def test_parse_hr(self) -> None:
        """测试水平线解析。"""
        for hr_text in ["---", "***", "___"]:
            ast = self.parser.parse(hr_text)
            self.assertEqual(ast.children[0].type, NodeType.HR)

    # --------------------------------------------------------
    # Frontmatter 解析测试
    # --------------------------------------------------------

    def test_parse_frontmatter(self) -> None:
        """测试Frontmatter解析。"""
        text = "---\ntitle: Test\ndate: 2024-01-01\n---\n\n# Hello"
        ast = self.parser.parse(text)
        self.assertEqual(ast.children[0].type, NodeType.FRONTMATTER)
        self.assertIn("title: Test", ast.children[0].content)

    # --------------------------------------------------------
    # 删除线解析测试
    # --------------------------------------------------------

    def test_parse_strikethrough(self) -> None:
        """测试删除线解析。"""
        ast = self.parser.parse("This is ~~deleted~~ text.")
        para = ast.children[0]
        self.assertTrue(any(c.type == NodeType.STRIKETHROUGH for c in para.children))

    # --------------------------------------------------------
    # AST to_dict 测试
    # --------------------------------------------------------

    def test_ast_to_dict(self) -> None:
        """测试AST节点序列化为字典。"""
        node = ASTNode(NodeType.HEADING, content="Test",
                        metadata={"level": 1})
        d = node.to_dict()
        self.assertEqual(d["type"], "heading")
        self.assertEqual(d["content"], "Test")
        self.assertEqual(d["metadata"]["level"], 1)


if __name__ == "__main__":
    unittest.main()
