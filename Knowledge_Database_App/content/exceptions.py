"""
Custom exceptions raised by content modules.

Exceptions:

    DuplicateVoteError, MissingKeyError, ApplicationError, ContentError,
    DuplicateError, DataMatchingError, VoteStatusError
"""


class DuplicateVoteError(Exception):
    """Exception to raise when a vote already exists."""


class MissingKeyError(Exception):
    """Exception to raise when a key is missing."""


class ApplicationError(Exception):
    """
    General exception raised when an unrecoverable error
    in application logic occurs.
    """


class ContentError(Exception):
    """
    General exception raised upon submission of an illegally formatted
    content piece or content part.
    """


class DuplicateError(Exception):
    """Exception raised when a content part is a duplicate of another."""


class DataMatchingError(Exception):
    """
    Exception raised when the submission data does not match the
    data in storage.
    """


class VoteStatusError(Exception):
    """
    Exception raised when an operation is called that requires an
    in-progress vote but the vote is already closed.
    """