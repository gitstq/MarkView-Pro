"""
Markdown质量评分引擎模块 - 多维度评估Markdown文档质量。

从结构完整性、可读性、规范度三个维度对Markdown文档进行评分，
输出综合评分（0-100分）和各维度的详细分析。

评分维度：
- 结构完整性（0-100）：标题层级、列表、代码块、链接等结构元素
- 可读性（0-100）：句子长度、段落长度、标题密度
- 规范度（0-100）：空行使用、缩进一致性、链接格式
"""

import json
import re
from typing import Any, Dict, List, Optional

from markview_pro.parser import MarkdownParser, ASTNode, NodeType


class MarkdownScorer:
    """
    Markdown质量评分引擎。

    对Markdown文档进行多维度质量评估。

    Usage:
        scorer = MarkdownScorer()
        result = scorer.score("# Hello\\n\\nWorld!")
        print(result["overall"])  # 综合评分
        print(result["structure"]["score"])  # 结构完整性评分
    """

    def __init__(self) -> None:
        """初始化评分引擎。"""
        self.parser = MarkdownParser()

    def score(self, text: str) -> Dict[str, Any]:
        """
        对Markdown文本进行质量评分。

        Args:
            text: Markdown源文本

        Returns:
            评分结果字典，包含综合评分和各维度详细分析
        """
        ast = self.parser.parse(text)

        # 各维度评分
        structure = self._score_structure(ast, text)
        readability = self._score_readability(ast, text)
        standardization = self._score_standardization(ast, text)

        # 综合评分（加权平均）
        overall = (
            structure["score"] * 0.35
            + readability["score"] * 0.35
            + standardization["score"] * 0.30
        )
        overall = round(min(100, max(0, overall)), 1)

        return {
            "overall": overall,
            "structure": structure,
            "readability": readability,
            "standardization": standardization,
            "grade": self._get_grade(overall),
        }

    def _get_grade(self, score: float) -> str:
        """
        根据分数获取等级。

        Args:
            score: 综合评分

        Returns:
            等级字符串 (S/A/B/C/D/F)
        """
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"

    # --------------------------------------------------------
    # 结构完整性评分
    # --------------------------------------------------------

    def _score_structure(self, ast: ASTNode, text: str) -> Dict[str, Any]:
        """
        评估文档结构完整性。

        检查文档是否包含标题、列表、代码块、链接等结构元素。

        Args:
            ast: 文档AST
            text: 原始文本

        Returns:
            结构评分结果
        """
        checks: List[Dict[str, Any]] = []
        score = 0
        max_score = 100

        # 检查是否有标题
        headings = self._count_nodes(ast, NodeType.HEADING)
        if headings > 0:
            has_h1 = any(
                child.metadata.get("level") == 1
                for child in ast.children
                if child.type == NodeType.HEADING
            )
            if has_h1:
                score += 15
                checks.append({"name": "标题", "status": "pass",
                                "detail": f"包含{headings}个标题，有H1标题"})
            else:
                score += 8
                checks.append({"name": "标题", "status": "warn",
                                "detail": f"包含{headings}个标题，但缺少H1标题"})
        else:
            checks.append({"name": "标题", "status": "fail",
                            "detail": "文档缺少标题"})

        # 检查标题层级结构
        if headings > 1:
            levels = set()
            for child in ast.children:
                if child.type == NodeType.HEADING:
                    levels.add(child.metadata.get("level", 0))
            if len(levels) > 1:
                score += 10
                checks.append({"name": "标题层级", "status": "pass",
                                "detail": f"使用了{len(levels)}个层级的标题"})
            else:
                score += 3
                checks.append({"name": "标题层级", "status": "warn",
                                "detail": "标题层级单一，建议使用多级标题"})

        # 检查段落
        paragraphs = self._count_nodes(ast, NodeType.PARAGRAPH)
        if paragraphs > 0:
            score += 10
            checks.append({"name": "段落", "status": "pass",
                            "detail": f"包含{paragraphs}个段落"})
        else:
            checks.append({"name": "段落", "status": "warn",
                            "detail": "文档缺少段落内容"})

        # 检查列表
        lists = (self._count_nodes(ast, NodeType.UNORDERED_LIST)
                 + self._count_nodes(ast, NodeType.ORDERED_LIST)
                 + self._count_nodes(ast, NodeType.TASK_LIST))
        if lists > 0:
            score += 10
            checks.append({"name": "列表", "status": "pass",
                            "detail": f"包含{lists}个列表"})
        else:
            score += 0
            checks.append({"name": "列表", "status": "info",
                            "detail": "文档没有使用列表"})

        # 检查代码块
        code_blocks = self._count_nodes(ast, NodeType.CODE_BLOCK)
        if code_blocks > 0:
            # 检查代码块是否有语言标识
            has_lang = all(
                child.metadata.get("language", "")
                for child in ast.children
                if child.type == NodeType.CODE_BLOCK
            )
            if has_lang:
                score += 15
                checks.append({"name": "代码块", "status": "pass",
                                "detail": f"包含{code_blocks}个带语言标识的代码块"})
            else:
                score += 10
                checks.append({"name": "代码块", "status": "warn",
                                "detail": f"包含{code_blocks}个代码块，部分缺少语言标识"})
        else:
            score += 0
            checks.append({"name": "代码块", "status": "info",
                            "detail": "文档没有代码块"})

        # 检查链接
        links = self._count_inline_nodes(ast, NodeType.LINK)
        if links > 0:
            score += 10
            checks.append({"name": "链接", "status": "pass",
                            "detail": f"包含{links}个链接"})
        else:
            score += 0
            checks.append({"name": "链接", "status": "info",
                            "detail": "文档没有链接"})

        # 检查表格
        tables = self._count_nodes(ast, NodeType.TABLE)
        if tables > 0:
            score += 10
            checks.append({"name": "表格", "status": "pass",
                            "detail": f"包含{tables}个表格"})
        else:
            score += 0
            checks.append({"name": "表格", "status": "info",
                            "detail": "文档没有表格"})

        # 检查引用
        blockquotes = self._count_nodes(ast, NodeType.BLOCKQUOTE)
        if blockquotes > 0:
            score += 5
            checks.append({"name": "引用", "status": "pass",
                                "detail": f"包含{blockquotes}个引用块"})

        # 检查图片
        images = self._count_inline_nodes(ast, NodeType.IMAGE)
        if images > 0:
            score += 5
            checks.append({"name": "图片", "status": "pass",
                            "detail": f"包含{images}个图片"})

        # 检查文档长度
        line_count = len(text.split("\n"))
        if line_count >= 10:
            score += 10
            checks.append({"name": "文档长度", "status": "pass",
                            "detail": f"文档共{line_count}行"})
        elif line_count >= 5:
            score += 5
            checks.append({"name": "文档长度", "status": "warn",
                            "detail": f"文档较短，仅{line_count}行"})
        else:
            checks.append({"name": "文档长度", "status": "warn",
                            "detail": f"文档非常短，仅{line_count}行"})

        return {
            "score": min(max_score, score),
            "max": max_score,
            "checks": checks,
        }

    # --------------------------------------------------------
    # 可读性评分
    # --------------------------------------------------------

    def _score_readability(self, ast: ASTNode, text: str) -> Dict[str, Any]:
        """
        评估文档可读性。

        分析句子长度、段落长度、标题密度等因素。

        Args:
            ast: 文档AST
            text: 原始文本

        Returns:
            可读性评分结果
        """
        score = 0
        max_score = 100
        checks: List[Dict[str, Any]] = []
        lines = text.split("\n")

        # 段落长度分析
        paragraphs = [child for child in ast.children
                      if child.type == NodeType.PARAGRAPH]
        if paragraphs:
            avg_para_len = sum(len(p.content) for p in paragraphs) / len(paragraphs)
            if 50 <= avg_para_len <= 500:
                score += 20
                checks.append({"name": "段落长度", "status": "pass",
                                "detail": f"平均段落长度{avg_para_len:.0f}字符，适中"})
            elif avg_para_len > 500:
                score += 10
                checks.append({"name": "段落长度", "status": "warn",
                                "detail": f"段落偏长（平均{avg_para_len:.0f}字符），建议拆分"})
            else:
                score += 15
                checks.append({"name": "段落长度", "status": "pass",
                                "detail": f"段落较短（平均{avg_para_len:.0f}字符）"})
        else:
            score += 5
            checks.append({"name": "段落长度", "status": "info",
                            "detail": "没有段落内容"})

        # 行长度分析
        non_empty_lines = [l for l in lines if l.strip()]
        if non_empty_lines:
            long_lines = sum(1 for l in non_empty_lines if len(l) > 100)
            long_ratio = long_lines / len(non_empty_lines)
            if long_ratio < 0.1:
                score += 20
                checks.append({"name": "行长度", "status": "pass",
                                "detail": f"仅{long_ratio*100:.0f}%的行超过100字符"})
            elif long_ratio < 0.3:
                score += 15
                checks.append({"name": "行长度", "status": "warn",
                                "detail": f"{long_ratio*100:.0f}%的行超过100字符"})
            else:
                score += 5
                checks.append({"name": "行长度", "status": "fail",
                                "detail": f"{long_ratio*100:.0f}%的行超过100字符，建议换行"})

        # 标题密度（标题占比）
        total_lines = len(lines)
        heading_lines = sum(1 for l in lines if re.match(r"^#{1,6}\s", l))
        if total_lines > 0:
            heading_ratio = heading_lines / total_lines
            if 0.02 <= heading_ratio <= 0.15:
                score += 20
                checks.append({"name": "标题密度", "status": "pass",
                                "detail": f"标题占比{heading_ratio*100:.1f}%，适中"})
            elif heading_ratio > 0.15:
                score += 10
                checks.append({"name": "标题密度", "status": "warn",
                                "detail": f"标题过多（占比{heading_ratio*100:.1f}%）"})
            else:
                score += 10
                checks.append({"name": "标题密度", "status": "warn",
                                "detail": "标题较少，建议增加标题提升可读性"})

        # 空行使用
        blank_lines = sum(1 for l in lines if not l.strip())
        if total_lines > 0:
            blank_ratio = blank_lines / total_lines
            if 0.05 <= blank_ratio <= 0.25:
                score += 20
                checks.append({"name": "空行使用", "status": "pass",
                                "detail": f"空行占比{blank_ratio*100:.1f}%，适中"})
            elif blank_ratio < 0.05:
                score += 10
                checks.append({"name": "空行使用", "status": "warn",
                                "detail": "空行较少，建议增加空行分隔内容"})
            else:
                score += 10
                checks.append({"name": "空行使用", "status": "warn",
                                "detail": "空行较多，建议减少不必要的空行"})

        # 内容丰富度（是否使用了多种格式）
        format_types = set()
        for child in ast.children:
            format_types.add(child.type)
        if len(format_types) >= 4:
            score += 20
            checks.append({"name": "格式丰富度", "status": "pass",
                            "detail": f"使用了{len(format_types)}种Markdown格式"})
        elif len(format_types) >= 2:
            score += 15
            checks.append({"name": "格式丰富度", "status": "warn",
                            "detail": f"仅使用了{len(format_types)}种格式，建议丰富内容"})
        else:
            score += 5
            checks.append({"name": "格式丰富度", "status": "fail",
                            "detail": "格式单一，建议使用更多Markdown特性"})

        return {
            "score": min(max_score, score),
            "max": max_score,
            "checks": checks,
        }

    # --------------------------------------------------------
    # 规范度评分
    # --------------------------------------------------------

    def _score_standardization(self, ast: ASTNode, text: str) -> Dict[str, Any]:
        """
        评估文档规范度。

        检查空行使用、缩进一致性、链接格式等。

        Args:
            ast: 文档AST
            text: 原始文本

        Returns:
            规范度评分结果
        """
        score = 0
        max_score = 100
        checks: List[Dict[str, Any]] = []
        lines = text.split("\n")

        # 行尾空白检查
        trailing_whitespace = sum(1 for l in lines if l != l.rstrip())
        if trailing_whitespace == 0:
            score += 15
            checks.append({"name": "行尾空白", "status": "pass",
                            "detail": "没有行尾空白"})
        else:
            score += 5
            checks.append({"name": "行尾空白", "status": "warn",
                            "detail": f"{trailing_whitespace}行有行尾空白"})

        # 连续空行检查
        consecutive_blanks = 0
        has_excessive_blanks = False
        for l in lines:
            if not l.strip():
                consecutive_blanks += 1
                if consecutive_blanks > 1:
                    has_excessive_blanks = True
                    break
            else:
                consecutive_blanks = 0

        if not has_excessive_blanks:
            score += 15
            checks.append({"name": "空行规范", "status": "pass",
                            "detail": "没有连续多余空行"})
        else:
            score += 5
            checks.append({"name": "空行规范", "status": "warn",
                            "detail": "存在连续多余空行"})

        # 标题格式检查
        heading_issues = 0
        for line in lines:
            if re.match(r"^#{1,6}\s", line):
                # 标题后应有空格
                if not re.match(r"^#{1,6}\s+\S", line):
                    heading_issues += 1
                # ATX风格标题不应有尾随#
                if re.search(r"\s+#+\s*$", line) and not re.match(
                        r"^#{1,6}\s+\S.*\s+#+\s*$", line):
                    heading_issues += 1

        if heading_issues == 0:
            score += 15
            checks.append({"name": "标题格式", "status": "pass",
                            "detail": "标题格式规范"})
        else:
            score += 5
            checks.append({"name": "标题格式", "status": "warn",
                            "detail": f"{heading_issues}个标题格式不规范"})

        # 列表格式检查
        list_issues = 0
        for line in lines:
            # 检查列表标记后是否有空格
            if re.match(r"^(\s*)[-*+]\S", line):
                list_issues += 1
            if re.match(r"^(\s*)\d+\.\S", line):
                list_issues += 1

        if list_issues == 0:
            score += 15
            checks.append({"name": "列表格式", "status": "pass",
                            "detail": "列表格式规范"})
        else:
            score += 5
            checks.append({"name": "列表格式", "status": "warn",
                            "detail": f"{list_issues}个列表项格式不规范"})

        # 链接格式检查
        link_issues = 0
        for line in lines:
            # 检查链接中是否有多余空格
            if re.search(r"\[\s+.+?\s+\]\(\s+.+?\s+\)", line):
                link_issues += 1
            # 检查空链接
            if re.search(r"\[\]\(\)", line):
                link_issues += 1

        if link_issues == 0:
            score += 15
            checks.append({"name": "链接格式", "status": "pass",
                            "detail": "链接格式规范"})
        else:
            score += 5
            checks.append({"name": "链接格式", "status": "warn",
                            "detail": f"{link_issues}个链接格式不规范"})

        # 代码块检查
        code_block_issues = 0
        for child in ast.children:
            if child.type == NodeType.CODE_BLOCK:
                if not child.metadata.get("language"):
                    code_block_issues += 1

        if code_block_issues == 0:
            score += 10
            checks.append({"name": "代码块规范", "status": "pass",
                            "detail": "所有代码块都有语言标识"})
        else:
            score += 3
            checks.append({"name": "代码块规范", "status": "warn",
                            "detail": f"{code_block_issues}个代码块缺少语言标识"})

        # 文件末尾换行检查
        if text.endswith("\n"):
            score += 15
            checks.append({"name": "末尾换行", "status": "pass",
                            "detail": "文件末尾有换行符"})
        else:
            score += 5
            checks.append({"name": "末尾换行", "status": "warn",
                            "detail": "文件末尾缺少换行符"})

        return {
            "score": min(max_score, score),
            "max": max_score,
            "checks": checks,
        }

    # --------------------------------------------------------
    # 辅助方法
    # --------------------------------------------------------

    def _count_nodes(self, ast: ASTNode, node_type: str) -> int:
        """
        统计AST中指定类型的节点数量。

        Args:
            ast: 文档AST
            node_type: 节点类型

        Returns:
            节点数量
        """
        count = 0
        for child in ast.children:
            if child.type == node_type:
                count += 1
        return count

    def _count_inline_nodes(self, ast: ASTNode, node_type: str) -> int:
        """
        递归统计AST中指定类型的行内节点数量。

        Args:
            ast: 文档AST
            node_type: 节点类型

        Returns:
            节点数量
        """
        count = 0

        def _walk(node: ASTNode) -> None:
            nonlocal count
            if node.type == node_type:
                count += 1
            for child in node.children:
                _walk(child)

        _walk(ast)
        return count

    def format_report(self, result: Dict[str, Any]) -> str:
        """
        格式化评分报告为可读文本。

        Args:
            result: score() 方法返回的评分结果

        Returns:
            格式化的评分报告文本
        """
        lines: List[str] = []

        lines.append("=" * 50)
        lines.append("  Markdown 质量评分报告")
        lines.append("=" * 50)
        lines.append("")

        # 综合评分
        grade = result["grade"]
        overall = result["overall"]
        lines.append(f"  综合评分: {overall}/100  等级: {grade}")
        lines.append("")

        # 各维度评分
        dimensions = [
            ("结构完整性", result["structure"]),
            ("可读性", result["readability"]),
            ("规范度", result["standardization"]),
        ]

        for dim_name, dim_data in dimensions:
            dim_score = dim_data["score"]
            dim_max = dim_data["max"]
            lines.append(f"  ┌─ {dim_name}: {dim_score}/{dim_max}")
            for check in dim_data["checks"]:
                status = check["status"]
                name = check["name"]
                detail = check["detail"]

                if status == "pass":
                    icon = "[OK]"
                elif status == "warn":
                    icon = "[!!]"
                elif status == "fail":
                    icon = "[XX]"
                else:
                    icon = "[--]"

                lines.append(f"  │  {icon} {name}: {detail}")
            lines.append(f"  └{'─' * 40}")

        lines.append("")
        lines.append("=" * 50)

        return "\n".join(lines)

    def format_json(self, result: Dict[str, Any]) -> str:
        """
        将评分结果格式化为JSON字符串。

        Args:
            result: score() 方法返回的评分结果

        Returns:
            JSON格式字符串
        """
        return json.dumps(result, ensure_ascii=False, indent=2)
