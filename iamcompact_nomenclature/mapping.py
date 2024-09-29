"""Functions for preforming region and variable mappings.

The main functionality in this module is for performing mapping of model-native
regions.
"""
from typing import (
    Literal,
    Optional,
    overload,
)

from nomenclature import (
    DataStructureDefinition,
    RegionProcessor,
)
import pyam

from . import (
    get_dsd,
    get_region_processor,
)
from .validation import get_invalid_model_regions
from .var_utils import not_none



@overload
def map_regions(
        iamdf: pyam.IamDataFrame,
        *,
        return_excluded: Literal[True],
        dsd: Optional[DataStructureDefinition] = None,
        region_processor: Optional[RegionProcessor] = None,
) -> tuple[pyam.IamDataFrame, pyam.IamDataFrame]:
    ...
@overload
def map_regions(
        iamdf: pyam.IamDataFrame,
        *,
        dsd: Optional[DataStructureDefinition] = None,
        region_processor: Optional[RegionProcessor] = None,
        return_excluded: Optional[bool] = None,
) -> pyam.IamDataFrame:
    ...
def map_regions(
        iamdf: pyam.IamDataFrame,
        *,
        dsd: Optional[DataStructureDefinition] = None,
        region_processor: Optional[RegionProcessor] = None,
        return_excluded: Optional[bool] = None,
) -> pyam.IamDataFrame | tuple[pyam.IamDataFrame, pyam.IamDataFrame]:
    """Perform region mapping without crashing on invalid regions.
    
    The function performs region mapping/aggregation like
    `nomenclature.RegionProcessor.apply`, but does not raise an exception if 
    invalid region names are encountered. Instead, those regions are excluded
    from the mapping. The function can return either only the processed results
    with only valid regions, or a tuple of both the processed results and the
    part of the input that was excluded from processing.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` to process.
    dsd : DataStructureDefinition, optional
        The `DataStructureDefinition` to validate against. Optional, will call
        `iamcompact_nomenclature.get_dsd()` if not provided.
    region_processor : nomenclature.RegionProcessor, optional
        The `RegionProcessor` object to use for the mapping. If not provided,
        `iamcompact_nomenclature.get_region_processor()` is used.
    return_excluded : bool, optional
        Whether to return the part of the input that was excluded from
        processing. Optional, by default False.

    Returns
    -------
    pyam.IamDataFrame or tuple of 2 pyam.IamDataFrame instances
        The processed `IamDataFrame` with mapped/aggregated/renamed regions, as
        well as any valid regions that were not changed. If `return_excluded` is
        True, a tuple is returned, where the 2nd element is an `IamDataFrame`
        with the part of the input that was excluded from processing (i.e.,
        invalid region names and unrecognized model/native-region combinations).
    """
    if return_excluded is None:
        return_excluded = False
    if dsd is None:
        dsd = get_dsd()
    if region_processor is None:
        region_processor = get_region_processor()
    invalid_regions_models: dict[str, list[str]] = get_invalid_model_regions(
        iamdf,
        dsd=dsd,
        region_processor=region_processor,
        return_valid_native_combos=False,
    )
    _filter_df = iamdf
    for _region, _models in invalid_regions_models.items():
        _filter_df = not_none(_filter_df.filter(region=_region, model=_models,
                                                keep=False))
        if len(_filter_df) == 0:
            break
    processed_iamdf: pyam.IamDataFrame = region_processor.apply(_filter_df)
    if not return_excluded:
        return processed_iamdf
    invalid_iamdfs: list[pyam.IamDataFrame] = [
        not_none(iamdf.filter(region=_region, model=_models))
        for _region, _models in invalid_regions_models.items()
    ]
    invalid_iamdf: pyam.IamDataFrame = pyam.concat(invalid_iamdfs)
    return processed_iamdf, invalid_iamdf
