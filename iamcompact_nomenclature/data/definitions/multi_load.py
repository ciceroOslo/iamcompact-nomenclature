"""Module for loading and merging multiple DataStructureDefinitions.

Functions
---------
read_multi_definitions(
        paths: Sequence[Path],
        dimensions: Sequence[str] | Sequence[Sequence[str]],
) -> DataStructureDefinition
    Read datstructure definitions from multiple directories, and merge them in
    prioritized order
read_multi_regionmaps(
        paths: Sequence[Path],
        dsds: DataStructureDefinition | Sequence[DataStructureDefinition],
) -> RegionProcessor
    Read region maps from multiple directories, and merge them in prioritized
    order
merge_dsds(dsds: Sequence[DataStructureDefinition]) -> DataStructureDefinition
    Merge multiple DataStructureDefinitions, in prioritized order
merge_regionmaps(regionmaps: Sequence[RegionProcessor]) -> RegionProcessor
    Merge multiple RegionProcessors, in prioritized order
"""
from collections.abc import Sequence
from pathlib import Path
import typing as tp

import nomenclature
from nomenclature import DataStructureDefinition, RegionProcessor



def read_multi_definitions(
        paths: Sequence[Path],
        dimensions: tp.Optional[Sequence[str] | Sequence[Sequence[str]]] = None,
) -> DataStructureDefinition:
    """Read and merge DataStructureDefinitions from multiple directories.

    The function loads `nomenclature.DataStructureDefinition` objects from a
    sequence of directories in order (given by the `paths` parameter). Each
    element of `paths` should follow the same conventions as for 
    `nomenclature.DataStructureDefinition`.

    After loading, the `DataStructureDefinition` objects are merged by taking
    the codes from each codelist in each object and producing new codelists that
    contain the codes from all of them. Where codelists overlap (i.e., if two
    codelists for the same dimension have codes with the same name), the first
    codelist in `paths` where the codee appears is used.

    Parameters
    ----------
    paths : sequence of pathlib.Path
        The paths to the directories containing the definitions. Like the paths
        passed to `nomenclature.DataStructureDefinition`, each path object
        should point to the directory that contains definitions (usually named
        `"definitions"`), not the parent directory that usually contains both
        the `definitions` and the `mappings` subdirectories. Also like for
        `nomenclature.DataStructureDefinition`, config yaml files must be named
        `nomenclature.yaml` and be located in the *parent* directory of the
        definitions subdirectory.
    dimensions : sequence of str or sequence of sequence of str, optional
        The dimensions that should be loaded for each `DataStructureDefinition`.
        Can be given either as a single list of dimensions to be used for each
        `DataStructureDefinition`, or as a list of lists, where the outer list
        must have the same length and ordering as `paths`. Optional. If not
        specified, the same defaults as in `nomenclature` are used (at the
        time of writing, this means reading definitions from `nomenclature.yaml`
        in each directory if present, or using `["variable", "region"]`). Note
        that an error will be raised if any of the specified dimensions is not
        present for the corresponding path.

    Returns
    -------
    DataStructureDefinition
        The merged definitions.
    """
    # Turn `dimensions`` into a list of lists, with the same length as paths for
    # the outer list.
    use_dimensions: list[list[str]] | list[None]
    if dimensions is None:
        use_dimensions = [None] * len(paths)
    if not isinstance(dimensions, Sequence):
        raise TypeError(
            f'`dimensions` must be None or a sequence, not {type(dimensions)}'
        )
    if isinstance(dimensions[0], str):
        dimensions = tp.cast(Sequence[str], dimensions)
        use_dimensions = [list(dimensions)] * len(paths)
    else:
        use_dimensions = [list(_dims) for _dims in dimensions]
    if len(use_dimensions) != len(paths):
        raise ValueError(
            '`dimensions` must have the same length as `paths` '
            f'({len(paths)}), not {len(use_dimensions)}.'
        )
    # Traverse the paths and load each `DataStructureDefinition`.
    definitions: list[DataStructureDefinition] = [
        _load_single_path_definitions(path=_path, dimensions=_dims)
        for _path, _dims in zip(paths, use_dimensions)
    ]
    # Merge the definitions
    dsd: DataStructureDefinition = merge_dsds(definitions)
    return dsd
###END def read_multi_definitions


def read_multi_regionmaps(
        paths: Sequence[Path],
        dsds: DataStructureDefinition | Sequence[DataStructureDefinition],
) -> RegionProcessor:
    """Read and merge RegionProcessors from multiple directories.

    The function loads `nomenclature.RegionProcessor` objects from a sequence
    of directories in order (given by the `paths` parameter). Each element of
    `paths` should follow the same conventions as for 
    `nomenclature.RegionProcessor`.

    After loading, the `RegionProcessor` objects are merged by taking the
    mappings from each region map in each object and producing new region maps
    that contain the mappings from all of them. Where region maps overlap, the
    first region map in `paths` where the mapping appears is used. "Overlap"
    here means that two region maps have mappings for the same model (where the
    model name including any version numbers must match exactly to be considered
    an overlap). The function does not support merging different region mappings
    for the same model (and it's not in general clear how such a merge would be
    done appropriately and robustly).

    Parameters
    ----------
    paths : sequence of pathlib.Path
        The paths to the directories containing the region maps. Like the paths
        passed to `nomenclature.RegionProcessor`, each path object should point
        to the directory that contains region maps (usually named
        `"mappings"`), not the parent directory that usually contains both
        the `definitions` and the `mappings` subdirectories. Also like for
        `nomenclature.RegionProcessor`, config yaml files must be named
        `nomenclature.yaml` and be located in the *parent* directory of the
        mappings subdirectory.
    dsds : DataStructureDefinition or Sequence[DataStructureDefinition]
        The data structure definitions to use in the region maps. Can either be
        a single `DataStructureDefinition` object to be used for all region
        maps, or a sequence of `DataStructureDefinition` objects with the same
        length and order as `paths`.

    Returns
    -------
    RegionProcessor
        The merged region maps.
    """
    # Convert `dsds` to a list if it's a single object
    if isinstance(dsds, DataStructureDefinition):
        dsds = [dsds] * len(paths)
    elif not isinstance(dsds, Sequence):
        raise TypeError(
            f'`dsds` must be a DataStructureDefinition or sequence, not '
            f'{type(dsds)}'
        )
    elif len(dsds) != len(paths):
        raise ValueError(
            f'`dsds` and `paths` must have the same length, not {len(dsds)} and '
            f'{len(paths)}'
        )
    # Load the region maps
    regionmaps: list[RegionProcessor] = [
        _load_single_path_regionmaps(path=_path, dsd=_dsd)
        for _path, _dsd in zip(paths, dsds)
    ]
    # Merge the region maps
    region_processor: RegionProcessor = merge_regionmaps(regionmaps)
    return region_processor
###END def read_multi_regionmaps
