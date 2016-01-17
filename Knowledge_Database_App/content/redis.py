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

from Knowledge_Database_App.storage.action_queries import InputError


class DuplicateVoteError(Exception):
    """Exception to raise when a vote already exists."""


class MissingKeyError(Exception):
    """Exception to raise when a key is missing."""


redis = StrictRedis()


def _setup_id_base():
    redis.setnx("next_edit_id", 1)


def store_edit(content_id, edit_text, edit_rationale, content_part,
               part_id, timestamp, start_timestamp, author_type, user_id):
    """
    Args:
        content_id: Integer.
        edit_text: String.
        edit_rationale: String.
        original_part_text: String.
        content_part: String, expects 'text', 'name', 'alternate_name',
            'keyword', 'content_type', or 'citation'.
        part_id: Integer.
        timestamp: Datetime.
        start_timestamp: Datetime.
        author_type: String, expects 'U' or an IP address.
        user_id: Integer.
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
            except:
                raise
            else:
                break

        # Now store the edit with the edit id
        if user_id is not None:
            pipe.lpush("user:" + str(user_id), edit_id)
        if content_part == "citation":
            pipe.lpush("citation:" + str(part_id), edit_id)
        elif content_part == "text":
            pipe.lpush("text:" + str(part_id), edit_id)
        elif content_part == "name" or content_part == "alternate_name":
            pipe.lpush("name:" + str(part_id), edit_id)
        elif content_part == "keyword":
            pipe.lpush("keyword:" + str(part_id), edit_id)
        elif content_part == "content_type":
            pipe.lpush("content_type:" + str(part_id), edit_id)
        else:
            raise InputError("Invalid argument!")
        pipe.lpush("content:" + str(content_id), edit_id)
        pipe.hmset("edit:" + str(edit_id), {
            "edit_id": edit_id,
            "content_id": content_id,
            "edit_text": edit_text,
            "edit_rationale": edit_rationale if edit_rationale else "",
            "content_part": content_part,
            "part_id": part_id,
            "timestamp": timestamp,
            "start_timestamp": start_timestamp,
            "author_type": author_type,
        })
        if user_id is not None:
            pipe.hset("edit:" + str(edit_id), "user_id", user_id)
        pipe.execute()

    return edit_id


def store_vote(edit_id, voter_id, vote_and_time):
    """
    Args:
        edit_id: Integer.
        voter_id: Integer.
        vote_and_time: String.
    """
    exists = redis.exists("edit:" + str(edit_id))
    if not exists:
        raise MissingKeyError("Key '" + str(edit_id) + "' not found!")
    else:
        response = redis.hsetnx("votes:" + str(edit_id),
                                voter_id, vote_and_time)
        if response == 0:
            raise DuplicateVoteError


def get_edits(content_id=None, user_id=None, text_id=None,
              citation_id=None, keyword_id=None, name_id=None,
              content_type_id=None, only_ids=False):
    """
    Args:
        content_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        text_id: Integer. Defaults to None.
        citation_id: Integer. Defaults to None.
        keyword_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        content_type_id: Integer. Defaults to None.
        only_ids: Boolean. Defaults to False. Determines whether to
            return edits or only edit ids.
    """
    if content_id is not None:
        edit_ids = redis.lrange("content:" + str(content_id), 0, -1)
    elif user_id is not None:
        edit_ids = redis.lrange("user:" + str(user_id), 0, -1)
    elif text_id is not None:
        edit_ids = redis.lrange("text:" + str(text_id), 0, -1)
    elif citation_id is not None:
        edit_ids = redis.lrange("citation:" + str(citation_id), 0, -1)
    elif keyword_id is not None:
        edit_ids = redis.lrange("keyword:" + str(keyword_id), 0, -1)
    elif name_id is not None:
        edit_ids = redis.lrange("name:" + str(name_id), 0, -1)
    elif content_type_id is not None:
        edit_ids = redis.lrange("content_type:" + str(content_type_id), 0, -1)
    else:
        raise InputError("Missing arguments!")
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


def delete_validation_data(content_id, edit_id, user_id,
                           part_id, content_part):
    """
    Args:
        content_id: Integer.
        edit_id: Integer.
        user_id: Integer.
        part_id: Integer.
        content_part: String, expects 'text', 'citation', 'keyword',
            'name', 'alternate_name', or 'content_type'.
    """
    with redis.pipeline() as pipe:
        if user_id is not None:
            pipe.lrem("user:" + str(user_id), 0, edit_id)
        if content_part == "text":
            pipe.lrem("text:" + str(part_id), 0, edit_id)
        elif content_part == "citation":
            pipe.lrem("citation:" + str(part_id), 0, edit_id)
        elif content_part == "name" or content_part == "alternate_name":
            pipe.lrem("name:" + str(part_id), 0, edit_id)
        elif content_part == "keyword":
            pipe.lrem("keyword:" + str(part_id), 0, edit_id)
        elif content_part == "content_type":
            pipe.lrem("content_type:" + str(part_id), 0, edit_id)
        else:
            raise InputError("Invalid argument!")
        pipe.lrem("content:" + str(content_id), 0, edit_id)
        pipe.delete("edit:" + str(edit_id))
        pipe.delete("votes:" + str(edit_id))
        pipe.execute()
