"""Script to generate an HTML (pandas) table of variable names and attributes.

This script is a cell script. Use Visual Studio Code to run it interactively,
or modify the output filename to your liking and run it as a script.
"""

# %% [markdown]
# Imports

# %%
import datetime
from pathlib import Path

from nomenclature import DataStructureDefinition

from iamcompact_nomenclature.dsd_utils.codelist_formatter \
    import PandasHTMLFormatter
from iamcompact_nomenclature.default_definitions import get_dsd

# %% [markdown]
# Define the output filename

# %%
output_filenames: dict[str, Path] = {
    _dim: Path(__file__).parent.parent / 'docs' / f'{_dim}_codelist.html'
    for _dim in ('variable', 'model', 'scenario')
}
attrs_dict: dict[str, tuple[str, ...]] = {
    'variable': ('unit', 'description'),
    'model': ('description',),
    'scenario': ('description',),
}

# %% [markdown]
# Load the default `iamcompact-nomenclature` definitions

# %%
dsd: DataStructureDefinition = get_dsd()

# %% [markdown]
# Generate the HTML table for the variable CodeList (`dsd.variable`)

# %%
html_files: dict[str, str] = {
    _dim: PandasHTMLFormatter().format(
        codelist=getattr(dsd, _dim),
        attrs=attrs_dict[_dim],
    header_title=f'IAM COMPACT {_dim}s (generated on {datetime.date.today().isoformat()})',
        intro_text=f'<!-- Generated using `generate_varlist_html_table.py` on ' \
            f'{datetime.datetime.now().isoformat(timespec="seconds")} -->',
    ) for _dim in attrs_dict
}

# %% [markdown]
# Write the HTML table to the output file

# %%
for _dim, _filename in output_filenames.items():
    with open(_filename, 'w', encoding='utf-8') as f:
        f.write(html_files[_dim])
