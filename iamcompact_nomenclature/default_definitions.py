"""Defaults for definitions to use."""
from collections.abc import Sequence
from pathlib import Path
from typing import Final, Optional

import nomenclature

from .multi_load import (
    MergedDataStructureDefinition,
    read_multi_definitions,
    read_multi_region_processors,
)


_data_root: Final[Path] = Path(__file__).parent / 'data'

definitions_paths: Final[list[Path]] = [
    _data_root / 'iamcompact-nomenclature-definitions' / 'definitions',
    _data_root / 'common-definitions-fork' / 'definitions',
]
mappings_path: Path = \
    _data_root / 'iamcompact-nomenclature-definitions' / 'mappings'
dimensions: Final[tuple[str, ...]] = (
    'model',
    'scenario',
    'region',
    'variable',
)
"""Defines which dimensions are provided by the data structure definition object
that is returned by `get_dsd`.

At the moment, this attribute is not used by the `iamcompact-nomenclature`
package itself (the dimensions are now specified in the nomenclature.yaml files
in the directories under `data`), but is kept since it may be used by external
code, and may be useful for internal use again in the future.
"""


_dsd: MergedDataStructureDefinition | None = None
_individual_dsds: list[nomenclature.DataStructureDefinition] | None = None
_region_processor: nomenclature.RegionProcessor | None = None


def _load_definitions(
        dimensions: Optional[Sequence[str]] = None,
) -> tuple[MergedDataStructureDefinition,
           list[nomenclature.DataStructureDefinition]]:
    """Load and return DataStructureDefinition from definitions_path."""
    return read_multi_definitions(
        definitions_paths,
        dimensions=dimensions,
        return_individual_dsds=True,
    )
###END def _load_definitions

def _load_region_processor() -> nomenclature.RegionProcessor:
    """Load and return RegionProcessor from mappings_path."""
    return nomenclature.RegionProcessor.from_directory(
        path=mappings_path,
        dsd=get_dsd()
    )


def get_dsd(
        force_reload: bool = False,
        dimensions: Optional[Sequence[str]] = None
) -> MergedDataStructureDefinition:
    """Return the definitions as a `nomenclature.DataStructureDefinition`.

    After the first call, the `DataStructureDefinition` object is cached and
    reused on subsequent calls unless `force_reload` is `True`. Note that this
    means that any changes made to the returned object will also affect future
    calls, until the next time the function is called with `force_reload=True`.
    
    Parameters
    ----------
    force_reload : bool, optional
        Whether to reload the definitions even if they have already been loaded
        before. Defaults to `False`.
    dimensions : sequence of str, optional
        The dimensions to be read. Defaults to `dimensions` from this module.
    """
    global _dsd
    global _individual_dsds
    global _region_processor
    if _dsd is None or force_reload:
        if dimensions is None:
            _dsd, _individual_dsds = _load_definitions()
        else:
            _dsd, _individual_dsds = _load_definitions(dimensions=dimensions)
    if force_reload:
        _region_processor = None
    return _dsd
###END def get_dsd


def get_region_processor(force_reload: bool = False) -> nomenclature.RegionProcessor:
    """Return the region processor.

    After the first call, the `RegionProcessor` object is cached and reused on
    subsequent calls unless `force_reload` is `True`. Note that this means that
    any changes made to the returned object will also affect future calls, until
    the next time the function is called with `force_reload=True`.
    
    Parameters
    ----------
    force_reload : bool, optional
        Whether to reload the region processor even if it has already been loaded
        before. Defaults to `False`. Note that since the region processor depends
        on the definitions, it will be reloaded if `force_reload` is `True` for
    """
    global _region_processor
    if _region_processor is None or force_reload:
        _region_processor = _load_region_processor()
    return _region_processor