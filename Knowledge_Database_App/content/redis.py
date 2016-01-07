"""
Storage for edits and votes active in the validation process.
Uses redis.

Exceptions:

    DuplicateVoteError

Functions:

    store_edit, store_vote, get_edits, get_validation_data,
    delete_validation_data
"""

from redis import StrictRedis, WatchError


class DuplicateVoteError(Exception):
    """Exception to raise when a vote already exists."""


redis = StrictRedis()


def _setup_id_base():
    redis.setnx("next_edit_id", 1)


def store_edit(content_id, edit_text, edit_rationale, original_part_text,
               content_part, part_id, timestamp, author_type, user_id=None):
    """
    Args:
        content_id: Integer.
        edit_text: String.
        edit_rationale: String.
        original_part_text: String.
        content_part: String, expects 'text', 'name', 'keyword',
            'content_type', or 'citation'.
        part_id: Integer.
        timestamp: Datetime.
        author_type: String, expects 'U' or an IP address.
        user_id: Integer. Defaults to None.
    Returns:
        An integer, the id of the edit in Redis.
    """
    with redis.pipeline() as pipe:
        # Get a unique edit id and increment it for the next edit
        while True:
            try:
                pipe.watch("next_edit_id")
                edit_id = pipe.get("next_edit_id")
                next_edit_id = edit_id + 1
                pipe.multi()
                pipe.set("next_edit_id", next_edit_id).execute()
            except WatchError:
                continue
            else:
                break

        # Now store the edit with the edit id
        pipe.lpush("content:" + str(content_id), edit_id)
        pipe.hmset("edit:" + str(edit_id), {
            "edit_text": edit_text,
            "edit_rationale": edit_rationale,
            "content_part": content_part,
            "part_id": part_id,
            "timestamp": timestamp,
            "author_type": author_type,
        })
        if user_id is not None:
            pipe.hset("edit:" + str(edit_id), "user_id", user_id)
        pipe.execute()

    return edit_id


def store_vote(edit_id, voter_id, vote):
    """
    Args:
        edit_id: Integer.
        voter_id: Integer.
        vote: String, expects 'Y' or 'N'.
    """
    response = redis.hsetnx("votes:" + str(edit_id), voter_id, vote)
    if response == 0:
        raise DuplicateVoteError


def get_edits(content_id, only_ids=False):
    """
    Args:
        content_id: Integer.
        only_ids: Boolean. Defaults to False. Determines whether to
            return edits or only edit ids.
    """
    edit_ids = redis.lrange("content:" + str(content_id), 0, -1)
    if only_ids:
        return edit_ids
    else:
        with redis.pipeline() as pipe:
            for edit_id in edit_ids:
                pipe.hgetall("edit:" + str(edit_id))
            edits = pipe.execute()
        return {edit_id:edit for edit_id, edit in zip(edit_ids, edits)}


def get_validation_data(edit_id):
    """
    Args:
        edit_id: Integer.
    """
    with redis.pipeline() as pipe:
        pipe.hgetall("edit:" + str(edit_id))
        pipe.hgetall("votes:" + str(edit_id))
        edit, votes = pipe.execute()

    return {"edit": edit, "votes": votes}


def delete_validation_data(content_id, edit_id):
    """
    Args:
        content_id: Integer.
        edit_id: Integer.
    """
    with redis.pipeline() as pipe:
        pipe.lrem("content:" + str(content_id), 0, edit_id)
        pipe.delete("edit:" + str(edit_id))
        pipe.delete("votes:" + str(edit_id))
        pipe.execute()
