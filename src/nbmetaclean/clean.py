from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import nbformat
from nbconvert.exporters.exporter import ResourcesDict
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.clearmetadata import ClearMetadataPreprocessor
from nbformat.notebooknode import NotebookNode
from rich.progress import track

from .core import read_nb, write_nb, PathOrStr


class ClearMetadataPreprocessorRes(ClearMetadataPreprocessor):
    """ClearMetadata Preprocessor same as at nbconvert
    but return True at resources.changed if nb changed."""

    def preprocess_cell(
        self,
        cell: NotebookNode,
        resources: ResourcesDict,
        cell_index: int,
    ) -> (NotebookNode, ResourcesDict):
        """Process cell."""
        if self.clear_cell_metadata and cell.cell_type == "code":
            # Remove metadata
            current_metadata = cell.metadata
            cell, resources = super().preprocess_cell(cell, resources, cell_index)
            if cell.metadata != current_metadata:
                resources["changed"] = True
        return cell, resources

    def preprocess(
        self, nb: NotebookNode, resources: ResourcesDict
    ) -> (NotebookNode, ResourcesDict):
        """Process notebook."""
        if self.clear_notebook_metadata:
            current_metadata = nb.metadata
            nb, resources = super().preprocess(nb, resources)
            if nb.metadata != current_metadata:
                resources["changed"] = True
        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index)
        return nb, resources


class ClearExecutionCountPreprocessor(Preprocessor):
    """
    Clear execution_count from all code cells in a notebook.
    """

    def preprocess_cell(
        self,
        cell: NotebookNode,
        resources: ResourcesDict,
        index: int,
    ) -> (NotebookNode, ResourcesDict):
        """Clean execution_count on each cell."""
        if cell.cell_type == "code":
            if cell.execution_count is not None:
                cell.execution_count = None
                resources["changed"] = True
            for output in cell.outputs:
                if "execution_count" in output and output.execution_count is not None:
                    output.execution_count = None
                    resources["changed"] = True
        return cell, resources


class MetadataCleaner:
    """Metadata cleaner.
    Wrapper for metadata and execution count preprocessors.
    """

    def __init__(self) -> None:
        self.cleaner_metadata = ClearMetadataPreprocessorRes(enabled=True)
        self.cleaner_execution_count = ClearExecutionCountPreprocessor(enabled=True)

    def __call__(
        self,
        nb: NotebookNode,
        resources: Optional[ResourcesDict] = None,
        clear_execution_count: bool = True,
    ) -> (NotebookNode, ResourcesDict):
        """Clean notebook metadata and execution_count.

        Args:
            nb (Notebook): Notebook to clean.
            resources (ResourcesDict, optional): ResourcesDict. Defaults to None.
            clear_execution_count (bool, optional): Clear execution_count. Defaults to True.

        Returns:
            Tuple[NotebookNode, ResourcesDict]: Cleaned notebook and resources
        """
        if resources is None:
            resources = ResourcesDict()
        resources["changed"] = False
        nb, resources = self.cleaner_metadata(nb, resources)
        if clear_execution_count:
            nb, resources = self.cleaner_execution_count(nb, resources)
        return nb, resources


def clean_nb(
    nb: NotebookNode,
    resources: Optional[ResourcesDict] = None,
    clear_execution_count: bool = True,
) -> (NotebookNode, ResourcesDict):
    """Clean notebook metadata and execution_count.

    Args:
        nb (Notebook): Notebook to clean.
        resources (ResourcesDict, optional): ResourcesDict. Defaults to None.
        clear_execution_count (bool, optional): Clear execution_count. Defaults to True.

    Returns:
        Tuple[NotebookNode, ResourcesDict]: Cleaned notebook and resources
    """
    cleaner = MetadataCleaner()
    return cleaner(
        nb=nb, resources=resources, clear_execution_count=clear_execution_count
    )


def clean_nb_file(
    path: Union[PathOrStr, list[PathOrStr]],
    clear_execution_count: bool = True,
    as_version: nbformat.Sentinel = nbformat.NO_CONVERT,
    silent: bool = False,
) -> list[Path]:
    """Clean metadata and execution count from notebook.

    Args:
        path (Union[str, PosixPath]): Notebook filename or list of names.
        as_version (int, optional): Nbformat version. Defaults to 4.
        clear_execution_count (bool, optional): Clean execution count. Defaults to True.
        silent (bool, optional): Silent mode. Defaults to False.

    Returns:
        List[Path]: List of cleaned notebooks
    """
    cleaner = MetadataCleaner()
    if not isinstance(path, list):
        path = [path]
    cleaned: list[PathOrStr] = []
    for filename in track(path, transient=True):
        nb = read_nb(filename)
        nb, resources = cleaner(nb, clear_execution_count=clear_execution_count)
        if resources["changed"]:
            cleaned.append(filename)
            write_nb(nb, filename, as_version)
            if not silent:
                print(f"done: {filename}")
    return cleaned
