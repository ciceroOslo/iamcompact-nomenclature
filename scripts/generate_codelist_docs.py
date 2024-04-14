"""Script to generate a Markdown file or HTML file with a codelist items.

The resulting HTML file will be rather large, so beware.
"""
from pathlib import Path
import argparse

import nomenclature
from nomenclature.code import VariableCode
from nomenclature.codelist import VariableCodeList

import iamcompact_nomenclature as icnom   
from iamcompact_nomenclature.dsd_utils.codelist_formatter \
    import VariableCodeListMarkdownFormatter


def main():
    """Run the script.
    
    The script accepts the following command line arguments:
    - `--dsdpath` (Optional): The path to the DSD directory to use. Uses iamcompact_nomenclature DSD by default.
    - `--codelist`: The name of the codelist attribute of the DSD to format.
    - `--output`: The path and name of output file to write.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dsdpath', type=Path, default=None,
                        help='The path to the directory containing the ' \
                            'datastructure definition.'
                        )
    parser.add_argument('--title', type=str, default=None,
                        help='Title to put at the top of the output file.'
                        )
    # parser.add_argument('dsdpath', type=Path,
    #                     help='The path to the directory containing the ' \
    #                         'datastructure definition.'
    #                     )
    parser.add_argument('--codelist', type=str,
                        help='The name of the codelist attribute of the DSD ' \
                            'to format.'
                        )
    parser.add_argument('--output', type=Path,
                        help='The path to the output file to write.')
    args = parser.parse_args()

    dsdpath: Path|None = args.dsdpath
    dsd: nomenclature.DataStructureDefinition
    if dsdpath is None:
        dsd = icnom.get_dsd()
    else:
        dsd = nomenclature.DataStructureDefinition(
            path=dsdpath,
            dimensions=[args.codelist]
        )

    codelist: VariableCodeList|None = getattr(dsd, args.codelist, None)
    if codelist is None:
        raise ValueError(f'No codelist named {args.codelist} found in DSD.')
    
    title: str|None = args.title

    formatter = VariableCodeListMarkdownFormatter()
    output: str = formatter.format(codelist, header_title=title)

    if args.output.exists():
        print(f'File {args.output} exists. Overwrite?')
        if input('y/n: ').lower() != 'y':
            print('Exiting without writing file.')
            return

    with open(args.output, 'w') as f:
        f.write(output)
###END def main

if __name__ == '__main__':
    main()
