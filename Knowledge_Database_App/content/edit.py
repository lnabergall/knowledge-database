"""
Content Edit API

Classes:

    Edit

Exceptions:

    DuplicateError

Functions:

    is_ip_address
"""

import re
from datetime import datetime, timedelta

from Knowledge_Database_App import _email as mail
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from . import redis
from . import edit_diff as diff
from .celery import celery_app
from .content import Content, Name, UserData


class DuplicateError(Exception):
    """Exception raised when a content part is a duplicate of another."""


class Edit:
    """
    Attributes:
        edit_id: Integer. Defaults to None.
        content_id: Integer. Defaults to None.
        timestamp: Datetime. Defaults to None.
        start_timestamp: Datetime. Defaults to None.
        validated_timestamp: Datetime. Defaults to None.
        validation_status: String, expects 'pending', 'validating',
            'accepted', or 'rejected'. Defaults to None.
        original_part_text: String. Defaults to None.
        edit_text: String. Defaults to None.
        applied_edit_text: String. Defaults to None.
        edit_rationale: String. Defaults to None.
        content_part: String, expects 'text', 'name', 'alternate_name',
            'keyword', 'content_type', or 'citation'.
        part_id: Integer.
        author_type: String, 'admin' or 'standard'.
        author: UserData object. Defaults to None.

    Properties:
        json_ready: Dictionary.
        conflict: Boolean, indicates whether this edit likely semantically
            conflicts with another edit.

    Instance Methods:
        _retrieve_from_storage, _retrieve_from_redis, _transfer,
        start_vote, save, validate, _accept, _compute_merging_diff,
        apply_edit, reject, _notify

    Class Methods:
        bulk_retrieve
    """

    storage_handler = orm.StorageHandler()

    edit_id = None              # Integer.
    content_id = None           # Integer.
    timestamp = None            # Datetime.
    start_timestamp = None      # Datetime.
    validated_timestamp = None  # Datetime.
    validation_status = None    # String, 'pending', 'validating',
                                # 'accepted', or 'rejected'.
    original_part_text = None   # String.
    edit_text = None            # String.
    applied_edit_text = None    # String.
    edit_rationale = None       # String.
    content_part = None         # String.
    part_id = None              # Integer.
    author_type = None          # String.
    author = None               # UserData object.

    def __init__(self, edit_id=None, validation_status=None, content_id=None,
                 edit_text=None, edit_rationale=None, content_part=None,
                 part_id=None, original_part_text=None, author_type=None,
                 author_id=None, start_timestamp=None, edit_object=None):
        """
        Args:
            edit_id: Integer. Defaults to None.
            validation_status: String, accepts 'validating', 'accepted',
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
            start_timestamp: Datetime. Defaults to None
            edit: AcceptedEdit or RejectedEdit object.
        """
        if (self.validation_status is not None and
                self.validation_status != "accepted" and
                self.validation_status != "rejected" and
                self.validation_status != "validating") or (
                author_type is not None and
                not is_ip_address(author_type) and author_type != "U"):
            raise select.InputError("Invalid argument!")

        self.validation_status = validation_status
        if edit_id is not None and self.validation_status is not None:
            if self.validation_status == "validating":
                try:
                    stored_edit = self._retrieve_from_redis(edit_id)
                except:
                    raise
                else:
                    if stored_edit is None:
                        stored_edit = self._retrieve_from_storage(
                            redis_edit_id=edit_id)
                self._transfer(stored_edit)
            else:
                stored_edit = self._retrieve_from_storage(edit_id=edit_id)
                self._transfer(stored_edit)
        elif edit_object is not None and self.validation_status is not None:
            self._transfer(edit_object)
        else:
            if (not content_id or edit_text is None or not content_part or
                    original_part_text is None or not author_type or
                    not start_timestamp):
                raise select.InputError("Required arguments not provided!")
            if not Content.check_uniqueness(content_id, edit_text, content_part):
                raise DuplicateError("Edit duplicates another content part!")
            self.validation_status = "pending"
            self.timestamp = datetime.utcnow()
            self.start_timestamp = start_timestamp
            self.author_type = author_type
            if self.author_type == "U":
                self.author = UserData(user_id=author_id)
            self.content_id = content_id
            self.content_part = content_part
            self.part_id = part_id
            self.original_part_text = original_part_text
            self.edit_text = diff.compute_diff(original_part_text, edit_text)
            self.edit_rationale = edit_rationale
            self.start_vote()

    def _retrieve_from_storage(self, edit_id=None, redis_edit_id=None):
        """
        Args:
            edit_id: Integer.
        Returns:
            AcceptedEdit or RejectedEdit object.
        """
        if edit_id is not None:
            if self.validation_status == "accepted":
                if edit_id is not None:
                    try:
                        edit = self.storage_handler.call(
                            select.get_accepted_edits, edit_id=edit_id)
                    except:
                        raise
            elif self.validation_status == "rejected":

                    try:
                        edit = self.storage_handler.call(
                            select.get_rejected_edits, edit_id=edit_id)
                    except:
                        raise
        elif self.validation_status == "validating" and redis_edit_id is not None:
            try:
                edit = self.storage_handler.call(
                    select.get_accepted_edits, redis_edit_id=redis_edit_id)
            except:
                try:
                    edit = self.storage_handler.call(
                        select.get_rejected_edits, redis_edit_id=redis_edit_id)
                except:
                    raise
                else:
                    self.validation_status = "rejected"
            else:
                self.validation_status = "accepted"
        else:
            raise select.InputError("Invalid argument!")

        return edit

    def _retrieve_from_redis(self, edit_id):
        """
        Args:
            edit_id: Integer.
        Returns:
            Dictionary.
        """
        if self.validation_status != "validating":
            return NotImplemented
        try:
            validation_data = redis.get_validation_data(edit_id)
        except:
            raise
        else:
            if validation_data:
                return validation_data["edit"]
            else:
                return

    def _transfer(self, edit_object):
        if self.validation_status == "validating":
            self.edit_id = edit_object["edit_id"]
            self.content_id = edit_object["content_id"]
            self.edit_text = edit_object["edit_text"]
            self.edit_rationale = (edit_object["edit_rationale"]
                                   if edit_object["edit_rationale"] else None)
            self.content_part = edit_object["content_part"]
            self.part_id = edit_object["part_id"]
            self.timestamp = edit_object["timestamp"]
            self.author_type = edit_object["author_type"]
            if self.author_type == "U":
                self.author = UserData(user_id=edit_object.author.user_id)
            self.start_timestamp = edit_object["start_timestamp"]
        else:
            self.content_id = edit_object.content_id
            self.edit_id = edit_object.edit_id
            self.edit_text = edit_object.edit_text
            self.edit_rationale = edit_object.edit_rationale
            self.content_part = edit_object.content_part
            self.start_timestamp = edit_object.start_timestamp
            self.timestamp = edit_object.timestamp
            if self.validation_status == "accepted":
                self.validated_timestamp = edit_object.acc_timestamp
                self.applied_edit_text = edit_object.applied_edit_text
            else:
                self.validated_timestamp = edit_object.rej_timestamp
            self.author_type = edit_object.author_type
            if self.author_type == "U":
                self.author = UserData(user_id=edit_object.author.user_id,
                                       user_name=edit_object.author.user_name)
            if edit_object.name_id:
                self.part_id = edit_object.name_id
            elif edit_object.text_id:
                self.part_id = edit_object.text_id
            elif edit_object.content_type_id:
                self.part_id = edit_object.content_type_id
            elif edit_object.keyword_id:
                self.part_id = edit_object.keyword_id
            else:
                self.part_id = edit_object.citation_id

    @classmethod
    def bulk_retrieve(cls, validation_status, user_id=None, content_id=None,
                      text_id=None, citation_id=None, name_id=None,
                      keyword_id=None, content_type_id=None, page_num=0,
                      ids_only=False):
        """
        Args:
            validation_status: String, expects 'validating', 'accepted',
                or 'rejected'.
            user_id: Integer. Defaults to None.
            content_id: Integer. Defaults to None.
            text_id: Integer. Defaults to None.
            citation_id: Integer. Defaults to None.
            name_id: Integer. Defaults to None.
            keyword_id: Integer. Defaults to None.
            content_type_id: Integer. Defaults to None.
            page_num: Integer. Defaults to 0.
            ids_only: Boolean. Defaults to False.
        Returns:
            If ids_only == True, returns list of Integers, otherwise returns
            list of Edits.
        """
        if user_id is not None:
            if validation_status == "validating":
                try:
                    edits = redis.get_edits(user_id=user_id).values()
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = cls.storage_handler.call(select.get_accepted_edits,
                                                      user_id=user_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = cls.storage_handler.call(select.get_rejected_edits,
                                                      user_id=user_id)
                except:
                    raise
            else:
                raise select.InputError("Invalid arguments!")
        elif citation_id is not None:
            if validation_status == "validating":
                try:
                    citation_edits = redis.get_edits(
                        citation_id=citation_id).values()
                    if content_id is not None:
                        citation_edits = set(citation_edits)
                        content_edits = set(redis.get_edits(
                            content_id=content_id).values())
                        edits = list(citation_edits & content_edits)
                    else:
                        edits = citation_edits
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = cls.storage_handler.call(
                        select.get_accepted_edits, content_id=content_id,
                        citation_id=citation_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = cls.storage_handler.call(
                        select.get_rejected_edits, content_id=content_id,
                        citation_id=citation_id)
                except:
                    raise
            else:
                raise select.InputError("Invalid arguments!")
        elif keyword_id is not None:
            if validation_status == "validating":
                try:
                    keyword_edits = redis.get_edits(
                        keyword_id=keyword_id).values()
                    if content_id is not None:
                        keyword_edits = set(keyword_edits)
                        content_edits = set(redis.get_edits(
                            content_id=content_id).values())
                        edits = list(keyword_edits & content_edits)
                    else:
                        edits = keyword_edits
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = cls.storage_handler.call(
                        select.get_accepted_edits, content_id=content_id,
                        keyword_id=keyword_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = cls.storage_handler.call(
                        select.get_rejected_edits, content_id=content_id,
                        keyword_id=keyword_id)
                except:
                    raise
            else:
                raise select.InputError("Invalid arguments!")
        elif content_type_id is not None:
            if validation_status == "validating":
                try:
                    content_type_edits = redis.get_edits(
                        content_type_id=content_type_id).values()
                    if content_id is not None:
                        content_type_edits = set(content_type_edits)
                        content_edits = set(redis.get_edits(
                            content_id=content_id).values())
                        edits = list(content_type_edits & content_edits)
                    else:
                        edits = content_type_edits
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = cls.storage_handler.call(
                        select.get_accepted_edits, content_id=content_id,
                        content_type_id=content_type_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = cls.storage_handler.call(
                        select.get_rejected_edits, content_id=content_id,
                        content_type_id=content_type_id)
                except:
                    raise
            else:
                raise select.InputError("Invalid arguments!")
        elif content_id is not None:
            if validation_status == "validating":
                try:
                    edits = redis.get_edits(content_id=content_id).values()
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = cls.storage_handler.call(select.get_accepted_edits,
                                                      content_id=content_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = cls.storage_handler.call(select.get_rejected_edits,
                                                      content_id=content_id)
                except:
                    raise
            else:
                raise select.InputError("Invalid arguments!")
        elif text_id is not None:
            if validation_status == "validating":
                try:
                    edits = redis.get_edits(text_id=text_id).values()
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = cls.storage_handler.call(select.get_accepted_edits,
                                                      text_id=text_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = cls.storage_handler.call(select.get_rejected_edits,
                                                      text_id=text_id)
                except:
                    raise
            else:
                raise select.InputError("Invalid arguments!")
        elif name_id is not None:
            if validation_status == "validating":
                try:
                    edits = redis.get_edits(name_id=name_id).values()
                except:
                    raise
            elif validation_status == "accepted":
                try:
                    edits = cls.storage_handler.call(select.get_accepted_edits,
                                                      name_id=name_id)
                except:
                    raise
            elif validation_status == "rejected":
                try:
                    edits = cls.storage_handler.call(select.get_rejected_edits,
                                                      name_id=name_id)
                except:
                    raise
            else:
                raise select.InputError("Invalid arguments!")
        else:
            return []

        edits = [Edit(edit=edit, validation_status=validation_status)
                 for edit in edits]
        if page_num != 0:
            edits = edits[10*(page_num-1) : 10*page_num]
        if ids_only:
            return [edit.edit_id for edit in edits]
        else:
            return edits

    def start_vote(self):
        """
        Saves the edit, notifies all authors of the submission of
        the edit, and schedules periodic validation and additional
        notifications.
        """
        if not self.validate():
            self.save()
            self.validate.apply_async(eta=self.timestamp+timedelta(days=5))
            self.validate.apply_async(eta=self.timestamp+timedelta(days=10))
            author_info = self.storage_handler.call(
                select.get_user_info, content_id=content_id)
            self._notify.apply_async(args=["edit_submitted"],
                kwargs={"author_info": author_info})
            self._notify.apply_async(args=["vote_reminder"],
                kwargs={"author_info": author_info, "days_remaining": 6},
                eta=self.timestamp+timedelta(days=4))
            self._notify.apply_async(args=["vote_reminder"],
                kwargs={"author_info": author_info, "days_remaining": 2},
                eta=self.timestamp+timedelta(days=8))

    def save(self):
        """
        Saves the edit to Redis for storage until validation completes.
        """
        try:
            edit_id = redis.store_edit(
                self.content_id, self.edit_text, self.edit_rationale,
                self.content_part, self.part_id, self.timestamp,
                self.start_timestamp, self.author_type,
                self.author.user_id if self.author else None)
        except:
            raise
        else:
            self.validation_status = "validating"
            self.edit_id = edit_id

    @celery_app.task(name="edit.validate")
    def validate(self):
        """
        Validates the edit based on the distribution of author votes
        and the number of days from submission.

        See the specifications for an explanation of the
        validation criteria.
        """
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
            self._reject(votes)

    def _accept(self, votes):
        """
        Updates the corresponding content part, stores the edit,
        deletes the edit from Redis, and notifies the author and other
        content authors of the edit's acceptance.
        """
        accepted_timestamp = datetime.utcnow()
        vote_string = NotImplemented    # Vote API
        self.apply_edit()
        try:
            edit_id = self.storage_handler.call(
                action.store_accepted_edit,
                self.edit_id,
                self.edit_text,
                self.applied_edit_text,
                self.edit_rationale,
                self.content_part,
                self.part_id,
                self.content_id,
                vote_string,
                votes.keys(),
                self.start_timestamp,
                self.timestamp,
                accepted_timestamp,
                self.author_type,
                self.author.user_id if self.author else None
            )
        except:
            raise
        redis_edit_id = self.edit_id
        self.edit_id = edit_id
        self.validation_status = "accepted"
        self.validated_timestamp = accepted_timestamp
        try:
            redis.delete_validation_data(
                self.content_id, redis_edit_id,
                self.author.user_id if self.author else None,
                self.part_id, self.content_part)
        except:
            raise
        try:
            author_info = self.storage_handler.call(
                select.get_user_info, content_id=content_id)
        except:
            raise
        self._notify.apply_async(args=["edit_accepted"])
        self._notify.apply_async(args=["author_acceptance"],
                                 kwargs={"author_info": author_info})

    def _compute_merging_diff(self):
        if self.content_part == "text":
            accepted_edits = Edit.bulk_retrieve(
                "accepted", text_id=self.part_id)
        elif self.content_part == "citation":
            accepted_edits = Edit.bulk_retrieve(
                "accepted", content_id=self.content_id,
                citation_id=self.part_id)
        else:
            return self.edit_text   # No merging keywords, names, content types
        prior_accepted_edits = [edit for edit in accepted_edits
            if edit.validated_timestamp < self.start_timestamp]
        if len(accepted_edits) == len(prior_accepted_edits):
            # All accepted edits already in original part text
            return self.edit_text
        else:
            conflicting_edits = [
                edit for edit in accepted_edits
                if edit not in prior_accepted_edits
                and diff.restore(edit.edit_text) != self.original_part_text
            ]
            accepted_edits_same_base = [
                edit for edit in accepted_edits
                if edit not in prior_accepted_edits
                and edit not in conflicting_edits
            ]
            if not conflicting_edits:
                if (accepted_edits_same_base[0].applied_edit_text
                        == self.edit_text):
                    return self.edit_text
                else:
                    return diff.merge([
                        accepted_edits_same_base[0].applied_edit_text,
                        self.edit_text
                    ])
            else:
                new_diff = diff.merge(
                    [prior_accepted_edits[0].applied_edit_text, self.edit_text],
                    base="first_diff")
                original_part_text = diff.restore(new_diff)
                remaining_conflicts = [edit for edit in conflicting_edits
                    if diff.restore(edit.edit_text) != original_part_text]
                if remaining_conflicts:
                    raise diff.DiffComputationError(
                        "Something went wrong, cannot compute a merge!")
                else:
                    if conflicting_edits[0].applied_edit_text == new_diff:
                        return new_diff
                    else:
                        return diff.merge(
                            [conflicting_edits[0].applied_edit_text, new_diff])

    def apply_edit(self):
        if not self.edit_text:
            new_part_text = ""
        elif (self.content_part == "keyword" or self.content_part == "name" or
                self.content_part == "alternate_name" or
                self.content_part == "content_type" or self.part_id is None):
            new_part_text = diff.restore(self.edit_text, version="edit")
        else:
            self.applied_edit_text = self._compute_merging_diff()
            new_part_text = diff.restore(self.applied_edit_text,
                                         version="edit")
        if self.part_id is None:
            if self.content_part == "alternate_name":
                new_part_text = Name(name=new_part_text,
                                     name_type="alternate_name",
                                     timestamp=self.timestamp).storage_object
            Content.update(self.content_id, self.content_part,
                           "add", self.timestamp, part_text=new_part_text)
        else:
            if new_part_text:
                Content.update(self.content_id, self.content_part, "modify",
                               self.timestamp, part_text=new_part_text,
                               part_id=self.part_id)
            else:
                Content.update(self.content_id, self.content_part,
                               "remove", self.timestamp, part_id=self.part_id)

    def _reject(self, votes):
        """
        Stores the edit, deletes the edit from Redis, and notifies
        the author and other content authors of the edit's rejection.
        """
        rejected_timestamp = datetime.utcnow()
        vote_string = NotImplemented    # Vote API
        try:
            edit_id = self.storage_handler.call(
                action.store_rejected_edit,
                self.edit_id,
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
        self.edit_id = edit_id
        self.validation_status = "rejected"
        self.validated_timestamp = rejected_timestamp
        try:
            redis.delete_validation_data(
                self.content_id, self.edit_id,
                self.author.user_id if self.author else None,
                self.part_id, self.content_part)
        except:
            raise
        try:
            author_info = self.storage_handler.call(
                select.get_user_info, content_id=content_id)
        except:
            raise
        self._notify.apply_async(args=["edit_rejected"])
        self._notify.apply_async(args=["author_rejection"],
                                 kwargs={"author_info": author_info})

    @celery_app.task(name="edit._notify")
    def _notify(self, email_type, days_remaining=None, author_info=None):
        """
        Args:
            email_type: String, accepts 'edit_submitted', 'vote_reminder',
                'edit_accepted', 'author_acceptance', 'edit_rejected', or
                'author_rejection'.
            days_remaining: Integer.
            author_info: List of Tuples of the form (user_name, email).
        """
        content_name = self.storage_handler.call(
            select.get_name, self.content_id)
        if email_type == "edit_submitted":
            if author_info is None:
                raise select.InputError("Invalid argument!")
            else:
                emails = [mail.Email(info_tuple[1], info_tuple[0],
                                       content_name,
                                       edit_text=self.edit_text)
                          for info_tuple in author_info]
                for email, info_tuple in zip(emails, author_info):
                    try:
                        mail.send_email(email, info_tuple[1])
                    except mail.EmailSendError:
                        continue
                    except:
                        raise
        elif email_type == "vote_reminder":
            if author_info is None or days_remaining is None:
                raise select.InputError("Invalid argument!")
            else:
                emails = [mail.Email(info_tuple[1], info_tuple[0],
                                     content_name,
                                     days_remaining=days_remaining,
                                     edit_text=self.edit_text)
                          for info_tuple in author_info]
                for email, info_tuple in zip(emails, author_info):
                    try:
                        mail.send_email(email, info_tuple[1])
                    except mail.EmailSendError:
                        continue
                    except:
                        raise
        elif email_type == "edit_accepted" or email_type == "edit_rejected":
            self.author.load_info()
            vote_result = True if self.validation_status == "accepted" else False
            email = mail.Email(self.author.email, self.author.user_name,
                               content_name, vote_result=vote_result)
            try:
                mail.send_email(email, self.author.email)
            except mail.EmailSendError:
                raise
        elif (email_type == "author_acceptance" or
                email_type == "author_rejection"):
            if author_info is None:
                raise select.InputError("Invalid argument!")
            else:
                vote_result = (True if self.validation_status == "accepted"
                               else False)
                emails = [mail.Email(info_tuple[1], info_tuple[0],
                                     content_name,
                                     edit_text=self.edit_text,
                                     vote_result=vote_result)
                          for info_tuple in author_info]
                for email, info_tuple in zip(emails, author_info):
                    try:
                        mail.send_email(email, info_tuple[1])
                    except mail.EmailSendError:
                        continue
                    except:
                        raise
        else:
            raise select.InputError("Invalid argument!")

    @property
    def conflict(self):
        if not self.original_part_text:
            return False
        if (self.validation_status == "accepted" or
                self.validation_status == "rejected"):
            return NotImplemented
        if self.content_part == "content_type":
            accepted_edits = Edit.bulk_retrieve(
                "accepted", content_id=self.content_id,
                content_type_id=self.part_id)
            validating_edits = Edit.bulk_retrieve(
                "validating", content_id=self.content_id,
                content_type_id=self.part_id)
            if not accepted_edits and not validating_edits:
                return False
            acc_match = any([edit for edit in accepted_edits
                if edit.validated_timestamp > self.start_timestamp and
                diff.restore(edit.applied_edit_text, version="edit")
                != diff.restore(self.edit_text, version="edit")])
            val_match = (True if len(validating_edits) > 2 or
                         (self.validation_status == "pending" and
                         len(validating_edits) == 1) else False)
            return acc_match or val_match
        elif (self.content_part == "name" or
                self.content_part == "alternate_name"):
            accepted_edits = Edit.bulk_retrieve(
                "accepted", name_id=self.part_id)
            validating_edits = Edit.bulk_retrieve(
                "validating", name_id=self.part_id)
            if not accepted_edits and not validating_edits:
                return False
            acc_match = any([edit for edit in accepted_edits
                if edit.validated_timestamp > self.start_timestamp and
                diff.restore(edit.applied_edit_text, version="edit")
                != diff.restore(self.edit_text, version="edit")])
            val_match = (True if len(validating_edits) > 2 or
                         (self.validation_status == "pending" and
                         len(validating_edits) == 1) else False)
            return acc_match or val_match
        elif self.content_part == "keyword":
            accepted_edits = Edit.bulk_retrieve(
                "accepted", content_id=self.content_id,
                keyword_id=self.part_id)
            validating_edits = Edit.bulk_retrieve(
                "validating", content_id=self.content_id,
                keyword_id=self.part_id)
            if not accepted_edits and not validating_edits:
                return False
            acc_match = any([edit for edit in accepted_edits
                if edit.validated_timestamp > self.start_timestamp and
                diff.restore(edit.applied_edit_text, version="edit")
                != diff.restore(self.edit_text, version="edit")])
            val_match = (True if len(validating_edits) > 2 or
                         (self.validation_status == "pending" and
                         len(validating_edits) == 1) else False)
            return acc_match or val_match
        elif self.content_part == "text":
            accepted_edits = Edit.bulk_retrieve(
                "accepted", text_id=self.part_id)
            validating_edits = Edit.bulk_retrieve(
                "validating", text_id=self.part_id)
        elif self.content_part == "citation":
            accepted_edits = Edit.bulk_retrieve(
                "accepted", content_id=self.content_id,
                citation_id=self.part_id)
            validating_edits = Edit.bulk_retrieve(
                "validating", content_id=self.content_id,
                citation_id=self.part_id)
        prior_accepted_edits = [edit for edit in accepted_edits
            if edit.validated_timestamp < self.start_timestamp]
        accepted_conflicting_edits = [
            edit for edit in accepted_edits
            if edit not in prior_accepted_edits
            and diff.restore(edit.edit_text) != self.original_part_text
        ]
        validating_conflicting_edits = [
            edit for edit in validating_edits
            if diff.restore(edit.edit_text) != self.original_part_text
        ]
        accepted_edits_same_base = [
            edit for edit in accepted_edits
            if edit not in prior_accepted_edits
            and edit not in accepted_conflicting_edits
        ]
        validating_edits_same_base = [
            edit for edit in validating_edits
            if edit not in validating_conflicting_edits
        ]
        new_diff = diff.merge(
                [prior_accepted_edits[0].applied_edit_text, self.edit_text],
                base="first_diff")
        original_part_text = diff.restore(new_diff)
        if not accepted_conflicting_edits:
            if accepted_edits_same_base[0].applied_edit_text == self.edit_text:
                acc_conflict = False
            else:
                acc_conflict = diff.conflict(
                    accepted_edits_same_base[0].applied_edit_text,
                    self.edit_text)
        else:
            remaining_conflicts = [edit for edit in accepted_conflicting_edits
                if diff.restore(edit.edit_text) != original_part_text]
            if remaining_conflicts:
                raise diff.DiffComputationError(
                    "Something went wrong, cannot compute a merge!")
            else:
                if accepted_conflicting_edits[0].applied_edit_text == new_diff:
                    acc_conflict = False
                else:
                    acc_conflict = diff.conflict(
                        accepted_conflicting_edits[0].applied_edit_text,
                        new_diff)
        if not validating_conflicting_edits:
            val_conflict = any([
                diff.conflict(edit.applied_edit_text, self.edit_text)
                if edit.applied_edit_text != self.edit_text else False
                for edit in validating_edits_same_base
            ])
        else:
            remaining_conflicts = [edit for edit in validating_conflicting_edits
                if diff.restore(edit.edit_text) != original_part_text]
            if remaining_conflicts:
                raise diff.DiffComputationError(
                    "Something went wrong, cannot compute a merge!")
            else:
                val_conflict = any([
                    diff.conflict(edit.applied_edit_text, new_diff)
                    if edit.applied_edit_text != new_diff else False
                    for edit in validating_conflicting_edits
                ])

        return val_conflict or acc_conflict

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
