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
VariableCodeListHTMLFormatter
    Formats a `nomenclature.codelist.VariableCodeList` as an HTML document,
    with optionally expandable items (using HTML details/summary elements) for
    each code.
VariableCodeHTMLFormatter
    Formats a `nomenclature.code.VariableCode` as an optionally expandable
    HTML list item, with the code's name and description show, and each of
    its attributes in the details element.
"""
import abc
from collections.abc import Mapping, Sequence
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


class VariableCodeHTMLFormatter(CodeFormatter):
    """Formats a `nomenclature.code.VariableCode` as an optionally expandable
    HTML <details> item, with the code's name and description show, and each of
    its attributes in the details element.
    """

    id_attrname: str = 'name'
    """The name of the attribute that gives the variable name, and should be
    be displayed in the non-collapsed part of the output string."""

    def get_attributes(
            self,
            code: VariableCode,
            attr_names: Optional[Sequence[str]] = None,
            include_none: bool = False
    ) -> Mapping[str, str|None]:
        """Return a dict with the code's attributes, optionally including None"""
        if attr_names is not None:
            attrs: dict[str, str|None] = {
                _attrname: getattr(code, _attrname) for _attrname in attr_names
            }
        else:
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
    ###END def VariableCodeHTMLFormatter.get_attributes

    def format(
            self,
            code: VariableCode,
            attr_names: Optional[Sequence[str]] = None,
    ) -> str:
        """Return an HTML <details> item for the code.

        Uses the `id_attrname` attribute as the name of the attribute that
        should be displayed in the non-collapsed part of the output string, and
        `self.get_attributes` to get the attributes to display in the details.
        """
        if attr_names is not None and self.id_attrname not in attr_names:
            attr_names = [self.id_attrname] + list(attr_names)
        attrs: Mapping[str, str|None] = self.get_attributes(code, attr_names=attr_names)
        # Print a collapsable list item, with the name as the summary part
        # and all other attributes returned by `self.get_attributes` in the
        # details part.
        list_top: str = f'<details><summary><b>{getattr(code, self.id_attrname)}</b></summary>\n<dl>\n'
        attrs_list: str = '\n'.join(
            f'    <dt>{attrname}</dt>\n'
            f'        <dd>{attrval}</dd>'
            for attrname, attrval in attrs.items()
            if attrname != self.id_attrname
        )
        list_bottom: str = '</dl>\n</details>\n'
        return list_top + attrs_list + list_bottom
    ###END def VariableCodeHTMLFormatter.format

###END class VariableCodeHTMLFormatter


class VariableCodeListHTMLFormatter(CodeListFormatter):
    """Formats a `nomenclature.codelist.VariableCodeList` as an HTML document,
    with optionally expandable items (using HTML details/summary elements) for
    each code.
    """

    def __init__(self, code_formatter: Optional[VariableCodeHTMLFormatter] = None):
        """Initialize the formatter with a `CodeFormatter` subclass."""
        if code_formatter is None:
            self.code_formatter = VariableCodeHTMLFormatter()
        else:
            self.code_formatter: VariableCodeHTMLFormatter = code_formatter
    ###END def VariableCodeListHTMLFormatter.__init__

    def format(
            self,
            codelist: VariableCodeList,
            header_title: str = '',
            attrs: Sequence[str] = ('unit', 'description')
    ) -> str:
        """Return an HTML document for the code list.

        Each code in the list is formatted using `self.code_formatter`, and the
        resulting strings are joined with newlines.
        """
        header: str = f'<html>\n<head><title>{header_title}</title></head>\n<body>\n<h1>{header_title}</h1>\n'
        body: str = '\n'.join(
            self.code_formatter.format(codelist[_codename], attr_names=attrs)
            for _codename in sorted(codelist.keys())
        )
        return header + body + '\n</body>\n</html>'
    ###END def VariableCodeListHTMLFormatter.format

###END class VariableCodeListHTMLFormatter
