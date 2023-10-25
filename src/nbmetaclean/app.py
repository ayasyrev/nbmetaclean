from dataclasses import dataclass
from pathlib import Path

import nbformat
from argparsecfg.app import App
from argparsecfg.core import field_argument
from rich import print as rprint

from .clean import clean_nb_file
from .core import get_nb_names


@dataclass
class AppCfg:
    path: str = field_argument("path", default=".", nargs="*")
    as_version: int = field_argument(
        default=nbformat.NO_CONVERT, help="Save as version, default - no convert"
    )
    silent: bool = field_argument("-s", default=False, action="store_true")


app = App(
    prog="nbclean",
    description="Clean metadata and execution_count from Jupyter notebooks.",
)


@app.main
def clean(
    cfg: AppCfg,
) -> None:
    """Clean metadata and execution_count from Jupyter notebook."""
    path_list = cfg.path if isinstance(cfg.path, list) else [cfg.path]
    nb_files: list[Path] = []
    for path in path_list:
        try:
            nb_files.extend(get_nb_names(path))
        except FileNotFoundError:
            rprint(f"{path} not exists!")
    rprint(f"find notebooks: {len(nb_files)} ")
    cleaned = clean_nb_file(nb_files, as_version=cfg.as_version, silent=cfg.silent)
    rprint(f"cleaned nbs: {len(cleaned)}")


if __name__ == "__main__":
    app()
