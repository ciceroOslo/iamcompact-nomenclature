"""Package to read and use definitions and mappings for IAM COMPACT."""
import functools

from .default_definitions import (
    definitions_path,
    mappings_path,
    dimensions,
    get_dsd,
    get_region_processor,
)

from . import validation
from . import aggregation

check_var_aggregates = functools.wraps(aggregation.check_var_aggregates)(
    functools.partial(aggregation.check_var_aggregates, dsd=get_dsd())
)
    