"""Defaults for definitions to use."""
from collections.abc import Sequence
import logging
from pathlib import Path
from typing import Final, Optional

import git
import nomenclature

from .multi_load import (
    MergedDataStructureDefinition,
    read_multi_definitions,
    read_multi_region_processors,
)



logger: logging.Logger = logging.getLogger(__name__)

_data_root: Final[Path] = Path(__file__).parent / 'data'

definitions_paths: Final[list[Path]] = [
    _data_root / 'definition_repos' / 'definitions',
]
mappings_path: Path = \
    _data_root / 'definition_repos' / 'mappings'
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


_dsd: nomenclature.DataStructureDefinition | None = None
_individual_dsds: list[nomenclature.DataStructureDefinition] | None = None
_region_processor: nomenclature.RegionProcessor | None = None


def _load_definitions(
        dimensions: Optional[Sequence[str]] = None,
) -> tuple[nomenclature.DataStructureDefinition,
           list[nomenclature.DataStructureDefinition]]:
    """Load and return DataStructureDefinition from definitions_path.

    If the module attribute `definitions_paths` contains more than one element,
    they are each read as separate `DataStructureDefinition` instances and then
    merged into a single `MergedDataStructureDefinition` object, which is then
    returned in a tuple along with a list of each individual
    DataStructureDefinition. If `definitions_path` contains just a single
    element, that element is returned as a `DataStructureDefinitions` instance,
    in a tuple with a list that now just contains that same
    `DataStructureDefinition` instance.
    """
    # First check for repos and pull them, to make sure we get the latest
    # of any custom branches. This is necessary because nomenclature only does a
    # pull for repos where the `main` branch is specified as the release to use,
    # possibly under the assumption that a specific tag is being used otherwise,
    # and it will never change which commit it points to.
    for _parent in (_p.parent for _p in definitions_paths):
        if not _parent.is_dir():
            continue
        for _child in _parent.iterdir():
            if not _child.is_dir():
                continue
            if (_child / '.git').is_dir():
                _repo = git.Repo(_child)
                logging.log(
                    level=logging.DEBUG,
                    msg='Pulling updates (if any) for nomenclature repo in ' \
                        f'{_child}...'
                )
                _repo.remotes.origin.pull()
    if len(definitions_paths) > 1:
        logger.log(
            level=logging.INFO,
            msg='Loading and merging DataStructureDefinitions from the ' \
                f'following paths: {definitions_paths}...'
        )
        return read_multi_definitions(
            definitions_paths,
            dimensions=dimensions,
            return_individual_dsds=True,
        )
    else:
        logger.log(
            level=logging.INFO,
            msg='Loading DataStructureDefinitions from the following path: ' \
                f'{definitions_paths[0]}...'
        )
        dsd: nomenclature.DataStructureDefinition = \
            nomenclature.DataStructureDefinition(
                path=definitions_paths[0],
                dimensions=dimensions,
            )
        return dsd, [dsd]
###END def _load_definitions

def _load_region_processor() -> nomenclature.RegionProcessor:
    """Load and return RegionProcessor from mappings_path."""
    logger.log(
        level=logging.INFO,
        msg='Loading RegionProcessor from the following path: ' \
            f'{mappings_path}...'
    )
    return nomenclature.RegionProcessor.from_directory(
        path=mappings_path,
        dsd=get_dsd()
    )


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