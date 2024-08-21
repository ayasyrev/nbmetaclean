from nbmetaclean.types import Nb


def check_nb_ec(nb: Nb, strict: bool = True) -> bool:
    """Check nb for correct sequence of execution_count.
    Expecting all code cells executed one after another.
    If `strict` is False, check that next cell executed after previous one, number can be more than `+1`

    Args:
        nb (Nb): Notebook to check.
        strict (bool, optional): Strict mode. Defaults to True.

    Returns:
        bool: True if correct.
    """

    current = 0
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            if not cell["source"]:
                if cell[
                    "execution_count"
                ]:  # if cell without code but with execution_count
                    return False
                continue
            if strict:
                if cell["execution_count"] != current + 1:
                    return False
            if cell["execution_count"] <= current:
                return False
            current = cell["execution_count"]
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
            for output in cell["outputs"]:
                if output["output_type"] == "error":
                    return False
    return True
