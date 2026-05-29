"""
智能格式化引擎测试模块。

测试MarkdownFormatter的格式化功能，包括标题空行规范化、
列表缩进统一、代码块语言标识补全、行尾空白清理等。
"""

import unittest

from markview_pro.formatter import MarkdownFormatter


class TestMarkdownFormatter(unittest.TestCase):
    """MarkdownFormatter 测试用例。"""

    def setUp(self) -> None:
        """测试前初始化格式化器。"""
        self.formatter = MarkdownFormatter()

    # --------------------------------------------------------
    # 行尾空白清理测试
    # --------------------------------------------------------

    def test_clean_trailing_whitespace(self) -> None:
        """测试行尾空白清理。"""
        text = "Hello   \nWorld   \n"
        result = self.formatter.format(text)
        self.assertNotIn("   \n", result)

    def test_clean_trailing_tabs(self) -> None:
        """测试行尾制表符清理。"""
        text = "line1\t\nline2\t\t\n"
        result = self.formatter.format(text)
        lines = result.split("\n")
        for line in lines:
            self.assertEqual(line, line.rstrip())

    # --------------------------------------------------------
    # 连续空行合并测试
    # --------------------------------------------------------

    def test_merge_blank_lines(self) -> None:
        """测试连续空行合并。"""
        text = "Hello\n\n\n\nWorld"
        result = self.formatter.format(text)
        # 最多保留一个空行
        parts = result.split("\n\n")
        for part in parts:
            self.assertNotIn("\n\n\n", part)

    def test_no_excessive_blank_lines(self) -> None:
        """测试格式化后不存在三个以上连续空行。"""
        text = "A\n\n\n\n\n\nB"
        result = self.formatter.format(text)
        self.assertNotIn("\n\n\n", result)

    # --------------------------------------------------------
    # 标题空行规范化测试
    # --------------------------------------------------------

    def test_heading_spacing_before(self) -> None:
        """测试标题前添加空行。"""
        text = "Some text\n# Title"
        result = self.formatter.format(text)
        self.assertIn("\n# Title", result)

    def test_heading_spacing_after(self) -> None:
        """测试标题后添加空行。"""
        text = "# Title\nSome text"
        result = self.formatter.format(text)
        self.assertIn("# Title\n\n", result)

    def test_first_heading_no_blank_before(self) -> None:
        """测试文档第一个标题前不需要空行。"""
        text = "# Title\n\nContent"
        result = self.formatter.format(text)
        self.assertTrue(result.startswith("# Title"))

    # --------------------------------------------------------
    # 代码块语言标识补全测试
    # --------------------------------------------------------

    def test_detect_python_language(self) -> None:
        """测试Python语言检测。"""
        code_lines = [
            "def hello():",
            "    print('world')",
        ]
        lang = self.formatter._detect_language(code_lines)
        self.assertEqual(lang, "python")

    def test_detect_javascript_language(self) -> None:
        """测试JavaScript语言检测。"""
        code_lines = [
            "const x = 10;",
            "console.log(x);",
        ]
        lang = self.formatter._detect_language(code_lines)
        self.assertEqual(lang, "javascript")

    def test_code_block_language_added(self) -> None:
        """测试代码块自动添加语言标识。"""
        text = "```\ndef foo():\n    pass\n```"
        result = self.formatter.format(text)
        self.assertIn("```python", result)

    # --------------------------------------------------------
    # 水平线规范化测试
    # --------------------------------------------------------

    def test_normalize_hr_asterisks(self) -> None:
        """测试星号水平线规范化为短横线。"""
        text = "text\n***\nmore text"
        result = self.formatter.format(text)
        self.assertIn("---", result)
        self.assertNotIn("***", result)

    def test_normalize_hr_underscores(self) -> None:
        """测试下划线水平线规范化为短横线。"""
        text = "text\n___\nmore text"
        result = self.formatter.format(text)
        self.assertIn("---", result)

    # --------------------------------------------------------
    # 链接格式统一测试
    # --------------------------------------------------------

    def test_normalize_link_spaces(self) -> None:
        """测试链接格式统一（去除多余空格）。"""
        text = "[ text ]( url )"
        result = self.formatter.format(text)
        self.assertIn("[text](url)", result)

    # --------------------------------------------------------
    # 中英文空格测试
    # --------------------------------------------------------

    def test_cjk_spaces_enabled(self) -> None:
        """测试中英文空格功能。"""
        formatter = MarkdownFormatter(add_cjk_spaces=True)
        text = "使用Python编程"
        result = formatter.format(text)
        self.assertIn("使用 Python 编程", result)

    def test_cjk_spaces_disabled(self) -> None:
        """测试中英文空格功能禁用。"""
        text = "使用Python编程"
        result = self.formatter.format(text)
        self.assertIn("使用Python编程", result)

    # --------------------------------------------------------
    # 末尾换行测试
    # --------------------------------------------------------

    def test_trailing_newline(self) -> None:
        """测试确保末尾有换行符。"""
        text = "Hello World"
        result = self.formatter.format(text)
        self.assertTrue(result.endswith("\n"))

    # --------------------------------------------------------
    # 综合格式化测试
    # --------------------------------------------------------

    def test_complex_formatting(self) -> None:
        """测试综合格式化场景。"""
        text = "Hello   \n\n\n\n#Title\nSome text\n***\nmore"
        result = self.formatter.format(text)
        # 行尾空白已清理
        self.assertNotIn("   \n", result)
        # 连续空行已合并
        self.assertNotIn("\n\n\n", result)
        # 水平线已规范化
        self.assertIn("---", result)


if __name__ == "__main__":
    unittest.main()
