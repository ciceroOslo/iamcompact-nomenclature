"""Functions for validating names and variable/unit combinations."""
from collections.abc import Sequence
from typing import Optional, Dict, List

import pyam
from nomenclature import DataStructureDefinition, CodeList
from nomenclature.code import VariableCode
import pandas as pd

from . import get_dsd



def get_invalid_names(
        iamdf: pyam.IamDataFrame,
        dsd: Optional[DataStructureDefinition] = None,
        dimensions: Optional[Sequence[str]] = None
) -> Dict[str, str]:
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
    invalid_names: Dict[str, str] = {
        _dim: getattr(dsd, _dim).validate_items(getattr(iamdf, _dim))
        for _dim in dimensions
    }
    return invalid_names


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
    df_vars: List[str] = getattr(iamdf, variable_dimname)
    if not raise_on_missing_var:
        check_vars: List[str] = \
            [_var for _var in df_vars if _var in codelist]
    else:
        # Use all the variables in the IamDataFrame, and accept an error if any
        # turn out to be missing from the codelist
        check_vars = df_vars
    del df_vars
    unit_mappings: Dict[str, str] = iamdf.unit_mapping
    check_units: List[str] = [unit_mappings[_var] for _var in check_vars]
    unit_validations: List[str | List[str] | None] = [
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
        unit: str | List[str]
) -> str | List[str] | None:
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
    expected_unit: str | List[str] = code.unit
    # Fast-pass checks
    if unit == expected_unit:
        return None
    if isinstance(unit, str):
        if isinstance(expected_unit, str):
            return unit if unit != expected_unit else None
        else:
            return unit if unit not in expected_unit else None
    expected_unit = pyam.utils.to_list(expected_unit)
    invalid_units: List[str] = [u for u in unit if u not in expected_unit]
    return invalid_units if len(invalid_units) > 0 else None
