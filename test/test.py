import re
import pytest

from typing import Dict
from pathlib import Path

from dwarf_parser import parse
from .cdecl import explain_c_declaration


def get_ref_prototype(line: str):
    try:
        return re.search(R".+\(.+(?= {)", line).group()
    except AttributeError:
        return None


def get_reference_prototypes():
    with Path("functions.c").open("r") as ref:
        return reversed(
            [x for line in ref if (x := get_ref_prototype(line)) is not None])


def get_parsed_prototypes(prototypes: Dict[str, str]):
    return (f"{function}({arguments})"
            for function, arguments in prototypes.items())


def get_all_test_suits():
    ref = get_reference_prototypes()
    out = get_parsed_prototypes(parse(Path("functions")))
    return [(r, o) for r, o in zip(ref, out)]


@pytest.fixture
def dwarf_fixture(request):
    ref, out = request.param
    yield ref, out


@pytest.mark.parametrize("dwarf_fixture", get_all_test_suits(), indirect=True)
def test_dwarf(dwarf_fixture):
    ref, out = dwarf_fixture
    assert explain_c_declaration(ref) == explain_c_declaration(out)
