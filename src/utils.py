import atexit

from elftools.elf.elffile import ELFFile


class Prototypes(dict):
    def __str__(self):
        if self:
            return "\n".join([f"{func}({arg})" for func, arg in self.items()])
        return "No prototypes"


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
        if self._message == "":
            return f"{self._die}"
        return f"{self._message}\n{self._die}"
