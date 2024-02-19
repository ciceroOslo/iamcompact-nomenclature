"""Module for computing and checking aggregations of variables."""
from typing import Optional
from collections.abc import Sequence
import itertools

import pandas as pd
import pyam

from . import var_utils



def check_var_aggregates(
        iamdf: pyam.IamDataFrame,
        variables: Optional[Sequence[str]] = None,
        num_sublevels: Optional[int] = None,
        require_complete: bool = True,
        variable_dimname: str = 'variable',
        method: str = 'sum',
        **kwargs,
) -> tuple[pd.DataFrame|None, dict[str, list[str]]]:
    """Check aggregated variables in an `IamDataFrame`.
    
    The function will check whether aggregated variables are sums of their
    component variables, or optionally just whether the component variables sum
    up to less than the aggregated variable. 

    If any of the component variables add up to something other than or greter
    than (depending on `require_complete`) the aggregated variable, the function
    will return a tuple of a `pandas.DataFrame` with the items that failed the
    check along with the aggregate variable value and the component sum, and a
    dictionary of the component variables that were summed and compared to the
    aggregate variable. If all checks pass, the first component of the returned
    tuple will be `None`.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` to check or process.
    variables : sequence of str, optional
        The aggregated variables to check. If not provided, the function will
        check all top-level variables (i.e., variables that don't have a parent
        variable), and all aggregated variables down to the level specified by
        `num_sublevels`. Defaults to `None`.
    num_sublevels : int, optional
        How deep to recurse to aggregated subvariables. Set to 0 to check only
        the variables in `variables` against the sum of components one level
        below, and not check any of the components that are aggregates of deeper
        sublevels. Set to `None` to check all sublevels. Defaults to `None`.
    require_complete : bool, optional
        Whether to require that the components sum up to the aggregated
        variable, or just that they not sum up to anything *greater than* the
        aggregated variable. Set to False if you don't want to require that the
        data have a complete set of components for each aggregated variable, but
        do want to check that the aggregate is not smaller than the sum of the
        included components. Defaults to `True` (i.e., require that the
        components sum up to the aggregated variable).
    variable_dimname : str, optional
        The name of the variable dimension in the `IamDataFrame`. Defaults to
        "variable".
    method : str, optional
        The method to use for finding the component variables (passed to
        `pyam.IamDataFrame.check_aggregate`). Defaults to "sum".
    rtol : float, optional
        Relative tolerance for the check. Passed to `numpy.isclose`, see the
        documentation of that function for details. At the time of writing, the
        default value is `1e-5`. Note that the relative and absolute tolerances
        are added together to produce the actual tolerance threshold.
    atol : float, optional
        Absolute tolerance for the check. Passed to `numpy.isclose`, see the
        documentation of that function for details. At the time of writing, the
        default value is `1e-8`. Note that the relative and absolute tolerances
        are added together to produce the actual tolerance threshold.

    Returns
    -------
    (failed_checks, aggregation_map) failed_checks : pandas.DataFrame or None
        A dataframe with the items that failed the checks. The columns are: -
        "variable": The value of the aggregated variable - "components": The sum
        of the components The index is equal to the index for each datapoint of
        the aggregated variable that failed the check. This DataFrame is the
        same as that returned by `IamDataFrame.check_aggregate`. If all checks
        pass, this will be `None`.
    aggregation_map : dict
        A dictionary of the component variables that were summed and compared to
        each aggregate variable. The keys are the aggregated variables, and the
        values are lists of the component variables that were included in the
        sum.
    """
    invalid_kwarg_keys = [_kwarg_key for _kwarg_key in kwargs
                          if _kwarg_key not in ['rtol', 'atol']]
    if len(invalid_kwarg_keys) > 0:
        raise TypeError(
            'Invalid keyword argument' + ('s' if len(invalid_kwarg_keys) > 1 else '') +
            f' for check_var_aggregates: {", ".join(invalid_kwarg_keys)}' +
            '. The only valid keyword arguments beyond the ones in the ' +
            'function signature are "rtol" and "atol".'
        )
    if variables is None:
        variables = [
            _var for _var in iamdf.variable if var_utils.get_aggregate_var(
                varname=_var,
                iamdf=iamdf,
                check_all_levels=False,
            ) is None
        ]
    if num_sublevels != 0:
        vars_to_check: Sequence[str] = list(itertools.chain.from_iterable([
            var_utils.get_component_vars(
                varname=_var,
                iamdf=iamdf,
                num_sublevels=num_sublevels,
                variable_dimname=variable_dimname,
            ) for _var in variables
        ]))
    else:
        vars_to_check: Sequence[str] = variables
    failed_checks_df_list: list[pd.DataFrame] = list()
    aggregation_map: dict[str, list[str]] = dict()
    for _var in vars_to_check:
        _subvars: list[str] = var_utils.get_component_vars(
            varname=_var,
            iamdf=iamdf,
            num_sublevels=1,
            variable_dimname=variable_dimname,
        )
        if(len(_subvars) > 0):
            _failed_checks = iamdf.check_aggregate(
                variable=_var,
                method=method,
                **kwargs,
            )
            if _failed_checks is not None:
                failed_checks_df_list.append(_failed_checks)
            aggregation_map[_var] = _subvars
    failed_checks_df: pd.DataFrame|None = None \
        if len(failed_checks_df_list) == 0 else pd.concat(
            failed_checks_df_list,
        )
    return failed_checks_df, aggregation_map


def find_missing_aggregate_vars(
        iamdf: pyam.IamDataFrame,
        variable_dimname: str = 'variable',
) -> dict[str, list[str]]:
    """Find missing aggregated variables in an `IamDataFrame`.
    
    The function will find all non-top-level variables in `iamdf` for whic there
    is no corresponding parent variable in `iamdf`. I.e., any variable of the
    form `"A|B|C" for which there is no variable `"A|B"` in `iamdf`.

    All variables in `iamdf` are included in the check. If you want to restrict
    what variables to check, you need to filter `iamdf` before calling this
    function. To do this, you can use the `pyam.IamDataFrame.filter()` method,
    passing variable patterns to the `variable` argument, and restricting what
    levels to include in the check by using the `level` argument (e.g., passing
    `level="n+"` to include only variables that are `n` or more levels below the
    top level, or `level="n-"` to include levels that are `n` or fewer levels
    below the top level; setting `level` to an exact number does not make
    sense for use with this function).

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` to check or process.
    variable_dimname : str, optional
        The name of the variable dimension in the `IamDataFrame`. Defaults to
        "variable".

    Returns
    -------
    dict
        A dict with the missing aggregated variables as keys, and the component
        variables that are present in `iamdf` as values.
    """
