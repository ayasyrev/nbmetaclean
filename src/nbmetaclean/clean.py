from __future__ import annotations
import copy

from pathlib import Path
from typing import Optional, Union

import nbformat

from nbformat.notebooknode import NotebookNode
from rich.progress import track

from .core import read_nb, write_nb, PathOrStr


NB_METADATA_PRESERVE_MASKS = [
    ("language_info", "name"),
]


def get_meta_by_mask(
    nb_meta: Union[NotebookNode, str],
    mask: Optional[tuple[str, ...]] = None,
) -> Union[NotebookNode, str]:
    """Get metadata by mask."""
    if isinstance(nb_meta, str) or mask == ():
        return nb_meta
    if mask is None:
        return NotebookNode()
    result = {}
    value = nb_meta.get(mask[0])
    if value is not None:
        new_mask = tuple(mask[1:])
        result[mask[0]] = get_meta_by_mask(value, new_mask) or value
    return NotebookNode(result)


def new_metadata(
    nb_meta: NotebookNode,
    masks: Optional[list[tuple[str, ...]]] = None,
) -> NotebookNode:
    """Clean notebooknode metadata."""
    if masks is None:
        return NotebookNode()
    filtered_meta = {}
    for mask in masks:
        filtered_meta.update(get_meta_by_mask(nb_meta, mask))
    return NotebookNode(filtered_meta)


def clean_cell_metadata(
    cell: NotebookNode,
    clear_execution_count: bool = True,
    clear_outputs: bool = False,
    preserve_cell_metadata_mask: Optional[list[tuple[str, ...]]] = None,
) -> bool:
    """Clean cell metadata."""
    changed = False
    if cell.metadata:
        old_metadata = copy.deepcopy(cell.metadata)
        cell.metadata = new_metadata(cell.metadata, preserve_cell_metadata_mask)
        if cell.metadata != old_metadata:
            changed = True
    if clear_outputs and hasattr(cell, "outputs") and cell.outputs:
        cell.outputs = []
        changed = True
    if (
        clear_execution_count
        and hasattr(cell, "execution_count")
        and cell.execution_count
    ):
        cell.execution_count = None
        changed = True
    if hasattr(cell, "outputs") and cell.outputs:
        for output in cell.outputs:
            if clear_execution_count and output.execution_count:
                output.execution_count = None
                changed = True
            if output.metadata:
                old_metadata = copy.deepcopy(output.metadata)
                output.metadata = new_metadata(
                    output.metadata, preserve_cell_metadata_mask
                )
                if output.metadata != old_metadata:
                    changed = True
    return changed


def clean_nb(
    nb: NotebookNode,
    clear_nb_metadata: bool = True,
    clear_cell_metadata: bool = True,
    clear_execution_count: bool = True,
    clear_outputs: bool = False,
    preserve_nb_metadata_masks: Optional[list[tuple[str, str]],] = None,
    preserve_cell_metadata_mask: Optional[str] = None,
) -> tuple[NotebookNode, bool]:
    """Clean notebook - metadata, execution_count, outputs.

    Args:
        nb (Notebook): Notebook to clean.
        clear_execution_count (bool, optional): Clear execution_count. Defaults to True.
        clear_outputs (bool, optional): Clear outputs. Defaults to False.

    Returns:
        bool: True if changed.
    """
    changed = False
    if clear_nb_metadata and nb.metadata:
        old_metadata = copy.deepcopy(nb.metadata)
        masks = preserve_nb_metadata_masks or NB_METADATA_PRESERVE_MASKS
        nb.metadata = new_metadata(nb.metadata, masks=masks)
        if nb.metadata != old_metadata:
            changed = True
    if clear_cell_metadata:
        for cell in nb.cells:
            result = clean_cell_metadata(
                cell,
                clear_execution_count=clear_execution_count,
                clear_outputs=clear_outputs,
                preserve_cell_metadata_mask=preserve_cell_metadata_mask,
            )
            if result:
                changed = True

    return nb, changed


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
    if not isinstance(path, list):
        path = [path]
    cleaned: list[PathOrStr] = []
    for filename in track(path, transient=True):
        nb = read_nb(filename)
        nb, result = clean_nb(
            nb,
            clear_execution_count=clear_execution_count,
        )
        if result:
            cleaned.append(filename)
            write_nb(nb, filename, as_version)
            if not silent:
                print(f"done: {filename}")
    return cleaned
