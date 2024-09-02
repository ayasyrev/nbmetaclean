from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .types import Nb, PathOrStr

__all__ = [
    "get_nb_names",
    "get_nb_names_from_list",
    "is_notebook",
    "read_nb",
    "write_nb",
]


def read_nb(path: PathOrStr) -> Nb:
    """Read notebook from filename.

    Args:
        path (Union[str, PosixPath): Notebook filename.

    Returns:
        Notebook: Jupyter Notebook as dict.
    """
    return json.load(open(path, "r", encoding="utf-8"))


def write_nb(
    nb: Nb,
    path: PathOrStr,
    timestamp: Optional[tuple[float, float]] = None,
) -> Path:
    """Write notebook to file, optionally set timestamp.

    Args:
        nb (Notebook): Notebook to write
        path (Union[str, PosixPath]): filename to write
        timestamp (Optional[tuple[float, float]]): timestamp to set, (st_atime, st_mtime) defaults to None
    Returns:
        Path: Filename of written notebook.
    """
    filename = Path(path)
    if filename.suffix != ".ipynb":
        filename = filename.with_suffix(".ipynb")
    with filename.open("w", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                nb,
                indent=1,
                separators=(",", ": "),
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
        )
    if timestamp is not None:
        os.utime(filename, timestamp)
    return filename


def is_notebook(path: Path, hidden: bool = False) -> bool:
    """Check if `path` is a notebook and not hidden. If `hidden` is True check also hidden files.

    Args:
        path (Union[Path, str]): Path to check.
        hidden bool: If True also check hidden files, defaults to False.

    Returns:
        bool: True if `path` is a notebook and not hidden.
    """
    if path.suffix == ".ipynb":
        if path.name.startswith(".") and not hidden:
            return False
        return True
    return False


def get_nb_names(
    path: Optional[PathOrStr] = None,
    recursive: bool = True,
    hidden: bool = False,
) -> list[Path]:
    """Return list of notebooks from `path`. If no `path` return notebooks from current folder.

    Args:
        path (Union[Path, str, None]): Path for nb or folder with notebooks.
        recursive bool: Recursive search.
        hidden bool: Skip or not hidden paths, defaults to False.

    Raises:
        sys.exit: If filename or dir not exists or not nb file.

    Returns:
        List[Path]: List of notebooks names.
    """
    nb_path = Path(path or ".")

    if not nb_path.exists():
        raise FileNotFoundError(f"{nb_path} not exists!")

    if nb_path.is_file():
        if is_notebook(nb_path, hidden):
            return [nb_path]

    if nb_path.is_dir():
        result = []
        for item in nb_path.iterdir():
            if item.is_file() and is_notebook(item, hidden):
                result.append(item)
            if item.is_dir() and recursive:
                if item.name.startswith(".") and not hidden:
                    continue
                if "checkpoint" in item.name:
                    continue
                result.extend(get_nb_names(item, recursive, hidden))

        return result

    return []


def get_nb_names_from_list(
    path_list: list[PathOrStr] | PathOrStr,
    recursive: bool = True,
    hidden: bool = False,
) -> list[Path]:
    """Return list of notebooks from `path_list`.

    Args:
        path_list (Union[Path, str, None]): Path for nb or folder with notebooks.
        recursive (bool): Recursive search.
        hidden (bool): Skip or not hidden paths, defaults to False.

    Returns:
        List[Path]: List of notebooks names.
    """
    path_list = [path_list] if isinstance(path_list, (str, Path)) else path_list
    nb_files: list[Path] = []
    for path in path_list:
        if Path(path).exists():
            nb_files.extend(get_nb_names(path, recursive, hidden))
        else:
            print(f"{path} not exists!")

    return nb_files
