from pathlib import Path

from nbmetaclean.core import read_nb


def test_read_nb():
    """test read notebook"""
    file = Path("tests/test_nbs/test_nb_1.ipynb")
    nb = read_nb(file)
    assert isinstance(nb, dict)
    assert nb["metadata"] == {"language_info": {"name": "python"}}
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
