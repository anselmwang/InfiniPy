import logging
import os

from space_key import SpaceKeyNode, SpaceKeyNodeListSearcher

logger = logging.getLogger(os.path.basename(__file__))
# logger.setLevel(logging.INFO)
branch_checkout_node = SpaceKeyNode("c", "checkout", None, lambda: logger.info("invoke checkout"))
branch_delete_node = SpaceKeyNode("d", "delete", None, lambda: logger.info("invoke delete"))
branch_node = SpaceKeyNode("b", "branch", [
    branch_checkout_node,
    branch_delete_node],
    None
)
push_node = SpaceKeyNode("p", "push", None, lambda: logger.info("invoke push"))
git_node = SpaceKeyNode("g", "git", [
    push_node,
    branch_node],
    None
    )

def test_constructor():
    assert git_node.key == 'g'

def test_walk():
    assert git_node.is_valid_next_key("d") == False
    assert git_node.walk_to("p") == push_node

def test_searcher():
    searcher = SpaceKeyNodeListSearcher(git_node.children)
    filtered_records, _, _ = searcher.filter("b")
    assert filtered_records == [branch_node]
    searcher = SpaceKeyNodeListSearcher(git_node.children)
    filtered_records, _, _ = searcher.filter("B")
    assert filtered_records == []