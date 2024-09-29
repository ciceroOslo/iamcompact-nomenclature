"""Functions for validating names and variable/unit combinations."""
from collections.abc import Sequence
from typing import (
    Literal,
    Optional,
    TypeVar,
    overload,
)

import pyam
from nomenclature import (
    CodeList,
    DataStructureDefinition,
    RegionProcessor,
)
from nomenclature.code import VariableCode
import pandas as pd

from . import (
    get_dsd,
    get_region_processor,
)
from .var_utils import not_none



def get_invalid_names(
        iamdf: pyam.IamDataFrame,
        dsd: Optional[DataStructureDefinition] = None,
        dimensions: Optional[Sequence[str]] = None
) -> dict[str, list[str]]:
    """Returns a dictionary of invalid names in a given `IamDataFrame`.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` with model output to be validated.
    dsd : DataStructureDefinition, optional
        The `DataStructureDefinition` to validate against. Optional, will call
        `iamcompact_nomenclature.get_dsd()` if not provided.
    dimensions : sequence of str, optional
        The dimensions to validate. Optional, defaults to the intersection of
        dimensions that are found in both `iamdf` and in `dsd`.

    Returns
    -------
    dict
        A dictionary with the dimensions as keys and a list of invalid names
        found in each dimension as values.
    """
    if dsd is None:
        dsd = get_dsd()
    if dimensions is None:
        dimensions = [_dim for _dim in dsd.dimensions
                      if _dim in iamdf.dimensions]
    # For each dimension, get the corresponding CodeList from `dsd` and validate
    # the names in `iamdf` against it
    invalid_names: dict[str, list[str]] = {
        _dim: getattr(dsd, _dim).validate_items(getattr(iamdf, _dim))
        for _dim in dimensions
    }
    return invalid_names


