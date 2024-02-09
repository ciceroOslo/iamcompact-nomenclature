"""Package to read and use definitions and mappings for IAM COMPACT."""
from pathlib import Path
from collections.abc import Sequence
from typing import Final, Optional

import nomenclature

from . import validation


_data_root: Path = Path(__file__).parent / 'data'

defintions_path: Path = _data_root / 'definitions'
mappings_path: Path = _data_root / 'mappings'
dimensions: Final[tuple[str, ...]] = (
    # Drop model dimension for now, is empty in the starting point from openENTRANCE
    # 'model',
    'scenario',
    'region',
    'variable',
)


def _load_definitions(
        dimensions: Sequence[str] = dimensions
) -> nomenclature.DataStructureDefinition:
    """Load and return DataStructureDefinition from definitions_path."""
    return nomenclature.DataStructureDefinition(
        defintions_path,
        dimensions=dimensions
    )
###END def _load_definitions

def _load_region_processor() -> nomenclature.RegionProcessor:
    """Load and return RegionProcessor from mappings_path."""
    return nomenclature.RegionProcessor.from_directory(
        path=mappings_path,
        dsd=get_dsd()
    )


_dsd: nomenclature.DataStructureDefinition | None = None
_region_processor: nomenclature.RegionProcessor | None = None


def get_dsd(
        force_reload: bool = False,
        dimensions: Optional[Sequence[str]] = None
) -> nomenclature.DataStructureDefinition:
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
    if _dsd is None or force_reload:
        if dimensions is None:
            _dsd = _load_definitions()
        else:
            _dsd = _load_definitions(dimensions=dimensions)
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
