"""Module for computing and checking aggregations of variables."""
from typing import Optional
from collections.abc import Sequence
import itertools
import dataclasses

import pandas as pd
import pyam
import nomenclature
from nomenclature import DataStructureDefinition
from nomenclature.code import VariableCode

from . import var_utils



@dataclasses.dataclass(kw_only=True, slots=True)
class AggregationCheckResult:
    """Result of a check for aggregated variables.
    
    Attributes
    ----------
    errors : pd.DataFrame|None
        A dataframe with the items that failed the checks. The columns are: -
        "variable": The value of the aggregated variable - "components": The sum
        of the components. The index is equal to the index for each datapoint of
        the aggregated variable that failed the check. This DataFrame is the
        same as that returned by `DataStructureDefinition.check_aggregate` and
        `IamDataFrame.check_aggregate`. Only variables for which the attribute
        `check-aggregate` is set in `dsd` will be checked, and only the
        components listed in the `components` attribute of each variable for
        which it exists (see the `nomenclature-iamc` documentation,
        https://nomenclature-iamc.readthedocs.io/en/stable/user_guide/variable.html).
        If all checks pass, this will be `None`.
    aggregation_map : dict[str, list[str]
        A dictionary of the component variables that were summed and compared to
        each aggregate variable. The keys are the aggregated variables, and the
        values are lists of the component variables that were included in the
        sum.
    not_checked : list[str]
        A list of the variables that were not checked. This will usually be
        equal to the variables that exist in both in the `iamdf` and `dsd`
        argument passed to `check_var_aggregates`, but for which the attribute
        `check-aggregate` is False or not set in `dsd`.
    unknown : list[str]
        A list of the variables in the `iamdf` argument to
        `check_var_aggregates` that are not present in the `dsd` argument. If
        `iamdf` has been through proper validation of variable names, this list
        should be empty.
    rtol, atol : float, optional
        Relative and absolute tolerances that were specified for the check
        (usually passed to `numpy.isclose`). Will be `None` if no tolerance
        arguments were passed to `check_var_aggregates`, in which the case the
        default tolerances for either `numpy.isclose` itself or for
        `nomenclature.DataStructureDefinition.check_aggregate` or
        `nomenclature.IamdDataFrame.check_aggregate` will have been used.
    """
    failed_checks: pd.DataFrame|None
    aggregation_map: dict[str, list[str] | list[dict[str, list[str]]] | None]
    not_checked: list[str]
    unkonwn: list[str]
    rtol: Optional[float] = None
    atol: Optional[float] = None



