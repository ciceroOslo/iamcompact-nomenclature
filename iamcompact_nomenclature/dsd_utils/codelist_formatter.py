"""Classes and functions to format CodeList objects for printing.

Abstract base classes
---------------------
CodeLiistFormatter
    Base class for formatting a `nomenclature.CodeList` object. Subclasses must
    implement the `format` method, which should use a consistent subclass of
    `CodeFormatter` to format the individual codes.
CodeFormatter
    Base class for formatting a single `nomenclature.code.Code` object.
    Subclasses must implement the `format` method, which should return a string
    representation of the code.

Classes
-------
VariableCodeListMarkdownFormatter
    Formats a `nomenclature.codelist.VariableCodeList` as a Markdown document,
    with optionally expandable items (using HTML details/summary elements) for
    each code.
VariableCodeMarkdownFormatter
    Formats a `nomenclature.code.VariableCode` as an optionally expandable
    Markdown list item, with the code's name and description show, and each of
    its attributes in the details element.
"""
import abc
from collections.abc import Mapping
from typing import Optional

import nomenclature
from nomenclature.codelist import CodeList, VariableCodeList
from nomenclature.code import Code, VariableCode



class CodeFormatter(abc.ABC):
    """Base class for formatting a single `nomenclature.code.Code` object.

    Subclasses must implement the `format` method, which should return a string
    representation of the code.
    """
    @abc.abstractmethod
    def format(self, code: Code) -> str:
        """Return a string representation of the code."""
        pass
    ###END def CodeFormatter.format

###END class CodeFormatter


class CodeListFormatter(abc.ABC):
    """Base class for formatting a `nomenclature.CodeList` object.

    Subclasses must implement the `format` method, which should use a consistent
    subclass of `CodeFormatter` to format the individual codes.
    """
    @abc.abstractmethod
    def format(self, codelist: CodeList) -> str:
        """Return a string representation of the code list."""
        pass
    ###END def CodeListFormatter.format

###END class CodeListFormatter


class VariableCodeMarkdownFormatter(CodeFormatter):
    """Formats a `nomenclature.code.VariableCode` as an optionally expandable
    Markdown list item, with the code's name and description show, and each of
    its attributes in the details element.
    """

    id_attrname: str = 'name'
    """The name of the attribute that gives the variable name, and should be
    be displayed in the non-collapsed part of the output string."""

    def get_attributes(self, code: VariableCode, include_none: bool = False) \
            -> Mapping[str, str|None]:
        """Return a dict with the code's attributes, optionally including None"""
        attrs: dict[str, str|None] = {
            _attrname: _attrval for _attrname, _attrval in code
        }
        if not include_none:
            attrs_nonone: dict[str, str] = {
                _attrname: _attrval for _attrname, _attrval in attrs.items()
                if _attrval is not None
            }
            return attrs_nonone
        return attrs
    ###END def VariableCodeMarkdownFormatter.get_attributes

    def format(self, code: VariableCode) -> str:
        """Return a Markdown list item for the code.

        Uses the `id_attrname` attribute as the name of the attribute that
        should be displayed in the non-collapsed part of the output string, and
        `self.get_attributes` to get the attributes to display in the details.
        """
        attrs: Mapping[str, str] = self.get_attributes(code)
        # Print a collapsable list item, with the name as the summary part
        # and all other attributes returned by `self.get_attributes` in the
        # details part.
        list_top: str = f'<details><summary>{getattr(code, self.id_attrname)}</summary>\n'
        attrs_list: str = '\n'.join(
            f'    - **{attrname}**: {attrval}' for attrname, attrval in attrs.items()
            if attrname != self.id_attrname
        )
        list_bottom: str = '\n</details>\n'
        return list_top + attrs_list + list_bottom
    ###END def VariableCodeMarkdownFormatter.format


    #     """Return a Markdown list item for the code."""
    #     # Start with the name and description
    #     code_str: str = f'- **{code.name}**\n  {code.description}\n'
    #     # Add the attributes in a details element
    #     code_str += '<details>\n<summary>Attributes</summary>\n\n'
    #     for attr_name, attr_value in code.attributes.items():
    #         code_str += f'- **{attr_name}**: {attr_value}\n'
    #     code_str += '</details>\n'
    #     return code_str
    # ###END def VariableCodeMarkdownFormatter.format

###END class VariableCodeMarkdownFormatter


class VariableCodeListMarkdownFormatter(CodeListFormatter):
    """Formats a `nomenclature.codelist.VariableCodeList` as a Markdown document,
    with optionally expandable items (using HTML details/summary elements) for
    each code.
    """

    def __init__(self, code_formatter: Optional[VariableCodeMarkdownFormatter] = None):
        """Initialize the formatter with a `CodeFormatter` subclass."""
        if code_formatter is None:
            self.code_formatter = VariableCodeMarkdownFormatter()
        else:
            self.code_formatter: CodeFormatter = code_formatter
    ###END def VariableCodeListMarkdownFormatter.__init__

    def format(self, codelist: VariableCodeList, header_title: Optional[str] = None) -> str:
        """Return a Markdown document for the code list.

        Each code in the list is formatted using `self.code_formatter`, and the
        resulting strings are joined with newlines.
        """
        header: str = header_title + '\n' + '=' * len(header_title) + '\n\n' \
            if header_title is not None else ''
        body: str = '\n'.join(
            self.code_formatter.format(code) for code in codelist.values()
        )
        return header + body
    ###END def VariableCodeListMarkdownFormatter.format

###END class VariableCodeListMarkdownFormatter
