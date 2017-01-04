"""
Custom exceptions raised by content modules.

Exceptions:

    DuplicateVoteError, MissingKeyError, ApplicationError, ContentError,
    DuplicateError, DataMatchingError, VoteStatusError
"""


class DuplicateVoteError(Exception):
    """Exception to raise when a vote already exists."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class MissingKeyError(Exception):
    """Exception to raise when a key is missing."""

    def __init__(self, *args, exception=None, key=None, message=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = exception
        self.key = key
        self.message = message


class ApplicationError(Exception):
    """
    General exception raised when an unrecoverable error
    in application logic occurs.
    """

    def __init__(self, *args, exception=None, error_data=None,
                 message=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = exception
        self.error_data = error_data
        self.message = message


class ContentError(Exception):
    """
    General exception raised upon submission of an illegally formatted
    content piece or content part.
    """

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class DuplicateError(Exception):
    """Exception raised when a content part is a duplicate of another."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class DataMatchingError(Exception):
    """
    Exception raised when the submission data does not match the
    data in storage.
    """

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class VoteStatusError(Exception):
    """
    Exception raised when an operation is called that requires an
    in-progress vote but the vote is already closed.
    """

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message