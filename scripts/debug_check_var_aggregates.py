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
        / 'Report_IAM_COMPACT_PROMETHEUS_regions_nolinksv2.xlsx'
        # / 'iam_compact_st1__GCAM_iamc_report.xlsx'
idf: pyam.IamDataFrame = pyam.IamDataFrame(data_file)

# %%
# Get a dsd and region processor
dsd: nomenclature.DataStructureDefinition = icnom.get_dsd()
regproc: nomenclature.RegionProcessor = icnom.get_region_processor()

# %%
# Do a test variable aggregation check
var_res: icnom.aggregation.VarAggregationCheckResult = \
    icnom.aggregation.check_var_aggregates(iamdf=idf, dsd=dsd)

# %%
# Do a test region aggregation check
reg_res: icnom.aggregation.RegionAggregationCheckResult = \
    icnom.aggregation.check_region_aggregates(
        iamdf=idf,
        dsd=dsd,
        processor=regproc,
    )

# %%
# Test aggregation of selected variables
failed_checks_partial: pd.DataFrame|None
aggregation_map_partial: dict[str, list[str]]
failed_checks_partial, aggregation_map_partial = \
    icnom.aggregation.check_var_aggregates_manual(
        iamdf=idf,
        # variables=['Capacity|Electricity']
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
