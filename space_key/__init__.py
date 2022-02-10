# %%
import logging
import os
from typing import Any, Callable, List, Optional

from search import ListSearcher, TextMatcher

logger = logging.getLogger(os.path.basename(__file__))


class SpaceKeyNode:
    def __init__(
        self,
        key: str,
        comment: str,
        children: "Optional[List[SpaceKeyNode]]",
        op_func: Optional[Callable[[], Any]] = None,
    ):
        assert len(key) == 1, "Can only have one char."
        self._key = key
        self._comment = comment
        assert (children is None and op_func is not None) or (
            children is not None and op_func is None
        )

        self._children = children
        self._op_func = op_func
        self._key_map = None
        if children is not None:
            self._key_map = {child.key: child for child in children}

    @staticmethod
    def _customize_key_sort_value(ch):
        """Customize sort algorithm, similar to VSpaceCode

        Args:
            ch ([type]): [description]

        Returns:
            [type]: [description]
        """
        if ch.isupper():
            return ord(ch) + 256
        return ord(ch)

    def _get_children(self):
        self._children.sort(key=lambda x: self._customize_key_sort_value(x.key))
        return self._children

    key = property(lambda self: self._key)
    comment = property(lambda self: self._comment)
    children = property(_get_children)
    op_func = property(lambda self: self._op_func)

    def is_leaf(self):
        return self._key_map is None

    def is_valid_next_key(self, key):
        return not self.is_leaf() and key in self._key_map

    def walk_to(self, key):
        assert len(key) == 1, "Can only have one char."
        assert self.is_valid_next_key(key)
        return self._key_map[key]

    def add_child(self, node):
        existing_node = self._key_map.get(node.key, None)
        if existing_node is not None:
            logger.warn(f"Overwrite from '{existing_node}' to '{node}'")
            self._children.remove(existing_node)
        self._children.append(node)
        self._key_map[node.key] = node

    def remove_child(self, key):
        assert key in self._key_map
        existing_node = self._key_map[key]
        del self._key_map[key]
        self._children.remove(existing_node)

    def __str__(self):
        return f'SpaceKeyNode(key="{self.key}", comment="{self.comment}", children="<skip>", op_func={self.op_func}'


# %%
class SpaceKeyNodeListSearcher(ListSearcher):
    def __init__(self, objects):
        super().__init__(objects, False)

    def _str_for_matcher(self, space_key_node: SpaceKeyNode):
        return space_key_node.key

    def _str_for_show(self, match_str: str, space_key_node: SpaceKeyNode):
        comment = space_key_node.comment
        if space_key_node.op_func is None:
            comment = "+" + comment
        return f"{match_str}    {comment}"


# %%
# %%
