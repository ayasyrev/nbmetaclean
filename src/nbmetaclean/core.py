import json
from pathlib import Path

import nbformat


NB_METADATA_PRESERVE = ("language_info", "name")
CELL_METADATA_PRESERVE = ()


def read_nb(filename: Path) -> dict:
    """Read a notebook as json from file."""
    return json.loads(open(filename, "r", encoding="utf-8").read())


def write_nb(nb: dict, filename: Path) -> None:
    """Write a notebook to file."""
    nbformat.write(
        nbformat.reads(json.dumps(nb), as_version=nbformat.NO_CONVERT),
        filename,
        version=nbformat.NO_CONVERT,
    )


def clear_execution_count(cell: dict) -> bool:
    """Clear the execution count of a cell.
    If cleared, return True.
    """
    changed = False
    if cell.get("execution_count") is not None:
        cell["execution_count"] = None
        changed = True
    if "outputs" in cell:
        for output in cell["outputs"]:
            if clear_execution_count(output):
                changed = True
    return changed
