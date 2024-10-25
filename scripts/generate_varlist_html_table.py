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
output_filename: Path = Path(__file__).parent / 'variable_codelist.html'

# %% [markdown]
# Load the default `iamcompact-nomenclature` definitions

# %%
dsd: DataStructureDefinition = get_dsd()

# %% [markdown]
# Generate the HTML table for the variable CodeList (`dsd.variable`)

# %%
html: str = PandasHTMLFormatter().format(
    codelist=dsd.variable,
    attrs=('unit', 'description'),
    header_title=f'IAM COMPACT variables (generated on {datetime.date.today().isoformat()})',
    intro_text=f'<!-- Generated using `generate_varlist_html_table.py` on ' \
        f'{datetime.datetime.now().isoformat(timespec="seconds")} -->',
)

# %% [markdown]
# Write the HTML table to the output file

# %%
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(html)
