import logging

from src.argument_parser import create_parser
from src.dwarf_parser import DwarfParser

logging.basicConfig()


def main():
    args = create_parser().parse_args()
    print(f"Found prototypes:\n{DwarfParser(args.elf).parse()}")


if __name__ == '__main__':
    main()
