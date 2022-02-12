import unittest

from src.utils import ElfFile, NoAttributeInDie


class NoAttributeInDieStringifyTest(unittest.TestCase):
    def setUp(self):
        self.die = "Parsed DIE entry"


class NoMessageTest(NoAttributeInDieStringifyTest):
    def test_no_msg(self):
        exception = NoAttributeInDie(self.die)
        self.assertEqual(self.die, str(exception))


class WithMessageTest(NoAttributeInDieStringifyTest):
    def test_msg(self):
        msg = 'Something went wrong'
        exception = NoAttributeInDie(self.die, msg)
        expected = f"{msg}\n{self.die}"
        self.assertEqual(expected, str(exception))


if __name__ == '__main__':
    unittest.main()
