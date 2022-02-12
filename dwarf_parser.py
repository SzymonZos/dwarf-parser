import re
import logging
from typing import Dict, Optional

from src.argument_parser import create_parser
from src.utils import ElfFile, NoAttributeInDie

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_prototypes = dict()
_current_function = ""

CVR_TYPE_QUALIFIERS_TAGS = [
    "DW_TAG_restrict_type",
    "DW_TAG_const_type",
    "DW_TAG_volatile_type"
]

SPECIAL_TYPE_DECLARATIONS = {
    "DW_TAG_structure_type": "struct",
    "DW_TAG_union_type": "union",
    "DW_TAG_enumeration_type": "enum"
}


def parse(elf_path) -> Optional[Dict[str, str]]:
    elf = ElfFile(elf_path)
    if not elf.has_dwarf_info():
        return None
    dwarf = elf.get_dwarf_info()
    for cu in dwarf.iter_CUs():
        logger.debug(f"Found a compile unit at offset {cu.cu_offset}, "
                     f"length {cu['unit_length']}")
        top_die = cu.get_top_DIE()
        logger.debug(f"Top DIE with tag={top_die.tag}, "
                     f"name={top_die.get_full_path()}")
        die_info_rec(top_die)
    return _prototypes


def get_attribute_value(die, attribute):
    try:
        return die.attributes[attribute].value.decode('utf-8')
    except KeyError:
        raise NoAttributeInDie(die)


def get_die_from_attribute(die, attribute):
    try:
        return die.get_DIE_from_attribute(attribute)
    except KeyError:
        raise NoAttributeInDie(die)


def get_type_qualifier(tag):
    return re.search(R"(?<=W_TAG_).+(?=_type)", tag).group()


def is_special_type(die):
    if die.tag in SPECIAL_TYPE_DECLARATIONS:
        return SPECIAL_TYPE_DECLARATIONS[die.tag] + " "
    return ""


def get_type(die, name="", temp=""):
    try:
        at_type = get_die_from_attribute(die, 'DW_AT_type')
        if at_type.tag in CVR_TYPE_QUALIFIERS_TAGS:
            temp = " " + get_type_qualifier(at_type.tag) + temp
        if at_type.tag == "DW_TAG_pointer_type":
            name = "*" + temp + name
            temp = ""
    except NoAttributeInDie:
        return "void" + temp + name
    try:
        return is_special_type(at_type) + \
               get_attribute_value(at_type, 'DW_AT_name') + temp + name
    except NoAttributeInDie:
        try:
            return get_type(at_type, name, temp)
        except Exception:
            logging.error(f"Should really not end up here", exc_info=True)


# In C one cannot just `inline` function like in C++
# Instead, one should proceed with `static inline`
def is_inline(die):
    if "DW_AT_inline" in die.attributes:
        return "static inline "
    return ""


def get_name(die):
    try:
        return get_attribute_value(die, 'DW_AT_name')
    except NoAttributeInDie:
        try:
            die = get_die_from_attribute(die, 'DW_AT_abstract_origin')
            return get_attribute_value(die, 'DW_AT_name')
        except NoAttributeInDie:
            return ""  # unnamed parameter, probably in function pointer


def process(die):
    return f"{is_inline(die)}{get_type(die)} {get_name(die)}"


def process_function(die):
    global _current_function
    _current_function = process(die)
    _prototypes[_current_function] = "void"


def process_arguments(die):
    _prototypes[_current_function] = process(die)


def die_info_rec(die):
    # We are interested only in prototypes, not function pointers
    if die.tag == "DW_TAG_subroutine_type":
        return

    # inlined subroutine should be checked separately:
    # http://lists.dwarfstd.org/pipermail/dwarf-discuss-dwarfstd.org/2020-July/004686.html
    # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=37801
    if die.tag == "DW_TAG_inlined_subroutine":
        die = get_die_from_attribute(die, 'DW_AT_abstract_origin')

    # There is no need to support "DW_TAG_entry_point" for now
    if die.tag == "DW_TAG_subprogram":
        process_function(die)
    if die.tag == "DW_TAG_formal_parameter":
        process_arguments(die)

    for child in die.iter_children():
        die_info_rec(child)


def main():
    args = create_parser().parse_args()
    if prototypes := parse(args.elf):
        for function, arguments in prototypes.items():
            print(f"{function}({arguments})")


if __name__ == '__main__':
    main()