@overload
def get_invalid_model_regions(
        iamdf: pyam.IamDataFrame,
        *,
        return_valid_native_combos: Literal[True],
        dsd: Optional[DataStructureDefinition] = None,
        region_processor: Optional[RegionProcessor] = None,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    ...
@overload
def get_invalid_model_regions(
        iamdf: pyam.IamDataFrame,
        *,
        dsd: Optional[DataStructureDefinition] = None,
        region_processor: Optional[RegionProcessor] = None,
        return_valid_native_combos: Optional[bool] = None,
) -> dict[str, list[str]]:
    ...
def get_invalid_model_regions(
        iamdf: pyam.IamDataFrame,
        *,
        dsd: Optional[DataStructureDefinition] = None,
        region_processor: Optional[RegionProcessor] = None,
        return_valid_native_combos: Optional[bool] = None,
) -> dict[str, list[str]] | tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Returns a dict of invalid region/model name combinations.

    Unlike `get_invalid_names`, this function will use a `RegionProcessor` to
    check whether unrecognized region names are defined as native regions for
    any models, and exclude any valid combinations of model and model-native
    region names from the returned invalid regions.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` with data to check for region names.
    dsd : DataStructureDefinition, optional
        The `DataStructureDefinition` to validate against. Optional, will call
        `iamcompact_nomenclature.get_dsd()` if not provided.
    region_processor : nomenclature.RegionProcessor, optional
        The `RegionProcessor` to use for finding model-native region names. If
        not provided, will call `nomenclature.get_region_processor()`.
    return_valid_native_combos : bool, optional
        Whether to additionally return a dict of region names in `iamdf` that
        are not valid common region names, but which were found in combination
        with a model name for which the region name is a recognized native
        region. The function will then return a tuple of dicts. Optional, by
        default False.

    Returns
    -------
    dict[str, list[str]] or tuple
        If `return_valid_native_combos` is False, returns a dict of invalid
        regionmodel name combinations. The invalid region names are the keys,
        and the values will be a list of models for which that region name is
        found in `iamdf`, but for which is not a recognized model-native region.
        If `return_valid_native_combos` is True, returns a tuple, with the
        dict of invalid region names as the first element, and as the second a
        dict with valid model-native region names as keys and a list of the
        corresponding models as values. The last dict only includes combinations
        of model-native region names and models that were found in `iamdf`. It
        does not include recobnized common names that are valid for all models,
        or reconized region/model combos that were not found in `iamdf`.
    """
    if return_valid_native_combos is None:
        return_valid_native_combos = False
    if region_processor is None:
        region_processor = get_region_processor()
    invalid_regions_common: list[str] = get_invalid_names(iamdf, dsd)['region']
    check_native_iamdf: pyam.IamDataFrame = \
        not_none(iamdf.filter(region=invalid_regions_common))
    invalid_combos: dict[str, list[str]] = dict()
    valid_combos: dict[str, list[str]] = dict()

    model_native_regions: dict[str, list[str]] = {
        _model: region_processor.mappings[_model].model_native_region_names
        for _model in region_processor.mappings.keys()
    }

    for _region in check_native_iamdf.region:
        _models = not_none(check_native_iamdf.filter(region=_region)).model
        if len(_models) == 0:
            raise RuntimeError(
                f'Invalid region {_region} found, but not used by any model. '
                'This should not be possible at this point in the code.'
            )
        _valid_models: list[str] = [
            _model for _model, _native_regions in model_native_regions.items()
            if _region in _native_regions
        ]
        _invalid_models: list[str] = [
            _model for _model in _models if _model not in _valid_models
        ]
        if len(_invalid_models) > 0:
            invalid_combos[_region] = _invalid_models
        if len(_valid_models) > 0:
            valid_combos[_region] = _valid_models

    if return_valid_native_combos:
        return invalid_combos, valid_combos
    else:
        return invalid_combos


def get_invalid_variable_units(
        iamdf: pyam.IamDataFrame,
        dsd: Optional[DataStructureDefinition] = None,
        raise_on_missing_var: bool = False,
        variable_dimname: str = 'variable'
) -> pd.DataFrame | None:
    """Gets all invalid variable/unit combinations in an `IamDataFrame`.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        IamDataFrame to validate
    dsd : DataStructureDefinition, optional
        The DataStructureDefinition to validate against. Optional, will call
        `iamcompact_nomenclature.get_dsd()` if not provided.
    raise_on_missing_var : bool, optional
        If True, raise a KeyError if `iamdf` contains variables that are not
        defined in `dsd`. If False, ignore such variables. Optional, default:
        False.

    Returns
    -------
    pandas.DataFrame` or None
        DataFrame with invalid and expected units for each variable in `df` that
        has an invalid unit. The DataFrame has the variable names in the index,
        and two columns that each contain strings or lists of strings: -
        "invalid": the invalid unit or list of units. For variables with
          multiple units, the element on the corresponding row will be a list of
          all the units that occur in `df` for that variable, including valid
          units in addition to the invalid one(s).
        - "expected": the expected (i.e., valid) unit or list of units for for
          each variable.

    Raises
    ------
    KeyError
        If `on_missing_var` is "raise" and `df` contains variables that are not
        defined in the codelist.
    """
    codelist: CodeList = getattr(dsd, variable_dimname)
    # If raise_on_missing_var is False, check only the variables that are
    # present in the codelist. If True, check all variables in the
    # IamDataFrame, and let the KeyError propagate if any are not in the
    # codelist.
    df_vars: list[str] = getattr(iamdf, variable_dimname)
    if not raise_on_missing_var:
        check_vars: list[str] = \
            [_var for _var in df_vars if _var in codelist]
    else:
        # Use all the variables in the IamDataFrame, and accept an error if any
        # turn out to be missing from the codelist
        check_vars = df_vars
    del df_vars
    unit_mappings: dict[str, str] = iamdf.unit_mapping
    check_units: list[str] = [unit_mappings[_var] for _var in check_vars]
    unit_validations: list[str | list[str] | None] = [
        _validate_unit(codelist[_var], _unit)
        for _var, _unit in zip(check_vars, check_units)
    ]
    validation_df: pd.DataFrame = pd.DataFrame(
        data={
            "variable": check_vars,
            "invalid": unit_validations
        }
    ).set_index("variable").loc[lambda df: df["invalid"].notnull()]
    if validation_df.empty:
        return None
    validation_df["expected"] = [
        codelist[_var].unit for _var in validation_df.index
    ]
    return validation_df


def _validate_unit(
        code: VariableCode,
        unit: str | list[str]
) -> str | list[str] | None:
    """Checks whether `unit` is a valid unit or list of units for `code`.

    `code` needs to represent a variable, i.e., be a
    `nomenclature.code.VariableCode` instance. The function will return `unit`
    if it is a string and not a valid unit for `code`, or a list of invalid
    units if `code` is a list of unit names.

    Parameters
    ----------
    code : Code
        The variable code instance to validate against.
    unit : str or list of str
        The unit or units to validate.

    Returns
    -------
    str or list of str or None
        The invalid unit or list of invalid units, or None if `unit` is valid.
        If `unit` is a list of units and there is just one invalid unit, the
        function will return a list of one element. If `unit` is a string and
        not a valid unit, the function will return the string.
    """
    expected_unit: str | list[str] = code.unit
    # Fast-pass checks
    if unit == expected_unit:
        return None
    if isinstance(unit, str):
        if isinstance(expected_unit, str):
            return unit if unit != expected_unit else None
        else:
            return unit if unit not in expected_unit else None
    expected_unit = pyam.utils.to_list(expected_unit)
    invalid_units: list[str] = [u for u in unit if u not in expected_unit]
    return invalid_units if len(invalid_units) > 0 else None
