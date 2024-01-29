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
We are planning to add functions to this package that you can use to perform the validation required for IAM COMPACT and to get lists of invalid names, variable/unit combinations and non-matching aggregate sums, without having to navigate the API of the `nomenclature` package. Until then, see the [nomenclature package documentation](https://nomenclature-iamc.readthedocs.io/) for how to perform validation with the definitions and region mappings provided in this repository.
