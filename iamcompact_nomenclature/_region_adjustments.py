"""Private module for adjusting region definitions.

The current version just modifies the entry for Kosovo in
`nomenclature.countries`, to ensure that the user-defined 3- and 2-letter codes
are recognized. Especially the 3-letter code is important, since the
`nomenclature` package will verify that the `iso3_codes` entries in the region
codelist are found in the `nomenclature.countries` list.
"""

from nomenclature import countries


# Assign user-defined ISO3 code for Kosovo (which is not defined in the
# ISO 3166-1 alpha-3 standard; "XKX" is used by the European Union, and "XKK"
# is used in the Unicode standard; "XK" is commonly used as an ISO 3166-1
# alpha-2 code).
kosovo_item = countries.lookup('Kosovo')
if not hasattr(kosovo_item, 'alpha_3'):
    kosovo_iso3: str = 'XKX'
    kosovo_iso2: str = 'XK'
    kosovo_item.note += \
        f'. User-defined ISO 3- and 2-letter codes: {kosovo_iso3}, {kosovo_iso2}.'
    kosovo_item.alpha_3 = kosovo_iso3
    kosovo_item.alpha_2 = kosovo_iso2
