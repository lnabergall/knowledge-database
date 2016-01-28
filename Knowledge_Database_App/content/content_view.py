"""
Content Piece View API
"""

from datetime import datetime

from .content import Content, Name, UserData
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
        # Retrieve activity info
        try:
            content_ids = Content.bulk_retrieve(user_id=user_id, ids_only=True)
            content_names = Name.bulk_retrieve(content_ids)
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
                "content_name": content_names[edit["content_id"]].name,
                "edit_id": edit["edit_id"],
                "timestamp": edit["timestamp"],
                "validated_timestamp": edit["validated_timestamp"],
                "validation_status": edit["validation_status"],
                "content_part": edit["content_part"],
                "author_type": edit["author_type"],
                "author": edit["author"],
            }
        return descending_edits[20*(page_num-1) : 20*page_num]

    @classmethod
    def validation_data(cls, user_id, content_id, validating_page_num=1,
                        closed_page_num=1):
        # Retrieve author names and edits
        try:
            authors = UserData.bulk_retrieve(content_id=content_id)
            validating_edits, val_edit_count = Edit.bulk_retrieve(
                "validating", content_id=content_id, return_count=True)
            accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                "accepted", content_id=content_id,
                page_num=closed_page_num, return_count=True)
            rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                "rejected", content_id=content_id,
                page_num=closed_page_num, return_count=True)
            val_edit_votes = AuthorVote.bulk_retrieve(
                "in-progress", content_id=content_id,
                validation_status="validating")
            acc_edit_votes = AuthorVote.bulk_retrieve(
                "ended", content_id=content_id,
                validation_status="accepted")
            rej_edit_votes = AuthorVote.bulk_retrieve(
                "ended", content_id=content_id,
                validation_status="rejected")
            votes_needed = AuthorVote.votes_needed(
                user_id, content_ids=[content_id])
        except:
            raise
        else:
            # Pair votes to edits
            validating_edits = [edit.json_ready for edit in validating_edits]
            accepted_edits = [edit.json_ready for edit in accepted_edits]
            rejected_edits = [edit.json_ready for edit in rejected_edits]
            for i in range(len(validating_edits)):
                del validating_edits[i]["start_timestamp"]
                del validating_edits[i]["edit_text"]
                del validating_edits[i]["applied_edit_text"]
                votes = val_edit_votes[validating_edits[i]["edit_id"]]
                for_count = 0
                against_count = 0
                for vote in votes:
                    if vote.vote == "Y":
                        for_count += 1
                    else:
                        against_count += 1
                validating_edits[i]["vote"] = {
                    "for_count": for_count,
                    "against_count": against_count,
                    "close_timestamp": votes[0].close_timestamp,
                }
            validating_edits = validating_edits[10*(validating_page_num-1)
                                                : 10*validating_page_num]
            for i in range(len(accepted_edits)):
                del accepted_edits[i]["start_timestamp"]
                del accepted_edits[i]["edit_text"]
                del accepted_edits[i]["applied_edit_text"]
                votes = acc_edit_votes[accepted_edits[i]["edit_id"]]
                for_count = 0
                against_count = 0
                for vote in votes:
                    if vote.vote == "Y":
                        for_count += 1
                    else:
                        against_count += 1
                accepted_edits[i]["vote"] = {
                    "for_count": for_count,
                    "against_count": against_count,
                    "close_timestamp": votes[0].close_timestamp,
                }
            for i in range(len(rejected_edits)):
                del rejected_edits[i]["start_timestamp"]
                del rejected_edits[i]["edit_text"]
                del rejected_edits[i]["applied_edit_text"]
                votes = rej_edit_votes[rejected_edits[i]["edit_id"]]
                for_count = 0
                against_count = 0
                for vote in votes:
                    if vote.vote == "Y":
                        for_count += 1
                    else:
                        against_count += 1
                rejected_edits[i]["vote"] = {
                    "for_count": for_count,
                    "against_count": against_count,
                    "close_timestamp": votes[0].close_timestamp,
                }

            def ordering_func(edit):
                if edit is None:
                    return datetime.min
                else:
                    return edit["validated_timestamp"]

            # Use ordering function to sort closed edits
            # in descending chronological order.
            closed_edits = []
            accepted_edits.reverse()
            rejected_edits.reverse()
            while True:
                try:
                    accepted_edit = accepted_edits[-1]
                except IndexError:
                    accepted_edit = None
                try:
                    rejected_edit = rejected_edits[-1]
                except IndexError:
                    rejected_edit = None
                if accepted_edit is None and rejected_edit is None:
                    break
                next_oldest_edit = max(accepted_edit, rejected_edit,
                                       key=ordering_func)
                if next_oldest_edit["validation_status"] == "accepted":
                    accepted_edits.pop()
                elif next_oldest_edit["validation_status"] == "rejected":
                    rejected_edits.pop()
                closed_edits.append(next_oldest_edit)

            return {
                "authors": [author.json_ready for author in authors],
                "validating_edit_count": val_edit_count,
                "validating_edits": validating_edits,
                "votes_needed": votes_needed[content_id],
                "closed_edit_count": acc_edit_count + rej_edit_count,
                "closed_edits": closed_edits,
            }
