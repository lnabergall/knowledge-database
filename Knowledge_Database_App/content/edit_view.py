"""
Content Edit View API

Classes:

    EditView
"""

from .edit import Edit


class EditView:
    """
    Attributes:
        edit: Dictionary.
        edit_object: Edit object.

    Properties:
        conflict

    Class Methods:
        bulk_retrieve
    """

    def __init__(self, edit_id=None, validation_status=None, content_id=None,
                 edit_text=None, edit_rationale=None, content_part=None,
                 part_id=None, original_part_text=None, author_type=None,
                 author_id=None, start_timestamp=None, submit=False):
        """
        Args:
            edit_id: Integer. Defaults to None.
            validation_status: String, accepts 'validating', 'accepted',
                or 'rejected'. Defaults to None.
            content_id: Integer. Defaults to None.
            edit_text: String. Defaults to None.
            edit_rationale: String. Defaults to None.
            content_part: String, accepts 'name', 'alternate_name', 'text',
                'content_type', 'keyword', or 'citation'. Defaults to None.
            part_id: Integer. Defaults to None.
            original_part_text: String. Defaults to None.
            author_type: String, accepts 'admin' or 'standard'.
                Defaults to None.
            author_id: Integer. Defaults to None.
            start_timestamp: Datetime. Defaults to None.
            submit: Boolean. Defaults to False.
        """
        if edit_id is not None:
            try:
                self.edit_object = Edit(edit_id=edit_id,
                    validation_status=validation_status)
            except:
                raise
            else:
                self.edit = self.edit_object.json_ready
        else:
            try:
                self.edit_object = Edit(validation_status=validation_status,
                    content_id=content_id, edit_text=edit_text,
                    edit_rationale=edit_rationale, content_part=content_part,
                    part_id=part_id, original_part_text=original_part_text,
                    author_type=author_type, author_id=author_id,
                    start_timestamp=start_timestamp, submit=submit)
            except:
                raise
            else:
                self.edit = self.edit_object.json_ready

    @classmethod
    def bulk_retrieve(cls, content_id=None, user_id=None, content_part=None,
                      part_id=None, page_num=1):
        """

            content_id: Integer. Defaults to None.
            user_id: Integer. Defaults to None.
            content_part: String, accepts 'text', 'name', 'alternate_name',
                'keyword', 'citation', or 'content_type'. Defaults to None.
            part_id: Integer. Defaults to None.
            page_num: Integer. Defaults to 1.
        """
        # Retrieve edits.
        if user_id is not None:
            try:
                validating_edits, val_edit_count = Edit.bulk_retrieve(
                    validation_status="validating", user_id=user_id,
                    page_num=page_num, return_count=True)
                accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                    validation_status="accepted", user_id=user_id,
                    page_num=page_num, return_count=True)
                rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                    validation_status="rejected", user_id=user_id,
                    page_num=page_num, return_count=True)
                content_names = Name.bulk_retrieve(content_ids)
            except:
                raise
            else:
                pass
        elif content_part == "text":
            try:
                validating_edits, val_edit_count = Edit.bulk_retrieve(
                    validation_status="validating", text_id=part_id,
                    page_num=page_num, return_count=True)
                accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                    validation_status="accepted", text_id=part_id,
                    page_num=page_num, return_count=True)
                rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                    validation_status="rejected", text_id=part_id,
                    page_num=page_num, return_count=True)
            except:
                raise
            else:
                pass
        elif content_part == "name" or content_part == "alternate_name":
            try:
                validating_edits, val_edit_count = Edit.bulk_retrieve(
                    validation_status="validating", name_id=part_id,
                    page_num=page_num, return_count=True)
                accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                    validation_status="accepted", name_id=part_id,
                    page_num=page_num, return_count=True)
                rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                    validation_status="rejected", name_id=part_id,
                    page_num=page_num, return_count=True)
            except:
                raise
            else:
                pass
        elif content_part == "citation":
            try:
                validating_edits, val_edit_count = Edit.bulk_retrieve(
                    validation_status="validating", citation_id=part_id,
                    page_num=page_num, return_count=True)
                accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                    validation_status="accepted", citation_id=part_id,
                    page_num=page_num, return_count=True)
                rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                    validation_status="rejected", citation_id=part_id,
                    page_num=page_num, return_count=True)
            except:
                raise
            else:
                pass
        elif content_part == "keyword":
            try:
                validating_edits, val_edit_count = Edit.bulk_retrieve(
                    validation_status="validating", keyword_id=part_id,
                    page_num=page_num, return_count=True)
                accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                    validation_status="accepted", keyword_id=part_id,
                    page_num=page_num, return_count=True)
                rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                    validation_status="rejected", keyword_id=part_id,
                    page_num=page_num, return_count=True)
            except:
                raise
            else:
                pass
        elif content_part == "content_type":
            try:
                validating_edits, val_edit_count = Edit.bulk_retrieve(
                    validation_status="validating", content_type_id=part_id,
                    page_num=page_num, return_count=True)
                accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                    validation_status="accepted", content_type_id=part_id,
                    page_num=page_num, return_count=True)
                rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                    validation_status="rejected", content_type_id=part_id,
                    page_num=page_num, return_count=True)
            except:
                raise
            else:
                pass
        else:
            try:
                validating_edits, val_edit_count = Edit.bulk_retrieve(
                    validation_status="validating", content_id=content_id,
                    page_num=page_num, return_count=True)
                accepted_edits, acc_edit_count = Edit.bulk_retrieve(
                    validation_status="accepted", content_id=content_id,
                    page_num=page_num, return_count=True)
                rejected_edits, rej_edit_count = Edit.bulk_retrieve(
                    validation_status="rejected", content_id=content_id,
                    page_num=page_num, return_count=True)
            except:
                raise
            else:
                pass

        def ordering_func(edit):
            if edit is None:
                return datetime.min
            else:
                return edit.validated_timestamp

        # Merge and sort accepted and rejected edits.
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
            if next_oldest_edit.validation_status == "accepted":
                accepted_edits.pop()
            elif next_oldest_edit.validation_status == "rejected":
                rejected_edits.pop()
            closed_edits.append(next_oldest_edit)

        # Format and serialize edits
        for i in range(len(validating_edits)):
            del validating_edits[i]["start_timestamp"]
            del validating_edits[i]["edit_text"]
            del validating_edits[i]["applied_edit_text"]
            if user_id is not None:
                validating_edits[i]["content_name"] = content_names[
                    validating_edits[i]["content_id"]].name
        for i in range(len(closed_edits)):
            del closed_edits[i]["start_timestamp"]
            del closed_edits[i]["edit_text"]
            del closed_edits[i]["applied_edit_text"]
            if user_id is not None:
                closed_edits[i]["content_name"] = content_names[
                    closed_edits[i]["content_id"]].name

        return {
            "validating_edit_count": val_edit_count,
            "validating_edits": validating_edits,
            "closed_edit_count": acc_edit_count + rej_edit_count,
            "closed_edits": closed_edits,
        }

    @property
    def conflict(self):
        return self.edit_object.conflict
