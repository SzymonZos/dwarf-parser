import unittest

from src.utils import Prototypes, NoAttributeInDie


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


class NoPrototypesDetectedTest(unittest.TestCase):
    def test_prototypes(self):
        self.assertEqual("No prototypes", str(Prototypes()))


class PrototypesDetectedTest(unittest.TestCase):
    def test_prototypes(self):
        prototypes = Prototypes()
        prototypes["int main"] = "void"
        prototypes["const char* foo"] = "size_t size"
        expected = "int main(void)\n" \
                   "const char* foo(size_t size)"
        self.assertEqual(expected, str(prototypes))


if __name__ == '__main__':
    unittest.main()
