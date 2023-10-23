import json
from pathlib import Path


NB_METADATA_PRESERVE = ("language_info", "name")
CELL_METADATA_PRESERVE = ()


def read_nb(filename: Path) -> dict:
    """Read a notebook as json from file."""
    return json.loads(open(filename, "r", encoding="utf-8").read())