def check_var_aggregates(
        iamdf: pyam.IamDataFrame,
        dsd: nomenclature.DataStructureDefinition,
        atol: Optional[float] = None,
        rtol: Optional[float] = None,
) -> AggregationCheckResult:
    """Check aggregated variables based on aggregate specs in a DSD.
    
    The function mainly performs the same task as
    `nomenclature.DataStructureDefinition.check_aggregate`: It checks whether
    aggregated variables with the attribute `check-aggregate` set to True in the
    DSD are equal to the sum (or other aggregation method) of their component
    variables. If the attribute `components` is set for an aggregated variable,
    only the component variables listed in the `components` attribute will be
    included in the sum, or the aggregate will be checked against multiple
    hierarchies of components if they are present in the `components` attribute.

    The function additionally provides information on which aggregate variables
    have been checked against which components, which variables were not
    checked, and which variables are not present in the data structure
    definition. This information is returned in an `AggregationCheckResult`
    object.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` to check.
    dsd : nomenclature.DataStructureDefinition
        The `DataStructureDefinition` to use for the check. This object should
        have been created with the `nomenclature` package, and should have been
        set up with the `check-aggregate` attribute for the variables that are
        to be checked, and optionally the `components` attribute for aggregate
        variables for which not all components should be included, or for which
        there are separate hierarchies of components (such as "Final Energy"
        being disaggregated both by sector and by energy carrier). If the
        function is called from the top-level as
        `iamcompact_nomenclature.check_var_aggregates`, `dsd` is an optional
        keyword argument, and will be set equal to the return value of
        `iamcompact_nomenclature.get_dsd()` by default. If it is called as
        `iamcompact_nomenclature.aggregation.check_var_aggregates`, `dsd` is a
        required argument.
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
    AggregationCheckResult
        Results of the check. See the docstring for `AggregationCheckResult` for
        definition of the attributes.
    """
    # Find the variables in `iamdf` that are not present in `dsd.variable`,
    # since these must be filtered out before passing to `dsd.check_aggregate`.
    unknown_vars: list[str] = [
        _var for _var in iamdf.variable if _var not in dsd.variable  # type: ignore
    ]
    # Make a temporary list of all variables present in both `iamdf` and `dsd`
    common_vars: dict[str, VariableCode] = {
        _varname: dsd.variable[_varname]  # type: ignore[attr-defined]
        for _varname in iamdf.variable if _varname in dsd.variable  # type: ignore
    }
    # Then get the ones that have `check-aggregate` set to True in `dsd`
    vars_to_check: dict[str, VariableCode] = {
        _varname: _var for _varname, _var in common_vars.items()
        if _var.check_aggregate  # type: ignore[attr-defined]
    }
    # Make the initial component mapping
    component_map: dict[str, list[str] | list[dict[str, list[str]]] | None] = {
        _varname: _var.components for _varname, _var in vars_to_check.items()
    }
    # For the variables that have component attribute equal to None at this
    # point, set it equal to all the direct components
    for _varname, _components in component_map.items():
        if _components is None:
            component_map[_varname] = var_utils.get_component_vars(
                varname=_varname,
                iamdf=iamdf,
                num_sublevels=1,
            )
    unchecked_vars: list[str] = [
        _varname for _varname in common_vars if _varname not in vars_to_check
    ]
    # Check the aggregate variable for all variables in `vars_to_check`
    check_kwargs: dict[str, float] = dict()
    if rtol is not None:
        check_kwargs['rtol'] = rtol
    if atol is not None:
        check_kwargs['atol'] = atol
    errors: pd.DataFrame|None = dsd.check_aggregate(
        df=iamdf.filter(variable=list(vars_to_check.keys())),  # type: ignore[arg-type]
        **check_kwargs,
    )
    return AggregationCheckResult(
        failed_checks=errors,
        aggregation_map=component_map,
        not_checked=unchecked_vars,
        unkonwn=unknown_vars,
        rtol=rtol,
        atol=atol,
    )


def check_var_aggregates_manual(
        iamdf: pyam.IamDataFrame,
        variables: Optional[Sequence[str]] = None,
        num_sublevels: Optional[int] = None,
        require_complete: bool = True,
        variable_dimname: str = 'variable',
        method: str = 'sum',
        **kwargs,
) -> tuple[pd.DataFrame|None, dict[str, list[str]]]:
    """Check aggregated variables in an `IamDataFrame` without using a
    `nomenclature.DataStructureDefinition`.
    
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
        `num_sublevels`. "Top-level" variables here may include variables that
        are components of other variables, but where there is no direct parent
        variable, e.g., because there is a gap of more than one level between
        the variable and the closest variable above it in the hierarchyl.
        Defaults to `None`.
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
    vars_to_check: list[str] = list(variables)
    if num_sublevels != 0:
        vars_to_check += list(itertools.chain.from_iterable([
            var_utils.get_component_vars(
                varname=_var,
                iamdf=iamdf,
                num_sublevels=num_sublevels,
                variable_dimname=variable_dimname,
            ) for _var in variables
        ]))
    # The procedure above may add some variables more than once, so keep only
    # the unique values of `vars_to_check`. We want to preserve the original
    # order of the variables in `vars_to_check`, so we can't use a set here.
    vars_to_check = list(dict.fromkeys(vars_to_check))
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
    raise NotImplementedError('This function has not been implemented yet '
                              '(and may never be).')
