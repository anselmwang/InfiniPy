import os

import package_config
from app_common import (
    PROJ_HOME,
    PROJ_NAME,
    SOURCE_CODE_ROOT,
    Leaf,
    add_space_key_children,
)
from package_config import *
from space_key import SpaceKeyNode

space_key_config_path = os.path.join(PROJ_HOME, "space_key_config.py")
if not os.path.isfile(space_key_config_path):
    space_key_config_path = os.path.join(SOURCE_CODE_ROOT, "space_key_config.py")
    if not os.path.isfile(space_key_config_path):
        raise Exception("Can't find space_key_config.py")


root_node = SpaceKeyNode(
    " ",
    "root",
    [
        Leaf(" ", "Run cmd", None, [], False),
        SpaceKeyNode(
            "w",
            "Window",
            [Leaf(" ", "Goto windows without space key", launcher.goto, [], False)],
        ),
        SpaceKeyNode(
            "W",
            "Window Manager",
            [
                Leaf("m", "Minimize", launcher.minimize),
                Leaf("M", "Maximize", launcher.maximize),
            ],
        ),
        SpaceKeyNode(
            "f",
            "File",
            [
                Leaf("s", "Goto scratch workspace", launcher.open_scratch_workspace),
                Leaf(
                    "o",
                    "Open clipboard file path",
                    launcher.open_clipboard_path_in_scratch_workspace,
                    [],
                ),
            ],
        ),
        SpaceKeyNode("d", "Directory", []),
        SpaceKeyNode("u", "URL", []),
        SpaceKeyNode("n", "OneNote Page", []),
        SpaceKeyNode("c", "Command", [Leaf("c", "Calculator", fun.calc)]),
        SpaceKeyNode(
            "D",
            f"{PROJ_NAME} Develop",
            [
                Leaf(
                    "p",
                    "open package config",
                    launcher.open_file_in_project_develop_environment,
                    [SOURCE_CODE_ROOT, package_config.__file__],
                ),
                Leaf(
                    "s",
                    "open Space Key config",
                    launcher.open_file_in_project_develop_environment,
                    [SOURCE_CODE_ROOT, space_key_config_path],
                ),
                Leaf(
                    "h", f"Goto to project home folder", launcher.goto_dir, [PROJ_HOME]
                ),
            ],
        ),
    ],
    None,
)


wm_table = {
    "b": ["browser", launcher.WindowFilter(proc_name="msedge.exe")],
    "t": ["totalcmd", launcher.WindowFilter(proc_name="TOTALCMD64.EXE")],
    "n": ["onenote", launcher.WindowFilter(proc_name="ONENOTE.EXE")],
    "o": ["outlook", launcher.WindowFilter(proc_name="OUTLOOK.EXE")],
    "c": ["console", launcher.WindowFilter(proc_name="ConEmu64.exe")],
    "e": ["emacs", launcher.WindowFilter(title="emacs main")],
    "d": ["dev", launcher.WindowFilter(proc_name="Code.exe")],
    "p": ["pdf", launcher.WindowFilter(proc_name="Acrobat.exe")],
}
add_space_key_children(root_node, "w", wm_table, launcher.goto_specific)


dir_table = {"o": ["Disk c", r"C:"]}
add_space_key_children(root_node, "d", dir_table, launcher.goto_dir)

url_table = {
    "a": ["Azure Portal", "https://portal.azure.com/"],
    "t": [
        "Translate",
        "https://www.google.com/search?q=translate+english+to+chinese&oq=translate+",
    ],
}
add_space_key_children(root_node, "u", url_table, launcher.goto_url)

note_table = {
    "w": ["main work page", "onenote:https://d.docs.live.net/fake_note_page"],
}
add_space_key_children(root_node, "n", note_table, launcher.goto_onenote)
