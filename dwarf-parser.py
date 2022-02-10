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


def parse(elf_path):
    elf = ElfFile(elf_path)
    if elf.has_dwarf_info():
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
            top_DIE = CU.get_top_DIE()
            print(f"    Top DIE with tag={top_DIE.tag}")

            print(f"    name={top_DIE.get_full_path()}")

            # Display DIEs recursively starting with top_DIE
            die_info_rec(top_DIE, CU, dwarf)


def get_type(die, name=""):
    try:
        dw_at_type = die.get_DIE_from_attribute('DW_AT_type')
        if dw_at_type.tag == "DW_TAG_const_type":
            name = " const" + name
        if dw_at_type.tag == "DW_TAG_volatile_type":
            name = " volatile" + name
        if dw_at_type.tag == "DW_TAG_pointer_type":
            name = name + "*"
    except KeyError:
        try:
            return f"{die.attributes['DW_AT_name'].value}{name}"
        except KeyError:
            return f"void{name}"
    try:
        return f"{dw_at_type.attributes['DW_AT_name'].value}{name}"
    except KeyError:
        try:
            return get_type(dw_at_type, name)
        except:
            print("really bad")


def die_info_rec(die, CU, dwarf, indent_level='    '):
    """ A recursive function for showing information about a DIE and its
        children.
    """
    if die.tag == "DW_TAG_inlined_subroutine":
        die = die.get_DIE_from_attribute('DW_AT_abstract_origin')
    if die.tag in ["DW_TAG_subprogram", "DW_TAG_formal_parameter"]:
        try:
            out = f"{die.attributes['DW_AT_name'].value.decode('utf-8')}"
        except KeyError:
            try:
                die = die.get_DIE_from_attribute('DW_AT_abstract_origin')
                out = f"{die.attributes['DW_AT_name'].value.decode('utf-8')}"
            except KeyError:
                out = ""  # unnamed parameter
        try:
            try:
                out = f"{get_type(die)} {out}"
            except Exception as e:
                out = f"{out} get_DIE_from_refaddr failed {e}: {die.get_DIE_from_attribute('DW_AT_type')}"  # TODO: to be removed
        except KeyError:
            out = f"void {out}"
    try:
        x = die.attributes["DW_AT_inline"]
        out = f"inline {out}"
    except KeyError:
        pass
    try:
        print(f"{indent_level}{out}")
    except UnboundLocalError:
        pass
    child_indent = indent_level + '  '
    for child in die.iter_children():
        die_info_rec(child, CU, dwarf, child_indent)


def main():
    args = create_parser().parse_args()
    parse(args.elf)


if __name__ == '__main__':
    main()
