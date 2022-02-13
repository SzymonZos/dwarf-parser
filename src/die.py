import re
import logging
from typing import Optional

from elftools.dwarf.die import DIE

from .utils import NoAttributeInDie, Prototypes

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Die:
    def __init__(self, die: DIE):
        self._die = die
        self.tag = self._die.tag

    def get_attribute_value(self, attribute: str) -> str:
        try:
            return self._die.attributes[attribute].value.decode('utf-8')
        except KeyError as e:
            raise NoAttributeInDie(self) from e

    def get_die_from_attribute(self, attribute: str) -> 'Die':
        try:
            return Die(self._die.get_DIE_from_attribute(attribute))
        except KeyError as e:
            raise NoAttributeInDie(self) from e

    # In C one cannot just `inline` function like in C++
    # Instead, one should proceed with `static inline`
    def is_inline(self) -> str:
        if "DW_AT_inline" in self._die.attributes:
            return "static inline "
        return ""

    def iter_children(self):
        return self._die.iter_children()

    def get_full_path(self) -> str:
        return self._die.get_full_path()


class Type:
    def __init__(self, die: Die):
        self._die = die
        self._name = ""
        self._temp = ""

    _CVR_QUALIFIERS_TAGS = [
        "DW_TAG_restrict_type",
        "DW_TAG_const_type",
        "DW_TAG_volatile_type"
    ]

    _SPECIAL_DECLARATIONS = {
        "DW_TAG_structure_type": "struct",
        "DW_TAG_union_type": "union",
        "DW_TAG_enumeration_type": "enum"
    }

    def get(self) -> Optional[str]:
        try:
            self._die = self._die.get_die_from_attribute('DW_AT_type')
            if self._die.tag in Type._CVR_QUALIFIERS_TAGS:
                self._temp = " " + self._get_qualifier(
                    self._die.tag) + self._temp
            if self._die.tag == "DW_TAG_pointer_type":
                self._name = "*" + self._temp + self._name
                self._temp = ""
        except NoAttributeInDie:
            return "void" + self._temp + self._name
        try:
            return self.is_special_type() + \
                   self._die.get_attribute_value(
                       'DW_AT_name') + self._temp + self._name
        except NoAttributeInDie:
            try:
                return self.get()
            except Exception:
                logger.error("Should really not end up here", exc_info=True)
                return None

    @staticmethod
    def _get_qualifier(tag: str) -> str:
        return re.search(R"(?<=W_TAG_).+(?=_type)", tag).group()

    def is_special_type(self) -> str:
        if self._die.tag in Type._SPECIAL_DECLARATIONS:
            return Type._SPECIAL_DECLARATIONS[self._die.tag] + " "
        return ""


class Name:
    def __init__(self, die: Die):
        self._die = die

    def get(self) -> str:
        try:
            return self._die.get_attribute_value('DW_AT_name')
        except NoAttributeInDie:
            try:
                self._die = self._die.get_die_from_attribute(
                    'DW_AT_abstract_origin')
                return self._die.get_attribute_value('DW_AT_name')
            except NoAttributeInDie:
                return ""  # unnamed parameter, probably in function pointer


class DieManager:
    def __init__(self, die: Die, prototypes: Prototypes):
        self._die = die
        self._prototypes = prototypes
        self._current_function = ""

    def recursively_traverse_dies(self):
        die = self._die
        # We are interested only in prototypes, not function pointers
        if self._die.tag == "DW_TAG_subroutine_type":
            return

        # inlined subroutine should be checked separately:
        # http://lists.dwarfstd.org/pipermail/dwarf-discuss-dwarfstd.org/2020-July/004686.html
        # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=37801
        if die.tag == "DW_TAG_inlined_subroutine":
            self._die = die.get_die_from_attribute('DW_AT_abstract_origin')

        # There is no need to support "DW_TAG_entry_point" for now
        if die.tag == "DW_TAG_subprogram":
            self._process_function()
        if die.tag == "DW_TAG_formal_parameter":
            self._process_arguments()

        for child in die.iter_children():
            self._die = Die(child)
            self.recursively_traverse_dies()

    def _process(self):
        return f"{self._die.is_inline()}" \
               f"{Type(self._die).get()} " \
               f"{Name(self._die).get()}"

    def _process_function(self):
        self._current_function = self._process()
        self._prototypes[self._current_function] = "void"

    def _process_arguments(self):
        self._prototypes[self._current_function] = self._process()
