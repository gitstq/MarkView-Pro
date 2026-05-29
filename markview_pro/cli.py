"""
CLI命令行入口模块 - MarkView-Pro 命令行接口。

使用 argparse 构建完整的CLI命令行接口。

支持的命令：
- markview preview <file>  - 实时预览Markdown文件
- markview format <file>   - 智能格式化Markdown文件
- markview score <file>    - Markdown质量评分
- markview export <file>   - 多格式导出
- markview serve <file>    - 启动TUI交互式仪表盘
- markview --version       - 版本信息
- markview --help          - 帮助信息
"""

import argparse
import os
import sys
from typing import List, Optional

from markview_pro import __version__
from markview_pro.utils import read_file, write_file, supports_color
from markview_pro.parser import MarkdownParser
from markview_pro.renderer import TerminalRenderer
from markview_pro.formatter import MarkdownFormatter
from markview_pro.scorer import MarkdownScorer
from markview_pro.exporter import MarkdownExporter
from markview_pro.watcher import FileWatcher
from markview_pro.tui import TUIDashboard


def create_parser() -> argparse.ArgumentParser:
    """
    创建CLI参数解析器。

    Returns:
        配置好的ArgumentParser实例
    """
    parser = argparse.ArgumentParser(
        prog="markview",
        description="MarkView-Pro - 轻量级终端Markdown实时预览与智能格式化引擎",
        epilog="使用 'markview <command> --help' 查看子命令帮助",
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"MarkView-Pro {__version__}"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="可用命令",
        description="MarkView-Pro 提供以下命令",
    )

    # --------------------------------------------------------
    # preview 命令
    # --------------------------------------------------------
    preview_parser = subparsers.add_parser(
        "preview",
        help="实时预览Markdown文件",
        description="在终端中预览Markdown文件的渲染效果",
    )
    preview_parser.add_argument(
        "file",
        help="Markdown文件路径"
    )
    preview_parser.add_argument(
        "--watch", "-w",
        action="store_true",
        default=False,
        help="启用文件监听模式，自动刷新预览"
    )
    preview_parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="禁用颜色输出"
    )
    preview_parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="指定终端宽度（默认自动检测）"
    )

    # --------------------------------------------------------
    # format 命令
    # --------------------------------------------------------
    format_parser = subparsers.add_parser(
        "format",
        help="智能格式化Markdown文件",
        description="自动规范化和优化Markdown文件格式",
    )
    format_parser.add_argument(
        "file",
        help="Markdown文件路径"
    )
    format_parser.add_argument(
        "--in-place", "-i",
        action="store_true",
        default=False,
        help="原地修改文件"
    )
    format_parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径"
    )
    format_parser.add_argument(
        "--indent",
        type=int,
        choices=[2, 4],
        default=2,
        help="列表缩进空格数（2或4，默认2）"
    )
    format_parser.add_argument(
        "--cjk-spaces",
        action="store_true",
        default=False,
        help="在中英文之间自动添加空格"
    )

    # --------------------------------------------------------
    # score 命令
    # --------------------------------------------------------
    score_parser = subparsers.add_parser(
        "score",
        help="Markdown质量评分",
        description="对Markdown文件进行多维度质量评估",
    )
    score_parser.add_argument(
        "file",
        help="Markdown文件路径"
    )
    score_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="以JSON格式输出评分结果"
    )

    # --------------------------------------------------------
    # export 命令
    # --------------------------------------------------------
    export_parser = subparsers.add_parser(
        "export",
        help="多格式导出",
        description="将Markdown文件导出为不同格式",
    )
    export_parser.add_argument(
        "file",
        help="Markdown文件路径"
    )
    export_parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["html", "text", "json"],
        default="html",
        help="导出格式（html/text/json，默认html）"
    )
    export_parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径（默认输出到终端）"
    )

    # --------------------------------------------------------
    # serve 命令
    # --------------------------------------------------------
    serve_parser = subparsers.add_parser(
        "serve",
        help="启动TUI交互式仪表盘",
        description="在终端中启动交互式Markdown预览界面",
    )
    serve_parser.add_argument(
        "file",
        help="Markdown文件路径"
    )

    return parser


