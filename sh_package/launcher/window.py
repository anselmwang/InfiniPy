from typing import Union
import logging
import os
from dataclasses import dataclass
from typing import List, Tuple

import psutil
import win32.lib.win32con as win32con
import win32gui
import win32process

from search import ListSearcher, MatchResult, TextMatcher

logger = logging.getLogger(os.path.basename(__file__))
# logger.setLevel(logging.DEBUG)


@dataclass
class Window:
    hwnd: int
    class_name: str
    proc_name: str
    title: str

    @staticmethod
    def get_top_most_window() -> "Window":
        return Window.get_windows()[0]

    @staticmethod
    def get_windows(window_filter: "WindowFilter" = None) -> "List[Window] ":
        windows = []

        def winEnumHandler(hwnd, ctx):
            if not win32gui.IsWindowVisible(hwnd):
                return
            if hwnd == self_hwnd:
                return
            title = win32gui.GetWindowText(hwnd)
            if title == "":
                return
            if title == "Windows Input Experience":
                return
            dw_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            if (dw_style & 0x08000000) or not (dw_style & 0x10000000):
                return
            dw_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if dw_ex_style & 0x00000080:
                return
            class_name = win32gui.GetClassName(hwnd)
            if class_name == "TApplication":
                return
            pid = win32process.GetWindowThreadProcessId(hwnd)
            proc_name = psutil.Process(pid[-1]).name()

            cur_win = Window(hwnd, class_name, proc_name, title)
            logger.debug(f"    cur_win: {cur_win}")
            if window_filter is not None and not window_filter.is_match(cur_win):
                return
            windows.append(cur_win)

        logger.debug("get_windows()")
        self_hwnd = win32gui.GetForegroundWindow()
        win32gui.EnumWindows(winEnumHandler, None)
        return windows

    def activate(self):
        tup = win32gui.GetWindowPlacement(self.hwnd)
        if tup[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)

    def maximize(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)
        win32gui.SetForegroundWindow(self.hwnd)

    def minimize(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)
        win32gui.SetForegroundWindow(self.hwnd)


@dataclass
class WindowFilter:
    hwnd: int = -1
    class_name: str = None
    proc_name: str = None
    title: str = None
    cmd: Union[str, List[str]] = ""

    def is_match(self, window: Window) -> bool:
        """Whether window match current filter condition

        hwnd, class_name, proc_name is exact match. `self.title` should be substring of `window.title`.

        Args:
            window (Window):

        Returns:
            bool:
        """
        return (
            (self.hwnd == -1 or self.hwnd == window.hwnd)
            and (self.class_name is None or self.class_name == window.class_name)
            and (self.proc_name is None or self.proc_name == window.proc_name)
            and (self.title is None or self.title in window.title)
        )


class WinListSearcher(ListSearcher):
    def _str_for_matcher(self, window: Window):
        PROC_NAME_MAX_LEN = 20
        return f"{window.proc_name.ljust(PROC_NAME_MAX_LEN)}    {window.title}"

    def _str_for_show(self, match_str: str, window: Window):
        return match_str
