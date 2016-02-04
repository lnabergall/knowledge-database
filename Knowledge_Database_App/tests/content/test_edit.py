"""
Content Edit Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from math import ceil
from unittest import TestCase, skipIf

from Knowledge_Database_App.content.content import Content
from Knowledge_Database_App.content.edit import Edit


class ContentEditTest(TestCase):

    def setUp(self):
        self.first_author_name = "Test Ai"
        self.first_author_id = 1
        self.content_type = "definition"
        self.name = "Kylo Ren"
        self.alternate_names = ["Ben Solo"]
        self.text = ("Kylo Ren is the master of the Knights of Ren, "
                     "a dark side Force user, and the son of "
                     "Han Solo and Leia Organa.[ref:1]")
        self.keywords = ["Star Wars", "The Force Awakens", "The First Order"]
        self.citations = ["[1] Abrams, J.J. Star Wars: The Force Awakens. 2016."]
        user_content_pieces = Content.bulk_retrieve(user_id=self.first_author_id)
        if self.name in [piece.name.name for piece in user_content_pieces]:
            self.piece = filter(lambda piece: piece.name.name == self.name,
                                user_content_pieces)[0]
        else:
            self.piece = Content(
                first_author_name=self.first_author_name,
                first_author_id=self.first_author_id,
                content_type=self.content_type,
                name=self.name,
                alternate_names=self.alternate_names,
                text=self.text,
                keywords=self.keywords,
                citations=self.citations
            )
            self.piece.store()
            self.piece = Content(content_id=self.content_id)
        self.content_id = self.piece.content_id
        self.start_timestamp = datetime.utcnow()
        self.edit_text = ("Kylo Ren is the master of the Knights of Ren, "
                          "a dark Force user, apprentice of Supreme Leader "
                          "Snoke, and the son of Han Solo and Leia Organa.[ref:1]")
        self.edit_rationale = "Unlimited power!"
        self.content_part = "text"
        self.part_id = self.piece.text.text_id
        self.failure = False

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_01_create(self):
        try:
            self.edit = Edit(
                content_id=self.content_id,
                edit_text=self.edit_text,
                edit_rationale=self.edit_rationale,
                content_part=self.content_part,
                part_id=self.part_id,
                original_part_text=self.text,
                author_type="U",
                author_id=self.first_author_id,
                start_timestamp=self.start_timestamp,
            )
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.edit.timestamp, datetime)
                self.assertEqual(self.edit.content_id, self.content_id)
                self.assertEqual(self.edit.edit_text, self.edit_text)
                self.assertEqual(self.edit.edit_rationale, self.edit_rationale)
                self.assertEqual(self.edit.content_part, self.content_part)
                self.assertEqual(self.edit.part_id, self.part_id)
                self.assertEqual(self.edit.original_part_text, self.text)
                self.assertEqual(self.edit.author_type, "U")
                self.assertEqual(self.edit.author.user_id, self.first_author_id)
                self.assertEqual(self.edit.start_timestamp,
                                 self.start_timestamp)
                self.assertEqual(self.edit.validation_status, "pending")
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_02_start_vote(self):
        try:
            self.edit.start_vote()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.edit.edit_id, int)
                self.assertEqual(self.edit.validation_status, "validating")
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_03_retrieve(self):
        try:
            self.edit = Edit(edit_id=self.edit.edit_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.edit.timestamp, datetime)
                self.assertEqual(self.edit.content_id, self.content_id)
                self.assertEqual(self.edit.edit_text, self.edit_text)
                self.assertEqual(self.edit.edit_rationale, self.edit_rationale)
                self.assertEqual(self.edit.content_part, self.content_part)
                self.assertEqual(self.edit.part_id, self.part_id)
                self.assertEqual(self.edit.original_part_text, self.text)
                self.assertEqual(self.edit.author_type, "U")
                self.assertEqual(self.edit.author.user_id, self.first_author_id)
                self.assertEqual(self.edit.start_timestamp,
                                 self.start_timestamp)
                self.assertEqual(self.edit.validation_status, "validating")
                self.assertIsInstance(self.edit.edit_metrics.applied_chars, int)
                self.assertIsInstance(self.edit.edit_metrics.original_chars, int)
                self.assertIsInstance(self.edit.edit_metrics.insertions, int)
                self.assertIsInstance(self.edit.edit_metrics.deletions, int)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_04_edits_validating(self):
        try:
            edit_indicator = Edit.edits_validating([self.content_id])
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(edit_indicator[self.content_id], True)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_05_bulk_retrieve(self):
        try:
            user_validating_edits, count1 = Edit.bulk_retrieve(
                "validating", user_id=self.first_author_id, return_count=True)
            user_validating_edit_ids = Edit.bulk_retrieve(
                "validating", user_id=self.first_author_id, ids_only=True)
            user_accepted_edits = Edit.bulk_retrieve(
                "accepted", user_id=self.first_author_id)
            user_rejected_edits = Edit.bulk_retrieve(
                "rejected", user_id=self.first_author_id)
            content_validating_edits, count2 = Edit.bulk_retrieve(
                "validating", content_id=self.content_id)
            content_accepted_edits = Edit.bulk_retrieve(
                "accepted", content_id=self.content_id)
            content_rejected_edits = Edit.bulk_retrieve(
                "rejected", content_id=self.content_id)
            text_validating_edits, count3 = Edit.bulk_retrieve(
                "validating", text_id=self.part_id)
            text_accepted_edits = Edit.bulk_retrieve(
                "accepted", text_id=self.part_id)
            text_rejected_edits = Edit.bulk_retrieve(
                "rejected", text_id=self.part_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(count1, int)
                self.assertIsInstance(count2, int)
                self.assertEqual(count3, 1)
                if count1 <= 10:
                    self.assertTrue(any([edit.edit_id == self.edit.edit_id
                                         for edit in user_validating_edits]))
                else:
                    for i in range(ceil(count1/10)):
                        try:
                            more_results = Edit.bulk_retrieve(
                                "validating",
                                user_id=self.first_author_id,
                                page_num=i+1,
                            )
                        except Exception as e:
                            self.failure = True
                            self.fail(str(e))
                        else:
                            found = any([edit.edit_id == self.edit.edit_id
                                         for edit in more_results])
                            if found:
                                break
                    self.assertTrue(found)
                self.assertEqual(user_validating_edit_ids,
                                 [edit.edit_id for edit in
                                  user_validating_edits])
                for edit in user_accepted_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.author.user_id, self.first_author_id)
                for edit in user_rejected_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.author.user_id, self.first_author_id)
                if count2 <= 10:
                    self.assertTrue(any([edit.edit_id == self.edit.edit_id
                                         for edit in content_validating_edits]))
                else:
                    for i in range(ceil(count2/10)):
                        try:
                            more_results = Edit.bulk_retrieve(
                                "validating",
                                content_id=self.content_id,
                                page_num=i+1,
                            )
                        except Exception as e:
                            self.failure = True
                            self.fail(str(e))
                        else:
                            found = any([edit.edit_id == self.edit.edit_id
                                         for edit in more_results])
                            if found:
                                break
                    self.assertTrue(found)
                for edit in content_accepted_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.content_id, self.content_id)
                for edit in content_rejected_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.content_id, self.content_id)
                self.assertEqual(text_validating_edits[0].edit_id,
                                 self.edit.edit_id)
                self.assertFalse(text_accepted_edits)
                self.assertFalse(text_rejected_edits)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_06_validate(self):
        try:
            self.edit.validate()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            text_accepted_edits = Edit.bulk_retrieve(
                "accepted", text_id=self.part_id)
            text_rejected_edits = Edit.bulk_retrieve(
                "rejected", text_id=self.part_id)
            try:
                self.assertFalse(text_accepted_edits)
                self.assertFalse(text_rejected_edits)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_07_conflict(self):
        try:
            conflict = self.edit.conflict
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertFalse(conflict)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_08_json_ready(self):
        try:
            json_ready_version = self.edit.json_ready
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_version["content_id"],
                                 self.edit.content_id)
                self.assertEqual(json_ready_version["edit_id"],
                                 self.edit.edit_id)
                self.assertEqual(json_ready_version["timestamp"],
                                 str(self.edit.timestamp))
                self.assertEqual(json_ready_version["start_timestamp"],
                                 str(self.edit.start_timestamp))
                self.assertEqual(json_ready_version["validated_timestamp"],
                                 self.edit.validated_timestamp)  # Since is None
                self.assertEqual(json_ready_version["validation_status"],
                                 self.edit.validation_status)
                self.assertEqual(json_ready_version["edit_text"],
                                 self.edit.edit_text)
                self.assertEqual(json_ready_version["applied_edit_text"],
                                 self.edit.applied_edit_text)
                self.assertEqual(json_ready_version["edit_rationale"],
                                 self.edit.edit_rationale)
                self.assertEqual(json_ready_version["content_part"],
                                 self.edit.content_part)
                self.assertEqual(json_ready_version["part_id"],
                                 self.edit.part_id)
                self.assertEqual(json_ready_version["author_type"],
                                 self.edit.author_type)
                self.assertIsInstance(json_ready_version["author"], dict)
                self.assertEqual(json_ready_version["author"]["user_id"],
                                 self.edit.author.user_id)
                self.assertEqual(json_ready_version["edit_metrics"], dict)
                self.assertEqual(
                    json_ready_version["edit_metrics"]["original_chars"],
                    self.edit.edit_metrics.original_chars
                )
                self.assertEqual(
                    json_ready_version["edit_metrics"]["applied_chars"],
                    self.edit.edit_metrics.applied_chars
                )
                self.assertEqual(
                    json_ready_version["edit_metrics"]["insertions"],
                    self.edit.edit_metrics.insertions
                )
                self.assertEqual(
                    json_ready_version["edit_metrics"]["deletions"],
                    self.edit.edit_metrics.deletions
                )
                self.assertEqual(json_ready_version["author_type"],
                                 self.edit.author_type)
            except AssertionError:
                self.failure = True
                raise
