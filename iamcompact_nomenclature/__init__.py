"""Package to read and use definitions and mappings for IAM COMPACT."""

from .default_definitions import (
    definitions_path,
    mappings_path,
    dimensions,
    get_dsd,
    get_region_processor,
)

from . import validation
