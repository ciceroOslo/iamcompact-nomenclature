"""Module for computing and checking aggregations of variables."""
from typing import Optional
from collections.abc import Sequence

import pandas as pd
import pyam



def check_var_aggregates(
        iamdf: pyam.IamDataFrame,
        variables: Optional[Sequence[str]] = None,
        num_sublevels: Optional[int] = None,
        tolerance: Optional[float] = 0.01,
        require_complete: bool = True,
        variable_dimname: str = 'variable',
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
    tolerance : float, optional
        The tolerance for the check. If the difference between the aggregated
        variable and the sum of its components is greater than this value, the
        check will fail. Note that this is *absolute* difference, not the
        relative ratio. Defaults to 0.01.
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

    Returns
    -------
    (failed_checks, aggregation_map)
    failed_checks : pandas.DataFrame or None
        A dataframe with the items that failed the checks. The columns are:
        - "aggregate": The value of the aggregated variable
        - "components": The sum of the components
        The index is equal to the index for each datapoint of the aggregated
        variable that failed the check. If all checks pass, this will be `None`.
    aggregation_map : dict
        A dictionary of the component variables that were summed and compared to
        each aggregate variable. The keys are the aggregated variables, and the
        values are lists of the component variables that were included in the
        sum.
    """
    # Get the variables to check
    if variables is None:
        variables = iamdf.filter(variable=variable_dimname).data[variable_dimname].unique()
    else:
        variables = list(variables)
    
    # Get the components for each variable
    components = {}
    for variable in variables:
        components[variable] = iamdf.filter(variable=variable).data[variable_dimname].unique()
    
    # Check the components
    failed_checks = pd.DataFrame()
    for variable, component_vars in components.items():
        # Get the data for the aggregated variable
        agg_data = iamdf.filter(variable=variable)
        # Get the data for the components
        comp_data = iamdf.filter(variable=component_vars)
        # Sum the components
        comp_sum = comp_data.timeseries().sum(axis=1)
        # Check the sum
        if require_complete:
            failed = agg_data.timeseries() - comp_sum
            failed = failed[failed.abs() > tolerance]
        else:
            failed = agg_data.timeseries() - comp_sum
            failed = failed[failed < -tolerance]
        if not failed.empty:
            failed_checks = failed_checks.append(
                pd.DataFrame(
                    {
                        "aggregate": agg_data.timeseries().values,
                        "components": comp_sum.values,
                        "component_vars": comp_sum.columns,
                    },
                    index=failed.index,
                )
            )
        # Add the "Other" variable if necessary
        if add_other:
            other = agg_data.timeseries() - comp_sum
            other = other[other.abs() > tolerance]
            if not other.empty:
                other = other.rename(columns={variable: other_label})
                if process_inplace:
                    iamdf.append(other, variable_dimname=variable_dimname)
                else:
                    if return_added_only:
                        return other
                    else:
                        iamdf = iamdf.append(other, variable_dimname=variable_dimname)
    
    # Return the processed dataframe and the failed checks
    if return_added_only:
        return None, failed_checks
    else:
        return iamdf, failed_checks
    
