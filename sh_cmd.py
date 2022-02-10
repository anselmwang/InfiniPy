import copy
import inspect
import logging
import os
import pprint
from dataclasses import dataclass
from inspect import _empty, getmembers, isbuiltin, isfunction, ismodule, signature
from typing import Callable, Dict, List, Tuple, Type, Union

from search import ListSearcher, StrSearcher

logger = logging.getLogger(os.path.basename(__file__))
# logger.setLevel(logging.INFO)


@dataclass
class Symbol:
    name: str
    description: str


@dataclass
class Op(Symbol):
    op: Callable


class SymbolListSearcher(ListSearcher):
    def _str_for_matcher(self, symbol: Symbol):
        return symbol.name

    def _str_for_show(self, match_str: str, symbol: Symbol):
        SYMBOL_NAME_MAX_LEN = 40
        return f"{match_str.ljust(SYMBOL_NAME_MAX_LEN)}    {symbol.description}"


def get_required_parameter_count(op):
    parameters = signature(op).parameters
    required_parameters = []
    for name, para in parameters.items():
        if para.default != inspect._empty:
            break
        required_parameters.append(name)
    return len(required_parameters)


def get_function_parameter_count(f):
    signature = inspect.signature(f)
    return len(signature.parameters)


def get_function_signature(f, cur_para_no=None) -> Union[str, Tuple[str, int, int]]:
    """Get function signature, also return the character range of `cur_para_no`

    Args:
        f ([type]): [description]
        cur_para_no ([type], optional): [description]. Defaults to None.

    Returns:
        Union[str, Tuple[str, int, int]]:
            Return signature only if `cur_para_no` is None, otherwise, also return the character range of `cur_para_no`
    """
    signature = inspect.signature(f)
    if cur_para_no is not None:
        assert cur_para_no < len(
            signature.parameters
        ), f"cur_para_no {cur_para_no} is larger than function parameter count {len(signature.parameters)}"

    result_list = [f"{f.__name__}("]
    cur_pos = len(result_list[0])
    for no, para in enumerate(signature.parameters.values()):
        if no == 0:
            result_list.append(str(para))
        else:
            result_list.append(f", {str(para)}")

        if no == cur_para_no:
            if no == 0:
                para_start = cur_pos
            else:
                para_start = cur_pos + 2  # skip the ", "
            para_end = cur_pos + len(result_list[-1])
        cur_pos += len(result_list[-1])

    result_list.append(")")
    if signature.return_annotation == inspect._empty:
        str_return_annotation = ""
    else:
        if isinstance(signature.return_annotation, type):
            str_return_annotation = f" -> {signature.return_annotation.__name__}"
        else:
            str_return_annotation = f" -> {signature.return_annotation}"
    result_list.append(str_return_annotation)

    str_sig = "".join(result_list)
    if cur_para_no is None:
        return str_sig
    else:
        return str_sig, para_start, para_end


class Cmd:
    def __init__(self, op_list: List[Op], package_manager):
        self._cmd = []
        self._op_list = op_list
        self._op_name_2_op_dict = {op.name: op for op in self._op_list}
        self._op_func_2_op_dict = {op.op: op for op in self._op_list}
        self._package_manager = package_manager

    def get_op(self):
        assert len(self._cmd) > 0
        return self._cmd[0]

    def set(self, func, args):
        cur_op: Op = self._op_func_2_op_dict[func]
        cmd_segs = [cur_op] + args
        self._cmd = cmd_segs

    def clear(self):
        self._cmd.clear()

    def append(self, seg):
        self._cmd.append(seg)
        logger.debug(f"Current cmd: {pprint.pformat(self._cmd)}")

    def pop(self):
        self._cmd.pop()
        logger.debug(f"Current cmd: {pprint.pformat(self._cmd)}")

    def __str__(self):
        return str(self._cmd)

    def get_help(self):
        cmd_segs = self._cmd
        file_path, line_no, help_message, para_start, para_end = (
            None,
            None,
            None,
            None,
            None,
        )
        if len(cmd_segs) != 0:
            op: Callable = cmd_segs[0].op
            cur_para_no = len(cmd_segs) - 1
            if cur_para_no == get_function_parameter_count(op):
                help_message = get_function_signature(op)
            else:
                help_message, para_start, para_end = get_function_signature(
                    op, cur_para_no
                )
            if op.__doc__ is not None:
                help_message += "\n" + op.__doc__

            try:
                # builtins like `listdir` doesn't have __globals__
                file_path = op.__globals__["__file__"]
                line_no = (
                    inspect.findsource(op)[1] + 1
                )  # the returned line number is right before `def`
            except:
                pass
        return file_path, line_no, help_message, para_start, para_end

    def execute(self):
        assert isinstance(self._cmd[0], Op)
        op: Callable = self._cmd[0].op
        sig = signature(op)
        para_names = list(sig.parameters.keys())
        arguments = []

        if get_required_parameter_count(op) > (len(self._cmd) - 1):
            return self.get_intellisense_searcher()

        if len(self._cmd) - 1 > len(para_names):
            return SymbolListSearcher(
                [
                    Symbol(
                        "Syntax Error", f"function signature: {op.__name__ + str(sig)}"
                    )
                ]
            )

        logger.info(f"Execute {self._cmd}")
        for para_no, argument in enumerate(self._cmd[1:]):
            para_name = para_names[para_no]
            para_type = sig.parameters[para_name].annotation
            if para_type == inspect._empty or isinstance(argument, para_type):
                pass
            elif isinstance(argument, str) and para_type != str:
                try:
                    argument = argument.strip()
                    if para_type == int or para_type == float:
                        argument = para_type(argument)
                    elif para_type == bool:
                        if argument == "True":
                            argument = True
                        elif argument == "False":
                            argument = False
                        else:
                            raise TypeError()
                    else:
                        raise TypeError()
                except:
                    raise TypeError(
                        f"Parameter {para_name}(no {para_no}): Can't convert {argument} to type {para_type}"
                    )
            else:
                raise TypeError(
                    f"Parameter {para_name}(no {para_no}): Can't convert {argument} to type {para_type}"
                )
            arguments.append(argument)

        return op(*arguments)

    def get_intellisense_searcher(self):
        segs = self._cmd
        if len(segs) == 0:
            return SymbolListSearcher(self._op_list)
        else:
            assert isinstance(segs[0], Op)
            op: Callable = segs[0].op
            sig = signature(op)
            para_names = list(sig.parameters.keys())
            cur_para_no = len(segs) - 1
            if cur_para_no >= len(para_names):
                return SymbolListSearcher(
                    [
                        Symbol(
                            "Syntax Error",
                            f"function signature: {op.__name__ + str(sig)}",
                        )
                    ]
                )
            elif self._package_manager.get_searcher_factory_by_op(op) is not None:
                return self._package_manager.get_searcher_factory_by_op(op)(
                    op, *self._cmd[1:]
                )
            else:
                para_name = para_names[cur_para_no]
                para_type = sig.parameters[para_name].annotation
                searcher_factory = self._package_manager.get_searcher_factory_by_type(
                    para_type
                )
                if searcher_factory is not None:
                    return searcher_factory()
                else:
                    return StrSearcher([])
