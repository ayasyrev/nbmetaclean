import copy
import os
from pathlib import Path

from pytest import CaptureFixture

from nbmetaclean.clean import (
    NB_METADATA_PRESERVE_MASKS,
    clean_cell_metadata,
    clean_nb,
    clean_nb_file,
    filter_meta_mask,
    filter_metadata,
)
from nbmetaclean.core import read_nb, write_nb


def test_get_meta_by_mask():
    """test get_meta_by_mask"""
    nb = read_nb(Path("tests/test_nbs/.test_nb_2_meta.ipynb"))
    nb_meta = nb.get("metadata")

    # string as nb_meta
    new_meta = filter_meta_mask("some string")
    assert new_meta == "some string"

    # no mask
    new_meta = filter_meta_mask(nb_meta)
    assert new_meta == {}

    # mask
    nb_meta["some key"] = "some value"
    new_meta = filter_meta_mask(nb_meta, ("some key",))
    assert new_meta == {"some key": "some value"}
    new_meta = filter_meta_mask(nb_meta, NB_METADATA_PRESERVE_MASKS[0])
    assert new_meta == {"language_info": {"name": "python"}}

    # mask for empty result
    new_meta = filter_meta_mask(nb_meta, ("some other key",))
    assert new_meta == {}


def test_new_metadata():
    """test new_metadata"""
    nb_meta = read_nb("tests/test_nbs/.test_nb_2_meta.ipynb").get("metadata")
    new_meta = filter_metadata(nb_meta)
    assert isinstance(new_meta, dict)
    assert not new_meta
    new_meta = filter_metadata(nb_meta, [("language_info", "name")])
    assert new_meta == {"language_info": {"name": "python"}}


def test_clean_cell_metadata():
    """test clean_cell_metadata"""
    test_nb = read_nb("tests/test_nbs/.test_nb_2_meta.ipynb")

    # clear outputs
    cell = copy.deepcopy(test_nb.get("cells")[1])
    assert cell.get("outputs")
    assert not cell.get("metadata")
    assert cell.get("execution_count") == 1
    cell["metadata"] = {"some key": "some value"}
    changed = clean_cell_metadata(cell, clear_outputs=True)
    assert changed
    assert not cell.get("outputs")
    assert not cell.get("metadata")
    assert not cell.get("execution_count")

    # dont clear outputs, execution_count, mask
    cell = copy.deepcopy(test_nb.get("cells")[1])
    cell["metadata"] = {"some key": "some value"}
    cell["outputs"][0]["metadata"] = {
        "some key": "some value",
        "some other key": "some value",
    }
    changed = clean_cell_metadata(
        cell,
        clear_execution_count=False,
        preserve_cell_metadata_mask=[("some key",)],
    )
    assert changed
    assert cell["outputs"][0]["metadata"] == {"some key": "some value"}
    assert cell["metadata"] == {"some key": "some value"}
    assert cell["execution_count"] == 1

    # clear outputs, same mask -> no changes meta, clear ex
    changed = clean_cell_metadata(cell, preserve_cell_metadata_mask=[("some key",)])
    assert changed
    assert cell["execution_count"] is None
    assert cell["metadata"] == {"some key": "some value"}

    # clear execution_count, metadata
    changed = clean_cell_metadata(cell)
    assert changed
    assert not cell["outputs"][0]["metadata"]
    assert not cell["execution_count"]
    assert not cell["metadata"]
    assert not cell["outputs"][0]["metadata"]


def test_clean_cell_metadata_markdown():
    """test clean_cell_metadata with markdown cell"""
    test_nb = read_nb("tests/test_nbs/.test_nb_2_meta.ipynb")
    cell = copy.deepcopy(test_nb["cells"][0])
    cell["metadata"] = {"some key": "some value"}
    changed = clean_cell_metadata(cell)
    assert changed
    assert not cell["metadata"]


