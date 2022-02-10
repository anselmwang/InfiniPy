# %%
from search import MatchResult, Span, StrSearcher
from sh_cmd import Cmd, Op, Symbol, SymbolListSearcher, get_function_signature
from sh_package import package_manager

package_manager.register_type_searcher_factory(
    str, lambda: StrSearcher(["candidate1", "candidate2"])
)


def concat(a: str, b: str):
    """concat two string"""
    return a + b


op_table = [Op("test.concat", concat.__doc__, concat)]


def test_filter():
    symbols = [
        Symbol("goto", "desc: goto a window"),
        Symbol("goto_edge", "desc: goto edge"),
    ]
    searcher = SymbolListSearcher(symbols)
    filtered_records, rendered_filtered_lines, filtered_match_results = searcher.filter(
        "edge"
    )
    assert filtered_records == [symbols[1]]
    assert len(rendered_filtered_lines) == 1
    assert rendered_filtered_lines[0].replace(
        " ", ""
    ) == "goto_edge  desc: goto edge".replace(" ", "")
    assert filtered_match_results == [MatchResult(spans=[Span(start=5, end=9)])]


def test_cmd_basic():
    cmd = Cmd(op_table, package_manager)
    cmd.append(op_table[0])
    cmd.append("a")
    cmd.append("b")
    assert cmd.execute() == "ab"


def test_cmd_get_intellisense_searcher():
    cmd = Cmd(op_table, package_manager)
    assert isinstance(cmd.get_intellisense_searcher(), SymbolListSearcher)
    cmd.append(op_table[0])
    assert isinstance(cmd.get_intellisense_searcher(), StrSearcher)
    cmd.append("a")
    assert isinstance(cmd.get_intellisense_searcher(), StrSearcher)


def f(x, y: int = 5) -> int:
    """doc string of f"""
    return x + y


def test_get_function_signature_with_range_of_a_parameter():
    str_sig, para_start, para_end = get_function_signature(f, 0)
    assert str_sig == "f(x, y: int = 5) -> int"
    assert str_sig[para_start:para_end] == "x"
    str_sig, para_start, para_end = get_function_signature(f, 1)
    assert str_sig[para_start:para_end] == "y: int = 5"
