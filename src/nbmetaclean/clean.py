from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

from .helpers import read_nb, write_nb

from .nb_types import Cell, CodeCell, Metadata, Nb, Output


__all__ = [
    "CleanConfig",
    "clean_cell",
    "clean_nb",
    "clean_nb_file",
    "clean_outputs",
    "filter_metadata",
    "filter_meta_mask",
    "NB_METADATA_PRESERVE_MASKS",
    "TupleStr",
]

TupleStr = Tuple[str, ...]

NB_METADATA_PRESERVE_MASKS = (
    ("language_info", "name"),
    ("authors",),
)


@dataclass
class CleanConfig:
    """Clean config.

    Args:
        clear_nb_metadata (bool, optional): Clear notebook metadata. Defaults to True.
        clear_cell_metadata (bool, optional): Clear cell metadata. Defaults to False.
        clear_execution_count (bool, optional): Clear cell execution count. Defaults to True.
        clear_outputs (bool, optional): Clear cell outputs. Defaults to False.
        preserve_timestamp (bool, optional): Preserve timestamp. Defaults to True.
        silent (bool, optional): Silent mode. Defaults to False.
        nb_metadata_preserve_mask (Optional[tuple[str, ...]], optional):
            Preserve mask for notebook metadata. Defaults to None.
        cell_metadata_preserve_mask (Optional[tuple[str, ...]], optional):
            Preserve mask for cell metadata. Defaults to None.
        mask_merge (bool): Merge masks. Add new mask to default.
            If False - use new mask. Defaults to True.
        dry_run (bool): perform a trial run, don't write results. Defaults to False.
        verbose (bool): Verbose mode. Print extra information. Defaults to False.
    """

    clear_nb_metadata: bool = True
    clear_cell_metadata: bool = False
    clear_execution_count: bool = True
    clear_outputs: bool = False
    preserve_timestamp: bool = True
    silent: bool = False
    nb_metadata_preserve_mask: Optional[tuple[TupleStr, ...]] = None
    cell_metadata_preserve_mask: Optional[tuple[TupleStr, ...]] = None
    mask_merge: bool = True
    dry_run: bool = False
    verbose: bool = False


def filter_meta_mask(
    nb_meta: Union[str, int, Metadata],
    mask: Optional[tuple[str, ...]] = None,
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
    masks: Optional[tuple[TupleStr, ...]] = None,
) -> Metadata:
    """Clean notebooknode metadata."""
    if masks is None:
        return {}
    filtered_meta: Metadata = {}
    for mask in masks:
        filtered_meta.update(filter_meta_mask(nb_meta, mask))  # type: ignore
    return filtered_meta


def clean_cell(
    cell: Cell | CodeCell,
    cfg: CleanConfig,
) -> bool:
    """Clean cell: optionally metadata, execution_count and outputs."""
    changed = False

    if cfg.clear_cell_metadata:
        if cell.get("metadata", None):
            metadata = cell["metadata"]
            old_metadata = copy.deepcopy(metadata)
            cell["metadata"] = filter_metadata(
                metadata, cfg.cell_metadata_preserve_mask
            )
            if cell["metadata"] != old_metadata:
                changed = True

    if cell["cell_type"] == "code":
        if cfg.clear_execution_count and cell.get("execution_count"):
            cell["execution_count"] = None  # type: ignore # it's code cell
            changed = True

        if cell.get("outputs"):
            if cfg.clear_outputs:
                cell["outputs"] = []  # type: ignore  # it's code cell
                changed = True
            elif cfg.clear_cell_metadata or cfg.clear_execution_count:
                result = clean_outputs(cell["outputs"], cfg)  # type: ignore # it's code cell
                if result:
                    changed = True

    return changed


def clean_outputs(outputs: list[Output], cfg: CleanConfig) -> bool:
    """Clean outputs."""
    changed = False
    for output in outputs:
        if cfg.clear_execution_count and output.get("execution_count", None):
            output["execution_count"] = None
            changed = True
        if cfg.clear_cell_metadata and (metadata := output.get("metadata", None)):
            old_metadata = copy.deepcopy(metadata)
            output["metadata"] = filter_metadata(
                metadata, cfg.cell_metadata_preserve_mask
            )
            if output["metadata"] != old_metadata:
                changed = True
    return changed


def clean_nb(
    nb: Nb,
    cfg: CleanConfig,
) -> bool:
    """Clean notebook - metadata, execution_count, outputs.

    Args:
        nb (Notebook): Notebook to clean.
        clear_execution_count (bool, optional): Clear execution_count. Defaults to True.
        clear_outputs (bool, optional): Clear outputs. Defaults to False.

    Returns:
        bool: True if changed.
    """
    changed = False
    if cfg.clear_nb_metadata and (metadata := nb.get("metadata")):
        old_metadata = copy.deepcopy(metadata)
        if cfg.nb_metadata_preserve_mask:
            if not cfg.mask_merge:
                masks = cfg.nb_metadata_preserve_mask
            else:
                masks = cfg.nb_metadata_preserve_mask + NB_METADATA_PRESERVE_MASKS
        else:
            masks = NB_METADATA_PRESERVE_MASKS
        nb["metadata"] = filter_metadata(metadata, masks=masks)
        if nb["metadata"] != old_metadata:
            changed = True
    if cfg.clear_cell_metadata or cfg.clear_execution_count or cfg.clear_outputs:
        for cell in nb["cells"]:
            result = clean_cell(
                cell,
                cfg,
            )
            if result:
                changed = True

    return changed


def clean_nb_file(
    path: Union[Path, list[Path]],
    cfg: Optional[CleanConfig] = None,
) -> tuple[list[Path], list[Path]]:
    """Clean metadata and execution count from notebook.

    Args:
        path (Union[str, PosixPath]): Notebook filename or list of names.
        cfg (CleanConfig, optional): Config for job, if None, used default settings. Default is None.

    Returns:
        tuple[List[Path], List[TuplePath]]: List of cleaned notebooks, list of notebooks with errors.
    """
    cfg = cfg or CleanConfig()
    if not isinstance(path, list):
        path = [path]
    cleaned: list[Path] = []
    errors: list[Path] = []
    for filename in path:
        nb = read_nb(filename)
        if nb is None:
            errors.append(filename)
            continue
        result = clean_nb(
            nb,
            cfg,
        )
        if result:
            cleaned.append(filename)
            if cfg.dry_run:
                continue
            if cfg.preserve_timestamp:
                stat = filename.stat()
                timestamp = (stat.st_atime, stat.st_mtime)
            else:
                timestamp = None
            write_nb(nb, filename, timestamp)

    return cleaned, errors