def cmd_preview(args: argparse.Namespace) -> int:
    """
    执行预览命令。

    Args:
        args: 命令行参数

    Returns:
        退出码（0成功，1失败）
    """
    try:
        text = read_file(args.file)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {args.file}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"错误: 无法读取文件 - {e}", file=sys.stderr)
        return 1

    no_color = args.no_color or not supports_color()
    renderer = TerminalRenderer(no_color=no_color, term_width=args.width)
    rendered = renderer.render_text(text)

    print(rendered)

    if args.watch:
        print(f"\n监听文件变更中... (按 Ctrl+C 退出)", file=sys.stderr)

        def on_change(filepath: str) -> None:
            """文件变更回调。"""
            try:
                updated_text = read_file(filepath)
                updated_rendered = renderer.render_text(updated_text)
                # 清屏并重新渲染
                print("\033[2J\033[H", end="")
                print(updated_rendered)
                print(f"\n文件已更新: {filepath}", file=sys.stderr)
            except Exception as e:
                print(f"刷新失败: {e}", file=sys.stderr)

        watcher = FileWatcher(args.file, callback=on_change)
        watcher.start()

    return 0


def cmd_format(args: argparse.Namespace) -> int:
    """
    执行格式化命令。

    Args:
        args: 命令行参数

    Returns:
        退出码（0成功，1失败）
    """
    try:
        text = read_file(args.file)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {args.file}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"错误: 无法读取文件 - {e}", file=sys.stderr)
        return 1

    formatter = MarkdownFormatter(
        indent_size=args.indent,
        add_cjk_spaces=args.cjk_spaces,
    )
    formatted = formatter.format(text)

    if args.in_place:
        write_file(args.file, formatted)
        print(f"已格式化: {args.file}")
    elif args.output:
        write_file(args.output, formatted)
        print(f"已输出到: {args.output}")
    else:
        print(formatted, end="")

    return 0


def cmd_score(args: argparse.Namespace) -> int:
    """
    执行评分命令。

    Args:
        args: 命令行参数

    Returns:
        退出码（0成功，1失败）
    """
    try:
        text = read_file(args.file)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {args.file}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"错误: 无法读取文件 - {e}", file=sys.stderr)
        return 1

    scorer = MarkdownScorer()
    result = scorer.score(text)

    if args.json:
        print(scorer.format_json(result))
    else:
        print(scorer.format_report(result))

    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """
    执行导出命令。

    Args:
        args: 命令行参数

    Returns:
        退出码（0成功，1失败）
    """
    try:
        text = read_file(args.file)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {args.file}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"错误: 无法读取文件 - {e}", file=sys.stderr)
        return 1

    exporter = MarkdownExporter()

    try:
        output = exporter.export(text, args.format)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    if args.output:
        write_file(args.output, output)
        print(f"已导出到: {args.output}")
    else:
        print(output, end="")

    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """
    执行TUI服务命令。

    Args:
        args: 命令行参数

    Returns:
        退出码（0成功，1失败）
    """
    if not os.path.exists(args.file):
        print(f"错误: 文件不存在 - {args.file}", file=sys.stderr)
        return 1

    dashboard = TUIDashboard(args.file)
    dashboard.run()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI主入口函数。

    解析命令行参数并分发到对应的子命令处理函数。

    Args:
        argv: 命令行参数列表，若为None则使用sys.argv

    Returns:
        退出码（0成功，1失败）
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    # 分发到子命令
    commands = {
        "preview": cmd_preview,
        "format": cmd_format,
        "score": cmd_score,
        "export": cmd_export,
        "serve": cmd_serve,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
