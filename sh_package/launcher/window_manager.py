from typing import List

from search import StrSearcher
import subprocess
from .. import package_manager
from .window import Window, WindowFilter, WinListSearcher


def _get_windows_skip_current_when_has_other(window_filter=None):
    cur_win = Window.get_top_most_window()
    windows: List[Window] = Window.get_windows(window_filter)
    windows_after_filtering = [win for win in windows if win.hwnd != cur_win.hwnd]
    # Avoid launch another instance of current application when user's query only match current window
    if len(windows_after_filtering) == 0:
        return windows
    else:
        return windows_after_filtering


def goto(window: Window) -> None:
    """Goto a window

    Args:
        window (Window):
    """
    window.activate()


package_manager.register_type_searcher_factory(
    Window, lambda: WinListSearcher(_get_windows_skip_current_when_has_other())
)


def goto_specific(window_filter: WindowFilter, window: Window = None):
    if window is None:
        windows = _get_windows_skip_current_when_has_other(window_filter)
        if len(windows) == 1:
            windows[0].activate()
        elif len(windows) == 0:
            result = f"Can't find window with filter '{window_filter}'." 
            launch_cmd = window_filter.cmd
            if launch_cmd != "":
                result += f"Launch by '{launch_cmd}'."
                subprocess.Popen(launch_cmd, shell=True)

                
            return StrSearcher([result])
        else:
            return WinListSearcher(windows)
    else:
        window.activate()


def _goto_specific_intellisense(func_name, *args):
    if len(args) < 1:
        return StrSearcher([])
    elif len(args) == 1:
        win_title = args[0]
        windows = Window.get_windows(win_title)
        return WinListSearcher(windows)


package_manager.register_op_intellisense(goto_specific, _goto_specific_intellisense)


def minimize():
    Window.get_top_most_window().minimize()


def maximize():
    Window.get_top_most_window().maximize()
