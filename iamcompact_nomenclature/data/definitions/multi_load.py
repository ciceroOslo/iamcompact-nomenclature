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
merge_dsds(dsds: Sequence[DataStructureDefinition]) \
        -> MergedDataStructureDefinition
    Merge multiple DataStructureDefinitions, in prioritized order
merge_regionmaps(regionmaps: Sequence[RegionProcessor]) -> RegionProcessor
    Merge multiple RegionProcessors, in prioritized order
"""
from collections.abc import Sequence
import git
import itertools
from pathlib import Path
import typing as tp

from nomenclature import (
    CodeList,
    DataStructureDefinition,
    RegionProcessor,
)
from nomenclature.code import Code
from nomenclature.config import NomenclatureConfig



class MergedDataStructureDefinition(DataStructureDefinition):
    """Merged data structure definition from multiple definitions.

    Since an instance of this class is a merger of multiple
    `DataStructureDefinition` objects, it does not have a single config file or
    project directory. It therefore does not define the `config`, `project`,
    `project_folder` or `repo` attributes of the parent class. These are
    instead replaced by plural versions, `configs`, `projects`,
    `project_folders` and `repos`, which are lists of the coresponding
    attributes from the source `DataStructureDefinition` objects, in the order
    of priority in which they were merged (i.e., earlier ones take precedence
    over definitions made in later ones).

    Init Parameters
    ---------------
    definitions : sequence of DataStructureDefinition
        The definitions to merge, in order of priority.
    dimensions : sequence of sequence of str, optional
        The dimensions that should be loaded for each `DataStructureDefinition`.
        If not provided, all dimensions for each definition are loaded.
    """

    def __init__(
            self,
            definitions: Sequence[DataStructureDefinition],
            dimensions: tp.Optional[Sequence[Sequence[str]]] = None,
    ) -> None:
        if dimensions is None:
            dimensions = [_dsd.dimensions for _dsd in definitions]
        all_dimensions: list[str] = \
            list(set(itertools.chain.from_iterable(dimensions)))
        self.dimensions: list[str] = all_dimensions
        dim_codelists_mapping: dict[str, list[CodeList]] = {
            _dim: [
                getattr(_dsd, _dim) for _dsd, _dsd_dims in zip(definitions, dimensions)
                if _dim in _dsd_dims
            ] for _dim in all_dimensions
        }
        codelists: dict[str, CodeList] = {
            _dim: self.merge_codelists(_codelists)
            for _dim, _codelists in dim_codelists_mapping.items()
        }
        for _dim, _codelist in codelists.items():
            setattr(self, _dim, _codelist)
        self.configs: list[NomenclatureConfig|None] \
            = [dsd.config for dsd in definitions]
        self.projects: list[str] = [dsd.project for dsd in definitions]
        self.project_folders: list[Path] \
            = [dsd.project_folder for dsd in definitions]
        self.repos: list[git.Repo|None] = [dsd.repo for dsd in definitions]
    ###END def MergedDataStructureDefinition.__init__

    def to_excel(self, *args, **kwargs):
        raise NotImplementedError(
            'MergedDataStructureDefinition has not added support for '
             '`to_excel` yet.'
        )
    ###END def MergedDataStructureDefinition.to_excel


    CodeListTypeVar = tp.TypeVar('CodeListTypeVar', bound=CodeList)

    @classmethod
    def merge_codelists(
            cls,
            codelists: Sequence[CodeListTypeVar],
            name: tp.Optional[str] = None,
    ) -> CodeListTypeVar:
        """Merge a sequence of codelists into a single codelist.

        The method will take codes from each codelist in the sequence and
        return a joint codelist that contains the codes from all of them.
        If codelists overlap, the codelist that comes earliest in the sequence
        takes precedence.

        Parameters
        ----------
        codelists : sequence of nomenclature.CodeList
            The codelists to merge, in order of priority.
        name : str, optional
            The name of the merged codelist. If not provided, the name of the
            first codelist is used.

        Returns
        -------
        nomenclature.CodeList or subclass
            The merged codelist. The type is the same as the type of the first
            codelist in the sequence (it is assumed and required that they are
            all of the same type).
        """
        if name is None:
            name = codelists[0].name
        codelist_class = type(codelists[0])
        mapping: dict[str, Code] = {}
        for _codelist in codelists[-1::-1]:
            mapping.update(_codelist.mapping)
        return codelist_class(name=name, mapping=mapping)
    ###END def MergedDataStructureDefinition.merge_codelists

###END class MergedDataStructureDefinition


def read_multi_definitions(
        paths: Sequence[Path],
        dimensions: tp.Optional[Sequence[str] | Sequence[Sequence[str]]] = None,
) -> MergedDataStructureDefinition:
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
    MergedDataStructureDefinition
        The merged definitions. The return value is a
        `MergedDataStructureDefinition`, which is a subclass of
        `DataStructureDefinition`, but with some changes to its attributes that
        are necessary given that it does not have a single config file or come
        from a single project directory.
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
    dsd: MergedDataStructureDefinition = MergedDataStructureDefinition(definitions)
    return dsd
###END def read_multi_definitions


def read_multi_regionmaps(
        paths: Sequence[Path],
        dsds: DataStructureDefinition | Sequence[DataStructureDefinition],
        merged_dsd: MergedDataStructureDefinition | None = None,
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
    merged_dsd : MergedDataStructureDefinition, optional
        The merged data structure definitions to use for the merged region map.
        This must be equal to the result of merging dsds. It is provided only
        for increaased performance. If not provided, dsds will be merged using
        the `MergedDataStructureDefinition` constructor, and the result is used.

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
    region_processor: RegionProcessor = merge_regionmaps(regionmaps, dsds=dsds)
    return region_processor
###END def read_multi_regionmaps


def _load_single_path_definitions(
        path: Path,
        dimensions: Sequence[str],
) -> DataStructureDefinition:
    """Load a single `DataStructureDefinition` from a single directory."""
    dsd = DataStructureDefinition(
        path=path,
        dimensions=dimensions
    )
    return dsd
###END def _load_single_path_definitions


def _load_single_path_regionmaps(
        path: Path,
        dsd: DataStructureDefinition,
) -> RegionProcessor:
    """Load a single `RegionProcessor` from a single directory."""
    region_processor = RegionProcessor.from_directory(
        path=path,
        dsd=dsd
    )
    return region_processor
###END def _load_single_path_regionmaps
