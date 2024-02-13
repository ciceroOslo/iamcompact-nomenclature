"""Module for computing and checking aggregations of variables."""
from typing import Optional
from collections.abc import Sequence

import pandas as pd
import pyam



def check_var_aggregates(
        iamdf: pyam.IamDataFrame,
        variables: Optional[Sequence[str]] = None,
        num_recurse_sublevels: Optional[int] = None,
        tolerance: Optional[float] = 0.01,
        require_complete: bool = True,
        add_other: bool = False,
        other_label: str = 'Other',
        return_added_only: bool = False,
        process_inplace: bool = False,
        variable_dimname: str = 'variable',
) -> tuple[pyam.IamDataFrame, pd.DataFrame]:
    """Check aggregated variables in an `IamDataFrame` or add missing parts.
    
    The function will check whether aggregated variables are sums of their
    component variables, or optionally just whether the component variables sum
    up to less than the aggregated variable. If components sum up to less than
    the aggregated variable, the function can optionally add the difference as a
    new variable ("Other").

    It will return a tuple of a processed `IamDataFrame` (either the complete
    dataframe with added "Other" variables, or just the added "Other" variables)
    and a `pandas.DataFrame` with the items that failed the checks.

    Parameters
    ----------
    iamdf : pyam.IamDataFrame
        The `IamDataFrame` to check or process.
    variables : sequence of str, optional
        The aggregated variables to check. If not provided, the function will
        check all top-level variables (i.e., variables that don't have a parent
        variable).
    num_recurse_sublevels : int, optional
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
    add_other : bool, optional
        Whether to add a new variable with the difference between the aggregated
        variable and the sum of its components. If True, `require_complete` is
        ignored. Defaults to `False`.
    other_label : str, optional
        The label to use for the "Other" variable if `add_other` is True.
        Defaults to "Other".
    return_added_only : bool, optional
        Whether to return only the added "Other" variables, or the complete
        dataframe with added "Other" variables. Defaults to `False`. Note that
        if this is True and `add_other` is False, the first component of the
        returned tuple will be `None`.
    process_inplace : bool, optional
        Whether to process the dataframe in place. Defaults to `False`. Ignored
        if `return_added_only` is True.
    variable_dimname : str, optional
        The name of the variable dimension in the `IamDataFrame`. Defaults to
        "variable".

    Returns
    -------
    processed_iamdf, failed_checks : tuple[pyam.IamDataFrame, pandas.DataFrame]
        A tuple of the processed `IamDataFrame` (either the complete dataframe
        with added "Other" variables, or just the added "Other" variables) and a
        `pandas.DataFrame` with the items that failed the checks.
        `failed_checks` has the following three columns:
        - "aggregate": The value of the aggregated variable
        - "components": The sum of the components
        - "component_vars": A list of the component variables that were included
            in the sum
        The index is equal to the index for each datapoint of the aggregated
        variable that failed the check.
    """

    
