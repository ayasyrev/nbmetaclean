from pathlib import Path

from nbmetaclean.helpers import read_nb, write_nb


def test_read_nb():
    """test read notebook"""
    file = Path("tests/test_nbs/test_nb_1.ipynb")
    nb = read_nb(file)
    assert isinstance(nb, dict)
    assert nb["metadata"]["language_info"] == {"name": "python"}
    assert nb["metadata"]["authors"][0]["name"] == "Andrei Yasyrev"
    assert nb["nbformat"] == 4
    assert nb["nbformat_minor"] == 2
    cells = nb["cells"]
    assert isinstance(cells, list)
    assert len(cells) == 2
    # markdown
    assert cells[0]["cell_type"] == "markdown"
    assert cells[0]["source"] == []
    assert cells[0]["metadata"] == {}
    # code
    assert cells[1]["cell_type"] == "code"
    assert cells[1]["source"] == []
    assert cells[1]["execution_count"] is None
    assert cells[1]["metadata"] == {}
    assert cells[1]["outputs"] == []


def test_write_nb(tmp_path: Path):
    """test write notebook"""
    file = Path("tests/test_nbs/test_nb_1.ipynb")
    nb = read_nb(file)
    write_nb(nb, tmp_path / file.name)
    with open(tmp_path / file.name, "r", encoding="utf-8") as fh:
        res_text = fh.read()
    with open(file, "r", encoding="utf-8") as fh:
        org_text = fh.read()
    assert res_text == org_text

    # write with name w/o suffix
    result = write_nb(nb, tmp_path / "test_nb_1")
    assert result == tmp_path / "test_nb_1.ipynb"

    # write with stat
    stat = file.stat()
    timestamp = (stat.st_atime, stat.st_mtime)
    result = write_nb(nb, tmp_path / "test_nb_1", timestamp=timestamp)
    res_stat = result.stat()
    assert timestamp == (res_stat.st_atime, res_stat.st_mtime)
