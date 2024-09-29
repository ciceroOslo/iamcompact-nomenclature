"""Utility functions for working with IAMC-style hierarchical variable names."""
import itertools
from typing import TypeVar

import pyam



def get_aggregate_var(
        varname: str,
        iamdf: pyam.IamDataFrame|None = None,
        check_all_levels: bool = False,
        sep: str = '|',
        variable_dimname: str = 'variable',
) -> str | None:
    """Get the aggregate variable of which a given variable is a component.

    This function can either try to find the aggreegate variable of a given
    component variable in an `IamDataFrame` and return None if it does not
    exist, or it can simply return the inferred aggregate variable based on the
    name of the component variable. The latter is done if the `iamdf` argument
    is not provided. The function then simply removes the last component from
    the variable name and returns the result.
    
    Parameters
    ----------
    variable : str
        The component variable for which to find the corresponding aggregate
    iamdf : pyam.IamDataFrame, optional
        The `IamDataFrame` to use for finding the aggregate variable. If not
        provided, the function will simply remove the last component from the
        variable name and return the result.
    check_all_levels : bool, optional
        Whether to check all levels of the variable hierarchy for the aggregate
        variable, or just the first level. Defaults to False. This argument is
        only used if `iamdf` is provided.
    sep : str, optional
        The separator used in the variable names. Defaults to "|".
    variable_dimname : str, optional
        The name of the variable dimension in the `IamDataFrame`. Defaults to
        "variable".
    
    Returns
    -------
    str or None
        The aggregate variable if found or inferred, or None. If `iamdf` is not
        provided and the variable name contains at last one separator, the
        function will return the variable name without the last component. If
        `iamdf` is provided, the function will return the aggregate variable if
        it is found, or None if it is not found. If `check_all_levels` is True,
        the function will check all levels above the level of `varname` and
        return the lowest-level aggregate variable that is found if any. If
        `check_all_levels` is False, the function will only check the first
        level above the level of `varname`, and return None if no direct
        aggregate variable is found.
    """
    # If the variable is already an aggregate variable, return it as is
    if sep not in varname:
        return None
    if iamdf is None:
        return sep.join(varname.split(sep)[:-1])
    idf_vars: list[str] = getattr(iamdf, variable_dimname)
    varname_components = varname.split(sep)
    if check_all_levels:
        for i in range(len(varname_components)-1, 0, -1):
            candidate = sep.join(varname_components[:i])
            if candidate in idf_vars:
                return candidate
    else:
        candidate = sep.join(varname_components[:-1])
        if candidate in idf_vars:
            return candidate
    return None


def get_component_vars(
        varname: str,
        iamdf: pyam.IamDataFrame,
        num_sublevels: int|None = None,
        sep: str = '|',
        variable_dimname: str = 'variable',
) -> list[str]:
    """Get the component variables of a given aggregate variable.

    This function returns a list of all the component variables of a given
    aggregate variable. If the aggregate variable is not found in the
    `IamDataFrame`, the function will return an empty list.

    Parameters
    ----------
    varname : str
        The aggregate variable for which to find the corresponding components
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` to use for finding the component variables
    num_sublevels : int, optional
        How many sublevels below `varname` to get component variables for. Set
        to None to get all sublevels. Optional, defaults to None.
    sep : str, optional
        The separator used in the variable names. Defaults to "|".
    variable_dimname : str, optional
        The name of the variable dimension in the `IamDataFrame`. Defaults to
        "variable".

    Returns
    -------
    list of str
        The component variables of the aggregate variable, or an empty list if
        the aggregate variable is not found in the `IamDataFrame`.
    """
    if varname not in getattr(iamdf, variable_dimname):
        return []
    component_vars: list[str] = [
        _var for _var in getattr(iamdf, variable_dimname)
        if _var.startswith(varname + sep) and (
            (num_sublevels is None) or
            (_var.count(sep) - varname.count(sep) <= num_sublevels)
        )
    ]
    # if num_sublevels > 1:
    #     subcomponent_vars = itertools.chain.from_iterable(
    #         [get_component_vars(
    #             varname=_var,
    #             iamdf=iamdf,
    #             num_sublevels=num_sublevels-1,
    #             sep=sep,
    #             variable_dimname=variable_dimname,
    #         ) for _var in component_vars]
    #     )
    # return component_vars + list(subcomponent_vars)
    return component_vars


TV = TypeVar('TV')

class IsNoneError(ValueError):
    """Raised when a value is None."""
    ...

def not_none(
        x: TV|None,
) -> TV:
    """Returns a value if None, otherwise raises an IsNoneError"""
    if x is None:
        raise IsNoneError()
    return x
