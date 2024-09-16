from __future__ import annotations

import argparse
from pathlib import Path
import sys

from nbmetaclean.check import check_nb_ec, check_nb_errors, check_nb_warnings
from nbmetaclean.helpers import get_nb_names_from_list, read_nb
from nbmetaclean.version import __version__


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
parser.add_argument(
    "-v",
    "--version",
    action="store_true",
    help="Print version information.",
)


def print_error(
    nbs: list[Path],
    message: str,
) -> None:
    """Print error message."""
    print(f"{len(nbs)} notebooks with {message}:")
    for nb in nbs:
        print("- ", nb)


def print_results(
    wrong_ec: list[Path],
    nb_errors: list[Path],
    nb_warnings: list[Path],
    read_error: list[Path],
) -> None:
    """Print results."""
    if wrong_ec:
        print_error(wrong_ec, "wrong execution_count")
    if nb_errors:
        print_error(nb_errors, "errors in outputs")
    if nb_warnings:
        print_error(nb_warnings, "warnings in outputs")
    if read_error:
        print_error(read_error, "read error")


def app_check() -> None:
    """Check notebooks for correct sequence of execution_count and errors in outputs."""
    cfg = parser.parse_args()

    if cfg.version:
        print(f"nbcheck from nbmetaclean, version: {__version__}")
        sys.exit(0)

    if not cfg.ec and not cfg.err and not cfg.warn:
        print(
            "No checks are selected. Please select at least one check: "
            "--ec (for execution_count) or "
            "--err (for errors in outputs) or "
            "--warn (for warnings in outputs)."
        )
        sys.exit(1)

    nb_files = get_nb_names_from_list(cfg.path)
    read_error: list[Path] = []
    if cfg.verbose:
        print(f"Checking {len(nb_files)} notebooks.")

    wrong_ec: list[Path] = []
    nb_errors: list[Path] = []
    nb_warnings: list[Path] = []
    for nb_name in nb_files:
        nb = read_nb(nb_name)
        if nb is None:
            read_error.append(nb_name)
            continue

        if cfg.ec and not check_nb_ec(nb, not cfg.not_strict, cfg.no_exec):
            wrong_ec.append(nb_name)

        if cfg.err and not check_nb_errors(nb):
            nb_errors.append(nb_name)

        if cfg.warn and not check_nb_warnings(nb):
            nb_warnings.append(nb_name)

    print_results(wrong_ec, nb_errors, nb_warnings, read_error)

    if wrong_ec or nb_errors or nb_warnings or read_error:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    app_check()
