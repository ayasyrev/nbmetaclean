import argparse

from .check import check_nb_ec, check_nb_errors
from .helpers import get_nb_names_from_list, read_nb

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
    "--not_strict",
    action="store_true",
    help="Not strict mode.",
)
parser.add_argument(
    "--not_exec",
    action="store_true",
    help="Ignore notebooks with all code cells without execution_count.",
)
parser.add_argument(
    "-V",
    "--verbose",
    action="store_true",
    help="Verbose mode. Print extra information.",
)


def app_check() -> None:
    """Check notebooks for correct sequence of execution_count and errors in outputs."""
    cfg = parser.parse_args()
    print(cfg)
    if not cfg.ec and not cfg.err:
        print(
            "No checks are selected. Please select at least one check: "
            "--ec (for execution_count) or --err (for errors in outputs)."
        )
        return

    nb_files = get_nb_names_from_list(cfg.path)
    if cfg.verbose:
        print(f"Checking {len(nb_files)} notebooks:")

    if cfg.ec:
        wrong_ec = []
        for nb in nb_files:
            result = check_nb_ec(
                read_nb(nb),
                not cfg.not_strict,
                cfg.not_exec,
            )
            if not result:
                wrong_ec.append(nb)

        if wrong_ec:
            print(f"{len(wrong_ec)} notebooks with wrong execution count:")
            for nb in wrong_ec:
                print("- ", nb)

    if cfg.err:
        wrong_err = []
        for nb in nb_files:
            result = check_nb_errors(read_nb(nb))
            if not result:
                wrong_err.append(nb)

        if wrong_err:
            print(f"{len(wrong_err)} notebooks with some errors in outputs:")
            for nb in wrong_err:
                print("- ", nb)


if __name__ == "__main__":
    app_check()
