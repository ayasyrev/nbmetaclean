from pathlib import Path, PosixPath
from typing import Dict, List, Literal, Optional, TypeVar, TypedDict, Union

PathOrStr = TypeVar("PathOrStr", Path, PosixPath, str)

NbNode = Dict[str, Union[str, int, "NbNode"]]
Metadata = Dict[str, Union[str, int, "Metadata"]]
MultilineText = Union[str, List[str]]


class NbMetadata(TypedDict):
    language_info: Metadata
    kernelspec: Metadata
    authors: Metadata


class Output(TypedDict):
    output_type: Literal[
        "execute_result",
        "display_data",
        "stream",
        "error",
    ]
    execution_count: Optional[int]
    metadata: Metadata


class ExecuteResult(Output):  # output_type = "execute_result"
    data: Dict[str, MultilineText]


class DisplayData(Output):  # output_type = "display_data"
    data: Dict[str, MultilineText]  # fix it - mimebundle


class Stream(Output):  # output_type = "stream"
    name: Literal["stdout", "stderr"]  # "The name of the stream (stdout, stderr)."
    text: MultilineText


class Error(Output):  # output_type = "error"
    ename: str  # "The name of the error."
    evalue: str  # "The value, or message, of the error."
    traceback: List[str]


class Cell(TypedDict):
    """Notebook cell base."""

    id: int  # from nbformat 4.5
    cell_type: Literal["code", "markdown", "raw"]
    metadata: Metadata
    source: MultilineText
    attachments: Optional[Dict[str, MultilineText]]


class CodeCell(Cell):  # cell_type = "code"
    """Code cell."""

    outputs: List[Output]
    execution_count: Optional[int]


class Nb(TypedDict):
    """Notebook."""

    nbformat: int
    nbformat_minor: int
    cells: List[Cell]
    metadata: Metadata
