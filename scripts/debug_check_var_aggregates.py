"""Debugging `aggregation.check_var_aggregates`"""

# %%
# Imports
from pathlib import Path

import pyam
import pandas as pd
import nomenclature

import iamcompact_nomenclature as icnom
from iamcompact_nomenclature.aggregation import check_var_aggregates
from iamcompact_nomenclature import var_utils

# %%
# Get data file
data_file: Path = Path.home() / 'src' / 'repos' / 'pyam_analyses' / 'data' \
    / 'IAM_COMPACT' / 'studies' / 'S01_NECPs' \
        / 'iam_compact_st1__GCAM_iamc_report.xlsx'
        # / 'Report_IAM_COMPACT_PROMETHEUS_regions_nolinksv2.xlsx'
idf: pyam.IamDataFrame = pyam.IamDataFrame(data_file)

# %%
# Get a dsd and region processor
dsd: nomenclature.DataStructureDefinition = icnom.get_dsd()
regproc: nomenclature.RegionProcessor = icnom.get_region_processor()

# %%
# Do a test check
res = icnom.aggregation.check_var_aggregates(iamdf=idf, dsd=dsd)

# %%
# Test aggregation of selected variables
failed_checks_partial: pd.DataFrame|None
aggregation_map_partial: dict[str, list[str]]
failed_checks_partial, aggregation_map_partial = check_var_aggregates(
    iamdf=idf,
    variables=['Capacity|Electricity']
)

# %%
# Test aggregation of all variables
failed_checks: pd.DataFrame|None
aggregation_map: dict[str, list[str]]
failed_checks, aggregation_map = check_var_aggregates(
    iamdf=idf,
)

# %%
# Now test region mapping
regmap: nomenclature.RegionProcessor = icnom.get_region_processor()
