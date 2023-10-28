import argparse
from pathlib import Path

from .clean import clean_nb_file
from .core import get_nb_names

parser = argparse.ArgumentParser(
    prog="nbclean",
    description="Clean metadata and execution_count from Jupyter notebooks.",
)
parser.add_argument(
    "path",
    default=".",
    nargs="*",
    help="Path for nb or folder with notebooks.",
)
parser.add_argument(
    "-s",
    "--silent",
    action="store_true",
    help="Silent mode.",
)
parser.add_argument(
    "--not-pt",
    action="store_true",
    help="Do not preserve timestamp.",
)


def app() -> None:
    """Clean metadata and execution_count from Jupyter notebook."""
    cfg = parser.parse_args()
    path_list = cfg.path if isinstance(cfg.path, list) else [cfg.path]
    nb_files: list[Path] = []
    if not cfg.silent:
        print(f"Path: {', '.join(cfg.path)}, preserve timestamp: {not cfg.not_pt}")
    for path in path_list:
        try:
            nb_files.extend(get_nb_names(path))
        except FileNotFoundError:
            print(f"{path} not exists!")
    if not cfg.silent:
        print(f"notebooks to check: {len(nb_files)} ")
    cleaned = clean_nb_file(
        nb_files,
        silent=cfg.silent,
        preserve_timestamp=not cfg.not_pt,
    )
    if not cfg.silent:
        print(f"cleaned nbs: {len(cleaned)}")


if __name__ == "__main__":
    app()
