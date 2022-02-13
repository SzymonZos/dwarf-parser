import atexit

from elftools.elf.elffile import ELFFile


class Prototypes(dict):
    def __str__(self):
        if self:
            return "\n".join([
                Prototypes._format(func, args) for func, args in self.items()])
        return "No prototypes"

    def entry_to_str(self, func: str) -> str:
        return Prototypes._format(func, self.get(func))

    @staticmethod
    def _format(func: str, args: str) -> str:
        return f"{func}({args})"


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
