import logging
from typing import Dict, Optional, Union
from pathlib import Path

from elftools.dwarf.dwarfinfo import DWARFInfo

from .utils import ElfFile, Prototypes
from .die import DieManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DwarfParser:
    def __init__(self, elf_path: Union[str, Path]):
        self._elf_path = elf_path
        self._prototypes = Prototypes()

    def parse(self) -> Optional[Dict[str, str]]:
        if not (dwarf := self._get_dwarf_info()):
            return None

        for cu in dwarf.iter_CUs():
            logger.debug(f"Found a compile unit at offset {cu.cu_offset}, "
                         f"length {cu['unit_length']}")
            top_die = cu.get_top_DIE()
            logger.debug(f"Top DIE with tag={top_die.tag}, "
                         f"name={top_die.get_full_path()}")
            DieManager(top_die, self._prototypes).recursively_traverse_dies()
        return self._prototypes

    def _get_dwarf_info(self) -> Optional[DWARFInfo]:
        elf = ElfFile(self._elf_path)
        if elf.has_dwarf_info():
            return elf.get_dwarf_info()
        return None
