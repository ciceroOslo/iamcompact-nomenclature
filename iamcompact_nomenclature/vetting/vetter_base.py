"""Base classes for performing vetting checks.

Classes
-------
Vetter
    Base class for performing vetting checks. Subclasses should implement the
    `.check` method, which takes an arbitrary object (with the data to be
    checked) as input, and returns a subclass of `VettingResults`. The class
    should also declare the `result_type` attribute, which should be the
    subclass of `VettingResults` that is returned by `.check`.
VettingResultsBase
    Base class for the results of a vetting check. Subclasses should implement
    the `__str__` method, which should return a string representation of the
    results. It should also declare a `status` attribute, which should be an
    enum that indicates the status of the check. By default, the enum is of the
    type `PassFail` defined in this module, which takes the values `PASS`
    and `FAIL`. The attribute `status_type` should be set to the type of the
    enum actually used in the subclass.
"""
import typing as tp
import enum
import abc

from pyam import IamDataFrame


StatusType = tp.TypeVar('StatusType', bound=enum.Enum)
"""TypeVar for the status of a vetting check (should be an enum)."""

class PassFail(str, enum.Enum):
    """Enum for the status of a vetting check."""
    PASS = enum.auto()
    FAIL = enum.auto()
###END enum class PassFail


class VettingResultsBase(tp.Generic[StatusType], abc.ABC):
    """Base class for the results of a vetting check.

    Subclasses should implement the `__str__` method, which should return a
    string representation of the results. It should also declare a `status`
    attribute, which should be an enum that indicates the status of the check.
    By default, the enum is of the type `PassFail` defined in this module,
    which takes the values `PASS` and `FAIL`. The attribute `status_type`
    should be set to the type of the enum actually used in the subclass.

    Init Parameters
    ---------------
    status : StatusType (TypeVar)
        The status of the check.
    """
    status: StatusType
    status_type: tp.Type[StatusType]

    def __init__(self, status: StatusType):
        self.status = status

    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

###END class VettingResultsBase


class PassFailResults(VettingResultsBase[PassFail], abc.ABC):
    """Base class for the results of a vetting check that uses the `PassFail`
    enum for the status.

    Subclasses should implement the `__str__` method, which should return a
    string representation of the results.
    """
    status_type = PassFail
###END class PassFailResults



CheckingDataType = tp.TypeVar('CheckingDataType')
"""TypeVar for data types to be checked by a Vetter."""
ResultsType = tp.TypeVar('ResultsType', bound=VettingResultsBase)
"""TypeVar for the results of a vetting check."""

class Vetter(tp.Generic[CheckingDataType, ResultsType], abc.ABC):
    """Base class for performing vetting checks.

    Subclasses should implement the `.check` method, which takes an arbitrary
    object (with the data to be checked) as input, and returns a subclass of
    `VettingResults`. The class should also declare the `result_type` attribute,
    which should be the subclass of `VettingResults` that is returned by `.check`.
    """
    result_type: tp.Type[ResultsType]

    @abc.abstractmethod
    def check(self, data: CheckingDataType) -> ResultsType:
        """Perform a vetting check on the given data.

        Parameters
        ----------
        data : CheckingDataType
            The data to be checked.

        Returns
        -------
        ResultsType
            The results of the vetting check.
        """
        raise NotImplementedError

###END class Vetter


class IamDataFrameVetter(
        Vetter[IamDataFrame, ResultsType],
        tp.Generic[ResultsType],
        abc.ABC
):
    """Base class for performing vetting checks on an `IamDataFrame`.

    Subclasses should implement the `.check` method, which takes an `IamDataFrame`
    as input, and returns a subclass of `VettingResults`. The class should also
    declare the `result_type` attribute, which should be the subclass of
    `VettingResults` that is returned by `.check`.
    """

    @abc.abstractmethod
    def check(self, data: IamDataFrame) -> ResultsType:
        """Perform a vetting check on the given `IamDataFrame`.

        Parameters
        ----------
        data : IamDataFrame
            The `IamDataFrame` to be checked.

        Returns
        -------
        ResultsType
            The results of the vetting check.
        """
        raise NotImplementedError
###END class IamDataFrameVetter
