from pathlib import Path, PosixPath
from typing import Dict, List, TypeVar, Union

PathOrStr = TypeVar("PathOrStr", Path, PosixPath, str)

NbNode = Dict[str, Union[str, int, "NbNode"]]
Metadata = Dict[str, Union[str, int, "Metadata"]]
Source = Union[str, List[str]]
