"""
Content Vote View API
"""

from .vote import AuthorVote


class VoteView:

    def __init__(self, vote_status, edit_id, vote, voter_id,
                 timestamp=None, close_timestamp=None):
        """
        Args:
            vote_status: String, accepts 'in-progress' or 'ended'.
            edit_id: Integer.
            vote: String, expects 'Y' or 'N'.
            voter_id: Integer.
            timestamp: Datetime. Defaults to None.
            close_timestamp: Datetime. Defaults to None.
        """
        try:
            vote = AuthorVote(vote_status, edit_id, vote, voter_id,
                              timestamp, close_timestamp)
            vote.save()
        except:
            raise
        else:
            self.vote = vote.json_ready
