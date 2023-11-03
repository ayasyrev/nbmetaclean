from __future__ import annotations
import copy
import os

from pathlib import Path
from typing import Optional, Union

from nbmetaclean.core import read_nb, write_nb

from .typing import NbNode, Metadata

NB_METADATA_PRESERVE_MASKS = [
    ("language_info", "name"),
]


def filter_meta_mask(
    nb_meta: Union[str, int, Metadata],
    mask: [tuple[str, ...]] = None,
) -> Union[str, int, Metadata]:
    """Filter metadata by mask. If no mask return empty dict."""
    if isinstance(nb_meta, (str, int)) or mask == ():
        return nb_meta
    if mask is None:
        return {}
    new_meta = {}
    value = nb_meta.get(mask[0])
    if value is not None:
        new_mask = tuple(mask[1:])
        new_meta[mask[0]] = filter_meta_mask(value, new_mask) or value
    return new_meta


def filter_metadata(
    nb_meta: Metadata,
    masks: Optional[list[tuple[str, ...]]] = None,
) -> Metadata:
    """Clean notebooknode metadata."""
    if masks is None:
        return {}
    filtered_meta: Metadata = {}
    for mask in masks:
        filtered_meta.update(filter_meta_mask(nb_meta, mask))  # type: ignore
    return filtered_meta


def clean_cell_metadata(
    cell: NbNode,
    clear_execution_count: bool = True,
    clear_outputs: bool = False,
    preserve_cell_metadata_mask: Optional[list[tuple[str, ...]]] = None,
) -> bool:
    """Clean cell metadata."""
    changed = False
    if metadata := cell.get("metadata", None):
        old_metadata = copy.deepcopy(metadata)
        cell["metadata"] = filter_metadata(metadata, preserve_cell_metadata_mask)
        if cell["metadata"] != old_metadata:
            changed = True
    if clear_outputs and cell.get("outputs"):
        cell["outputs"] = []
        changed = True
    if clear_execution_count and cell.get("execution_count"):
        cell["execution_count"] = None
        changed = True
    if outputs := cell.get("outputs"):
        for output in outputs:
            if clear_execution_count and output.get("execution_count", None):
                output["execution_count"] = None
                changed = True
            if metadata := output.get("metadata", None):
                old_metadata = copy.deepcopy(metadata)
                output["metadata"] = filter_metadata(
                    metadata, preserve_cell_metadata_mask
                )
                if output["metadata"] != old_metadata:
                    changed = True
    return changed


def clean_nb(
    nb: NbNode,
    clear_nb_metadata: bool = True,
    clear_cell_metadata: bool = True,
    clear_execution_count: bool = True,
    clear_outputs: bool = False,
    preserve_nb_metadata_masks: Optional[list[tuple[str, ...]],] = None,
    preserve_cell_metadata_mask: Optional[tuple[str, ...]] = None,
) -> tuple[NbNode, bool]:
    """Clean notebook - metadata, execution_count, outputs.

    Args:
        nb (Notebook): Notebook to clean.
        clear_execution_count (bool, optional): Clear execution_count. Defaults to True.
        clear_outputs (bool, optional): Clear outputs. Defaults to False.

    Returns:
        bool: True if changed.
    """
    changed = False
    if clear_nb_metadata and (metadata := nb.get("metadata")):
        old_metadata = copy.deepcopy(metadata)
        masks = preserve_nb_metadata_masks or NB_METADATA_PRESERVE_MASKS
        nb["metadata"] = filter_metadata(metadata, masks=masks)
        if nb["metadata"] != old_metadata:
            changed = True
    if clear_cell_metadata:
        for cell in nb["cells"]:
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
    path: Union[Path, list[Path]],
    clear_nb_metadata: bool = True,
    clear_cell_metadata: bool = True,
    clear_execution_count: bool = True,
    clear_outputs: bool = False,
    preserve_timestamp: bool = True,
    silent: bool = False,
) -> tuple[list[Path], list[tuple[Path, Exception]]]:
    """Clean metadata and execution count from notebook.

    Args:
        path (Union[str, PosixPath]): Notebook filename or list of names.
        clear_nb_metadata (bool): Clear notebook metadata. Defaults to True.
        clear_cell_metadata (bool): Clear cell metadata. Defaults to True.
        clear_outputs (bool): Clear outputs. Defaults to False.
        preserve_timestamp (bool): Preserve timestamp. Defaults to True.
        clear_execution_count (bool, optional): Clean execution count. Defaults to True.
        silent (bool): Silent mode. Defaults to False.

    Returns:
        tuple[List[Path], List[TuplePath]]: List of cleaned notebooks, list of notebooks with errors.
    """
    if not isinstance(path, list):
        path = [path]
    cleaned: list[Path] = []
    errors: list[tuple[Path, Exception]] = []
    to_clean = len(path)
    for num, filename in enumerate(path):
        try:
            nb = read_nb(filename)
        except Exception as ex:
            errors.append((filename, ex))
            continue
        nb, result = clean_nb(
            nb,
            clear_execution_count=clear_execution_count,
            clear_outputs=clear_outputs,
            clear_nb_metadata=clear_nb_metadata,
            clear_cell_metadata=clear_cell_metadata,
        )
        if result:
            cleaned.append(filename)
            if preserve_timestamp:
                stat = filename.stat()
            write_nb(nb, filename)
            if preserve_timestamp:
                os.utime(filename, (stat.st_atime, stat.st_mtime))
            if not silent:
                print(f"done {num + 1} of {to_clean}: {filename}")
    return cleaned, errors
