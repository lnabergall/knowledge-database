"""
Content Piece View API
"""

from datetime import datetime

from .content import Content
from .edit import Edit
from .vote import AuthorVote


class ContentView:

    def __init__(self, content_id=None, first_author_name=None, 
                 first_author_id=None, content_type=None, name=None,
                 alternate_names=None, text=None, keywords=None, 
                 citations=None):
        """
        Args:
            content_id: Integer.
            first_author_name: String.
            first_author_id: Integer.
            content_type: String.
            name: String.
            alternate_names: List of Strings.
            text: String.
            keywords: List of Strings.
            citations: List of Strings.
        """
        if content_id is not None:
            try:
                content = Content(content_id=content_id)
            except:
                raise
            else:
                self.content = content.json_ready
        else:
            try:
                content = Content(first_author_name=first_author_name,
                                  first_author_id=first_author_id, 
                                  content_type=content_type, name=name,
                                  alternate_names=alternate_names, text=text,
                                  keywords=keywords, citations=citations)
            except:
                raise
            else:
                self.content = content.json_ready

    @classmethod
    def user_content(cls, user_id, page_num=0):
        try:
            content = Content.bulk_retrieve(user_id=user_id, page_num=page_num)
            content_ids = [piece.content_id for piece in content]
            edit_existence_dict = Edit.edits_validating(content_ids)
            votes_needed = AuthorVote.votes_needed(
                user_id, content_ids=content_ids)
        except:
            raise
        else:
            content = [piece.json_ready for piece in content]
            for i in range(len(content)):
                content_id = content[i]["content_id"]
                content[i]["edits_validating"] = edit_existence_dict[content_id]
                content[i]["votes_needed"] = votes_needed[content_id]
            return content

    @classmethod
    def get_content_types(cls):
        try:
            content_types = Content.get_content_types()
        except:
            raise
        else:
            return content_types

    @classmethod
    def search(cls, query, page_num=1):
        try:
            results = Content.search(query, page_num=page_num)
        except:
            raise
        else:
            return results

    @classmethod
    def filter_by(cls, content_part, part_string, page_num=1):
        try:
            results = Content.filter_by(content_part, part_string, 
                                        page_num=page_num)
        except:
            raise
        else:
            return results

    @classmethod
    def autocomplete(cls, content_part, query):
        try:
            completions = Content.autocomplete(content_part, query)
        except:
            raise
        else:
            return completions

    @classmethod
    def recent_activity(cls, user_id, page_num=1):
        try:
            content_ids = Content.bulk_retrieve(user_id=user_id, ids_only=True)
            validating_edits = Edit.bulk_retrieve(
                "validating", content_ids=content_ids)
            accepted_edits = Edit.bulk_retrieve(
                "accepted", content_ids=content_ids)
            rejected_edits = Edit.bulk_retrieve(
                "rejected", content_ids=content_ids)
            user_rejected_edits = Edit.bulk_retrieve(
                "rejected", user_id=user_id)
        except:
            raise
        else:
            user_rejected_edits = [edit for edit in user_rejected_edits
                                   if edit.content_id not in content_ids]

        def ordering_func(edit):
            if edit is None:
                return datetime.min
            if edit.validation_status == "validating":
                return edit.timestamp
            else:
                return edit.validated_timestamp

        # Use ordering function to sort edits 
        # in descending chronological order.
        validating_edits.reverse()
        accepted_edits.reverse()
        rejected_edits.reverse()
        user_rejected_edits.reverse()
        descending_edits = []
        while True:
            try:
                validating_edit = validating_edits[-1]
            except IndexError:
                validating_edit = None
            try:
                accepted_edit = accepted_edits[-1]
            except IndexError:
                accepted_edit = None
            try:
                rejected_edit = rejected_edits[-1]
            except IndexError:
                rejected_edit = None
            try:
                user_rejected_edit = user_rejected_edits[-1]
            except IndexError:
                user_rejected_edit = None
            if (validating_edit is None and accepted_edit is None
                    and rejected_edit is None and user_rejected_edit is None):
                break
            next_oldest_edit = max(validating_edit, accepted_edit, 
                                   rejected_edit, user_rejected_edit, 
                                   key=ordering_func)
            if next_oldest_edit.validation_status == "validating":
                validating_edits.pop()
            elif next_oldest_edit.validation_status == "accepted":
                accepted_edits.pop()
            else:
                if next_oldest_edit.content_id in content_ids:
                    rejected_edits.pop()
                else:
                    user_rejected_edits.pop()
            descending_edits.append(next_oldest_edit)

        # Now serialize and remove excess data.
        for i in range(len(descending_edits)):
            edit = descending_edits[i].json_ready
            descending_edits[i] = {
                "content_id": edit["content_id"],
                "edit_id": edit["edit_id"],
                "timestamp": edit["timestamp"],
                "validated_timestamp": edit["validated_timestamp"],
                "validation_status": edit["validation_status"],
                "content_part": edit["content_part"],
                "author_type": edit["author_type"],
                "author": edit["author"],
            }
        return descending_edits

    @classmethod
    def validation_data(cls):
        pass
