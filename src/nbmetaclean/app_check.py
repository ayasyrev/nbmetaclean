from __future__ import annotations

import argparse
from pathlib import Path
import sys

from nbmetaclean.check import check_nb_ec, check_nb_errors, check_nb_warnings
from nbmetaclean.helpers import get_nb_names_from_list, read_nb

parser = argparse.ArgumentParser(
    prog="nbcheck",
    description="Check Jupyter notebooks for correct sequence of execution_count and (or) errors in outputs.",
)
parser.add_argument(
    "path",
    default=".",
    nargs="*",
    help="Path for nb or folder with notebooks.",
)
parser.add_argument(
    "--ec",
    action="store_true",
    help="Check execution_count.",
)
parser.add_argument(
    "--err",
    action="store_true",
    help="Check errors in outputs.",
)
parser.add_argument(
    "--warn",
    action="store_true",
    help="Check warnings in outputs.",
)
parser.add_argument(
    "--not_strict",
    action="store_true",
    help="Not strict mode.",
)
parser.add_argument(
    "--no_exec",
    action="store_true",
    help="Ignore notebooks with all code cells without execution_count.",
)
parser.add_argument(
    "-V",
    "--verbose",
    action="store_true",
    help="Verbose mode. Print extra information.",
)


def check_ec(nb_files: list[Path], strict: bool, no_exec: bool) -> list[Path]:
    """Check notebooks for correct sequence of execution_count and errors in outputs."""
    wrong_ec = []
    for nb in nb_files:
        result = check_nb_ec(
            read_nb(nb),
            strict,
            no_exec,
        )
        if not result:
            wrong_ec.append(nb)

    return wrong_ec


def check_errors(nb_files: list[Path]) -> list[Path]:
    """Check notebooks for errors in outputs."""
    nb_errors = []
    for nb in nb_files:
        result = check_nb_errors(read_nb(nb))
        if not result:
            nb_errors.append(nb)

    return nb_errors


def check_warnings(nb_files: list[Path]) -> list[Path]:
    """Check notebooks for warnings in outputs."""
    nb_warnings = []
    for nb in nb_files:
        result = check_nb_warnings(read_nb(nb))
        if not result:
            nb_warnings.append(nb)

    return nb_warnings


def print_results(
    nbs: list[Path],
    message: str,
) -> None:
    """Print results."""
    print(f"{len(nbs)} notebooks with {message}:")
    for nb in nbs:
        print("- ", nb)


def app_check() -> None:
    """Check notebooks for correct sequence of execution_count and errors in outputs."""
    cfg = parser.parse_args()
    if not cfg.ec and not cfg.err and not cfg.warn:
        print(
            "No checks are selected. Please select at least one check: "
            "--ec (for execution_count) or "
            "--err (for errors in outputs) or "
            "--warn (for warnings in outputs)."
        )
        return

    nb_files = get_nb_names_from_list(cfg.path)
    if cfg.verbose:
        print(f"Checking {len(nb_files)} notebooks:")

    check_passed = True
    if cfg.ec:
        wrong_ec = check_ec(nb_files, not cfg.not_strict, cfg.no_exec)

        if wrong_ec:
            print_results(wrong_ec, "wrong execution_count")
            check_passed = False

    if cfg.err:
        nb_errors = check_errors(nb_files)

        if nb_errors:
            print_results(nb_errors, "errors in outputs")
            check_passed = False

    if cfg.warn:
        nb_warnings = check_warnings(nb_files)

        if nb_warnings:
            print_results(nb_warnings, "warnings in outputs")
            check_passed = False

    if not check_passed:
        sys.exit(1)


if __name__ == "__main__":
    app_check()
