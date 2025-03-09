import argparse
import os
import sys
from typing import Iterable, List, Optional

from pathspec import PathSpec

from .control_block_spacer import lint


def _load_git_ignore() -> Optional[PathSpec]:
    try:
        with open(".gitignore", "r") as f:
            content = f.read()

        return PathSpec.from_lines("gitwildmatch", content.splitlines())

    except IOError:
        return None


def _py_file_iter(root_dir: str = ".") -> Iterable[str]:
    ignore_spec: Optional[PathSpec] = _load_git_ignore()

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                filename: str = os.path.join(root, file)
                if ignore_spec is None or not ignore_spec.match_file(filename):
                    yield filename


def main() -> None:
    parser = argparse.ArgumentParser(
        description="py-tidy: a small utility for custom code linting and formatting\n\n*If no filenames given, it will lint all .py files in the current directory and its subdirectories.*",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Lint files")
    lint_parser.add_argument(
        "filenames", type=str, nargs="*", help="Files to be linted"
    )

    # Format command
    format_parser = subparsers.add_parser(
        "format", help="Format files. CAUTION: in-place fixes will be applied!!!"
    )
    format_parser.add_argument(
        "filenames", type=str, nargs="*", help="Files to be formatted"
    )

    args = parser.parse_args()
    total_files: int = 0
    total_error_files: int = 0

    filename_iter = args.filenames if args.filenames else _py_file_iter()

    for filename in filename_iter:
        with open(filename, "r") as f:
            err_cnt: int
            result: List[str]
            err_cnt, result = lint(f.read(), autofix=args.command == "format")

        total_files += 1

        if err_cnt == 0:
            continue

        total_error_files += 1

        if args.command == "lint":
            for line in result:
                print(f"{filename}:{line}")

        elif args.command == "format":
            with open(filename, "w") as f:
                f.write("\n".join(result))

            print(f"{filename}: {err_cnt} auto fixes applied.")

        else:
            raise ValueError("Invalid command")

    if total_error_files > 0:
        if args.command == "lint":
            sys.exit(1)

    else:
        print(f"Processed {total_files} files. No errors found.")


if __name__ == "__main__":
    main()
