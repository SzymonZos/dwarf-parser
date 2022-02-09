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


def die_info_rec(die, CU, dwarf, indent_level='    '):
    """ A recursive function for showing information about a DIE and its
        children.
    """
    if die.tag in ["DW_TAG_subprogram", "DW_TAG_formal_parameter"]:
        out = f"{indent_level} + 'DIE tag={die.tag}"
        try:
            out = f"{out}: {die.attributes['DW_AT_name'].value.decode('utf-8')}"
        except KeyError:
            out = f"{out}: DW_AT_name not found"
        try:
            offset_to_find = die.attributes['DW_AT_type'].value
            out = f"{out}: {offset_to_find}"
            try:
                print(
                    f"{out}: HUGE DIE: {dwarf.get_DIE_from_refaddr(offset_to_find).attributes['DW_AT_name'].value}")
            except:
                print(f"{out} get_DIE_from_refaddr failed")
        except KeyError:
            print(f"{out}: DW_AT_type not found")
    child_indent = indent_level + '  '
    for child in die.iter_children():
        die_info_rec(child, CU, dwarf, child_indent)


def main():
    args = create_parser().parse_args()
    parse(args.elf)


if __name__ == '__main__':
    main()
