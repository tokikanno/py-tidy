import ast
from typing import List, Tuple, Type


def _check_next_line_is_empty(lines: List[str], line_number: int) -> bool:
    if line_number + 1 >= len(lines):
        return True

    return lines[line_number + 1].strip() == ""


def find_spacer_line_numbers(
    node: ast.AST, origin_lines: List[str], ignore_single_line_body: bool = False
) -> List[int]:
    """
    returns: line numbers that need to append a blank line after it.

    CAUTION: the line number starts from 0 and mapped to the origin_lines index.
    """
    result: List[int] = []

    # it's an inline if
    if node.lineno == node.end_lineno:
        return result

    to_check_line_nunbers: List[int] = []
    if node.body:
        if ignore_single_line_body and node.body[0].lineno == node.body[-1].end_lineno:
            pass
        else:
            to_check_line_nunbers.append(node.body[-1].end_lineno)

    if not isinstance(node, ast.ExceptHandler):
        to_check_line_nunbers.append(node.end_lineno)

    for line_number in to_check_line_nunbers:
        # 注意: ast 的 lineno 是從 1 開始的，所以要減 1 才能對應到 list 的 index
        line_number -= 1
        if not _check_next_line_is_empty(origin_lines, line_number):
            result.append(line_number)

    return result


_TO_CHECK_AST_NODE_TYPES: List[Type] = (
    ast.If,
    ast.For,
    ast.While,
    ast.With,
    ast.AsyncFor,
    ast.AsyncWith,
    ast.Try,
    ast.ExceptHandler,
)

# add support for match if possible
try:
    _TO_CHECK_AST_NODE_TYPES += (ast.Match,)
except AttributeError:
    pass


def lint(
    code: str, autofix: bool = False, ignore_single_line_body: bool = False
) -> Tuple[int, List[str]]:
    """
    returns: (error_count, fixed lines/error lines)
    """
    tree = ast.parse(code)
    lines: list[str] = code.splitlines()
    add_empty_line_at_lineno_set: set[int] = set()

    node: ast.AST
    for node in ast.walk(tree):
        if isinstance(
            node,
            _TO_CHECK_AST_NODE_TYPES,
        ):
            if add_empty_line_at := find_spacer_line_numbers(
                node, lines, ignore_single_line_body=ignore_single_line_body
            ):
                add_empty_line_at_lineno_set.update(add_empty_line_at)

    result: List[str] = []

    if autofix:
        for idx, line in enumerate(lines):
            result.append(line)
            if idx in add_empty_line_at_lineno_set:
                result.append("")

    else:
        for line_number in sorted(list(add_empty_line_at_lineno_set)):
            # 此處的 line_number 已經轉換為檔案順序 (從 1 開始計算)
            result.append(f"{line_number + 1}: empty line required")

    return len(add_empty_line_at_lineno_set), result


if __name__ == "__main__":
    code: str = """def test(a: int) -> None:
    if (
       a > 0
       and a == 1
    ):
        # test
        print()
        for i in range(5):
            print(i)
        print("1")
    elif a == 2:
       print("2")
    elif a == 3:
       print("3")    
    else:
        print("else")
    while True:
        print("a")
    else:
        print("b")
    for _ in range(10):
        print("c")
    else:
        print("d")
        try:
           pass
        except Exception as e:
            pass
        finally:
            pass
        with open("xxx.txt") as f:
            print(f.read())
    """

    error_count, lines = lint(code, autofix=True, ignore_single_line_body=False)
    print(f"total {error_count} errors")
    print("\n".join(lines))
