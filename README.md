# dwarf-parser

Parser of ELF executable format containing DWARF debug symbols.  
Currently, one feature is supported, i.e. listing function prototypes.

## Installation

```bash
git clone https://github.com/SzymonZos/dwarf-parser.git
cd dwarf-parser
python -m venv venv
. ./venv/bin/activate # or whatever is supported on your OS
pip isntall -r requirements.txt
```

## Usage

```bash
python ./dwarf_parser.py --elf <path/to/file.elf>
```
