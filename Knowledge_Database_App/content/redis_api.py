"""
Storage for edits and votes active in the validation process.
Uses redis.

Classes:

    CustomStrictRedis

Functions:

    store_edit, store_vote, store_confirm, get_confirm_info,
    expire_confirm, store_report, get_reports, get_admin_assignments, 
    delete_report, get_edits, get_votes, get_validation_data, 
    delete_validation_data
"""

import dateutil.parser as dateparse
from redis import StrictRedis, WatchError
from redis.client import BasePipeline

from Knowledge_Database_App.storage.exceptions import InputError
from .exceptions import DuplicateVoteError, MissingKeyError


def decode_response(response):
    response_type = type(response)
    if response_type != bool:
        try:
            response = int(response)
        except (TypeError, ValueError):  
            try:
                if response_type == bytes:
                    response = response.decode("utf-8")
                    try:
                        response_parsed = dateparse.parse(response)
                    except ValueError:
                        pass
                    else:
                        if str(response_parsed) == response:
                            response = response_parsed
                elif response_type == list:
                    for i in range(len(response)):
                        response[i] = decode_response(response[i])
                elif response_type == dict:
                    keys = list(response.keys())
                    for key in keys:
                        decoded_value = decode_response(response[key])
                        decoded_key = decode_response(key)
                        response[decoded_key] = decoded_value
                        del response[key]
            except (TypeError, ValueError, AttributeError):
                raise NotImplementedError   # Programming error

    return response


class CustomStrictRedis(StrictRedis):
    """
    Customized StrictRedis superclass with type interpretation 
    and decoding via a modified version of the parse_response method.
    """

    def parse_response(self, connection, command_name, **options):
        response = super().parse_response(connection, command_name, **options)
        return decode_response(response)

    def pipeline(self, transaction=True, shard_hint=None):
        return CustomStrictPipeline(
            self.connection_pool, 
            self.response_callbacks, 
            transaction, 
            shard_hint
        )


class CustomBasePipeline(BasePipeline):
    """
    Customized BasePipeline superclass with type interpretation 
    and decoding.
    """

    def parse_response(self, connection, command_name, **options):
        result = CustomStrictRedis.parse_response(
            self, connection, command_name, **options)
        if command_name in self.UNWATCH_COMMANDS:
            self.watching = False
        elif command_name == 'WATCH':
            self.watching = True
        return result


class CustomStrictPipeline(CustomBasePipeline, CustomStrictRedis):
    """Pipeline for the CustomStrictRedis class."""
    pass


redis = CustomStrictRedis()


def _setup_id_base():
    # Only call once.
    redis.setnx("next_edit_id", 1)
    redis.setnx("next_report_id", 1)


def _reset_db():
    redis.flushdb()
    _setup_id_base()


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
                edit_id = int(pipe.get("next_edit_id"))
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
        raise MissingKeyError(key=edit_id, message="Edit " + str(edit_id)
                              + " not found. Either this edit does not exist "
                              "or it has already been accepted.")
    if edit_id in user_votes:
        raise DuplicateVoteError(message="You have already voted on this edit. "
                                 "You may only vote once.")
    else:
        with redis.pipeline() as pipe:
            pipe.hsetnx("votes:" + str(edit_id),
                        voter_id, vote_and_time)
            pipe.lpush("voter:" + str(voter_id), edit_id)
            response_list = pipe.execute()
        if response_list[0] == 0:
            raise DuplicateVoteError(message="You have already voted on "
                                     "this edit. You may only vote once.")


def store_confirm(email, confirmation_id_hash, expire_timestamp):
    redis.hset("user_email:" + str(email), confirmation_id_hash,
               str(expire_timestamp))


def get_confirm_info(email):
    confirmation_dict = redis.hgetall("user_email:" + str(email))
    return confirmation_dict


def expire_confirm(email):
    redis.delete("user_email:" + str(email))


def store_report(content_id, report_text, report_type, admin_id, 
                 timestamp, author_type, author_id=None):
    """
    Args:
        content_id: Integer. 
        report_text: String.
        report_type: String, expects 'content' or 'authors'.
        admin_id: Integer.
        timestamp: Datetime.
        author_type: String, expects 'U' or IP address.
        author_id: Integer. Defaults to None.
    Returns:
        Report ID integer.
    """
    with redis.pipeline() as pipe:
        # Get a unique report id and increment it for the next report
        while True:
            try:
                pipe.watch("next_report_id")
                report_id = int(pipe.get("next_report_id"))
                next_report_id = report_id + 1
                pipe.multi()
                pipe.set("next_report_id", next_report_id).execute()
            except WatchError:
                continue
            except:
                raise
            else:
                break
        # Now store the report with the report id
        if author_id is not None:
            pipe.lpush("user_reports:" + str(author_id), report_id)
        pipe.lpush("admin_reports:" + str(admin_id), report_id)
        pipe.lpush("content_reports:" + str(content_id), report_id)
        pipe.hmset("report:" + str(report_id), {
            "report_id": report_id,
            "content_id": content_id,
            "report_text": report_text,
            "report_type": report_type,
            "admin_id": admin_id,
            "timestamp": timestamp,
            "author_type": author_type,
        })
        if author_id is not None:
            pipe.hset("report:" + str(report_id), "author_id", author_id)
        pipe.execute()

    return report_id


def get_reports(report_id=None, content_id=None, user_id=None, admin_id=None):
    """
    Args:
        report_id: Integer. Defaults to None.
        content_id: Integer. Defaults to None.
        user_id: Integer. Defaults to None.
        admin_id: Integer. Defaults to None.
    Returns:
        Dictionary of the form
        {
            "report_id": int,
            "content_id": int,
            "report_text": string,
            "report_type": string,
            "admin_id": int,
            "timestamp": string,
            "author_type": string,
            "author_id": int
        }
    """
    if report_id is not None:
        report_dict = redis.hgetall("report:" + str(report_id))
        return report_dict
    elif content_id is not None:
        report_ids = redis.lrange("content_reports:" + str(content_id), 0, -1)
    elif user_id is not None:
        report_ids = redis.lrange("user_reports:" + str(user_id), 0, -1)
    elif admin_id is not None:
        report_ids = redis.lrange("admin_reports:" + str(admin_id), 0, -1)
    else:
        raise InputError("Missing arguments!")
    with redis.pipeline() as pipe:
            for report_id in report_ids:
                pipe.hgetall("report:" + str(report_id))
            report_dicts = pipe.execute()

    return report_dicts


def get_admin_assignments(admin_ids):
    with redis.pipeline() as pipe:
        for admin_id in admin_ids:
            pipe.lrange("admin_reports:" + str(admin_id), 0, -1)
        admin_assignments = pipe.execute()
        if len(admin_ids) != len(admin_assignments):
            raise RuntimeError      # If this raises on testing will need to recode

    return {admin_ids[i]: admin_assignments[i] for i in range(len(admin_ids))}


def delete_report(report_id):
    report_dict = get_reports(report_id=report_id)
    content_id = report_dict["content_id"]
    if report_dict["author_type"] == "U":
        user_id = report_dict["author_id"]
    admin_id = report_dict["admin_id"]
    with redis.pipeline() as pipe:
        pipe.lrem("content_reports:" + str(content_id), 0, report_id)
        if report_dict["author_type"] == "U":
            pipe.lrem("user_reports:" + str(user_id), 0, report_id)
        pipe.lrem("admin_reports:" + str(admin_id), 0, report_id)
        pipe.delete("report:" + str(report_id))
        pipe.execute()


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
