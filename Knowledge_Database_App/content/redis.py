"""
Storage for edits and votes active in the validation process.
Uses redis.

Exceptions:

    DuplicateVoteError

Functions:

    store_edit, store_vote, store_confirm, get_confirm_info,
    expire_confirm, get_edits, get_votes, get_validation_data,
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


def store_edit(content_id, edit_text, edit_rationale, content_part, part_id,
               timestamp, start_timestamp, author_type, user_id=None):
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
    with redis.pipeline() as pipe:
        pipe.exists("edit:" + str(edit_id))
        pipe.lrange("voter:" + str(), 0, -1)
        exists, user_votes = pipe.execute()
    if not exists:
        raise MissingKeyError("Key '" + str(edit_id) + "' not found!")
    if edit_id in user_votes:
        raise DuplicateVoteError
    else:
        with redis.pipeline() as pipe:
            pipe.hsetnx("votes:" + str(edit_id),
                        voter_id, vote_and_time)
            pipe.lpush("voter:" + str(voter_id), edit_id)
            response_list = pipe.execute()
        if response_list[0] == 0:
            raise DuplicateVoteError


def store_confirm(email, confirmation_id_hash, expire_timestamp):
    redis.hset("user_email:" + email, confirmation_id_hash,
               str(expire_timestamp))


def get_confirm_info(email):
    confirmation_dict = redis.hgetall("user_email:" + email)
    return confirmation_dict


def expire_confirm(email):
    redis.delete("user_email:" + email)


def get_edits(content_id=None, content_ids=None, user_id=None, voter_id=None,
              text_id=None, citation_id=None, keyword_id=None, name_id=None,
              content_type_id=None, only_ids=False):
    """
    Args:
        content_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        voter_id: Integer. Defaults to None.
        text_id: Integer. Defaults to None.
        citation_id: Integer. Defaults to None.
        keyword_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        content_type_id: Integer. Defaults to None.
        only_ids: Boolean. Defaults to False. Determines whether to
            return edits or only edit ids.
    Returns:
        If only_ids is False and content_ids is None:
            Dictionary of the form
            {edit_id1: edit_dict1, edit_id2: edit_dict2, ...}.
        If only_ids is True and content_ids is None:
            List of integers.
        If only_ids is True and content_ids is not None:
            Dictionary of the form
            {content_id1: List of edit IDs,
             content_id2: List of edit IDS, ...}
    """
    if content_id is not None:
        edit_ids = redis.lrange("content:" + str(content_id), 0, -1)
    elif content_ids is not None:
        with redis.pipeline() as pipe:
            for content_id in content_ids:
                pipe.lrange("content:" + str(content_id), 0, -1)
            edit_id_lists = pipe.execute()
            if only_ids:
                return {content_id: edit_ids for content_id, edit_ids
                        in zip(content_ids, edit_id_lists)}
            else:
                raise InputError("Invalid arguments!")
    elif user_id is not None:
        edit_ids = redis.lrange("user:" + str(user_id), 0, -1)
    elif voter_id is not None:
        edit_ids = redis.lrange("voter:" + str(voter_id), 0, -1)
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


def get_votes(content_id):
    """
    Args:
        content_id: Integer.
    Returns:
        Dictionary of the form
        {edit_id1: vote_dict1, edit_id2: vote_dict2, ...}.
    """
    edits_ids = redis.lrange("content:" + str(content_id), 0, -1)
    with redis.pipeline() as pipe:
        for edit_id in edits_ids:
            pipe.hgetall("votes:" + str(edit_id))
        votes = pipe.execute()

    return {edit_id:vote for edit_id, vote in zip(edits_ids, votes)}


def get_validation_data(edit_id):
    """
    Args:
        edit_id: Integer.
    Returns:
        Dictionary of the form {"edit": edit_dict, "vote": vote_dict}.
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
    voters = get_validation_data(edit_id)["votes"]
    with redis.pipeline() as pipe:
        pipe.lrem("user:" + str(user_id), 0, edit_id)
        pipe.lrem("voter:" + str(user_id), 0, edit_id)
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
        for voter_id in voters:
            pipe.lrem("voter:" + str(voter_id), 0, edit_id)
        pipe.execute()
