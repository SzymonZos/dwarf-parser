import pytest
from dwarf_parser import parse


def get_all_test_suits():
    parse("./test/functions")
    return [(1, 1), (2, 2)]


@pytest.fixture
def dwarf_fixture(request):
    ref, out = request.param
    yield ref, out


@pytest.mark.parametrize("dwarf_fixture", get_all_test_suits(), indirect=True)
def test_dwt(dwarf_fixture):
    ref, out = dwarf_fixture
    assert ref == out
