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

# %%
# Get a list of the variables that have identical definitions (Code objects) in
# both iamcompact-nomenclature-definitions and common-definitions, and a dict
# with them by file.
attrs_to_compare: tuple[str, ...] = (
    'description', 'extra_attributes', 'unit', 'weight', 'region_aggregation',
    'skip_region_aggregation', 'method', 'check_aggregate', 'components',
    'drop_negative_weights',
)
vars_icnom_common_identical: list[Code] = [
    vars_icnom[_codename] for _codename in vars_icnom_overlap
    if all(
        getattr(vars_icnom[_codename], _attr) == getattr(vars_common[_codename], _attr)
        for _attr in attrs_to_compare
    )
]

vars_icnom_common_identical_by_file: dict[str|Path|None, list[Code]] \
    = get_codes_by_file(codes=vars_icnom_common_identical)

# %%
# Get a list of variables that have the same name but are not identical in
# iamcompact-nomenclature-definitions and common-definitions
vars_icnom_common_not_identical: list[Code] = [
    vars_icnom[_codename] for _codename in vars_icnom_overlap
    if not all(
        getattr(vars_icnom[_codename], _attr) == getattr(vars_common[_codename], _attr)
        for _attr in attrs_to_compare
    )
]

vars_icnom_common_not_identical_by_file: dict[str|Path|None, list[Code]] \
    = get_codes_by_file(codes=vars_icnom_common_not_identical)

# %%
# Find the attributes that are different for all codes that have the same name
# but are not identical in iamcompact-nomenclature-definitions and
# common-definitions
vars_icnom_common_differences: dict[str, dict[str, tuple[tp.Any, tp.Any]]] \
    = dict()

for _varname in [_code.name for _code in vars_icnom_common_not_identical]:
    _icnom_var = vars_icnom[_varname]
    _common_var = vars_common[_varname]
    _icnom_common_diffs: dict[str, tuple[tp.Any, tp.Any]] = {
        _attr: (getattr(_icnom_var, _attr), getattr(_common_var, _attr))
        for _attr in attrs_to_compare
        if getattr(_icnom_var, _attr) != getattr(_common_var, _attr)
    }
    vars_icnom_common_differences[_varname] = _icnom_common_diffs


# %%
