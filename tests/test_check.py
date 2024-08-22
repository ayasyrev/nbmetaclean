from nbmetaclean.check import check_nb_ec, check_nb_errors
from nbmetaclean.helpers import read_nb


def test_check_nb_ec():
    """test check_nb_ec"""
    test_nb = read_nb("tests/test_nbs/test_nb_3_ec.ipynb")
    result = check_nb_ec(test_nb)
    assert not result

    test_nb["cells"][2]["execution_count"] = 1
    test_nb["cells"][3]["execution_count"] = 2
    test_nb["cells"][5]["execution_count"] = 3

    result = check_nb_ec(test_nb)
    assert result

    # test strict
    test_nb["cells"][5]["execution_count"] = 4
    result = check_nb_ec(test_nb)
    assert not result
    result = check_nb_ec(test_nb, strict=False)
    assert result

    # empty source, but with execution_count
    test_nb["cells"][5]["execution_count"] = 3
    test_nb["cells"][6]["execution_count"] = 4

    result = check_nb_ec(test_nb)
    assert not result
    result = check_nb_ec(test_nb, strict=False)
    assert not result

    # start not from 1
    test_nb = read_nb("tests/test_nbs/test_nb_3_ec.ipynb")
    test_nb["cells"][2]["execution_count"] = 2
    test_nb["cells"][3]["execution_count"] = 3
    test_nb["cells"][5]["execution_count"] = 4

    result = check_nb_ec(test_nb)
    assert not result
    result = check_nb_ec(test_nb, strict=False)
    assert result

    # next is less
    test_nb["cells"][3]["execution_count"] = 5

    result = check_nb_ec(test_nb, strict=False)
    assert not result


def test_check_nb_errors():
    """test check_nb_errors"""
    test_nb = read_nb("tests/test_nbs/test_nb_3_ec.ipynb")
    result = check_nb_errors(test_nb)
    assert result

    test_nb["cells"][2]["outputs"][0]["output_type"] = "error"
    result = check_nb_errors(test_nb)
    assert not result
