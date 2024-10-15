"""Notebook script to find overlaps between `common-definitions` and
`iamcompact-nomenclature-definitions`.
"""
# %%
# Imports
from collections.abc import Sequence
from pathlib import Path
import typing as tp

from nomenclature import (
    DataStructureDefinition,
)
from nomenclature.code import (
    Code,
    VariableCode,
)
from nomenclature.codelist import VariableCodeList

import iamcompact_nomenclature as icnom
from iamcompact_nomenclature.multi_load import MergedDataStructureDefinition

# %%
# Define paths for loading definitions from common-definitions and 
# iamcompact-nomenclature-definitions
DATA_ROOT: tp.Final[Path] = Path(icnom.__file__).parent / 'data'
ICNOM_DEFINITIONS_ROOT: tp.Final[Path] \
    = DATA_ROOT / 'iamcompact-nomenclature-definitions'
COMMON_DEFINITIONS_ROOT: tp.Final[Path] \
    = DATA_ROOT / 'common-definitions-fork'

# %%
# Load definitions and get the variable codelists
dsd_icnom: DataStructureDefinition = DataStructureDefinition(
    path=ICNOM_DEFINITIONS_ROOT / 'definitions'
)
vars_icnom: VariableCodeList = dsd_icnom.variable
dsd_common: DataStructureDefinition = DataStructureDefinition(
    path=COMMON_DEFINITIONS_ROOT / 'definitions'
)
vars_common: VariableCodeList = dsd_common.variable

# %%
# Get a dict of all variable codes in iamcompact-nomenclature-definitions
# that are also in common-definitions, and ones that are not.
varnames_icnom_in_common: set[str] = set(vars_icnom) & set(vars_common)
vars_icnom_overlap: dict[str, Code] = {
    _varname: vars_icnom[_varname]
    for _varname in sorted(varnames_icnom_in_common)
}
varnames_icnom_not_in_common: set[str] = set(vars_icnom) - set(vars_common)
vars_icnom_not_in_common: dict[str, Code] = {
    _varname: vars_icnom[_varname]
    for _varname in sorted(varnames_icnom_not_in_common)
}

# %%
# Define a function that takes a list of variable codes, and returns a dict from
# file names (given by the `file` attribute of each code) to lists of all codes
# that are in that file
def get_codes_by_file(codes: Sequence[Code]) -> dict[str|Path|None, list[Code]]:
    file_names: set[str|Path|None] = {_code.file for _code in codes}
    codes_by_file: dict[str|Path|None, list[Code]] = {
        _file_name: [_code for _code in codes if _code.file == _file_name]
        for _file_name in sorted(file_names)
    }
    return codes_by_file
###END def get_codes_by_file

# %%
# Get the overlapping codes in iamcompact-nomenclature-definitions by file name,
# and similarly for codes that are *not* in common-definitions
codes_by_file_icnom_in_common: dict[str|Path|None, list[Code]] \
    = get_codes_by_file(codes=list(vars_icnom_overlap.values()))

codes_by_file_icnom_not_in_common: dict[str|Path|None, list[Code]] \
    = get_codes_by_file(codes=list(vars_icnom_not_in_common.values()))
