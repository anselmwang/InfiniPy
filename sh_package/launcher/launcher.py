import functools
import logging
import os
import subprocess
import sys
import time
import webbrowser
from os.path import expanduser
from typing import Callable

from .clipboard import get_clipboard_text
from .window import Window, WindowFilter

logger = logging.getLogger(os.path.basename(__file__))

def goto_dir(dir_path: str):
    if not os.access(dir_path, os.F_OK):
        raise FileNotFoundError(dir_path)
    if not os.path.isdir(dir_path):
        raise ValueError(f"'{dir_path} is not a directory")
    os.startfile(dir_path)
    # hwnd = win32api.ShellExecute(None, "open", dir_path, None, None, 1)

def goto_url(url: str):
    webbrowser.open_new_tab(url)

def goto_onenote(onenote_url: str):
    assert onenote_url.startswith("onenote:https://")
    os.startfile(onenote_url)

def open_with_vscode(vscode_title: str, file_path: str, func_to_start_vscode: Callable=None, line_no=0):
    smart_activate(WindowFilter(proc_name="Code.exe", title=vscode_title), func_to_start_vscode)
    subprocess.run(["code", "-r", "-g", f"{file_path}:{line_no}"], shell=True)     

def open_with_vscode_using_clipboard_path(vscode_title: str, func_to_start_vscode: Callable=None):
    file_path: str = get_clipboard_text()
    if not os.path.isfile(file_path):
        raise Exception(f"'{file_path}' is not a file")
    open_with_vscode(vscode_title, file_path, func_to_start_vscode)

def smart_activate(window_filter: WindowFilter, func_to_start: Callable = None, check_interval: float = 1, max_retry: int = 20):
    windows = Window.get_windows(window_filter)
    if len(windows) > 1:
        raise Exception(f"Find more than one window with filter '{window_filter}'")
    elif len(windows) == 0:
        if func_to_start is not None:
            func_to_start()
            for i in range(max_retry):
                time.sleep(check_interval)
                windows = Window.get_windows(window_filter)
                if len(windows) != 0:
                    # one additional sleep to ensure window fully ready, vscode need this additional sleep, otherwise activate() will fail
                    time.sleep(check_interval)
                    break
            else:
                raise Exception(f"Fail to find window {window_filter} after {max_retry} retries.")
        else:
            raise Exception(f"Can't find window with filter '{window_filter}'")
    windows = Window.get_windows(window_filter)
    windows[0].activate()

def open_folder_with_vscode(folder_path: str):
    subprocess.run(["code", folder_path], shell=True)

def open_file_in_project_develop_environment(proj_folder, file_path):
    proj_name = os.path.basename(os.path.normpath(proj_folder))
    return open_with_vscode(proj_name, file_path, functools.partial(open_folder_with_vscode, proj_folder))


HOME = os.getenv("HOME")
if HOME is None:
    HOME = expanduser("~")

SCRATCH_WORKSPACE_NAME = "scratch_workspace"
SCRATCH_WORKSPACE_ROOT = os.path.join(HOME, SCRATCH_WORKSPACE_NAME)
SCRATCH_FILE_PATH = os.path.join(SCRATCH_WORKSPACE_ROOT, SCRATCH_WORKSPACE_NAME + ".md")
if not os.access(SCRATCH_WORKSPACE_ROOT, os.F_OK):
    os.makedirs(SCRATCH_WORKSPACE_ROOT, exist_ok=True)
if not os.path.isdir(SCRATCH_WORKSPACE_ROOT):
    print(f"{SCRATCH_WORKSPACE_ROOT} is not a directory.")
    sys.exit(1)
else:
    if not os.access(SCRATCH_FILE_PATH, os.F_OK):
        open(SCRATCH_FILE_PATH, "w", encoding="utf-8").close()
    if not os.path.isfile(SCRATCH_FILE_PATH):
        print(f"{SCRATCH_FILE_PATH} is not a file.")
        sys.exit(1)

def open_scratch_workspace():
    OPEN_SCRATCH_WORKSPACE = functools.partial(open_folder_with_vscode, SCRATCH_WORKSPACE_ROOT)
    open_with_vscode(SCRATCH_WORKSPACE_NAME, SCRATCH_FILE_PATH, OPEN_SCRATCH_WORKSPACE)

def open_clipboard_path_in_scratch_workspace():
    OPEN_SCRATCH_WORKSPACE = functools.partial(open_folder_with_vscode, SCRATCH_WORKSPACE_ROOT)
    open_with_vscode_using_clipboard_path(SCRATCH_WORKSPACE_NAME, OPEN_SCRATCH_WORKSPACE)
