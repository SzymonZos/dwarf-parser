from argparse import ArgumentParser


def create_parser():
    parser = ArgumentParser(description="Extract dwarf info")
    parser.add_argument("-e", "--elf", type=str, action="store",
                        help="Select elf file")
    return parser
