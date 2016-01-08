"""
Content Edit API
"""

import re
from datetime import datetime, timedelta

from Knowledge_Database_App import email
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from . import redis
from . import edit_diff as diff
from .celery import celery_app
from .content import Content, Name, Text, UserData


class Edit:

    storage_handler = orm.StorageHandler()

    edit_id = None              # Integer.
    content_id = None           # Integer.
    timestamp = None            # Datetime.
    validated_timestamp = None  # Datetime.
    validation_status = None    # String, 'pending', 'accepted', or 'rejected'.
    edit_text = None            # String.
    edit_rationale = None       # String.
    content_part = None         # String.
    part_id = None              # Integer.
    author_type = None          # String.
    author = None               # Integer.

    def __init__(self, edit_id=None, validation_status=None, content_id=None,
                 edit_text=None, edit_rationale=None, content_part=None,
                 part_id=None, original_part_text=None, author_type=None,
                 author_id=None, edit=None):
        """
        Args:
            edit_id: Integer. Defaults to None.
            validation_status: String, accepts 'pending', 'accepted',
                or 'rejected'. Defaults to None.
            content_id: Integer. Defaults to None.
            edit_text: String. Defaults to None.
            edit_rationale: String. Defaults to None.
            content_part: String, expects 'name', 'alternate_name',
                'content_type', 'text', 'keyword', or 'citation'.
                Defaults to None.
            part_id: Integer. Defaults to None.
            original_part_text: String. Defaults to None.
            author_type: String, expects 'U' or an IP address.
                Defaults to None.
            author_id: Integer. Defaults to None.
            edit: AcceptedEdit or RejectedEdit object.
        """
        if (self.validation_status is not None and
                self.validation_status != "accepted" and
                self.validation_status != "rejected" and
                self.validation_status != "pending") or (
                author_type is not None and
                not is_ip_address(author_type) and author_type != "U"):
            raise action.InputError("Invalid argument!")

        self.validation_status = validation_status
        if edit_id is not None and self.validation_status is not None:
            if self.validation_status == "pending":
                edit = self._retrieve_from_redis(edit_id)
                self._transfer(edit)
            else:
                edit = self._retrieve_from_storage(edit_id)
                self._transfer(edit)
        elif edit is not None and self.validation_status is not None:
            self._transfer(edit)
        else:
            if (not content_id or not edit_text or not content_part or
                    not part_id or original_part_text is None or not author_type):
                self.validation_status = "pending"
                self.timestamp = datetime.utcnow()
                self.author_type = author_type
                if self.author_type == "U":
                    self.author = UserData(user_id=author_id)
                self.content_id = content_id
                self.edit_text = diff.compute_diff(original_part_text, edit_text)
                self.edit_rationale = edit_rationale
                self.content_part = content_part
                self.part_id = part_id
                self.start_vote()

    def _retrieve_from_storage(self, edit_id):
        """
        Args:
            edit_id: Integer.
        Returns:
            AcceptedEdit or RejectedEdit object.
        """
        if self.validation_status == "accepted":
            try:
                edit = self.storage_handler.call(
                    select.get_accepted_edits, edit_id)
            except:
                raise
        elif self.validation_status == "rejected":
            try:
                edit = self.storage_handler.call(
                    select.get_rejected_edits, edit_id)
            except:
                raise
        else:
            raise action.InputError("Invalid argument!")

        return edit

    def _retrieve_from_redis(self, edit_id):
        if self.validation_status != "pending":
            return NotImplemented
        try:
            validation_data = redis.get_validation_data(edit_id)
        except:
            raise
        else:
            return validation_data["edit"]

    def _transfer(self, edit):
        if self.validation_status == "pending":
            self.edit_id = edit["edit_id"]
            self.content_id = edit["content_id"]
            self.edit_text = edit["edit_text"]
            self.edit_rationale = (edit["edit_rationale"]
                                   if edit["edit_rationale"] else None)
            self.content_part = edit["content_part"]
            self.part_id = edit["part_id"]
            self.timestamp = edit["timestamp"]
            self.author_type = edit["author_type"]
            if self.author_type == "U":
                self.author = UserData(user_id=edit.author.user_id)
        else:
            self.content_id = edit.content_id
            self.edit_id = edit.edit_id
            self.edit_text = edit.edit_text
            self.edit_rationale = edit.edit_rationale
            self.content_part = edit.content_part
            self.timestamp = edit.timestamp
            if self.validation_status == "accepted":
                self.validated_timestamp = edit.acc_timestamp
            else:
                self.validated_timestamp = edit.rej_timestamp
            self.author_type = edit.author_type
            if self.author_type == "U":
                self.author = UserData(user_id=edit.author.user_id,
                                       user_name=edit.author.user_name)
            if edit.name_id:
                self.part_id = edit.name_id
            elif edit.text_id:
                self.part_id = edit.text_id
            elif edit.content_type_id:
                self.part_id = edit.content_type_id
            elif edit.keyword_id:
                self.part_id = edit.keyword_id
            else:
                self.part_id = edit.citation_id

    @classmethod
    def bulk_retrieve(cls, validation_status, user_id=None,
                      content_id=None, text_id=None, name_id=None,
                      page_num=1):
        if user_id is not None:
            if validation_status == "pending":
                try:
                    edits = redis.get_edits(user_id=user_id).values()
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = self.storage_handler.call(select.get_accepted_edits,
                                                      user_id=user_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = self.storage_handler.call(select.get_rejected_edits,
                                                      user_id=user_id)
                except:
                    raise
            else:
                raise action.InputError("Invalid arguments!")
        elif content_id is not None:
            if validation_status == "pending":
                try:
                    edits = redis.get_edits(content_id=content_id).values()
                except:
                    raise
                else:
                    return [Edit(edit=edit, validation_status=validation_status)
                            for edit in edits][10*(page_num-1) : 10*page_num]
            elif validation_status == "accepted":
                try:
                    edits = self.storage_handler.call(select.get_accepted_edits,
                                                      content_id=content_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = self.storage_handler.call(select.get_rejected_edits,
                                                      content_id=content_id)
                except:
                    raise
            else:
                raise action.InputError("Invalid arguments!")
        elif text_id is not None:
            if validation_status == "accepted":
                try:
                    edits = self.storage_handler.call(select.get_accepted_edits,
                                                      text_id=text_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = self.storage_handler.call(select.get_rejected_edits,
                                                      text_id=text_id)
                except:
                    raise
            else:
                raise action.InputError("Invalid arguments!")
        elif name_id is not None:
            if validation_status == "accepted":
                try:
                    edits = self.storage_handler.call(select.get_accepted_edits,
                                                      name_id=text_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = self.storage_handler.call(select.get_rejected_edits,
                                                      name_id=text_id)
                except:
                    raise
            else:
                raise action.InputError("Invalid arguments!")
        else:
            return []

        return [Edit(edit=edit, validation_status=validation_status)
                for edit in edits][10*(page_num-1) : 10*page_num]

    def start_vote(self):
        if not self.validate():
            self.save()
            self.validate.apply_async(eta=self.timestamp+timedelta(days=5))
            self.validate.apply_async(eta=self.timestamp+timedelta(days=10))
            self._notify.apply_async()
            self._notify.apply_async(eta=self.timestamp+timedelta(days=4))
            self._notify.apply_async(eta=self.timestamp+timedelta(days=8))

    def save(self):
        try:
            edit_id = redis.store_edit(
                self.content_id, self.edit_text, self.edit_rationale,
                self.content_part, self.part_id, self.timestamp,
                self.author_type, self.author.user_id if self.author else None)
        except:
            raise
        else:
            self.edit_id = edit_id

    @celery_app.task(name="edit.validate")
    def validate(self):  # async task, called each vote
        try:
            author_count = self.storage_handler.call(select.get_author_count,
                                                     self.content_id)
        except:
            raise
        try:
            votes = redis.get_validation_data(self.edit_id)["votes"]
        except:
            raise
        vote_count = len(votes)
        for_vote_count = len([True for vote in votes.items()
                              if vote[1] == "Y"])
        against_vote_count = vote_count - for_vote_count
        days_since_creation = (datetime.utcnow() - self.timestamp).days
        if not votes:
            if author_count == 0 or days_since_creation >= 10:
                self._accept(votes)
                return
        else:
            if ((author_count == vote_count and
                    for_vote_count/vote_count >= 0.5) or
                    (vote_count >= author_count/2 and
                     for_vote_count/vote_count >= 0.75) or
                    (days_since_creation >= 5 and vote_count >= 2 and
                     for_vote_count/vote_count >= .66) or
                    (days_since_creation >= 10 and
                     for_vote_count/vote_count >= 0.5)):
                self._accept(votes)
                return

        if against_vote_count >= author_count/2 or days_since_creation >= 10:
            self._reject()

    def _accept(self, votes):
        accepted_timestamp = datetime.utcnow()
        vote_string = NotImplemented    # Vote API
        try:
            self.storage_handler.call(
                action.store_accepted_edit,
                self.edit_text,
                self.edit_rationale,
                self.content_part,
                self.part_id,
                self.content_id,
                vote_string,
                votes.keys(),
                self.timestamp,
                accepted_timestamp,
                self.author_type,
                self.author.user_id if self.author else None
            )
        except:
            raise
        self.validation_status = "accepted"
        self.validated_timestamp = accepted_timestamp
        try:
            redis.delete_validation_data(
                self.content_id, self.edit_id,
                self.author.user_id if self.author else None)
        except:
            raise
        self._notify.apply_async()

    def _reject(self, votes):
        rejected_timestamp = datetime.utcnow()
        vote_string = NotImplemented    # Vote API
        try:
            self.storage_handler.call(
                action.store_rejected_edit,
                self.edit_text,
                self.edit_rationale,
                self.content_part,
                self.part_id,
                self.content_id,
                vote_string,
                votes.keys(),
                self.timestamp,
                rejected_timestamp,
                self.author_type,
                self.author.user_id if self.author else None
            )
        except:
            raise
        self.validation_status = "rejected"
        self.validated_timestamp = rejected_timestamp
        try:
            redis.delete_validation_data(
                self.content_id, self.edit_id,
                self.author.user_id if self.author else None)
        except:
            raise
        self._notify.apply_async()

    @celery_app.task(name="edit._notify")
    def _notify(self):
        pass

    @property
    def json_ready(self):
        return {
            "content_id": self.content_id,
            "edit_id": self.edit_id,
            "timestamp": (str(self.timestamp)
                          if self.timestamp is not None else None),
            "validated_timestamp": (str(self.validated_timestamp)
                                    if self.validated_timestamp is not None
                                    else None),
            "validation_status": self.validation_status,
            "edit_text": self.edit_text,
            "edit_rationale": self.edit_rationale,
            "content_part": self.content_part,
            "part_id": self.part_id,
            "author_type": self.author_type,
            "author": (self.author.json_ready
                       if self.author is not None else None),
        }


def is_ip_address(string):
    result = re.fullmatch(r"(^(?:[0-9]{1,3}\.){3}[0-9]{1,3})|"
                          r"^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$", string)
    return bool(result)
