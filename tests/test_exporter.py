"""
多格式导出测试模块。

测试MarkdownExporter的导出功能，包括HTML、JSON AST、纯文本格式导出。
"""

import json
import unittest

from markview_pro.exporter import MarkdownExporter


class TestMarkdownExporter(unittest.TestCase):
    """MarkdownExporter 测试用例。"""

    def setUp(self) -> None:
        """测试前初始化导出器。"""
        self.exporter = MarkdownExporter()

    # --------------------------------------------------------
    # HTML 导出测试
    # --------------------------------------------------------

    def test_export_html_basic(self) -> None:
        """测试基本HTML导出。"""
        result = self.exporter.export_to_html("# Hello World")
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<h1>", result)
        self.assertIn("Hello World", result)

    def test_export_html_with_paragraph(self) -> None:
        """测试段落HTML导出。"""
        result = self.exporter.export_to_html("A paragraph.")
        self.assertIn("<p>", result)
        self.assertIn("A paragraph.", result)

    def test_export_html_with_bold(self) -> None:
        """测试粗体HTML导出。"""
        result = self.exporter.export_to_html("**bold**")
        self.assertIn("<strong>", result)
        self.assertIn("bold", result)

    def test_export_html_with_link(self) -> None:
        """测试链接HTML导出。"""
        result = self.exporter.export_to_html("[Google](https://google.com)")
        self.assertIn('<a href="https://google.com">', result)
        self.assertIn("Google", result)

    def test_export_html_with_code_block(self) -> None:
        """测试代码块HTML导出。"""
        text = "```python\nprint('hi')\n```"
        result = self.exporter.export_to_html(text)
        self.assertIn("<pre>", result)
        self.assertIn("<code", result)

    def test_export_html_with_table(self) -> None:
        """测试表格HTML导出。"""
        text = "| A | B |\n| --- | --- |\n| 1 | 2 |"
        result = self.exporter.export_to_html(text)
        self.assertIn("<table>", result)
        self.assertIn("<th>", result)
        self.assertIn("<td>", result)

    def test_export_html_css(self) -> None:
        """测试HTML包含CSS样式。"""
        result = self.exporter.export_to_html("# Title")
        self.assertIn("<style>", result)
        self.assertIn("</style>", result)

    # --------------------------------------------------------
    # JSON AST 导出测试
    # --------------------------------------------------------

    def test_export_json_basic(self) -> None:
        """测试基本JSON AST导出。"""
        result = self.exporter.export_to_json("# Hello")
        parsed = json.loads(result)
        self.assertEqual(parsed["type"], "document")
        self.assertTrue(len(parsed["children"]) > 0)

    def test_export_json_heading(self) -> None:
        """测试JSON AST中标题节点。"""
        result = self.exporter.export_to_json("# Title")
        parsed = json.loads(result)
        heading = parsed["children"][0]
        self.assertEqual(heading["type"], "heading")
        self.assertEqual(heading["metadata"]["level"], 1)

    def test_export_json_valid_json(self) -> None:
        """测试JSON输出是有效的JSON。"""
        result = self.exporter.export_to_json("# Title\n\nParagraph.")
        # 不应抛出异常
        parsed = json.loads(result)
        self.assertIsInstance(parsed, dict)

    # --------------------------------------------------------
    # 纯文本导出测试
    # --------------------------------------------------------

    def test_export_text_basic(self) -> None:
        """测试基本纯文本导出。"""
        result = self.exporter.export_to_text("# Hello World")
        self.assertIn("Hello World", result)
        # 不应包含HTML标签
        self.assertNotIn("<h1>", result)

    def test_export_text_strip_bold(self) -> None:
        """测试纯文本导出去除粗体标记。"""
        result = self.exporter.export_to_text("**bold** text")
        self.assertIn("bold", result)
        self.assertNotIn("**", result)

    def test_export_text_strip_italic(self) -> None:
        """测试纯文本导出去除斜体标记。"""
        result = self.exporter.export_to_text("*italic* text")
        self.assertIn("italic", result)
        self.assertNotIn("*", result)

    # --------------------------------------------------------
    # export() 通用方法测试
    # --------------------------------------------------------

    def test_export_html_via_format(self) -> None:
        """测试通过export()方法导出HTML。"""
        result = self.exporter.export("# Title", "html")
        self.assertIn("<!DOCTYPE html>", result)

    def test_export_json_via_format(self) -> None:
        """测试通过export()方法导出JSON。"""
        result = self.exporter.export("# Title", "json")
        parsed = json.loads(result)
        self.assertIsInstance(parsed, dict)

    def test_export_text_via_format(self) -> None:
        """测试通过export()方法导出纯文本。"""
        result = self.exporter.export("# Title", "text")
        self.assertIn("Title", result)

    def test_export_invalid_format(self) -> None:
        """测试不支持的导出格式抛出异常。"""
        with self.assertRaises(ValueError):
            self.exporter.export("# Title", "xml")


if __name__ == "__main__":
    unittest.main()
