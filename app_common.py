import os
from os.path import expanduser
from typing import Callable, List, Tuple, Union

from space_key import SpaceKeyNode

PROJ_NAME = "InfiniPy"

HOME = os.getenv("HOME")
if HOME is None:
    HOME = expanduser("~")
print(HOME)

PROJ_HOME = os.path.join(HOME, "." + PROJ_NAME.lower())
LOG_PATH = "{0}/log.txt".format(PROJ_HOME)
SOURCE_CODE_ROOT = os.getcwd()


def invoke_cmd_frame(func: Callable, args: List, is_execute):
    raise NotImplementedError("Please call register_invoke_cmd_frame first")


def register_invoke_cmd_frame(func):
    global invoke_cmd_frame
    invoke_cmd_frame = func


def build_function_to_invoke_cmd_frame(
    func: Callable = None, args: List = [], is_execute=False
):
    def inner():
        invoke_cmd_frame(func, args, is_execute)

    return inner


class Leaf(SpaceKeyNode):
    def __init__(
        self,
        key: str,
        comment: str,
        cmd_func: Callable = None,
        args=[],
        is_execute=True,
    ):
        wrapped_func = build_function_to_invoke_cmd_frame(cmd_func, args, is_execute)
        super().__init__(key, comment, None, wrapped_func)


def add_space_key_children(root_node: SpaceKeyNode, key_seq, config_table, func):
    parent_node = walk_space_key_tree(root_node, key_seq)
    for key, parameters in config_table.items():
        canonical_name = parameters[0]
        parent_node.add_child(Leaf(key, f"Goto {canonical_name}", func, parameters[1:]))


def walk_space_key_tree(root_node: SpaceKeyNode, key_seq: List):
    parent_node = root_node
    for key in key_seq:
        parent_node = parent_node.walk_to(key)
    return parent_node
