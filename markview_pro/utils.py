"""
工具函数模块 - 提供文件读取、ANSI颜色、终端宽度检测等通用工具。

本模块是整个项目的基础设施层，提供：
- 文件读取与编码检测
- ANSI颜色转义码生成
- 终端宽度自适应检测
- 通用文本处理工具
"""

import os
import sys
import re
from typing import Optional, Tuple, List


# ============================================================
# ANSI 颜色与样式常量
# ============================================================

class ANSIStyle:
    """ANSI 终端样式常量集合。"""

    # 重置
    RESET = "\033[0m"

    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"

    # 样式
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"


# ============================================================
# 颜色主题定义
# ============================================================

# 默认终端渲染颜色主题
DEFAULT_THEME = {
    "h1": ANSIStyle.BRIGHT_CYAN + ANSIStyle.BOLD,
    "h2": ANSIStyle.BRIGHT_BLUE + ANSIStyle.BOLD,
    "h3": ANSIStyle.BRIGHT_MAGENTA + ANSIStyle.BOLD,
    "h4": ANSIStyle.BRIGHT_GREEN + ANSIStyle.BOLD,
    "h5": ANSIStyle.BRIGHT_YELLOW + ANSIStyle.BOLD,
    "h6": ANSIStyle.BRIGHT_WHITE + ANSIStyle.BOLD,
    "bold": ANSIStyle.BOLD,
    "italic": ANSIStyle.ITALIC,
    "strikethrough": ANSIStyle.STRIKETHROUGH,
    "code_inline": ANSIStyle.BRIGHT_YELLOW,
    "code_block": ANSIStyle.BRIGHT_GREEN,
    "link_text": ANSIStyle.BRIGHT_BLUE + ANSIStyle.UNDERLINE,
    "link_url": ANSIStyle.BRIGHT_BLACK,
    "image": ANSIStyle.BRIGHT_MAGENTA,
    "blockquote": ANSIStyle.BRIGHT_BLACK,
    "blockquote_border": ANSIStyle.BRIGHT_BLACK,
    "list_bullet": ANSIStyle.BRIGHT_YELLOW,
    "list_number": ANSIStyle.BRIGHT_YELLOW,
    "hr": ANSIStyle.BRIGHT_BLACK,
    "table_header": ANSIStyle.BRIGHT_CYAN + ANSIStyle.BOLD,
    "table_border": ANSIStyle.BRIGHT_BLACK,
    "task_done": ANSIStyle.BRIGHT_GREEN,
    "task_pending": ANSIStyle.BRIGHT_RED,
    "frontmatter": ANSIStyle.BRIGHT_BLACK,
    # 语法高亮颜色
    "keyword": ANSIStyle.BRIGHT_MAGENTA,
    "string": ANSIStyle.BRIGHT_GREEN,
    "comment": ANSIStyle.BRIGHT_BLACK + ANSIStyle.ITALIC,
    "number": ANSIStyle.BRIGHT_YELLOW,
    "function": ANSIStyle.BRIGHT_BLUE,
    "type": ANSIStyle.BRIGHT_CYAN,
    "operator": ANSIStyle.BRIGHT_RED,
    "decorator": ANSIStyle.BRIGHT_YELLOW,
    "builtin": ANSIStyle.BRIGHT_CYAN,
    "variable": ANSIStyle.WHITE,
    "punctuation": ANSIStyle.WHITE,
    "tag": ANSIStyle.BRIGHT_BLUE,
    "attribute": ANSIStyle.BRIGHT_YELLOW,
    "value": ANSIStyle.BRIGHT_GREEN,
}

# 暗色主题
DARK_THEME = {
    "h1": ANSIStyle.CYAN + ANSIStyle.BOLD + ANSIStyle.UNDERLINE,
    "h2": ANSIStyle.BLUE + ANSIStyle.BOLD,
    "h3": ANSIStyle.MAGENTA + ANSIStyle.BOLD,
    "h4": ANSIStyle.GREEN + ANSIStyle.BOLD,
    "h5": ANSIStyle.YELLOW + ANSIStyle.BOLD,
    "h6": ANSIStyle.WHITE + ANSIStyle.BOLD,
    "bold": ANSIStyle.BOLD,
    "italic": ANSIStyle.ITALIC,
    "strikethrough": ANSIStyle.STRIKETHROUGH,
    "code_inline": ANSIStyle.YELLOW,
    "code_block": ANSIStyle.GREEN,
    "link_text": ANSIStyle.BLUE + ANSIStyle.UNDERLINE,
    "link_url": ANSIStyle.DIM,
    "image": ANSIStyle.MAGENTA,
    "blockquote": ANSIStyle.DIM,
    "blockquote_border": ANSIStyle.DIM,
    "list_bullet": ANSIStyle.YELLOW,
    "list_number": ANSIStyle.YELLOW,
    "hr": ANSIStyle.DIM,
    "table_header": ANSIStyle.CYAN + ANSIStyle.BOLD,
    "table_border": ANSIStyle.DIM,
    "task_done": ANSIStyle.GREEN,
    "task_pending": ANSIStyle.RED,
    "frontmatter": ANSIStyle.DIM,
    "keyword": ANSIStyle.MAGENTA,
    "string": ANSIStyle.GREEN,
    "comment": ANSIStyle.DIM + ANSIStyle.ITALIC,
    "number": ANSIStyle.YELLOW,
    "function": ANSIStyle.BLUE,
    "type": ANSIStyle.CYAN,
    "operator": ANSIStyle.RED,
    "decorator": ANSIStyle.YELLOW,
    "builtin": ANSIStyle.CYAN,
    "variable": ANSIStyle.WHITE,
    "punctuation": ANSIStyle.WHITE,
    "tag": ANSIStyle.BLUE,
    "attribute": ANSIStyle.YELLOW,
    "value": ANSIStyle.GREEN,
}


