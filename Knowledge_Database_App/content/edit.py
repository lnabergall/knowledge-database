"""
Content Edit API
"""

import re
from datetime import datetime

from Knowledge_Database_App import email
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from . import redis
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
        elif edit is not None:
            pass
        else:
            pass

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
        try:
            validation_data = redis.get_validation_data(edit_id)
        except:
            raise
        else:
            return validation_data["edit"]

    def _transfer(self, edit):
        if self.validation_status == "pending":
            pass
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
    def bulk_retrieve_from_storage(cls):
        pass

    def start_vote(self):   # sync
        pass

    def save(self):     # sync, called by start_vote
        pass

    @celery_app.task(name="edit.validate")
    def validate(self): # async task, scheduled by start_vote, called each vote
        pass

    def accept(self):   # sync, called by validate
        pass

    def reject(self):   # sync, called by validate
        pass

    @celery_app.task(name="edit._notify")
    def _notify(self):
        pass

    @property
    def json_ready(self):
        pass


def is_ip_address(string):
    result = re.fullmatch(r"(^(?:[0-9]{1,3}\.){3}[0-9]{1,3})|"
                          r"^(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}$", string)
    return bool(result)
