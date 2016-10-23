"""
Content Vote View API

Exceptions:

    DuplicateVoteError

Classes:

    VoteView
"""

from . import redis_api
from .vote import AuthorVote, VoteStatusError


class DuplicateVoteError(redis_api.DuplicateVoteError):
    """
    Wrapper around redis.DuplicateVoteError to raise in
    APIs which call this view layer.
    """


class VoteView:

    def __init__(self, vote_status=None, edit_id=None, vote=None,
                 voter_id=None, timestamp=None, close_timestamp=None):
        """
        Args:
            vote_status: String, accepts 'in-progress' or 'ended'.
                Defaults to None.
            edit_id: Integer. Defaults to None.
            vote: String, expects 'Y' or 'N'. Defaults to None.
            voter_id: Integer. Defaults to None.
            timestamp: Datetime. Defaults to None.
            close_timestamp: Datetime. Defaults to None.
        """
        if vote:
            try:
                vote = AuthorVote(vote_status, edit_id, vote, voter_id,
                                  timestamp, close_timestamp)
                self.error_response = vote.save()
            except redis_api.DuplicateVoteError as e:
                raise DuplicateVoteError(str(e))
            except:
                raise
            else:
                self.vote = vote.json_ready
                self.__dict__.update(self.vote)

    @classmethod
    def get_vote_results(cls, vote_status, edit_id, validation_status=None):
        """
        Args:
            vote_status: String, expects 'in-progress' or 'ended'.
            edit_id: Integer.
            validation_status: String, expects 'validating', 'accepted',
                or 'rejected'. Defaults to None.
        Returns:
            Dictionary of the form
            {'Y': int, 'N': int}
        """
        votes = AuthorVote.bulk_retrieve(vote_status, edit_id=edit_id,
                                         validation_status=validation_status)
        for_count = 0
        against_count = 0
        for author_vote in votes:
            if author_vote.vote == "Y":
                for_count += 1
            else:
                against_count += 1

        return {"Y": for_count, "N": against_count}

