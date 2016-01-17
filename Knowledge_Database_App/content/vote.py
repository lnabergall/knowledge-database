"""
Content Vote API

Exceptions:

    VoteStatusError

Classes:

    AuthorVote
"""
from datetime import datetime

from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from . import redis
from .content import UserData


class VoteStatusError(Exception):
    """
    Exception raised when an operation is called that requires an
    in-progress vote but the vote is already closed.
    """


class AuthorVote:

    storage_handler = orm.StorageHandler()

    edit_id = None      # Integer.
    vote_status = None  # String, expects 'in-progress' or 'completed'.
    vote = None         # String, expects 'Y' or 'N'.
    timestamp = None    # Datetime.
    author = None       # UserData object.

    def __init__(self, vote_status, edit_id, vote, voter_id):
        if (not content_id or not edit_id or
                (vote != "Y" and vote != "N") or not voter_id or
                (vote_status is not None and vote_status != "in-progress"
                and vote_status != "completed")):
            raise select.InputError("Invalid arguments!")
        else:
            self.edit_id = edit_id
            self.vote_status = vote_status
            self.vote = vote
            self.timestamp = datetime.utcnow()
            self.author = UserData(user_id=voter_id)

    @classmethod
    def unpack_vote_summary(cls):
        pass

    @classmethod
    def _retrieve_from_storage(cls, edit_id=None, vote_id=None,
                               validation_status=None):
        if edit_id is not None:
            try:
                if validation_status == "accepted":
                    vote_object = cls.storage_handler.call(
                        select.get_accepted_votes, edit_id=edit_id)
                elif validation_status == "rejected":
                    vote_object = cls.storage_handler.call(
                        select.get_rejected_votes, edit_id=edit_id)
                else:
                    raise select.InputError("Invalid argument!")
            except:
                raise
        elif vote_id is not None:
            try:
                if validation_status == "accepted":
                    vote_object = cls.storage_handler.call(
                        select.get_accepted_votes, vote_id=vote_id)
                elif validation_status == "rejected":
                    vote_object = cls.storage_handler.call(
                        select.get_rejected_votes, vote_id=vote_id)
                else:
                    raise select.InputError("Invalid argument!")
            except:
                raise

        return vote_object

    @classmethod
    def _retrieve_from_redis(cls, edit_id):
        try:
            vote_dict = redis.get_validation_data(edit_id)["votes"]
        except:
            raise
        else:
            return vote_dict

    @classmethod
    def bulk_retrieve(cls, edit_id=None, vote_id=None, vote_status=None):
        pass

    @classmethod
    def get_vote_summary(cls, edit_id=None, votes=None):
        pass

    def save(self):
        if self.vote_status != "in-progress":
            raise NotImplementedError
        else:
            try:
                redis.store_vote(self.edit_id, self.author.user_id, self.vote)
            except redis.DuplicateVoteError:
                raise redis.DuplicateVoteError(
                    "Vote already submitted by user " +
                    str(self.author.user_id) + "!")
            except redis.MissingKeyError as e:
                raise VoteStatusError(str(e))
            except:
                raise

    @property
    def json_ready(self):
        return {
            "edit_id": self.edit_id,
            "vote_status": self.vote_status,
            "timestamp": str(self.timestamp),
            self.author.user_id: self.vote,
        }