# iamcompact-nomenclature
Data structure definition for validation of model outputs in the HORIZON EUROPE
project IAM COMPACT, using nomenclature-iamc

## Installation
This package can either be installed as a Python package, or the
`/iamcompact-nomenclature/data/definitions` folder can be downloaded and used
directly with the `nomenclature-iamc` package.

To install as a Python package using `pip`:
```
pip install git+https://github.com/ciceroOslo/iamcompact-nomenclature.git
```
Or to install a specific branch or version (`branchname` in the command below):
```
pip install git+https://github.com/ciceroOslo/iamcompact-nomenclature.git@branchname
```

If you use [poetry](https://python-poetry.org/docs/), you can use the following
commands (when in your project directory):
```
poetry add git+https://github.com/ciceroOslo/iamcompact-nomenclature.git
```
or
```
poetry add git+https://github.com/ciceroOslo/iamcompact-nomenclature.git#branchname
```

Eventually, the package will probably be published on [PyPi](https://pypi.org/)
so that you can install it directly with a command like `pip install
iamcompact-nomenclature`. At the moment, this has not been done, hence the need
for using the more complex commands above to install from the repository.

At the moment, there are no plans to create a
[conda](https://docs.conda.io/en/latest/) package. If you have a pressing need
for that, please [create an
issue](https://github.com/ciceroOslo/iamcompact-nomenclature/issues).


## Usage
You can either
1. use the files in this repository directly with the `nomenclature` package to
   validate model outputs, or
2. use the API in the Python package defined by this repository to obtain a
   nomenclature `DataStructureDefinition` object and a `RegionProcessor` object,
   which can then be used with the nomenclature API to perform validation and
   aggregation checking.

### 1. Use files directly

To use the files directly, download or clone the repository to a folder on your
computer.

The data definitions and region mappings are then found in the directories
`<repo_path>/iamcompact_nomenclature/data/definitions/` and
`<repo_path>/iamcompact_nomenclature/data/mappings/`, respectively, where
`<repo_path>` is the path to the root folder of the downloaded/cloned
repository. Pass these paths to `nomenclature.DataSrructureDefinition()` and
`nomenclature.RegionProcessor.from_directory()`, respectively, to get
`DataStructureDefinition` and `RegionProcessor` objects that you can use for
validation.

### 2. Get `DataStructureDefinition` and `RegionProcessor` objects from code in this package

To get a `nomenclature.DataSrructureDefinition` and
`nomenclature.RegionProcessor` object directly from the code in this repository,
use the following code (assumes you have installed the package as in
"Installation" above):

```
import iamcompact_nomenclature as icnom

dsd = icnom.get_dsd()
processor = icnom.get_region_processor()
```

These objects can then be passed to `nomenclature.process()`, or you can call
`dsd.validate()` or `processor.check_region_aggregation()` to perform
validations and region aggregation checks.

Note that definitions and region mappings are read from disk only at the first
call to `get_dsd()` and `get_region_processor()`. The resulting objects are
cached, and subsequent calls just return the same objects. If you need the
functions to read from disk again, you can pass the keyword argument
`force_reload=True` to both functions. Note that if the data structure
definition has changed and you reload it with `get_dsd(force_reload=True)`, you
should also reload the region processor through
`get_region_mapping(force_reload=True)`, since the region mapping ususally
depends on the data structure definition.

## Perform validation
You can validate names (models, scenarios, variables, regions, ...) and
variable/unit combinations using the functions `get_invalid_items()` and
`get_invalid_variable_units()` in the `iamcompact_nomenclature.validation`
module. Both take a `pyam.IamDataFrame` with your model results as input, and
return a dictionary of invalid names for each dimension, or DataFrame of invalid
units, respectively (see details below).

To use them with the names and variable/unit combos defined in the included
datastructure definition, use the following (where `data_path` is the path and
filename of your IAMC-formatted CSV or Excel file with model output):

```
import pyam
import iamcompact_nomenclature as icnom

iamdf = pyam.IamDataFrame(data_path)

invalid_names = icnom.validation.get_invalid_items(iamdf)

invalid_units = icnom.validation.get_invalid_variable_units(iamdf)
```

Here, `invalid_names` will be a dictionary with dimension names as keys, and a
list of invalid variable names for each dimension as the corresponding value.

`invalid_units` will be `None` if no invalid units are found, and otherwise a
DataFrame with one row for each variable for which any invalid units were found.
The DataFrame has the variable names in the index, and two columns:
  1. `invalid`: The invalid unit name(s), as a string if `iamdf` contains just
      one unit for the given variable, or a list of strings if there are
      several different units for the same variable in `iamdf`.
   2. `expected`: The correct unit name(s) for the given variable, as a string
      or list of strings.

Both functions accept an optional keyword argument `dsd`, which lets you use the
function with an alternative DataStructureDefinition instance (the default is
the built-in one, as returned by `iamcompact_nomenclature.get_dsd()`).

`get_invalid_items()` additionally accepts a keyword argument `dimensions`, that
lets you specify which dimensions to check names for as a list of strings (must
match exactly the dimension names used in `iamdf`, including case). By default,
it uses all dimensions that are present in both `iamdf` and in `dsd` (and
silently ignores any dimensions that are present in `iamdf` but not in `dsd`).


## Check aggregations

The package can be used to check whether the values of aggregate variables are
equal to the sum of their component variables, and whether the values of
extensive variables for aggregate regions are equal to the sum of the values for
each constituent country or subregion.

Both require the data structure
definition used (stored in `iamcompact_nomenclature/data/definitions` or
supplied as an external `nomenclature.DataStructureDefinition` object) to
contain tags that specify which variables are aggregate variables that should
be checked and/or extensive variables that can be summed across regions.
Checking regional aggregations also require a `nomenclature.RegionProcessor`
instance that contains the region mappings, either obtained from
`iamcompact_nomenclature/data/mappings` through the `get_region_processor()`
function or by supplying an externally constructed instance.

### Aggregate variables check

To check all aggregate variables in an `IamDataFrame` named `iamdf`, use the
following call:

```
import iamcompact_nomenclature as icnom

results = icnom.check_var_aggregates(iamdf)
```

This call will by default use the data structure definition supplied by
`icnom.get_dsd()`. You can override this by passing a custom
`nomenclature.DataStructureDefinition` object to `check_var_aggregates` through
the `dsd` keyword argument. See the function docstring for more details about
other optional arguments, which let you specify tolerance margins.

`results` is returned as a `VarAggregationCheckResults` object with the following
attributes:
* `failed_checks` (`pandas.DataFrame` or `None`): A DataFrame with the checks that did
  not pass. The value of the aggregate variable is in the column `variable`, the
  sum of the components in `components`. Will be `None` if all checks passed.
* `aggregation_map` (`dict`): A dictionary with the aggregated variables that
  were checked as keys, and the corresponding components used in the sum as
  values. The latter will either be a list of component variable names in the
  case of an aggregate with a single set of components, or a list of dicts if
  the aggregate variables has multiple component hierarchies (such as final
  energy being disaggregated both by energy type and by sector). In the latter
  case, the key of each dict will be the name assigned to that hierarchy in the
  definition of the aggregate variable in the datastructure definition, and the
  value will be a list of component variable names for that hierarchy. See the
  [section on variable
  codelists](https://nomenclature-iamc.readthedocs.io/en/stable/user_guide/variable.html#consistency-across-the-variable-hierarchy)
  in the nomenclature-iamc documentation for more details about how variable
  aggregations are specified in nomenclature.
* `not_checked` (`list` of `str`): A list of variable names that were not
  checked as aggregate variables. This list will include component variables
  that were considered only components and not checked as aggregate variables
  with their own subcomponents.
* `unknown` (`list` of `str`): List of variables in the checked `IamDataFrame`
  that were not found in the datastructure definition. This list *should* be
  empty if the variable names have been validated.
* `rtol`, `atol` (`float` or `None`): Relative and absolute tolerances used in
  the check. They will be `None` if they weren't explicitly specified, in which
  case the defaults values in `numpy.isclose` will have been used.

Even if `.errors` is None, you should check through `.not_checked` to make
sure that it does not include any variables that should have been checked, and
also that `.unknown` is empty.

**NB!** `check_var_aggregates` will **only** check variables for which the
`check-aggregate` attribute in the datastructure definition has been specified.
See the [section on variable
codelists](https://nomenclature-iamc.readthedocs.io/en/stable/user_guide/variable.html#consistency-across-the-variable-hierarchy)
in the nomenclature-iamc documentation for more details. If you don't supply
your own `dsd`, `check-aggregate` and `components` should usually have been set
for the appropriate variables, but still check `results.not_checked` and
`results.aggregation_map` to make sure that the function used the aggregates
that you expected and didn't leave out anything that should have been included.

### Region aggregation check

To check that variables set for aggregate regions match the sum of the same
variable in constituent regions and countries, use the following call:

```
import iamcompact_nomenclature as icnom

results = icnom.check_region_aggregates(iamdf)
```

By default this will use the datastructure definition fom `icnom.get_dsd()` and
the `RegionProcessor` object returned by `icnom.get_region_processor()`. To
override, use the `dsd` or `processor` keyword arguments to
`check_region_aggregates`.

Results are returned as a `RegionAggregationCheckResults` object with the
following attributes (see also the docstring of
`iamcompact_nomenclature.aggregation.RegionAggregationCheckResults`):
  * `failed_checks` (`pandas.DataFrame` or `None`): A dataframe with the items
    that failed the checks. It contains three columns:
    * `original`: The value of the variable for the aggregate, model-native
      region.
    * `agregated`: The aggregate of the values for the variable in the
      constituent regions or countries.
    * `difference (%)`: The difference between the two values, in percent
      relative to `original`.
  * `aggregation_map` (`dict`): A dictionary of dictionaries of the aggregated
    regions (keys of the inner dict) and constituent regions (values of the
    inner dict) that were used in the checks for each model. The keys of the
    outer dict are the model names, which will be just one if you are only
    checking output from a single model.
  * `regions_not_checked` (`dict`): A dictionary of lists of regions that were
    not checked for each model. The keys are the model names, and the values are
    lists of region names.
  * `vars_not_checked` (`list`): A list of variable names that were not checked
    for any model.
  * `unknown_regions` (`dict`): A dictionary of lists of regions that were not
    found in the region mappings. The keys are the model names, and the values
    are lists of region names. Should be empty if the region names in `iamdf`
    have been properly validated.
  * `unknown_vars` (`list`): A list of variable names that were not found in the
    datastructure definition. Should be empty if the variable names in `iamdf`
    have been properly validated.
  * `dsd` (`nomenclature.DataStructureDefinition`): The data structure
    definition used in the checks.
  * `processor` (`nomenclature.RegionProcessor`): The region processor used in
    the checks.
  * `rtol` (`float`): The relative tolerance used in the checks.
