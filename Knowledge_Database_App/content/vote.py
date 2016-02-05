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
                                            select_queries as select)
from . import redis
from . import edit as edit_api
from .content import Content, ApplicationError


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
        close_timestamp: Datetime. Defaults to None.
        author: UserData object. Defaults to None.

    Properties:
        json_ready: Dictionary.

    Instance Methods:
        check_vote_order, save

    Class Methods:
        unpack_vote_summary, _retrieve_from_storage,
        _retrieve_from_redis, bulk_retrieve, get_vote_summary
    """

    storage_handler = orm.StorageHandler()

    edit_id = None          # Integer.
    vote_status = None      # String, expects 'in-progress' or 'ended'.
    vote = None             # String, expects 'Y' or 'N'.
    timestamp = None        # Datetime.
    close_timestamp = None  # Datetime.
    author = None           # UserData object.

    def __init__(self, vote_status, edit_id, vote, voter_id,
                 timestamp=None, close_timestamp=None):
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
            self.close_timestamp = close_timestamp
            self.author = UserData(user_id=voter_id)

    @classmethod
    def unpack_vote_summary(cls, vote_summary):
        if vote_summary[0] != "<":
            cutoff_index = vote_summary.find("<")   # Should not be -1
            vote_summary = vote_summary[cutoff_index:]
        vote_lists = [
            vote_string[:-3].split(", ")
            if vote_string.endswith(">, ") else vote_string[:-1].split(", ")
            for vote_string in vote_summary.split("<")
        ]
        vote_dict = {
            int(vote_list[0]): vote_list[1] + str("; ") + vote_list[2]
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
            validation_status: String, expects 'validating', 'accepted',
                or 'rejected'. Defaults to None.
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
                                     key, timestamp=dateparse.parse(value[3:]),
                                     close_timestamp=vote_object.close_timestamp)
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
                                     key, timestamp=dateparse.parse(value[3:]),
                                     close_timestamp=vote_object.close_timestamp)
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
                                key, timestamp=dateparse.parse(value[3:]),
                                close_timestamp=vote_object.close_timestamp)
                     for key, value in vote_dict.items()]
        else:
            raise select.InputError("Invalid argument!")

        return votes

    @classmethod
    def get_vote_summary(cls, votes):
        close_timestamp = votes[0].close_timestamp
        vote_summary = (str(close_timestamp) + " "
                        if close_timestamp is not None else "")
        for vote in votes:
            vote_summary += ("<" + vote.vote + ", " + str(vote.author.user_id) +
                             ", " + str(vote.timestamp) + ">, ")
        return vote_summary[:-2]

    def check_vote_order(self):
        """
        Returns:
            Tuple of the form (bool, integer), where bool is True if
            and only if this vote is on the earliest (chronologically)
            submitted validating edit and integer is the edit id of the
            earliest submitted validating edit.

        Note: Properly ordered vote boolean returned despite redundancy
            to keep logic within method.
        """
        edit = edit_api.Edit(edit_id=self.edit_id,
                             validation_status="validating")
        if (edit.content_part == "name" or
                edit.content_part == "alternate_name"):
            edit_ids = edit_api.Edit.bulk_retrieve(
                validation_status="validating", name_id=edit.part_id,
                page_num=0, ids_only=True)
        elif edit.content_part == "text":
            edit_ids = edit_api.Edit.bulk_retrieve(
                validation_status="validating", text_id=edit.part_id,
                page_num=0, ids_only=True)
        elif edit.content_part == "keyword":
            edit_ids = edit_api.Edit.bulk_retrieve(
                validation_status="validating", content_id=edit.content_id,
                keyword_id=edit.part_id, page_num=0, ids_only=True)
        elif edit.content_part == "content_type":
            edit_ids = edit_api.Edit.bulk_retrieve(
                validation_status="validating", content_id=edit.content_id,
                content_type_id=edit.part_id, page_num=0, ids_only=True)
        elif edit.content_part == "citation":
            edit_ids = edit_api.Edit.bulk_retrieve(
                validation_status="validating", content_id=edit.content_id,
                citation_id=edit.part_id, page_num=0, ids_only=True)
        else:
            raise ApplicationError("Unexpected edit argument!")

        return edit_ids[-1] == self.edit_id, edit_ids[-1]

    def save(self):
        if self.vote_status != "in-progress":
            raise NotImplementedError
        valid_vote, edit_to_vote_on = self.check_vote_order()
        if not valid_vote:
            return edit_to_vote_on
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

    @classmethod
    def votes_needed(cls, user_id, content_ids=None):
        """
        Args:
            user_id: Integer.
            content_ids: List of integers. Defaults to None.

        Returns:
            Dictionary of the form

                {content_id1: list of edit ids of edits not yet voted on,
                 content_id2: list of edit ids of edits not yet voted on,
                 ...},

            where the each list is sorted in descending chronological
            order by submission time.
        """
        if content_ids is None:
            content_ids = Content.bulk_retrieve(
                user_id=user_id, ids_only=True)
        try:
            edit_ids = redis.get_edits(
                content_ids=content_ids, only_ids=True)
            edits_voted_on = redis.get_edits(voter_id=user_id, only_ids=True)
        except:
            raise
        else:
            return {content_id: [edit_id for edit_id in edit_ids[content_id]
                                 if edit_id not in edits_voted_on]
                    for content_id in edit_ids}

    @property
    def json_ready(self):
        return {
            "edit_id": self.edit_id,
            "vote_status": self.vote_status,
            "timestamp": str(self.timestamp),
            "close_timestamp": (str(self.close_timestamp)
                                if self.close_timestamp is not None
                                else None),
            self.author.user_id: self.vote,
        }

# TODO: Add code attribute to say explicitly how vote closed