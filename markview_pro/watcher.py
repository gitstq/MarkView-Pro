"""
文件监听模块 - 基于轮询的文件变更监听器。

使用 os 模块轮询文件修改时间实现文件变更检测，
不依赖 watchdog 等外部库。

功能特性：
- 可配置轮询间隔
- 文件变更时触发回调函数
- 支持优雅退出（Ctrl+C）
- 文件创建/删除检测
"""

import os
import sys
import time
from typing import Callable, Optional


class FileWatcher:
    """
    基于轮询的文件变更监听器。

    通过定期检查文件的修改时间戳来检测文件变更，
    当检测到变更时调用用户指定的回调函数。

    Attributes:
        filepath: 监听的文件路径
        interval: 轮询间隔（秒）
        callback: 文件变更时的回调函数
        running: 是否正在运行
    """

    def __init__(self, filepath: str,
                 callback: Optional[Callable[[str], None]] = None,
                 interval: float = 1.0) -> None:
        """
        初始化文件监听器。

        Args:
            filepath: 要监听的文件路径
            callback: 文件变更时的回调函数，接收文件路径作为参数
            interval: 轮询间隔（秒），默认1.0秒
        """
        self.filepath: str = filepath
        self.callback: Optional[Callable[[str], None]] = callback
        self.interval: float = interval
        self.running: bool = False
        self._last_mtime: float = 0.0
        self._last_size: int = 0

    def start(self) -> None:
        """
        启动文件监听。

        开始轮询文件变更，阻塞当前线程直到调用 stop()。
        支持通过 Ctrl+C (KeyboardInterrupt) 优雅退出。

        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"文件不存在: {self.filepath}")

        self.running = True
        self._last_mtime = self._get_mtime()
        self._last_size = self._get_size()

        try:
            while self.running:
                self._check()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stop()
            print("\n文件监听已停止。")

    def stop(self) -> None:
        """
        停止文件监听。

        将 running 标志设为 False，使轮询循环退出。
        """
        self.running = False

    def check_once(self) -> bool:
        """
        执行一次文件变更检查。

        非阻塞方式检查文件是否有变更。

        Returns:
            True 表示文件有变更，False 表示无变更
        """
        if not os.path.exists(self.filepath):
            return False

        current_mtime = self._get_mtime()
        current_size = self._get_size()

        if current_mtime != self._last_mtime or current_size != self._last_size:
            self._last_mtime = current_mtime
            self._last_size = current_size
            return True

        return False

    def _check(self) -> None:
        """
        执行一次文件变更检查并触发回调。

        内部方法，在轮询循环中调用。
        """
        if not os.path.exists(self.filepath):
            # 文件被删除
            if self.callback:
                self.callback(self.filepath)
            return

        if self.check_once():
            if self.callback:
                self.callback(self.filepath)

    def _get_mtime(self) -> float:
        """
        获取文件修改时间。

        Returns:
            文件修改时间戳

        Raises:
            OSError: 文件访问失败
        """
        try:
            stat = os.stat(self.filepath)
            return stat.st_mtime
        except OSError:
            return 0.0

    def _get_size(self) -> int:
        """
        获取文件大小。

        Returns:
            文件大小（字节）
        """
        try:
            stat = os.stat(self.filepath)
            return stat.st_size
        except OSError:
            return 0

    def set_callback(self, callback: Callable[[str], None]) -> None:
        """
        设置或更新文件变更回调函数。

        Args:
            callback: 回调函数，接收文件路径作为参数
        """
        self.callback = callback

    def set_interval(self, interval: float) -> None:
        """
        设置轮询间隔。

        Args:
            interval: 轮询间隔（秒）
        """
        if interval < 0.1:
            raise ValueError("轮询间隔不能小于0.1秒")
        self.interval = interval
