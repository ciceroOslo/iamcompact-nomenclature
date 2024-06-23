"""Code to make common.yaml file in common-definitions nomenclature-compliant.

The `common.yaml` file with region definitions in the `common-definitions`
repository has a non-compliant format. It does not contain a list of ISO codes
in an `iso3_codes` attribute, and instead contains a `countries` attribute that
has country names separated by commas, but not surrounded by brackets, making it
a single string rather than a list.

This script reads the `common.yaml` file, reads in the region definitions, and
for each item it then converts the `countries` attribute from a string to a
list, and adds an `iso3_codes` attribute with the corresponding ISO 3-letter
country codes, obtained using `nomenclature.countries`. Finally, it writes the
resulting codelist out a a yaml file.
"""

# %%
# Imports
from pathlib import Path
from pprint import pprint
from collections.abc import Mapping, Sequence
import typing as tp
import sys
import copy

import ruamel.yaml as yaml
from nomenclature import countries
from nomenclature.codelist import RegionCodeList

import iamcompact_nomenclature as icnom

# %%
# Assign user-defined ISO3 code for Kosovo (which is not defined in the
# ISO 3166-1 alpha-3 standard; "XKX" is used by the European Union, and "XKK"
# is used in the Unicode standard; "XK" is commonly used as an ISO 3166-1
# alpha-2 code).
kosovo_item = countries.lookup('Kosovo')
kosovo_iso3: str = 'XKX'
kosovo_iso2: str = 'XK'
kosovo_item.note += \
    f'. User-defined ISO 3- and 2-letter codes: {kosovo_iso3}, {kosovo_iso2}.'
kosovo_item.alpha_3 = kosovo_iso3
kosovo_item.alpha_2 = kosovo_iso2

# %%
# Get the source file
data_dir: Path = Path(icnom.__file__).parent / 'data' / 'definitions' / 'region'
data_file: Path = data_dir / 'common.yaml'

# %%
# Read the data into a yaml object
rt_yaml = yaml.YAML(typ='rt')
regions_yaml: Sequence = rt_yaml.load(data_file)

# %%
# Go through each top-level hierarchy dict (which should have only one element
# each), then go through each region dict in each hierarchy dict, and for each
# of them convert the `countries` element from a string to a list, and add an
# `iso3_codes` element with the corresponding ISO 3-letter country codes.
# _region_dict: Mapping[str, Sequence[str|Mapping[str, tp.Any]]]
regions_yaml_new = copy.deepcopy(regions_yaml)
rt_yaml.default_flow_style = True
for _region_dict in regions_yaml_new:
    if len(_region_dict) != 1:
        raise ValueError('Each top-level hierarchy dict should have exactly one element')
    _region_key, region_list = list(_region_dict.items())[0]
    for _subregion in region_list:
        if not isinstance(_subregion, str):
            for _subregion_name, _subregion_dict in _subregion.items():
                if 'countries' in _subregion_dict:
                    # _subregion_dict.fa.set_flow_style()
                    _subregion_dict['countries'] = _subregion_dict['countries'].split(', ')
                    _subregion_dict['iso3_codes'] = [
                        getattr(countries.lookup(_country), 'alpha_3', f'YYYZZZ{_country}') for _country in _subregion_dict['countries']
                    ]

# %%
# Try to write to file
rt_yaml.dump(regions_yaml_new, sys.stdout)

output_dir: Path = Path(__file__).parent
output_file = output_dir / 'common_tempcopy.yaml'

rt_yaml.dump(regions_yaml_new, output_file)
