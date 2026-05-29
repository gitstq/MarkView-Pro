"""
TUI交互式仪表盘模块 - 基于curses的Markdown文件交互式预览。

使用Python标准库curses构建终端交互界面。

功能特性：
- 左侧显示文件内容预览
- 右侧显示文件信息面板
- 底部状态栏显示快捷键提示
- 支持上下滚动浏览
- 快捷键：q退出、r刷新、f格式化、s评分
"""

import os
import sys
import time
from typing import Optional, List

try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False


class TUIDashboard:
    """
    TUI交互式仪表盘。

    使用curses库构建Markdown文件的交互式预览界面。

    Attributes:
        filepath: 预览的文件路径
        scroll_offset: 当前滚动偏移量
        rendered_lines: 渲染后的内容行列表
    """

    def __init__(self, filepath: str) -> None:
        """
        初始化TUI仪表盘。

        Args:
            filepath: 要预览的Markdown文件路径
        """
        self.filepath: str = filepath
        self.scroll_offset: int = 0
        self.rendered_lines: List[str] = []
        self.info_lines: List[str] = []
        self.last_modified: float = 0.0
        self.score_text: str = ""
        self.needs_refresh: bool = True
        self.status_message: str = ""
        self.status_time: float = 0.0

    def run(self) -> None:
        """
        启动TUI仪表盘。

        使用curses初始化终端并进入主循环。
        """
        if not CURSES_AVAILABLE:
            print("错误: curses 库不可用，无法启动TUI模式。")
            print("请使用 'markview preview' 命令替代。")
            return

        try:
            curses.wrapper(self._run_curses)
        except Exception as e:
            print(f"TUI 错误: {e}")

    def _run_curses(self, stdscr: "curses.window") -> None:
        """
        curses主循环。

        Args:
            stdscr: curses标准窗口
        """
        # 初始化
        self._init_curses(stdscr)
        self._refresh_content()

        # 主循环
        while True:
            self._draw(stdscr)

            # 检查文件变更
            self._check_file_change()

            # 处理输入（非阻塞）
            try:
                stdscr.timeout(100)  # 100ms超时
                key = stdscr.getch()

                if key == -1:
                    continue
                elif key == ord("q") or key == ord("Q"):
                    break
                elif key == ord("r") or key == ord("R"):
                    self._refresh_content()
                    self._set_status("已刷新", stdscr)
                elif key == ord("f") or key == ord("F"):
                    self._format_file()
                    self._set_status("已格式化", stdscr)
                elif key == ord("s") or key == ord("S"):
                    self._show_score(stdscr)
                elif key == curses.KEY_UP or key == ord("k"):
                    self._scroll_up()
                elif key == curses.KEY_DOWN or key == ord("j"):
                    self._scroll_down()
                elif key == curses.KEY_PPAGE or key == ord("K"):
                    self._scroll_page_up()
                elif key == curses.KEY_NPAGE or key == ord("J"):
                    self._scroll_page_down()
                elif key == curses.KEY_HOME:
                    self.scroll_offset = 0
                elif key == curses.KEY_END:
                    max_scroll = max(0, len(self.rendered_lines) - 1)
                    self.scroll_offset = max_scroll
            except curses.error:
                continue

    def _init_curses(self, stdscr: "curses.window") -> None:
        """
        初始化curses设置。

        Args:
            stdscr: curses标准窗口
        """
        # 隐藏光标
        curses.curs_set(0)

        # 启用颜色
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            # 定义颜色对
            curses.init_pair(1, curses.COLOR_CYAN, -1)      # 标题
            curses.init_pair(2, curses.COLOR_BLUE, -1)       # 链接
            curses.init_pair(3, curses.COLOR_GREEN, -1)      # 成功
            curses.init_pair(4, curses.COLOR_YELLOW, -1)     # 警告
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)    # 强调
            curses.init_pair(6, curses.COLOR_WHITE, -1)      # 普通文本
            curses.init_pair(7, curses.COLOR_BLACK, -1)      # 暗色
            curses.init_pair(8, curses.COLOR_RED, -1)        # 错误
            curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLACK)  # 状态栏

    def _draw(self, stdscr: "curses.window") -> None:
        """
        绘制TUI界面。

        Args:
            stdscr: curses标准窗口
        """
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if width < 40 or height < 10:
            stdscr.addstr(0, 0, "终端窗口太小，请调整大小。")
            stdscr.refresh()
            return

        # 计算布局
        content_width = max(width * 2 // 3, width - 30)
        info_width = width - content_width - 1

        # 绘制分隔线
        sep_x = content_width
        try:
            stdscr.vline(0, sep_x, curses.ACS_VLINE, height - 2)
        except curses.error:
            pass

        # 绘制内容区域（左侧）
        self._draw_content(stdscr, 0, 0, height - 2, content_width)

        # 绘制信息面板（右侧）
        self._draw_info(stdscr, 0, sep_x + 1, height - 2, info_width)

        # 绘制状态栏（底部）
        self._draw_status_bar(stdscr, height - 1, width)

        stdscr.refresh()

    def _draw_content(self, stdscr: "curses.window",
                      y_start: int, x_start: int,
                      height: int, width: int) -> None:
        """
        绘制内容区域。

        Args:
            stdscr: curses标准窗口
            y_start: 起始行
            x_start: 起始列
            height: 可用高度
            width: 可用宽度
        """
        # 标题栏
        title = f" {os.path.basename(self.filepath)}"
        if len(title) > width:
            title = title[:width - 1]
        try:
            stdscr.addstr(y_start, x_start, title, curses.A_REVERSE)
        except curses.error:
            pass

        # 内容行
        max_scroll = max(0, len(self.rendered_lines) - (height - 2))
        self.scroll_offset = min(self.scroll_offset, max_scroll)

        for i in range(height - 2):
            line_idx = self.scroll_offset + i
            if line_idx < len(self.rendered_lines):
                line = self.rendered_lines[line_idx]
                # 截断过长的行
                if len(line) > width - 1:
                    line = line[:width - 1]
                try:
                    # 行号
                    line_num = f"{line_idx + 1:>4} "
                    stdscr.addstr(y_start + 1 + i, x_start, line_num,
                                 curses.A_DIM if curses.has_colors() else 0)
                    stdscr.addstr(y_start + 1 + i, x_start + 5, line)
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(y_start + 1 + i, x_start, "~")
                except curses.error:
                    pass

    def _draw_info(self, stdscr: "curses.window",
                   y_start: int, x_start: int,
                   height: int, width: int) -> None:
        """
        绘制信息面板。

        Args:
            stdscr: curses标准窗口
            y_start: 起始行
            x_start: 起始列
            height: 可用高度
            width: 可用宽度
        """
        # 标题
        title = " 信息面板"
        if len(title) > width:
            title = title[:width - 1]
        try:
            stdscr.addstr(y_start, x_start, title, curses.A_REVERSE)
        except curses.error:
            pass

        # 信息内容
        for i, line in enumerate(self.info_lines):
            if i >= height - 2:
                break
            display_line = line[:width - 1] if len(line) > width - 1 else line
            try:
                stdscr.addstr(y_start + 1 + i, x_start, display_line)
            except curses.error:
                pass

    def _draw_status_bar(self, stdscr: "curses.window",
                        y: int, width: int) -> None:
        """
        绘制底部状态栏。

        Args:
            stdscr: curses标准窗口
            y: 状态栏行号
            width: 终端宽度
        """
        # 快捷键提示
        keys = "[Q]退出 [R]刷新 [F]格式化 [S]评分 [Up/Down]滚动 [PgUp/PgDn]翻页"
        if len(keys) > width:
            keys = keys[:width - 1]

        # 状态消息
        status = self.status_message
        if status and time.time() - self.status_time < 3:
            status_part = f" {status}"
        else:
            status_part = ""

        # 滚动信息
        scroll_info = f" 行 {self.scroll_offset + 1}/{len(self.rendered_lines)}"

        try:
            if curses.has_colors():
                stdscr.addstr(y, 0, keys, curses.color_pair(9))
            else:
                stdscr.addstr(y, 0, keys, curses.A_REVERSE)

            if status_part:
                stdscr.addstr(y, width - len(scroll_info) - len(status_part),
                             status_part)
            stdscr.addstr(y, width - len(scroll_info), scroll_info)
        except curses.error:
            pass

    def _refresh_content(self) -> None:
        """
        刷新文件内容和渲染结果。
        """
        try:
            from markview_pro.utils import read_file
            from markview_pro.renderer import TerminalRenderer

            text = read_file(self.filepath)
            renderer = TerminalRenderer(no_color=True)
            self.rendered_lines = renderer.render_text(text).split("\n")

            # 更新文件信息
            self._update_info(text)

            # 更新修改时间
            stat = os.stat(self.filepath)
            self.last_modified = stat.st_mtime

            self.needs_refresh = False
        except Exception as e:
            self.rendered_lines = [f"错误: 无法读取文件 - {e}"]
            self.info_lines = ["文件读取错误"]

    def _update_info(self, text: str) -> None:
        """
        更新信息面板内容。

        Args:
            text: 文件文本
        """
        lines = text.split("\n")
        file_size = os.path.getsize(self.filepath)

        # 格式化文件大小
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"

        self.info_lines = [
            "=== 文件信息 ===",
            f"文件: {os.path.basename(self.filepath)}",
            f"路径: {self.filepath}",
            f"大小: {size_str}",
            f"行数: {len(lines)}",
            f"字符数: {len(text)}",
            "",
            "=== 结构统计 ===",
        ]

        # 统计结构元素
        from markview_pro.parser import MarkdownParser, NodeType
        parser = MarkdownParser()
        ast = parser.parse(text)

        headings = sum(1 for c in ast.children if c.type == NodeType.HEADING)
        paragraphs = sum(1 for c in ast.children if c.type == NodeType.PARAGRAPH)
        code_blocks = sum(1 for c in ast.children if c.type == NodeType.CODE_BLOCK)
        lists = sum(1 for c in ast.children
                    if c.type in (NodeType.UNORDERED_LIST, NodeType.ORDERED_LIST,
                                  NodeType.TASK_LIST))
        tables = sum(1 for c in ast.children if c.type == NodeType.TABLE)
        blockquotes = sum(1 for c in ast.children if c.type == NodeType.BLOCKQUOTE)

        self.info_lines.extend([
            f"标题: {headings}",
            f"段落: {paragraphs}",
            f"代码块: {code_blocks}",
            f"列表: {lists}",
            f"表格: {tables}",
            f"引用: {blockquote}",
        ])

    def _check_file_change(self) -> None:
        """
        检查文件是否有变更。
        """
        try:
            stat = os.stat(self.filepath)
            if stat.st_mtime != self.last_modified:
                self._refresh_content()
        except OSError:
            pass

    def _format_file(self) -> None:
        """
        格式化当前文件。
        """
        try:
            from markview_pro.utils import read_file, write_file
            from markview_pro.formatter import MarkdownFormatter

            text = read_file(self.filepath)
            formatter = MarkdownFormatter()
            formatted = formatter.format(text)
            write_file(self.filepath, formatted)
            self._refresh_content()
        except Exception as e:
            self.status_message = f"格式化失败: {e}"
            self.status_time = time.time()

    def _show_score(self, stdscr: "curses.window") -> None:
        """
        显示评分结果。

        Args:
            stdscr: curses标准窗口
        """
        try:
            from markview_pro.utils import read_file
            from markview_pro.scorer import MarkdownScorer

            text = read_file(self.filepath)
            scorer = MarkdownScorer()
            result = scorer.score(text)

            self.score_text = scorer.format_report(result)
            self._set_status(
                f"评分: {result['overall']}/100 ({result['grade']})",
                stdscr
            )
        except Exception as e:
            self._set_status(f"评分失败: {e}", stdscr)

    def _set_status(self, message: str,
                    stdscr: "curses.window") -> None:
        """
        设置状态栏消息。

        Args:
            message: 状态消息
            stdscr: curses标准窗口
        """
        self.status_message = message
        self.status_time = time.time()

    def _scroll_up(self, amount: int = 1) -> None:
        """
        向上滚动。

        Args:
            amount: 滚动行数
        """
        self.scroll_offset = max(0, self.scroll_offset - amount)

    def _scroll_down(self, amount: int = 1) -> None:
        """
        向下滚动。

        Args:
            amount: 滚动行数
        """
        max_scroll = max(0, len(self.rendered_lines) - 1)
        self.scroll_offset = min(max_scroll, self.scroll_offset + amount)

    def _scroll_page_up(self) -> None:
        """向上翻页。"""
        self._scroll_up(20)

    def _scroll_page_down(self) -> None:
        """向下翻页。"""
        self._scroll_down(20)
