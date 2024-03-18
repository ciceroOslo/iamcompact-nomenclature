"""For checking scenario and variable names used in the result files"""

# %%
# Imports
from pathlib import Path
import typing as tp

import pyam
import pandas as pd
import nomenclature
import openpyxl

import iamcompact_nomenclature as icnom
from iamcompact_nomenclature.aggregation import check_var_aggregates
from iamcompact_nomenclature import var_utils


# %%
# Create a helper function that takes a function as an argument, and returns
# a modified function which will return the return value of the original
# function if it returns, but catch any exceptions and return them. The function
# should be properly type-annotated, with ParamSpecs to ensure that the
# modified function has the same signature and return type as the original
# function, except that it can return an exception as well as the original
# return type.
PS = tp.ParamSpec('PS')  # Parameter specifiction
RT = tp.TypeVar('RT')  # Return type
def return_exceptions(
    func: tp.Callable[PS, RT]
) -> tp.Callable[PS, RT|Exception]:
    def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RT|Exception:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return e
    return wrapper

# %%
# Define a function to open IAMC excel files with multiple sheets
def open_multisheet_iamc(path: Path|str) -> \
        pyam.IamDataFrame|Exception|dict[str, pyam.IamDataFrame|Exception]:
    sheetnames: list[str] = openpyxl.open(path).sheetnames
    if len(sheetnames) == 1:
        return return_exceptions(pyam.IamDataFrame)(path)
    else:
        return {
            sheetname: return_exceptions(pyam.IamDataFrame) \
                (path, sheet_name=sheetname)
            for sheetname in sheetnames
        }

# %%
# Get data files, and create a nested dict of IamDataFrames
data_root: Path = Path.home() / 'src' / 'repos' / 'pyam_analyses' / 'data' \
    / 'IAM_COMPACT' / 'studies'
data_dict: dict[str, pyam.IamDataFrame | Exception |
                      dict[str, pyam.IamDataFrame | Exception]] = dict()
_p: Path
_idf: pyam.IamDataFrame | Exception | dict[str, pyam.IamDataFrame | Exception]
relpaths: dict[Path, Path] = {
    _p: _p.relative_to(data_root)
    for _p in data_root.glob('**/*.xlsx')
}
for _abspath, _relpath in relpaths.items():
    _idf = open_multisheet_iamc(_abspath)
    data_dict[str(_relpath)] = _idf

# %%
# Flatten the dict by inserting an @ sign in front of tab names for files that
# have multiple tabs
flat_data_dict: dict[str, pyam.IamDataFrame | Exception] = dict()
for _relpath, _idf in data_dict.items():
    if isinstance(_idf, dict):
        for _tabname, _idf_tab in _idf.items():
            flat_data_dict[f'{_relpath}@{_tabname}'] = _idf_tab
    else:
        flat_data_dict[_relpath] = _idf

# %%
# Find all the scenarios in the data files
file_scenarios: dict[str, list[str]] = {
    _datafile: _idf.scenario for _datafile, _idf in flat_data_dict.items()
    if isinstance(_idf, pyam.IamDataFrame)
}

# %%
# Get a dsd and region processor
dsd: nomenclature.DataStructureDefinition = icnom.get_dsd()
regproc: nomenclature.RegionProcessor = icnom.get_region_processor()
