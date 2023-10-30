from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .typing import NbNode, PathOrStr


def read_nb(path: PathOrStr) -> NbNode:
    """Read notebook from filename.

    Args:
        path (Union[str, PosixPath): Notebook filename.

    Returns:
        Notebook: Jupyter Notebook as dict.
    """
    return json.load(open(path, "r", encoding="utf-8"))


def write_nb(
    nb: NbNode,
    path: PathOrStr,
) -> Path:
    """Write notebook to file

    Args:
        nb (Notebook): Notebook to write
        path (Union[str, PosixPath]): filename to write
    Returns:
        Path: Filename of writed Nb.
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
    return filename


def get_nb_names(
    path: Optional[PathOrStr] = None,
    recursive: bool = True,
    filter_hidden: bool = True,
) -> list[Path]:
    """Return list of notebooks from `path`. If no `path` return notebooks from current folder.

    Args:
        path (Union[Path, str, None]): Path for nb or folder with notebooks.
        recursive bool: Recursive search.
        filter_hidden bool: Filter hidden paths.

    Raises:
        sys.exit: If filename or dir not exists or not nb file.

    Returns:
        List[Path]: List of notebooks names.
    """
    nb_path = Path(path or ".")

    if not nb_path.exists():
        raise FileNotFoundError(f"{nb_path} not exists!")

    if nb_path.is_dir():
        result = []
        for item in nb_path.iterdir():
            if item.is_file() and item.suffix == ".ipynb":
                if filter_hidden and item.name.startswith("."):
                    continue
                result.append(item)
            if item.is_dir():
                if recursive:
                    if filter_hidden and item.name.startswith("."):
                        continue
                    result.extend(get_nb_names(item, recursive, filter_hidden))

        return result

    return [nb_path]
