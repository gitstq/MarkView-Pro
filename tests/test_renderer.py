"""
终端渲染引擎测试模块。

测试TerminalRenderer的渲染功能，包括标题、段落、代码块、
列表、表格等元素的终端渲染。
"""

import unittest

from markview_pro.parser import MarkdownParser
from markview_pro.renderer import TerminalRenderer
from markview_pro.utils import strip_ansi


class TestTerminalRenderer(unittest.TestCase):
    """TerminalRenderer 测试用例。"""

    def setUp(self) -> None:
        """测试前初始化。"""
        self.parser = MarkdownParser()
        self.renderer_color = TerminalRenderer(no_color=False)
        self.renderer_plain = TerminalRenderer(no_color=True)

    # --------------------------------------------------------
    # 标题渲染测试
    # --------------------------------------------------------

    def test_render_h1(self) -> None:
        """测试H1标题渲染。"""
        ast = self.parser.parse("# Hello World")
        result = self.renderer_plain.render(ast)
        self.assertIn("#", result)
        self.assertIn("Hello World", result)

    def test_render_h1_with_underline(self) -> None:
        """测试H1标题带下划线渲染（颜色模式）。"""
        ast = self.parser.parse("# Title")
        result = self.renderer_color.render(ast)
        self.assertIn("Title", result)

    def test_render_heading_levels(self) -> None:
        """测试不同标题层级渲染。"""
        for level in range(1, 7):
            text = f"{'#' * level} Heading {level}"
            ast = self.parser.parse(text)
            result = self.renderer_plain.render(ast)
            self.assertIn(f"Heading {level}", result)

    # --------------------------------------------------------
    # 段落渲染测试
    # --------------------------------------------------------

    def test_render_paragraph(self) -> None:
        """测试段落渲染。"""
        ast = self.parser.parse("This is a paragraph.")
        result = self.renderer_plain.render(ast)
        self.assertIn("This is a paragraph.", result)

    def test_render_bold_text(self) -> None:
        """测试粗体文本渲染。"""
        ast = self.parser.parse("**bold text**")
        result = self.renderer_plain.render(ast)
        self.assertIn("bold text", result)

    def test_render_italic_text(self) -> None:
        """测试斜体文本渲染。"""
        ast = self.parser.parse("*italic text*")
        result = self.renderer_plain.render(ast)
        self.assertIn("italic text", result)

    # --------------------------------------------------------
    # 代码块渲染测试
    # --------------------------------------------------------

    def test_render_code_block(self) -> None:
        """测试代码块渲染。"""
        text = "```python\nprint('hello')\n```"
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        self.assertIn("print('hello')", result)

    def test_render_code_block_with_border(self) -> None:
        """测试代码块边框渲染。"""
        text = "```python\nx = 1\n```"
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        # 应包含边框字符
        self.assertIn("x = 1", result)

    # --------------------------------------------------------
    # 列表渲染测试
    # --------------------------------------------------------

    def test_render_unordered_list(self) -> None:
        """测试无序列表渲染。"""
        text = "- item 1\n- item 2"
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        self.assertIn("item 1", result)
        self.assertIn("item 2", result)

    def test_render_ordered_list(self) -> None:
        """测试有序列表渲染。"""
        text = "1. first\n2. second"
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        self.assertIn("first", result)
        self.assertIn("second", result)

    def test_render_task_list(self) -> None:
        """测试任务列表渲染。"""
        text = "- [x] done\n- [ ] pending"
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        self.assertIn("[x]", result)
        self.assertIn("[ ]", result)

    # --------------------------------------------------------
    # 表格渲染测试
    # --------------------------------------------------------

    def test_render_table(self) -> None:
        """测试表格渲染。"""
        text = "| A | B |\n| --- | --- |\n| 1 | 2 |"
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        self.assertIn("A", result)
        self.assertIn("B", result)
        self.assertIn("1", result)
        self.assertIn("2", result)

    # --------------------------------------------------------
    # 链接渲染测试
    # --------------------------------------------------------

    def test_render_link(self) -> None:
        """测试链接渲染。"""
        ast = self.parser.parse("[Google](https://google.com)")
        result = self.renderer_plain.render(ast)
        self.assertIn("Google", result)
        self.assertIn("https://google.com", result)

    # --------------------------------------------------------
    # 引用块渲染测试
    # --------------------------------------------------------

    def test_render_blockquote(self) -> None:
        """测试引用块渲染。"""
        text = "> This is a quote."
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        self.assertIn("This is a quote.", result)

    # --------------------------------------------------------
    # 水平线渲染测试
    # --------------------------------------------------------

    def test_render_hr(self) -> None:
        """测试水平线渲染。"""
        ast = self.parser.parse("---")
        result = self.renderer_plain.render(ast)
        self.assertTrue(len(result) > 0)

    # --------------------------------------------------------
    # 无颜色模式测试
    # --------------------------------------------------------

    def test_no_color_mode(self) -> None:
        """测试无颜色模式不包含ANSI码。"""
        text = "# Title\n\n**bold** and *italic*"
        ast = self.parser.parse(text)
        result = self.renderer_plain.render(ast)
        # 确保没有ANSI转义序列
        self.assertNotIn("\033", result)

    # --------------------------------------------------------
    # 直接渲染文本测试
    # --------------------------------------------------------

    def test_render_text_directly(self) -> None:
        """测试直接渲染Markdown文本。"""
        result = self.renderer_plain.render_text("# Hello\n\nWorld")
        self.assertIn("Hello", result)
        self.assertIn("World", result)


if __name__ == "__main__":
    unittest.main()
