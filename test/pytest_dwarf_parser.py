from pathlib import Path
import re
import pytest

from src.dwarf_parser import DwarfParser
from .cdecl import explain_c_declaration


def get_ref_prototype(line: str):
    if re.search(R"//", line):
        return None
    try:
        return re.search(R".+\(.+(?= {)", line).group()
    except AttributeError:
        return None


def get_reference_prototypes():
    with Path("test/functions.c").open("r") as ref:
        return reversed([prototype for line in ref if
                         (prototype := get_ref_prototype(line)) is not None])


def get_all_test_suits():
    ref = get_reference_prototypes()
    out = DwarfParser(Path("test/functions")).parse()
    return ((f"{r};", f"{out.entry_to_str(o)};") for r, o in zip(ref, out))


@pytest.fixture
def dwarf_fixture(request):
    ref, out = request.param
    yield ref, out


@pytest.mark.parametrize("dwarf_fixture", get_all_test_suits(), indirect=True)
def test_dwarf(dwarf_fixture):
    ref, out = dwarf_fixture
    assert explain_c_declaration(ref) == explain_c_declaration(out)
