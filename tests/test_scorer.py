"""
Markdown质量评分引擎测试模块。

测试MarkdownScorer的评分功能，包括结构完整性、可读性、
规范度三个维度的评分。
"""

import unittest

from markview_pro.scorer import MarkdownScorer


class TestMarkdownScorer(unittest.TestCase):
    """MarkdownScorer 测试用例。"""

    def setUp(self) -> None:
        """测试前初始化评分器。"""
        self.scorer = MarkdownScorer()

    # --------------------------------------------------------
    # 综合评分测试
    # --------------------------------------------------------

    def test_score_returns_dict(self) -> None:
        """测试评分返回字典格式。"""
        result = self.scorer.score("# Hello")
        self.assertIn("overall", result)
        self.assertIn("structure", result)
        self.assertIn("readability", result)
        self.assertIn("standardization", result)
        self.assertIn("grade", result)

    def test_score_range(self) -> None:
        """测试评分在0-100范围内。"""
        result = self.scorer.score("# Title\n\nSome content.")
        self.assertGreaterEqual(result["overall"], 0)
        self.assertLessEqual(result["overall"], 100)

    def test_grade_assignment(self) -> None:
        """测试等级分配。"""
        # 简单文档应该有等级
        result = self.scorer.score("# Title\n\nContent here.\n\n- item 1\n- item 2")
        self.assertIn(result["grade"], ["S", "A", "B", "C", "D", "F"])

    # --------------------------------------------------------
    # 结构完整性评分测试
    # --------------------------------------------------------

    def test_structure_with_headings(self) -> None:
        """测试有标题的结构评分。"""
        result = self.scorer.score("# Title\n## Section\n### Subsection")
        structure = result["structure"]
        self.assertGreater(structure["score"], 0)

    def test_structure_without_headings(self) -> None:
        """测试无标题的结构评分。"""
        result = self.scorer.score("Just plain text.")
        structure = result["structure"]
        # 无标题应该有警告
        checks = structure["checks"]
        heading_check = next(c for c in checks if c["name"] == "标题")
        self.assertEqual(heading_check["status"], "fail")

    def test_structure_with_code_blocks(self) -> None:
        """测试有代码块的结构评分。"""
        text = "# Title\n\n```python\nprint('hi')\n```"
        result = self.scorer.score(text)
        structure = result["structure"]
        code_check = next(c for c in structure["checks"] if c["name"] == "代码块")
        self.assertEqual(code_check["status"], "pass")

    # --------------------------------------------------------
    # 可读性评分测试
    # --------------------------------------------------------

    def test_readability_score(self) -> None:
        """测试可读性评分。"""
        result = self.scorer.score("# Title\n\nA reasonable paragraph of text.")
        readability = result["readability"]
        self.assertGreaterEqual(readability["score"], 0)
        self.assertLessEqual(readability["score"], 100)

    def test_readability_checks_exist(self) -> None:
        """测试可读性检查项存在。"""
        result = self.scorer.score("Some text here.")
        readability = result["readability"]
        check_names = [c["name"] for c in readability["checks"]]
        self.assertIn("段落长度", check_names)

    # --------------------------------------------------------
    # 规范度评分测试
    # --------------------------------------------------------

    def test_standardization_clean_text(self) -> None:
        """测试干净文本的规范度评分。"""
        text = "# Title\n\nA paragraph.\n\n- item 1\n- item 2\n"
        result = self.scorer.score(text)
        standardization = result["standardization"]
        self.assertGreater(standardization["score"], 0)

    def test_standardization_trailing_whitespace(self) -> None:
        """测试行尾空白影响规范度评分。"""
        text = "Hello   \nWorld   \n"
        result = self.scorer.score(text)
        standardization = result["standardization"]
        ws_check = next(c for c in standardization["checks"]
                        if c["name"] == "行尾空白")
        self.assertEqual(ws_check["status"], "warn")

    def test_standardization_no_trailing_newline(self) -> None:
        """测试缺少末尾换行影响规范度评分。"""
        text = "# Title"
        result = self.scorer.score(text)
        standardization = result["standardization"]
        nl_check = next(c for c in standardization["checks"]
                        if c["name"] == "末尾换行")
        self.assertEqual(nl_check["status"], "warn")

    # --------------------------------------------------------
    # 报告格式测试
    # --------------------------------------------------------

    def test_format_report(self) -> None:
        """测试报告格式化。"""
        result = self.scorer.score("# Title\n\nContent.")
        report = self.scorer.format_report(result)
        self.assertIn("Markdown", report)
        self.assertIn("综合评分", report)

    def test_format_json(self) -> None:
        """测试JSON格式输出。"""
        result = self.scorer.score("# Title\n\nContent.")
        json_str = self.scorer.format_json(result)
        import json
        parsed = json.loads(json_str)
        self.assertIn("overall", parsed)


if __name__ == "__main__":
    unittest.main()
