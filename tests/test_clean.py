from pathlib import Path
from nbconvert.exporters.exporter import ResourcesDict

from nbmetaclean.clean import clean_nb, clean_nb_file
from nbmetaclean.core import read_nb, write_nb


def test_clean_nb():
    """test clean nb"""
    path = Path("tests/test_nbs")
    nb_path = path / "test_nb_2.ipynb"
    nb_clean = path / "test_nb_2_clean.ipynb"
    nb = read_nb(nb_path)
    assert nb.cells[1].execution_count == 1
    assert nb.cells[1].outputs[0].execution_count == 1
    nb, resources = clean_nb(nb)
    assert resources["changed"] is True
    assert nb.cells[1].execution_count is None
    assert nb.cells[1].outputs[0].execution_count is None
    nb_clean = read_nb(nb_clean)
    assert nb == nb_clean

    # try clean cleaned
    nb, resources = clean_nb(nb_clean)
    assert resources["changed"] is False

    # clean metadata, leave execution_count
    nb = read_nb(nb_path)
    nb, resources = clean_nb(nb, clear_execution_count=False)
    assert resources["changed"] is True
    assert nb.cells[1].execution_count == 1
    assert nb.cells[1].outputs[0].execution_count == 1
    assert nb.metadata == nb_clean.metadata

    resources = ResourcesDict()
    empty_resources = ResourcesDict()
    nb, resources = clean_nb(nb, resources=resources)
    assert resources["changed"] is True

    nb, resources = clean_nb(nb, resources=resources)
    assert resources["changed"] is False
    resources.pop("changed")
    assert resources == empty_resources


def test_clean_nb_file(tmp_path: Path):
    """test clean nb file"""
    path = Path("tests/test_nbs")
    nb_name = "test_nb_2.ipynb"
    nb_clean = read_nb(path / "test_nb_2_clean.ipynb")

    # prepare temp test notebook
    test_nb_path = write_nb(read_nb(path / nb_name), tmp_path / nb_name)

    # clean meta, leave execution_count
    result = clean_nb_file(test_nb_path, clear_execution_count=False)
    assert len(result) == 1
    nb = read_nb(result[0])
    assert nb.metadata == nb_clean.metadata
    assert nb.cells[1].execution_count == 1
    assert nb.cells[1].outputs[0].execution_count == 1

    # clean meta, execution_count
    result = clean_nb_file(test_nb_path)
    assert len(result) == 1
    nb = read_nb(result[0])
    assert nb == nb_clean

    # try clean cleaned
    result = clean_nb_file(test_nb_path)
    assert len(result) == 0
