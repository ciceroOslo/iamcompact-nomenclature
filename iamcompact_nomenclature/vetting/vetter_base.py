"""Base classes for performing vetting checks.

Classes
-------
Vetter
    Base class for performing vetting checks. Subclasses should implement the
    `.check` method, which takes an arbitrary object (with the results to be
    checked) as input, and returns a subclass of `VettingResults`. The class
    should also declare the `result_type` attribute, which should be the
    subclass of `VettingResults` that is returned by `.check`.
VettingResults
    Base class for the results of a vetting check. Subclasses should implement
    the `__str__` method, which should return a string representation of the
    results. It should also declare a `status` attribute, which should be an
    enum that indicates the status of the check. By default, the enum is of the
    type `VettingStatus` defined in this module, which takes the values `PASS`
    and `FAIL`. The attribute `status_type` should be set to the type of the
    enum actually used in the subclass.
"""
