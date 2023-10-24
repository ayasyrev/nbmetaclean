from __future__ import annotations

from pathlib import Path, PosixPath
from typing import Optional, TypeVar

import nbformat
from nbformat.notebooknode import NotebookNode

PathOrStr = TypeVar("PathOrStr", str, Path, PosixPath)


def read_nb(path: PathOrStr) -> NotebookNode:
    """Read notebook from filename.

    Args:
        path (Union[str, PosixPath): Notebook filename.

    Returns:
        Notebook: Jupyter Notebook.
    """
    with Path(path).open("r", encoding="utf-8") as fh:
        nb: NotebookNode = nbformat.read(fh, as_version=nbformat.NO_CONVERT)
    return nb


def write_nb(
    nb: NotebookNode,
    path: PathOrStr,
    as_version: nbformat.Sentinel = nbformat.NO_CONVERT,
) -> Path:
    """Write notebook to file

    Args:
        nb (Notebook): Notebook to write
        path (Union[str, PosixPath]): filename to write
        as_version (_type_, optional): Nbformat version. Defaults to nbformat.NO_CONVERT.
    Returns:
        Path: Filename of writed Nb.
    """
    filename = Path(path)
    if filename.suffix != ".ipynb":
        filename = filename.with_suffix(".ipynb")
    with filename.open("w", encoding="utf-8") as fh:
        nbformat.write(nb, fh, version=as_version)  # type: ignore
    return filename


def get_nb_names(path: Optional[PathOrStr] = None) -> list[Path]:
    """Return list of notebooks from `path`. If no `path` return notebooks from current folder.

    Args:
        path (Union[Path, str, None]): Path for nb or folder with notebooks.

    Raises:
        sys.exit: If filename or dir not exists or not nb file.

    Returns:
        List[Path]: List of notebooks names.
    """
    nb_path = Path(path or ".")

    if not nb_path.exists():
        raise FileNotFoundError(f"{nb_path} not exists!")

    if nb_path.is_dir():
        return list(nb_path.rglob("*.ipynb"))

    return [nb_path]