# ============================================================
# 文件操作工具
# ============================================================

def read_file(filepath: str, encoding: Optional[str] = None) -> str:
    """
    读取文件内容，自动检测编码。

    Args:
        filepath: 文件路径
        encoding: 指定编码，若为None则自动检测

    Returns:
        文件内容字符串

    Raises:
        FileNotFoundError: 文件不存在
        IOError: 文件读取失败
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")

    if encoding:
        with open(filepath, "r", encoding=encoding) as f:
            return f.read()

    # 尝试常见编码
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "gb18030", "latin-1"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            # 验证读取结果是否包含乱码
            if enc in ("utf-8", "utf-8-sig"):
                return content
            # 对于其他编码，检查是否有明显的解码错误
            if "\ufffd" not in content:
                return content
        except (UnicodeDecodeError, UnicodeError):
            continue

    # 最后回退到 latin-1（不会失败）
    with open(filepath, "r", encoding="latin-1") as f:
        return f.read()


def write_file(filepath: str, content: str, encoding: str = "utf-8") -> None:
    """
    将内容写入文件。

    Args:
        filepath: 文件路径
        content: 要写入的内容
        encoding: 文件编码，默认utf-8

    Raises:
        IOError: 文件写入失败
    """
    # 确保目录存在
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(filepath, "w", encoding=encoding) as f:
        f.write(content)


def detect_encoding(filepath: str) -> str:
    """
    检测文件编码。

    通过读取BOM标记和尝试解码来判断文件编码。

    Args:
        filepath: 文件路径

    Returns:
        检测到的编码名称字符串
    """
    with open(filepath, "rb") as f:
        raw = f.read(4096)

    # 检查BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if raw.startswith(b"\xff\xfe"):
        return "utf-16-le"
    if raw.startswith(b"\xfe\xff"):
        return "utf-16-be"

    # 尝试UTF-8
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass

    # 尝试GBK
    try:
        raw.decode("gbk")
        return "gbk"
    except UnicodeDecodeError:
        pass

    return "latin-1"


# ============================================================
# 终端工具
# ============================================================

def get_terminal_width(default: int = 80) -> int:
    """
    获取终端宽度。

    尝试通过终端控制序列或环境变量获取终端宽度，
    如果无法获取则返回默认值。

    Args:
        default: 无法获取时的默认宽度

    Returns:
        终端宽度（列数）
    """
    # 方法1：通过 os.get_terminal_size
    try:
        size = os.get_terminal_size()
        return size.columns
    except (OSError, ValueError):
        pass

    # 方法2：通过环境变量
    try:
        cols = os.environ.get("COLUMNS")
        if cols:
            return int(cols)
    except (ValueError, TypeError):
        pass

    return default


def get_terminal_height(default: int = 24) -> int:
    """
    获取终端高度。

    Args:
        default: 无法获取时的默认高度

    Returns:
        终端高度（行数）
    """
    try:
        size = os.get_terminal_size()
        return size.lines
    except (OSError, ValueError):
        pass

    try:
        rows = os.environ.get("LINES")
        if rows:
            return int(rows)
    except (ValueError, TypeError):
        pass

    return default


def supports_color() -> bool:
    """
    检测终端是否支持ANSI颜色。

    检查是否在支持颜色的终端环境中运行。

    Returns:
        True表示支持颜色，False表示不支持
    """
    # 如果明确设置了NO_COLOR环境变量，则不支持
    if os.environ.get("NO_COLOR"):
        return False

    # Windows 10+ 支持 ANSI 颜色
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # 启用虚拟终端处理
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            if handle:
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                kernel32.SetConsoleMode(
                    handle, mode.value | 0x0004
                )
                return True
        except Exception:
            return False

    # 检查是否为真实的终端（非管道/重定向）
    if not sys.stdout.isatty():
        return False

    # 检查TERM环境变量
    term = os.environ.get("TERM", "")
    if term in ("dumb", "unknown"):
        return False

    return True


def clear_screen() -> None:
    """
    清除终端屏幕。

    使用ANSI转义序列清除屏幕并将光标移到左上角。
    """
    # ANSI 清屏序列
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def move_cursor(row: int, col: int) -> None:
    """
    移动终端光标到指定位置。

    Args:
        row: 行号（从0开始）
        col: 列号（从0开始）
    """
    sys.stdout.write(f"\033[{row + 1};{col + 1}H")
    sys.stdout.flush()


def hide_cursor() -> None:
    """隐藏终端光标。"""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    """显示终端光标。"""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


# ============================================================
# ANSI 颜色工具函数
# ============================================================

def colorize(text: str, style: str, no_color: bool = False) -> str:
    """
    为文本添加ANSI颜色样式。

    Args:
        text: 要着色的文本
        style: ANSI样式字符串（如 ANSIStyle.RED + ANSIStyle.BOLD）
        no_color: 是否禁用颜色

    Returns:
        着色后的文本（或原始文本，如果no_color为True）
    """
    if no_color or not text:
        return text
    return f"{style}{text}{ANSIStyle.RESET}"


def strip_ansi(text: str) -> str:
    """
    去除文本中的所有ANSI转义序列。

    Args:
        text: 可能包含ANSI码的文本

    Returns:
        纯文本（不含ANSI码）
    """
    # ANSI 转义序列正则：ESC [ ... m 或 ESC [ ... H 等
    ansi_pattern = re.compile(r"\033\[[0-9;]*[a-zA-Z]")
    return ansi_pattern.sub("", text)


def ansi_len(text: str) -> int:
    """
    计算文本的显示宽度（忽略ANSI转义序列）。

    Args:
        text: 可能包含ANSI码的文本

    Returns:
        文本在终端中的显示宽度
    """
    return len(strip_ansi(text))


def pad_text(text: str, width: int, align: str = "left",
             fill_char: str = " ") -> str:
    """
    将文本填充到指定宽度（考虑ANSI码）。

    Args:
        text: 可能包含ANSI码的文本
        width: 目标宽度
        align: 对齐方式 ("left", "center", "right")
        fill_char: 填充字符

    Returns:
        填充后的文本
    """
    display_len = ansi_len(text)
    if display_len >= width:
        return text

    padding = width - display_len
    if align == "right":
        return fill_char * padding + text
    elif align == "center":
        left_pad = padding // 2
        right_pad = padding - left_pad
        return fill_char * left_pad + text + fill_char * right_pad
    else:
        return text + fill_char * padding


def truncate_text(text: str, max_width: int, placeholder: str = "...") -> str:
    """
    截断文本到指定显示宽度（考虑ANSI码）。

    Args:
        text: 可能包含ANSI码的文本
        max_width: 最大显示宽度
        placeholder: 截断后添加的占位符

    Returns:
        截断后的文本
    """
    display_len = ansi_len(text)
    if display_len <= max_width:
        return text

    placeholder_len = len(placeholder)
    target_len = max_width - placeholder_len
    if target_len <= 0:
        return placeholder[:max_width]

    # 逐步截断，保留ANSI码的完整性
    result = []
    current_display = 0
    i = 0
    clean_text = strip_ansi(text)

    while i < len(clean_text) and current_display < target_len:
        char = clean_text[i]
        result.append(char)
        current_display += 1
        i += 1

    return "".join(result) + placeholder


# ============================================================
# 文本处理工具
# ============================================================

def count_chinese_chars(text: str) -> int:
    """
    统计文本中的中文字符数量。

    Args:
        text: 输入文本

    Returns:
        中文字符数量
    """
    count = 0
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            count += 1
    return count


def is_chinese_char(char: str) -> bool:
    """
    判断单个字符是否为中文字符。

    Args:
        char: 单个字符

    Returns:
        True表示是中文字符
    """
    if len(char) != 1:
        return False
    cp = ord(char)
    # CJK 统一汉字
    if 0x4E00 <= cp <= 0x9FFF:
        return True
    # CJK 扩展A
    if 0x3400 <= cp <= 0x4DBF:
        return True
    # CJK 扩展B
    if 0x20000 <= cp <= 0x2A6DF:
        return True
    # CJK 标点符号
    if 0x3000 <= cp <= 0x303F:
        return True
    # 全角标点
    if 0xFF00 <= cp <= 0xFFEF:
        return True
    return False


def display_width(text: str) -> int:
    """
    计算文本的显示宽度（考虑CJK全角字符占2列）。

    Args:
        text: 输入文本

    Returns:
        显示宽度
    """
    width = 0
    for char in text:
        cp = ord(char)
        if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF
                or 0xFF00 <= cp <= 0xFFEF or 0x3000 <= cp <= 0x303F):
            width += 2
        else:
            width += 1
    return width


def split_lines_preserving_newlines(text: str) -> List[str]:
    """
    分割文本为行列表，保留换行符信息。

    Args:
        text: 输入文本

    Returns:
        行列表
    """
    return text.split("\n")


def ensure_trailing_newline(text: str) -> str:
    """
    确保文本以换行符结尾。

    Args:
        text: 输入文本

    Returns:
        以换行符结尾的文本
    """
    if text and not text.endswith("\n"):
        return text + "\n"
    return text


def remove_trailing_newline(text: str) -> str:
    """
    移除文本末尾的换行符。

    Args:
        text: 输入文本

    Returns:
        不以换行符结尾的文本
    """
    return text.rstrip("\n")
