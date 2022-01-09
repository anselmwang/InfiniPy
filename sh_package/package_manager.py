import inspect
from inspect import getmembers, isbuiltin, isfunction, ismodule, signature, _empty
from types import ModuleType
from typing import List
from sh_cmd import Op

TYPE_2_SEARCHER_FACTORY_DICT = {
}

def register_type_searcher_factory(type_obj, searcher_factory):
    assert type_obj not in TYPE_2_SEARCHER_FACTORY_DICT
    TYPE_2_SEARCHER_FACTORY_DICT[type_obj] = searcher_factory

def get_searcher_factory_by_type(type_obj):
    return TYPE_2_SEARCHER_FACTORY_DICT.get(type_obj, None)


OP_2_SEARCHER_FACTORY_DICT = {
}
def register_op_intellisense(op, searcher_factory):
    assert op not in OP_2_SEARCHER_FACTORY_DICT
    OP_2_SEARCHER_FACTORY_DICT[op] = searcher_factory

def get_searcher_factory_by_op(op):
    return OP_2_SEARCHER_FACTORY_DICT.get(op, None)

def build_op_list(package_config: ModuleType) -> List[Op]:
    """Given a module which imported a list of packages, discover all exposed operations in the packages"""
    op_list = []
    module_pairs = getmembers(package_config, ismodule)
    module_pairs.append(("", package_config))
    for module_name, module in module_pairs:
        op_pairs = getmembers(module, lambda member: isfunction(member) or isbuiltin(member))
        for op_name, one_op in op_pairs:
            if op_name.startswith("_"):
                continue
            sig = signature(one_op)
            if one_op.__doc__ is None:
                simple_doc = ""
            else:
                lines = one_op.__doc__.split("\n")
                if len(lines) == 0:
                    simple_doc = ""
                else:
                    simple_doc = lines[0]
            op_full_name = f"{module_name}.{op_name}"
            op_list.append(Op(op_full_name, simple_doc, one_op))
    return op_list