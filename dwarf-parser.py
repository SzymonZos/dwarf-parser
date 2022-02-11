import atexit

from argparse import ArgumentParser
from elftools.elf.elffile import ELFFile


def create_parser():
    parser = ArgumentParser(description="extract dwarf info")
    parser.add_argument("-e", "--elf", type=str, action="store",
                        help="Select elf file")
    return parser


class ElfFile(ELFFile):
    def __init__(self, path):
        self._fd = open(path, 'rb')
        super().__init__(self._fd)
        atexit.register(lambda: self._fd.close())


class NoAttributeInDie(Exception):
    def __init__(self, die, message=""):
        self._message = message
        self._die = die
        super().__init__(self._message)

    def __str__(self):
        return f"{self._message}\n{self._die}"


def parse(elf_path):
    elf = ElfFile(elf_path)
    if not elf.has_dwarf_info():
        return
    dwarf = elf.get_dwarf_info()
    for CU in dwarf.iter_CUs():
        # DWARFInfo allows to iterate over the compile units contained in
        # the .debug_info section. CU is a CompileUnit object, with some
        # computed attributes (such as its offset in the section) and
        # a header which conforms to the DWARF standard. The access to
        # header elements is, as usual, via item-lookup.
        print(
            f"  Found a compile unit at offset {CU.cu_offset}, length {CU['unit_length']}")

        # Start with the top DIE, the root for this CU's DIE tree
        top_die = CU.get_top_DIE()
        print(f"    Top DIE with tag={top_die.tag}")

        print(f"    name={top_die.get_full_path()}")

        # Display DIEs recursively starting with top_DIE
        die_info_rec(top_die)


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


def get_type(die, name=""):
    try:
        dw_at_type = get_die_from_attribute(die, 'DW_AT_type')
        if dw_at_type.tag == "DW_TAG_const_type":
            name = " const" + name
        if dw_at_type.tag == "DW_TAG_volatile_type":
            name = " volatile" + name
        if dw_at_type.tag == "DW_TAG_pointer_type":
            name = name + "*"
    except NoAttributeInDie:
        return f"void{name}"
    try:
        return f"{get_attribute_value(dw_at_type, 'DW_AT_name')}{name}"
    except NoAttributeInDie:
        try:
            return get_type(dw_at_type, name)
        except Exception:
            print("Should really not end up here")


def is_inline(die):
    if "DW_AT_inline" in die.attributes:
        return "inline"
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
    return f"{is_inline(die)} {get_type(die)} {get_name(die)}"


def die_info_rec(die, indent_level='    '):
    """ A recursive function for showing information about a DIE and its
        children.
    """
    # We are interested only in prototypes, not function pointers
    if die.tag == "DW_TAG_subroutine_type":
        return
    if die.tag == "DW_TAG_inlined_subroutine":
        die = die.get_DIE_from_attribute('DW_AT_abstract_origin')
    # I guess there is no need to support "DW_TAG_entry_point" for now
    if die.tag in ["DW_TAG_subprogram", "DW_TAG_formal_parameter"]:
        print(f"{indent_level}{process(die)}")

    child_indent = indent_level + '  '
    # print(f"{indent_level} {die.tag}")
    for child in die.iter_children():
        die_info_rec(child, child_indent)


def main():
    args = create_parser().parse_args()
    parse(args.elf)


if __name__ == '__main__':
    main()
