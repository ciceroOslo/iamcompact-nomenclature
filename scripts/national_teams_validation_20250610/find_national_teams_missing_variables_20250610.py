"""Script to find variables that national teams reported to be missing or wanted
to be added in email sent to Shivika on 2025-05-26.
"""

# %% [markdown]
# Imports
# %%
import enum
from pathlib import Path

import nomenclature
import nomenclature.codelist
import pandas as pd
import pyam

from iamcompact_nomenclature import get_dsd

# %% [markdown]
# Increase pandas DataFrame display sizes so we can view more rows
# %%
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# %% [markdown]
# Get data
# %%
dsd: nomenclature.DataStructureDefinition = get_dsd()
var_cl: nomenclature.codelist.VariableCodeList = dsd.variable

national_teams_var_file: Path = Path(__file__).parent / \
    'Variables_national_teams_20250526.xlsx'
national_teams_var_df: pd.DataFrame = pd.read_excel(national_teams_var_file)

# %% [markdown]
# Define column names
# %%
class TeamsVarsCol(enum.StrEnum):
    VARNAME = 'Variable Name '
    DESCRIPTION = 'Description'
    UNIT = 'Unit'

class CodeListCol(enum.StrEnum):
    VARIABLE = 'variable'
    DESCRIPTION = 'description'
    UNIT = 'unit'

class CodeListRenamedCol(enum.StrEnum):
    VARIABLE = TeamsVarsCol.VARNAME
    DESCRIPTION = f'{TeamsVarsCol.DESCRIPTION} (from codelist)'
    UNIT = f'{TeamsVarsCol.UNIT} (from codelist)'

class MergedDfExtraCols(enum.StrEnum):
    VARNAME_MATCH = 'Already added'
    UNITS_MATCH = 'Units match'
    STATUS = 'Status'

# %% [markdown]
# Create sets of variables in `var_cl` and in `national_teams_var_df`, and find
# which variables in the latter are not present in the former. Note that the
# column name 'Variable Name ' from the teams has an extra space at the end of
# the column name.
# %%
var_cl_vars: set[str] = set(var_cl.variables)
var_cl_df: pd.DataFrame = var_cl.to_pandas()
national_teams_vars: set[str] = \
    set(national_teams_var_df[TeamsVarsCol.VARNAME].str.strip())

# %%
unrecognized_vars: set[str] = national_teams_vars - var_cl_vars
unrecognized_vars_df: pd.DataFrame = national_teams_var_df[
    national_teams_var_df[TeamsVarsCol.VARNAME].isin(unrecognized_vars)
]

# %% [markdown]
# Produce a new DataFrame with the same rows as the national teams file, but
# with description and units from the variable codelist added in new columns
# where the name matches one in the codelist.
# %%
# joined_df: pd.DataFrame = national_teams_var_df.dropna(
#     axis=0, subset=[TeamsVarsCol.VARNAME]
# ).set_index(TeamsVarsCol.VARNAME).join(
#     var_cl_df.loc[
#         :,
#         [
#             CodeListCol.VARIABLE,
#             CodeListCol.DESCRIPTION,
#             CodeListCol.UNIT,
#         ]
#     ].rename(
#         columns={
#             CodeListCol.VARIABLE: str(CodeListRenamedCol.VARIABLE),
#             CodeListCol.DESCRIPTION: str(CodeListRenamedCol.DESCRIPTION),
#             CodeListCol.UNIT: str(CodeListRenamedCol.UNIT),
#         }
#     ).set_index(CodeListRenamedCol.VARIABLE),
#     on=str(TeamsVarsCol.VARNAME),
#     how='left',
# )

# %%
joined_df: pd.DataFrame = pd.merge(
    national_teams_var_df,
    var_cl_df.loc[
        :,
        [
            CodeListCol.VARIABLE,
            CodeListCol.DESCRIPTION,
            CodeListCol.UNIT,
        ]
    ].rename(
        columns={
            CodeListCol.VARIABLE: str(CodeListRenamedCol.VARIABLE),
            CodeListCol.DESCRIPTION: str(CodeListRenamedCol.DESCRIPTION),
            CodeListCol.UNIT: str(CodeListRenamedCol.UNIT),
        }
    ).assign(**{MergedDfExtraCols.VARNAME_MATCH: True}),
    on=str(TeamsVarsCol.VARNAME),
    how='left',
)

# %% [markdown]
# Add columns for whether or not units match
# %%
joined_df[str(MergedDfExtraCols.UNITS_MATCH)] = (
    joined_df[str(CodeListRenamedCol.UNIT)] == joined_df[str(TeamsVarsCol.UNIT)]
).mask(joined_df[CodeListRenamedCol.UNIT].isna(), '')

joined_df[MergedDfExtraCols.VARNAME_MATCH] = \
    joined_df[MergedDfExtraCols.VARNAME_MATCH].where(
        joined_df[MergedDfExtraCols.VARNAME_MATCH],
        False,
    )

joined_df = joined_df.fillna('')

# %% [markdown]
# Add comment that unit has been added in common-definitions where 
joined_df[MergedDfExtraCols.STATUS] = ''
joined_df[MergedDfExtraCols.STATUS] = \
    joined_df[MergedDfExtraCols.STATUS].case_when(
        [
            (
                joined_df[MergedDfExtraCols.UNITS_MATCH],
                'Added through common-definitions in latest version'
            ),
            (
                joined_df[MergedDfExtraCols.VARNAME_MATCH],
                'Added through common-definitions, but units do not match. ' \
                'Please consider whether you can swith to the unit listed in '
                f'the column {CodeListRenamedCol.UNIT}.'
            ),
        ]
    )
