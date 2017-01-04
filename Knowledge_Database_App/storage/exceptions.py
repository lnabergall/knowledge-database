"""
Custom exceptions raised by storage modules.

Exceptions:

    MultipleValuesFound, ActionError, SelectError, InputError,
    MissingDataError, UniquenessViolationError
"""

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import IntegrityError


class MultipleValuesFound(ValueError, MultipleResultsFound):
    """
    Exception raised by `Query.values` when multiple values
    were found in a single result row; should indicate an
    implementation error.
    """


class ActionError(Exception):
    """General exception raised when a database action query fails."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        if message is None:
            self.message = "There was a problem submitting the provided data."
        else:
            self.message = message


class SelectError(Exception):
    """
    General exception raised when a database select query returns an
    invalid result.
    """

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        if message is not None:
            self.message = message
        elif type(exception) == NoResultFound:
            self.message = "No object found."
        elif type(exception) == MultipleResultsFound:
            self.message = "Multiple objects found."


class InputError(Exception):
    """
    General exception raised when a function is called with invalid
    argument values.
    """

    def __init__(self, *args, inputs=None, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.inputs = inputs    # Dictionary of invalid argument value set
        self.message = message


class MissingDataError(Exception):
    """Exception raised when a query unexpectedly returns no results."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class UniquenessViolationError(Exception):
    """Exception raised when a query violates a unique constraint."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        if type(exception) == IntegrityError:
            self.parameter = str(exception.orig)[
                str(exception.orig).index(".")+1:].strip()
        self.message = message