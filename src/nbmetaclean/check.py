from typing import cast
from nbmetaclean.types import CodeCell, Nb


__all__ = ["check_nb_ec", "check_nb_errors"]


def check_nb_ec(nb: Nb, strict: bool = True, no_exec: bool = False) -> bool:
    """Check nb for correct sequence of execution_count.
    Expecting all code cells executed one after another.
    If `strict` is False, check that next cell executed after previous one, number can be more than `+1`
    If `no_exec` is True, ignore notebooks with all code cells without execution_count.

    Args:
        nb (Nb): Notebook to check.
        strict (bool, optional): Strict mode. Defaults to True.
        no_exec (bool): Ignore notebooks with all code cells without execution_count.

    Returns:
        bool: True if correct.
    """

    current = 0
    no_exec_cells = 0
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell = cast(CodeCell, cell)
            if not cell["source"]:
                if cell[
                    "execution_count"
                ]:  # if cell without code but with execution_count
                    return False
                continue

            if not cell["execution_count"]:
                if not no_exec:
                    return False
                else:
                    no_exec_cells += 1
            else:
                if cell["execution_count"] != current + 1 and strict:
                    return False
                if cell["execution_count"] <= current:
                    return False
                current = cell["execution_count"]
    if no_exec_cells and current:  # if we got not executed cells and executed.
        return False
    return True


def check_nb_errors(nb: Nb) -> bool:
    """Check nb for cells with errors.

    Args:
        nb (Nb): Notebook to check.

    Returns:
        bool: True if no errors.
    """
    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and "outputs" in cell:
            cell = cast(CodeCell, cell)
            for output in cell["outputs"]:
                if output["output_type"] == "error":
                    return False
    return True


def check_nb_warnings(nb: Nb) -> bool:
    """Check nb for cells with warnings.

    Args:
        nb (Nb): Notebook to check.

    Returns:
        bool: True if no warnings.
    """
    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and "outputs" in cell:
            cell = cast(CodeCell, cell)
            for output in cell["outputs"]:
                if output["output_type"] == "stream" and output["name"] == "stderr":
                    return False
    return True
