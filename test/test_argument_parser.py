import unittest

from src.argument_parser import create_parser


class PreprocessParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()


class AbbreviationTest(PreprocessParserTest):
    def test_elf(self):
        val = 'path/to/some.elf'
        parsed = self.parser.parse_args(['-e', val])
        self.assertEqual(val, parsed.elf)


class FullParamNameTest(PreprocessParserTest):
    def test_elf(self):
        val = 'path/to/some.elf'
        parsed = self.parser.parse_args(['--elf', val])
        self.assertEqual(val, parsed.elf)


if __name__ == '__main__':
    unittest.main()