def test_clean_nb():
    """test clean nb"""
    path = Path("tests/test_nbs")
    nb_path = path / ".test_nb_2_meta.ipynb"
    nb_clean = path / "test_nb_2_clean.ipynb"
    nb = read_nb(nb_path)
    assert nb["cells"][1]["execution_count"] == 1
    assert nb["cells"][1]["outputs"][0]["execution_count"] == 1
    assert nb["metadata"]
    nb, result = clean_nb(nb)
    assert result is True
    assert nb["cells"][1]["execution_count"] is None
    assert nb["cells"][1]["outputs"][0]["execution_count"] is None
    nb_clean = read_nb(nb_clean)
    assert nb == nb_clean

    # # try clean cleaned
    nb, result = clean_nb(nb_clean)
    assert not result

    # # clean metadata, leave execution_count
    nb = read_nb(nb_path)
    nb, result = clean_nb(nb, clear_execution_count=False)
    assert result
    assert nb["cells"][1]["execution_count"] == 1
    assert nb["cells"][1]["outputs"][0]["execution_count"] == 1
    assert nb["metadata"] == nb_clean["metadata"]

    # clean nb metadata, leave cells metadata
    nb = read_nb(nb_path)
    nb["cells"][1]["metadata"] = {"some key": "some value"}
    nb, result = clean_nb(nb, clear_cell_metadata=False)
    assert result
    assert nb["metadata"] == nb_clean["metadata"]
    assert nb["cells"][1]["metadata"] == {"some key": "some value"}
    assert nb["cells"][1]["execution_count"] == 1

    # clean cells metadata, leave nb metadata
    nb = read_nb(nb_path)
    nb_meta = copy.deepcopy(nb["metadata"])
    nb, result = clean_nb(nb, clear_nb_metadata=False)
    assert result
    assert nb["metadata"] == nb_meta
    assert nb["cells"][1]["execution_count"] is None


def test_clean_nb_file(tmp_path: Path, capsys: CaptureFixture[str]):
    """test clean nb file"""
    path = Path("tests/test_nbs")
    nb_name = ".test_nb_2_meta.ipynb"
    nb_clean = read_nb(path / "test_nb_2_clean.ipynb")

    # prepare temp test notebook
    test_nb_path = write_nb(read_nb(path / nb_name), tmp_path / nb_name)

    # clean meta, leave execution_count
    cleaned, errors = clean_nb_file(test_nb_path, clear_execution_count=False)
    assert len(cleaned) == 1
    assert len(errors) == 0
    nb = read_nb(cleaned[0])
    assert nb["metadata"] == nb_clean["metadata"]
    assert nb["cells"][1]["execution_count"] == 1
    assert nb["cells"][1]["outputs"][0]["execution_count"] == 1

    # clean meta, execution_count
    # path as list
    cleaned, errors = clean_nb_file([test_nb_path])
    captured = capsys.readouterr()
    out = captured.out
    assert out.startswith("done")
    assert "test_clean_nb_file0/.test_nb_2_meta.ipynb" in out
    assert len(cleaned) == 1
    nb = read_nb(cleaned[0])
    assert nb == nb_clean

    # try clean cleaned
    cleaned, errors = clean_nb_file(test_nb_path)
    assert len(cleaned) == 0
    captured = capsys.readouterr()
    out = captured.out
    assert not out.strip()

    # silent
    test_nb_path = write_nb(read_nb(path / nb_name), tmp_path / nb_name)
    cleaned, errors = clean_nb_file(test_nb_path, silent=True)
    assert len(cleaned) == 1
    captured = capsys.readouterr()
    assert not captured.out.strip()


def test_clean_nb_file_timestamp(tmp_path: Path):
    """test clean_nb_file, timestamp"""
    path = Path("tests/test_nbs")
    nb_name = ".test_nb_2_meta.ipynb"
    nb_stat = (path / nb_name).stat()

    # prepare temp test notebook, set timestamp
    test_nb_path = write_nb(read_nb(path / nb_name), tmp_path / nb_name)
    os.utime(test_nb_path, (nb_stat.st_atime, nb_stat.st_mtime))
    test_nb_stat = test_nb_path.stat()
    assert test_nb_stat.st_atime == nb_stat.st_atime
    assert test_nb_stat.st_mtime == nb_stat.st_mtime

    cleaned, errors = clean_nb_file(test_nb_path)
    assert len(cleaned) == 1
    cleaned_stat = cleaned[0].stat()
    assert True
    assert cleaned_stat.st_mtime == test_nb_stat.st_mtime

    # dont preserve timestamp
    test_nb_path = write_nb(read_nb(path / nb_name), tmp_path / nb_name)
    os.utime(test_nb_path, (nb_stat.st_atime, nb_stat.st_mtime))
    cleaned, errors = clean_nb_file(test_nb_path, preserve_timestamp=False)
    assert len(cleaned) == 1
    cleaned_stat = cleaned[0].stat()
    assert True
    assert cleaned_stat.st_mtime != nb_stat.st_mtime
