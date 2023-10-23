from pathlib import Path

from nbmetaclean.core import clear_execution_count, read_nb


def test_clear_execution_count():
    """test clear execution count"""
    nb = read_nb(Path("tests/test_nbs/test_nb_1.ipynb"))
    result = clear_execution_count(nb["cells"][1])
    assert not result
    nb["cells"][1]["execution_count"] = 1
    result = clear_execution_count(nb["cells"][1])
    assert result
    assert nb["cells"][1]["execution_count"] is None
