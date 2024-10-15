"""Package to read and use definitions and mappings for IAM COMPACT."""
import functools

# Import _region_adjustments to make sure region attributes are adjusted as
# needed before the definitions are loaded.
# Change: Don't adjust for regions yet. Since the ISO3 code check in
# `nomenclature.RegionCode` happens directly against the ISO2 codes in
# `pycountry.countries`, making adjustments here won't be enough. Need to wait
# until the `nomenclature` code is changed, if ever.
# from . import _region_adjustments

from .default_definitions import (
    dimensions,
    get_dsd,
    get_region_processor,
)

from . import validation
from . import aggregation
from . import mapping

check_var_aggregates = functools.wraps(aggregation.check_var_aggregates)(
    functools.partial(aggregation.check_var_aggregates, dsd=get_dsd())
)

check_region_aggregates = functools.wraps(aggregation.check_region_aggregates)(
    functools.partial(
        aggregation.check_region_aggregates,
        dsd=get_dsd(),
        processor=get_region_processor(),
    )
)
    