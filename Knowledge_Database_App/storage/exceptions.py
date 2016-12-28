"""
Custom exceptions raised by storage modules.

Exceptions:

    MultipleValuesFound, ActionError, SelectError, InputError,
    MissingDataError, UniquenessViolationError
"""

from sqlalchemy.orm.exc import MultipleResultsFound


class MultipleValuesFound(ValueError, MultipleResultsFound):
    """
    Exception raised by `Query.values` when multiple values
    were found in a single result row.
    """


class ActionError(Exception):
    """General exception raised when a database action query fails."""


class SelectError(Exception):
    """
    General exception raised when a database select query returns an
    invalid result.
    """


class InputError(Exception):
    """
    General exception raised when a function is called with invalid
    argument values.
    """


class MissingDataError(Exception):
    """Exception raised when a query unexpectedly returns no results."""


class UniquenessViolationError(Exception):
    """Exception raised when a query violates a unique constraint."""