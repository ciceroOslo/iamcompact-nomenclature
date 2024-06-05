"""Script to make a countries.yaml file in nomenclature-compliant format.

Will countain all countries in `nomenclature.countries` as separate regions,
with the following mandatory attributes:
- `description`: Will be equal to the `name` attribute.
- `iso3_codes`: The ISO 3-letter country code. Will be equal to the `alpha_3`
    attribute.
- `alpha_3`: The ISO 3-letter country code. Taken directly from the
    `nomenclature.countries` item.
- `alpha_2`: The ISO 2-letter country code. Taken directly from the
    `nomenclature.countries` item.

Will also contain the following optional attributes, if the corresponding
attribute is present in the `nomenclature.countries` item:
- `official_name`: The official name of the country. Taken directly from the
    `nomenclature.countries` item.
- `note`: A note about the country. Taken directly from the
   `nomenclature.countries` item.
"""

# %%
# Imports
from pathlib import Path
import sys

import ruamel.yaml as yaml
from nomenclature import countries

# %%
# NB! THIS CELL WAS COPIED FROM THE `convert_common_definitions_region_file.py`
# SCRIPT. CHANGES HERE MUST BE COORDINATED WITH THAT SCRIPT. CONSIDER
# REFACTORING INTO A SEPARATE MODULE IF THESE SCRIPTS ARE REUSED.
#
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
# Create the basic yaml nested list/dict structure
country_list_yaml: list[dict[str, dict[str, str]]] = [
    {
        _country_item.name: {
            'description': _country_item.name,
            'iso3_codes': _country_item.alpha_3,
            'name': _country_item.name,
            'alpha_3': _country_item.alpha_3,
            'alpha_2': _country_item.alpha_2,
        } | {
            _key: _value for _key, _value in list(_country_item)
            if _key in ['official_name', 'note']
        }
    }
    for _country_item in countries
]

yaml_dictlist: list[dict[str, list[dict[str, dict[str, str]]]]] = [
    {
        'countries': country_list_yaml
    }
]


# %%
# Write the yaml file
output_dir: Path = Path(__file__).parent
output_name: str = 'countries.yaml'

yaml_obj = yaml.YAML(typ='rt')

yaml_obj.dump(yaml_dictlist, sys.stdout)
yaml_obj.dump(yaml_dictlist, output_dir / output_name)
