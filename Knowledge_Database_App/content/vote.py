"""
Content Vote API

Exceptions:

    VoteStatusError

Classes:

    AuthorVote
"""

from datetime import datetime

import dateutil.parser as dateparse

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
    """
    Attributes:
        edit_id: Integer. Defaults to None.
        vote_status: String, expects 'in-progress' or 'ended'.
            Defaults to None.
        vote: String, expects 'Y' or 'N'. Defaults to None.
        timestamp: Datetime. Defaults to None.
        author: UserData object. Defaults to None.

    Properties:
        json_ready: Dictionary.

    Instance Methods:
        save

    Class Methods:
        unpack_vote_summary, _retrieve_from_storage,
        _retrieve_from_redis, bulk_retrieve, get_vote_summary
    """

    storage_handler = orm.StorageHandler()

    edit_id = None      # Integer.
    vote_status = None  # String, expects 'in-progress' or 'ended'.
    vote = None         # String, expects 'Y' or 'N'.
    timestamp = None    # Datetime.
    author = None       # UserData object.

    def __init__(self, vote_status, edit_id, vote, voter_id, timestamp=None):
        if (not content_id or not edit_id or
                (vote != "Y" and vote != "N") or not voter_id or
                (vote_status is not None and vote_status != "in-progress"
                and vote_status != "ended")):
            raise select.InputError("Invalid arguments!")
        else:
            self.edit_id = edit_id
            self.vote_status = vote_status
            self.vote = vote
            self.timestamp = (datetime.utcnow() if timestamp is None
                              else timestamp)
            self.author = UserData(user_id=voter_id)

    @classmethod
    def unpack_vote_summary(cls, vote_summary):
        vote_lists = [
            vote_string[:-3].split(", ")
            if vote_string.endswith(">, ") else vote_string[:-1].split(", ")
            for vote_string in vote_summary.split("<")
        ]
        vote_dict = {
            vote_list[0]: vote_list[1] + str("; ") + vote_list[2]
            for vote_list in vote_lists[1:]
        }
        return vote_dict

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
    def bulk_retrieve(cls, vote_status, edit_id=None, vote_id=None,
                      content_id=None, validation_status=None):
        """
        Args:
            vote_status: String, expects 'in-progress' or 'ended'.
            edit_id: Integer. Defaults to None.
            vote_id: Integer. Defaults to None.
            validation_status: String, expects 'accepted' or 'rejected'.
                Defaults to None.
        Returns:
            List of AuthorVotes or dictionary of the form
            {edit_id1: list1 of AuthorVotes,
             edit_id2: list2 of AuthorVotes,
             ...}
        """
        if vote_status == "in-progress":
            if edit_id is None:
                vote_dict = cls._retrieve_from_redis(edit_id)
                votes = [AuthorVote(vote_status, edit_id, value[0],
                                    key, timestamp=dateparse.parse(value[3:]))
                         for key, value in vote_dict.items()]
            elif content_id is not None:
                try:
                    vote_dicts = redis.get_votes(content_id)
                except:
                    raise
                else:
                    votes = {edit_id: [AuthorVote(vote_status, edit_id, value[0],
                              key, timestamp=datetime.parse(value[3:]))
                              for key, value in vote_dict.items()]
                             for edit_id, vote_dict in vote_dicts.items()}
            else:
                raise select.InputError("Invalid arguments!")
        elif vote_status == "ended":
            if edit_id is not None:
                vote_object = cls._retrieve_from_storage(
                    edit_id=edit_id, validation_status=validation_status)
            elif vote_id is not None:
                vote_object = cls._retrieve_from_storage(
                    vote_id=vote_id, validation_status=validation_status)
            elif content_id is not None:
                if validation_status == "accepted":
                    vote_objects = cls.storage_handler.call(
                        select.get_accepted_votes, content_id=content_id)
                    votes = {}
                    for vote_object in vote_objects:
                        edit_id = vote_object.accepted_edit_id
                        vote_dict = cls.unpack_vote_summary(vote_object.vote)
                        vote_list = [AuthorVote(vote_status, edit_id, value[0],
                                 key, timestamp=dateparse.parse(value[3:]))
                                 for key, value in vote_dict.items()]
                        votes[edit_id] = vote_list
                elif validation_status == "rejected":
                    vote_objects = cls.storage_handler.call(
                        select.get_rejected_votes, content_id=content_id)
                    votes = {}
                    for vote_object in vote_objects:
                        edit_id = vote_object.rejected_edit_id
                        vote_dict = cls.unpack_vote_summary(vote_object.vote)
                        vote_list = [AuthorVote(vote_status, edit_id, value[0],
                                 key, timestamp=dateparse.parse(value[3:]))
                                 for key, value in vote_dict.items()]
                        votes[edit_id] = vote_list
                else:
                    raise select.InputError("Invalid arguments!")
                return votes
            else:
                raise select.InputError("Invalid arguments!")
            vote_dict = cls.unpack_vote_summary(vote_object.vote)
            if edit_id is None:
                if validation_status == "accepted":
                    edit_id = vote_object.accepted_edit_id
                elif validation_status == "rejected":
                    edit_id = vote_object.rejected_edit_id
                else:
                    raise select.InputError("Invalid argument!")
            votes = [AuthorVote(vote_status, edit_id, value[0],
                                key, timestamp=dateparse.parse(value[3:]))
                     for key, value in vote_dict.items()]
        else:
            raise select.InputError("Invalid argument!")

        return votes

    @classmethod
    def get_vote_summary(cls, votes):
        vote_summary = ""
        for vote in votes:
            vote_summary += ("<" + vote.vote + ", " + str(vote.author.user_id) +
                             ", " + str(vote.timestamp) + ">, ")
        return vote_summary[:-2]

    def save(self):
        if self.vote_status != "in-progress":
            raise NotImplementedError
        else:
            try:
                redis.store_vote(self.edit_id, self.author.user_id,
                                 self.vote + "; " + str(self.timestamp))
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