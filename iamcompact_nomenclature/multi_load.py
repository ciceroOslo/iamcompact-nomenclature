"""Module for loading and merging multiple DataStructureDefinitions.

Functions
---------
read_multi_definitions(
        paths: Sequence[Path],
        dimensions: Sequence[str] | Sequence[Sequence[str]],
) -> DataStructureDefinition
    Read datstructure definitions from multiple directories, and merge them in
    prioritized order
read_multi_region_processors(
        paths: Sequence[Path],
        dsds: DataStructureDefinition | Sequence[DataStructureDefinition],
) -> RegionProcessor
    Read region mappings from multiple directories, and merge them in
    prioritized order into a joint RegionProcessor
merge_dsds(dsds: Sequence[DataStructureDefinition]) \
        -> MergedDataStructureDefinition
    Merge multiple DataStructureDefinitions, in prioritized order
merge_region_processors(regionmaps: Sequence[RegionProcessor]) \
        -> RegionProcessor
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
    RegionAggregationMapping,
)
from nomenclature.code import Code
from nomenclature.codelist import (
    RegionCodeList,
    VariableCodeList,
)
from nomenclature.config import NomenclatureConfig



CodeListTypeVar = tp.TypeVar('CodeListTypeVar', bound=CodeList)

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
    """

    region: RegionCodeList
    variable: VariableCodeList

    def __init__(
            self,
            definitions: Sequence[DataStructureDefinition],
            dimensions: tp.Optional[Sequence[Sequence[str]]] = None,
    ) -> None:
        """
        Parameters
        ----------
        definitions : sequence of DataStructureDefinition
            The definitions to merge, in order of priority.
        dimensions : sequence of sequence of str, optional
            The dimensions that should be loaded for each
            `DataStructureDefinition`. If not provided, all dimensions for each
            definition are loaded.
        """
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
        self.config = self.merge_configs([_dsd.config for _dsd in definitions])
    ###END def MergedDataStructureDefinition.__init__

    def to_excel(self, *args, **kwargs):
        raise NotImplementedError(
            'MergedDataStructureDefinition has not added support for '
             '`to_excel` yet.'
        )
    ###END def MergedDataStructureDefinition.to_excel


    @staticmethod
    def merge_codelists(
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
        merged_codelist: CodeListTypeVar = codelist_class(
            name=name,
            mapping={},
        )  # We need to create an empty CodeList first, since the validation
           # when creating using the constructor will fail (it expects a dict
           # coming from a yaml file, not directly from an already initialized
           # CodeList).
        merged_codelist.mapping = mapping
        return merged_codelist
    ###END def MergedDataStructureDefinition.merge_codelists

    @classmethod
    def merge_configs(
            cls,
            configs: Sequence[NomenclatureConfig],
    ) -> NomenclatureConfig:
        """Merge a config objects for multiple DataStructureDefinitions

        Parameters
        ----------
        configs : sequence of nomenclature.NomenclatureConfig
            The configs to merge, in the same order that the corresponding
            `DataStructureDefinitions` objects were merged.

        Returns
        -------
        nomenclature.NomenclatureConfig
            The merged config.
        """
        new_conf: NomenclatureConfig = configs[0].model_copy(deep=True)
        new_conf.dimensions = list(set.union(*[set(_c.dimensions or list())
                                               for _c in configs]))
        new_conf.repositories = {}
        for _c in configs[-1::-1]:
            new_conf.repositories.update(_c.repositories)
        ### TODO: Still need to merge `definitions` and `mappings` attributes
        # new_conf.definitions = cls.merge_data_structure_configs(
        #     [_c.definitions for _c in configs]
        # )
        return new_conf
    ###END def MergedDataStructureDefinition.merge_configs

###END class MergedDataStructureDefinition


@tp.overload
def read_multi_definitions(
        paths: Sequence[Path],
        dimensions: tp.Optional[Sequence[str] | Sequence[Sequence[str]]] = None,
        *,
        return_individual_dsds: tp.Literal[True],
) -> tuple[MergedDataStructureDefinition, list[DataStructureDefinition]]:
    ...
@tp.overload
def read_multi_definitions(
        paths: Sequence[Path],
        dimensions: tp.Optional[Sequence[str] | Sequence[Sequence[str]]] = None,
        *,
        return_individual_dsds: bool = False,
) -> MergedDataStructureDefinition:
    ...
def read_multi_definitions(
        paths: Sequence[Path],
        dimensions: tp.Optional[Sequence[str] | Sequence[Sequence[str]]] = None,
        *,
        return_individual_dsds: bool = False,
) -> MergedDataStructureDefinition \
        | tuple[MergedDataStructureDefinition, list[DataStructureDefinition]]:
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
    return_individual_dsds : bool, optional
        Whether to return the individual definitions as well as the merged
        definition. Defaults to `False`.

    Returns
    -------
    MergedDataStructureDefinition or tuple of MergedDataStructureDefinition and
    list of DataStructureDefinition
        The merged definitions. The return value is a
        `MergedDataStructureDefinition`, which is a subclass of
        `DataStructureDefinition`, but with some changes to its attributes that
        are necessary given that it does not have a single config file or come
        from a single project directory.
        If `return_individual_dsds` is `True`, the return value is a tuple
        where the first element is the merged definition and the second
        element is a list of the individual definitions, in the same order as
        `paths`.
    """
    # Turn `dimensions`` into a list of lists, with the same length as paths for
    # the outer list.
    use_dimensions: list[list[str]] | list[None]
    if dimensions is None:
        use_dimensions = [None] * len(paths)
    elif not isinstance(dimensions, Sequence):
        raise TypeError(
            f'`dimensions` must be None or a sequence, not {type(dimensions)}'
        )
    elif isinstance(dimensions[0], str):
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
    if return_individual_dsds:
        return dsd, definitions
    return dsd
###END def read_multi_definitions


def read_multi_region_processors(
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
        The joint RegionProcessor from the merged region maps.
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
    region_processors: list[RegionProcessor] = [
        _load_single_path_regionmaps(path=_path, dsd=_dsd)
        for _path, _dsd in zip(paths, dsds)
    ]
    # Merge the region maps
    joined_region_processor: RegionProcessor
    if merged_dsd is not None:
        joined_region_processor = merge_region_processors(
            region_processors=region_processors,
            merged_dsd=merged_dsd
        )
    else:
        joined_region_processor = merge_region_processors(
            region_processors=region_processors,
            dsds=dsds
        )
    # Return the merged region map
    merge_region_processors(region_processors, dsds=dsds)
    return joined_region_processor
###END def read_multi_regionmaps


def _load_single_path_definitions(
        path: Path,
        dimensions: Sequence[str]|None,
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


def merge_region_processors(
        region_processors: Sequence[RegionProcessor],
        *,
        dsds: tp.Optional[Sequence[DataStructureDefinition]] = None,
        merged_dsd: tp.Optional[MergedDataStructureDefinition] = None,
) -> RegionProcessor:
    """Merge a sequence of `RegionProcessor` objects.

    Parameters
    ----------
    region_processors : Sequence[RegionProcessor]
        The region processors to merge.
    dsds : Sequence[DataStructureDefinition], optional
        The data structure definitions used to define each of the region
        processors. If provided, the definitions will be merged into a single
        `MergedDataStructureDefinition` object. If not provided, the
        `merged_dsd` parameter must be provided. `dsds` is ignored if
        `merged_dsd` is provided.
    merged_dsd : MergedDataStructureDefinition, optional
        The merged data structure definitions to use for the merged region
        processor. This must be equal to the result of merging the
        `DataStructureDefinition` objects used to define the RegionProcessors in
        `region_processors`, but can be limited to the `region` and `variable`
        dimensions, since only those are used. Optional. If not provided, the
        `dsds` parameter must be provided. If provided, `dsds` will be ignored.
    """
    if merged_dsd is None:
        if dsds is None:
            raise ValueError(
                'If `merged_dsd` is not provided, `dsds` must be provided'
            )
        merged_dsd = MergedDataStructureDefinition(
            definitions=dsds,
            dimensions=[['region', 'variable']]*len(dsds)
        )
    mappings: dict[str, RegionAggregationMapping] = {}
    for _region_processor in region_processors:
        mappings.update(_region_processor.mappings)
    return RegionProcessor(
        mappings=mappings,
        region_codelist=merged_dsd.region,
        variable_codelist=merged_dsd.variable,
    )
