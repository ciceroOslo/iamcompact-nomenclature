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

### Perform validation
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

A function to check variable and region aggregation sums is in the works, but
not yet complete.
