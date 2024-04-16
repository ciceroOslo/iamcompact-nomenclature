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


QuantityType = tp.TypeVar('QuantityType')

class RangeCheckResultsBase(
        VettingResultsBase[StatusType],
        tp.Generic[QuantityType, StatusType],
        abc.ABC
):
    """Base class for checking that a quantity is within a specified range.
    
    This is an abstract base class, and the "quantity" in question can be of any
    type (referred to by the type varialbe `QuantityType` below), to be
    specified further by subclasses.

    Attributes
    ----------
    value : QuantityType
        The value of the quantity that was checked.
    target_value : QuantityType | None
        The target value of the quantity that was checked. Can be None if there
        is no specific target value but only a range.
    target_range : tp.Tuple[QuantityType|None, QuantityType|None]
        The target range for the quantity that was checked. Should always
        contain `target_value` if it exists. If the target range is just a lower
        or upper bound, the other bound should be set to `None`.

    Properties
    ----------
    is_in_range : bool
        Whether the value of the quantity is within the target range. Abstract,
        must be overridden by subclasses.
    lower_bound : QuantityType
        The lower bound of the target range. If the target range is just an
        upper bound (i.e., `self.target_range[0]` is `None`), a `ValueError`
        will be raised.
    upper_bound : QuantityType
        The upper bound of the target range. If the target range is just a lower
        bound (i.e., `self.target_range[1]` is `None`), a `ValueError` will be
        raised.

    Init Parameters
    ---------------
    value : QuantityType
        The value of the quantity that was checked.
    target_range : tp.Tuple[QuantityType, QuantityType]
        The target range for the quantity that was checked, as a tuple of
        `(lower_bound, upper_bound)`. If the target range is just a lower or
        upper bound, the other bound should be set to `None`.
    target_value : QuantityType, Optional
        The target value of the quantity that was checked. Can be None if there
        is no specific target value but only a range. Optional, defaults to
        None.
    status : StatusType, Optional
        The status of the check. Optional, defaults to None. If None, the method
        `self._compute_status()` will be called to determine the status. This
        function must be implemented by subclasses that want to keep `status`
        as an optional rather than a mandatory parameter.

    Methods
    -------
    _perform_check() -> StatusType
        Perform the check on the value of the quantity, and return the status.
        Should be overridden by subclasses as needed.
    __str__() -> str
        Return a string representation of the results.
    range_str() -> str
        Return a string representation of the range, which is used in the string
        representation of the results. To be overridden by subclasses. By
        default returns `f'[{str(self.lower_bound)}, {str(self.upper_bound)}]'`.
        Will only be used if both `lower_bound` and `upper_bound` are not None.
    value_str() -> str
        Return a string representation of the value, which is used in the string
        representation of the results.
    target_value_str() -> str
        Return a string representation of the target value, which is used in the
        string representation of the results.
    """

    value: QuantityType
    target_value: tp.Optional[QuantityType]
    target_range: tp.Tuple[tp.Optional[QuantityType], tp.Optional[QuantityType]]
    status: StatusType

    def _compute_status(self) -> StatusType:
        """Compute the status of the check.

        This method should be overridden by subclasses that want to keep `status`
        as an optional rather than a mandatory parameter.
        """
        raise NotImplementedError
    ###END def RangeCheckResultsBase._compute_status

    def __init__(
            self,
            value: QuantityType,
            target_range: tp.Tuple[tp.Optional[QuantityType],
                                   tp.Optional[QuantityType]],
            target_value: tp.Optional[QuantityType],
            status: tp.Optional[StatusType] = None
    ):
        self.value = value
        self.target_value = target_value
        self.target_range = target_range
        if status is None:
            status = self._compute_status()
        super().__init__(status)
    ###END def RangeCheckResultsBase.__init__

    @abc.abstractmethod
    def __str__(self) -> str:
        pass
    ###END def RangeCheckResultsBase.__str__

    @abc.abstractmethod
    def range_str(self) -> str:
        pass
    ###END def RangeCheckResultsBase.range_str

    def value_str(self) -> str:
        return f'{str(self.value)}'
    ###END def RangeCheckResultsBase.value_str

    def target_value_str(self) -> str:
        if self.target_value is not None:
            return f', target value: {str(self.target_value)}'
        return ''
    ###END def RangeCheckResultsBase.target_value_str

    @property
    def lower_bound(self) -> QuantityType:
        if self.target_range[0] is None:
            raise ValueError('Lower bound is None')
        return self.target_range[0]
    ###END property def RangeCheckResultsBase.lower_bound

    @property
    def upper_bound(self) -> QuantityType:
        if self.target_range[1] is None:
            raise ValueError('Upper bound is None')
        return self.target_range[1]
    ###END property def RangeCheckResultsBase.upper_bound

    abc.abstractmethod
    @property
    def is_in_range(self) -> bool:
        raise NotImplementedError
    ###END property def RangeCheckResultsBase.is_in_range

###END class RangeCheckResultsBase
