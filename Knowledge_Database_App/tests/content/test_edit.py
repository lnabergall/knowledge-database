"""
Content Edit Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

import warnings
from datetime import datetime
from math import ceil
from unittest import TestCase, skipIf

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.tests.storage import PostgresTest
from Knowledge_Database_App.tests.content.test_redis import RedisTest
from Knowledge_Database_App.tests.search import ElasticsearchTest
from Knowledge_Database_App.content.edit_diff import restore
from Knowledge_Database_App.content.content import Content
from Knowledge_Database_App.content.edit import Edit


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            test_func(self, *args, **kwargs)
    return do_test


warnings.filterwarnings("ignore", category=ResourceWarning)


class ContentEditTest(PostgresTest, RedisTest, ElasticsearchTest):
    failure = False

    @classmethod
    def setUpClass(cls):
        PostgresTest.setUpClass.__func__(cls)
        RedisTest.setUpClass.__func__(cls)
        ElasticsearchTest.setUpClass.__func__(cls)
        cls.first_author_name = "Test Ai"
        cls.first_author_id = 1
        cls.content_type = "definition"
        cls.name = "Kylo Ren"
        cls.alternate_names = ["Ben Solo"]
        cls.text = ("Kylo Ren is the master of the Knights of Ren, "
                     "a dark side Force user, and the son of "
                     "Han Solo and Leia Organa.[ref:1]")
        cls.keywords = ["Star Wars", "The Force Awakens", "The First Order"]
        cls.citations = ["[1] Abrams, J.J. Star Wars: The Force Awakens. 2016."]
        user_content_pieces = Content.bulk_retrieve(user_id=cls.first_author_id)
        if cls.name in [piece.name.name for piece in user_content_pieces]:
            cls.piece = filter(lambda piece: piece.name.name == cls.name,
                                user_content_pieces)[0]
        else:
            cls.piece = Content(
                first_author_name=cls.first_author_name,
                first_author_id=cls.first_author_id,
                content_type=cls.content_type,
                name=cls.name,
                alternate_names=cls.alternate_names,
                text=cls.text,
                keywords=cls.keywords,
                citations=cls.citations
            )
            cls.piece.store()
            cls.piece = Content(content_id=cls.piece.content_id)
        cls.content_id = cls.piece.content_id
        cls.start_timestamp = datetime.utcnow()
        cls.edit_text = ("Kylo Ren is the master of the Knights of Ren, "
                          "a dark Force user, apprentice of Supreme Leader "
                          "Snoke, and the son of Han Solo and Leia Organa.[ref:1]")
        cls.edit_rationale = "Unlimited power!"
        cls.content_part = "text"
        cls.part_id = cls.piece.text.text_id

    @classmethod
    def tearDownClass(cls):
        PostgresTest.tearDownClass.__func__(cls)
        RedisTest.tearDownClass.__func__(cls)
        ElasticsearchTest.tearDownClass.__func__(cls)

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_01_create(self):
        try:
            self.__class__.edit = Edit(
                content_id=self.__class__.content_id,
                edit_text=self.__class__.edit_text,
                edit_rationale=self.__class__.edit_rationale,
                content_part=self.__class__.content_part,
                part_id=self.__class__.part_id,
                original_part_text=self.__class__.text,
                author_type="U",
                author_id=self.__class__.first_author_id,
                start_timestamp=self.__class__.start_timestamp,
            )
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.__class__.edit.timestamp, datetime)
                self.assertEqual(self.__class__.edit.content_id, 
                                 self.__class__.content_id)
                self.assertEqual(restore(self.__class__.edit.edit_text, "edit"), 
                                 self.__class__.edit_text)
                self.assertEqual(self.__class__.edit.edit_rationale, 
                                 self.__class__.edit_rationale)
                self.assertEqual(self.__class__.edit.content_part, 
                                 self.__class__.content_part)
                self.assertEqual(self.__class__.edit.part_id, 
                                 self.__class__.part_id)
                self.assertEqual(self.__class__.edit.original_part_text, 
                                 self.__class__.text)
                self.assertEqual(self.__class__.edit.author_type, "U")
                self.assertEqual(self.__class__.edit.author.user_id, 
                                 self.__class__.first_author_id)
                self.assertEqual(self.__class__.edit.start_timestamp,
                                 self.__class__.start_timestamp)
                self.assertEqual(self.__class__.edit.validation_status, 
                                 "pending")
            except AssertionError:
                self.__class__.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_02_start_vote(self):
        try:
            self.__class__.edit.start_vote()
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.__class__.edit.edit_id, int)
                self.assertEqual(self.__class__.edit.validation_status, "validating")
            except AssertionError:
                self.__class__.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_03_retrieve(self):
        try:
            self.__class__.edit = Edit(edit_id=self.__class__.edit.edit_id, 
                                       validation_status="validating")
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.__class__.edit.timestamp, datetime)
                self.assertEqual(self.__class__.edit.content_id, 
                                 self.__class__.content_id)
                self.assertEqual(restore(self.__class__.edit.edit_text, "edit"), 
                                 self.__class__.edit_text)
                self.assertEqual(self.__class__.edit.edit_rationale, 
                                 self.__class__.edit_rationale)
                self.assertEqual(self.__class__.edit.content_part, 
                                 self.__class__.content_part)
                self.assertEqual(self.__class__.edit.part_id, 
                                 self.__class__.part_id)
                self.assertEqual(self.__class__.edit.original_part_text, 
                                 self.__class__.text)
                self.assertEqual(self.__class__.edit.author_type, "U")
                self.assertEqual(self.__class__.edit.author.user_id, 
                                 self.__class__.first_author_id)
                self.assertEqual(self.__class__.edit.start_timestamp,
                                 self.__class__.start_timestamp)
                self.assertEqual(self.__class__.edit.validation_status, 
                                 "validating")
                self.assertIsInstance(
                    self.__class__.edit.edit_metrics.applied_chars, 
                    (int, type(None)))
                self.assertIsInstance(
                    self.__class__.edit.edit_metrics.original_chars, int)
                self.assertIsInstance(
                    self.__class__.edit.edit_metrics.insertions, int)
                self.assertIsInstance(
                    self.__class__.edit.edit_metrics.deletions, int)
            except AssertionError:
                self.__class__.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_04_edits_validating(self):
        try:
            edit_indicator = Edit.edits_validating([self.__class__.content_id])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(edit_indicator[self.__class__.content_id], True)
            except AssertionError:
                self.__class__.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_05_bulk_retrieve(self):
        try:
            user_validating_edits, count1 = Edit.bulk_retrieve(
                "validating", user_id=self.__class__.first_author_id, 
                return_count=True)
            user_validating_edit_ids = Edit.bulk_retrieve(
                "validating", user_id=self.__class__.first_author_id, 
                ids_only=True)
            user_accepted_edits = Edit.bulk_retrieve(
                "accepted", user_id=self.__class__.first_author_id)
            user_rejected_edits = Edit.bulk_retrieve(
                "rejected", user_id=self.__class__.first_author_id)
            content_validating_edits, count2 = Edit.bulk_retrieve(
                "validating", content_id=self.__class__.content_id,
                return_count=True)
            content_accepted_edits = Edit.bulk_retrieve(
                "accepted", content_id=self.__class__.content_id)
            content_rejected_edits = Edit.bulk_retrieve(
                "rejected", content_id=self.__class__.content_id)
            text_validating_edits, count3 = Edit.bulk_retrieve(
                "validating", text_id=self.__class__.part_id,
                return_count=True)
            text_accepted_edits = Edit.bulk_retrieve(
                "accepted", text_id=self.__class__.part_id)
            text_rejected_edits = Edit.bulk_retrieve(
                "rejected", text_id=self.__class__.part_id)
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(count1, int)
                self.assertIsInstance(count2, int)
                self.assertEqual(count3, 1)
                if count1 <= 10:
                    self.assertTrue(any([
                        edit.edit_id == self.__class__.edit.edit_id
                        for edit in user_validating_edits]))
                else:
                    for i in range(ceil(count1/10)):
                        try:
                            more_results = Edit.bulk_retrieve(
                                "validating",
                                user_id=self.__class__.first_author_id,
                                page_num=i+1,
                            )
                        except Exception as e:
                            self.__class__.failure = True
                            self.fail(str(e))
                        else:
                            found = any([
                                edit.edit_id == self.__class__.edit.edit_id
                                for edit in more_results])
                            if found:
                                break
                    self.assertTrue(found)
                self.assertEqual(user_validating_edit_ids,
                                 [edit.edit_id for edit in
                                  user_validating_edits])
                for edit in user_accepted_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.author.user_id, 
                                     self.__class__.first_author_id)
                for edit in user_rejected_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.author.user_id, 
                                     self.__class__.first_author_id)
                if count2 <= 10:
                    self.assertTrue(any([
                        edit.edit_id == self.__class__.edit.edit_id
                        for edit in content_validating_edits]))
                else:
                    for i in range(ceil(count2/10)):
                        try:
                            more_results = Edit.bulk_retrieve(
                                "validating",
                                content_id=self.__class__.content_id,
                                page_num=i+1,
                            )
                        except Exception as e:
                            self.__class__.failure = True
                            self.fail(str(e))
                        else:
                            found = any([
                                edit.edit_id == self.__class__.edit.edit_id
                                for edit in more_results])
                            if found:
                                break
                    self.assertTrue(found)
                for edit in content_accepted_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.content_id, self.__class__.content_id)
                for edit in content_rejected_edits:
                    self.assertIsInstance(edit, Edit)
                    self.assertEqual(edit.content_id, self.__class__.content_id)
                self.assertEqual(text_validating_edits[0].edit_id,
                                 self.__class__.edit.edit_id)
                self.assertFalse(text_accepted_edits)
                self.assertFalse(text_rejected_edits)
            except AssertionError:
                self.__class__.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_06_validate(self):
        try:
            self.__class__.edit.validate()
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            text_accepted_edits = Edit.bulk_retrieve(
                "accepted", text_id=self.__class__.part_id)
            text_rejected_edits = Edit.bulk_retrieve(
                "rejected", text_id=self.__class__.part_id)
            try:
                self.assertFalse(text_accepted_edits)
                self.assertFalse(text_rejected_edits)
            except AssertionError:
                self.__class__.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_07_conflict(self):
        try:
            conflict = self.__class__.edit.conflict
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertFalse(conflict)
            except AssertionError:
                self.__class__.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    @ignore_warnings
    def test_08_json_ready(self):
        try:
            json_ready_version = self.__class__.edit.json_ready
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_version["content_id"],
                                 self.__class__.edit.content_id)
                self.assertEqual(json_ready_version["edit_id"],
                                 self.__class__.edit.edit_id)
                self.assertEqual(json_ready_version["timestamp"],
                                 str(self.__class__.edit.timestamp))
                self.assertEqual(json_ready_version["start_timestamp"],
                                 str(self.__class__.edit.start_timestamp))
                self.assertEqual(json_ready_version["validated_timestamp"],
                    self.__class__.edit.validated_timestamp)  # Since is None
                self.assertEqual(json_ready_version["validation_status"],
                                 self.__class__.edit.validation_status)
                self.assertEqual(json_ready_version["edit_text"],
                                 self.__class__.edit.edit_text)
                self.assertEqual(json_ready_version["applied_edit_text"],
                                 self.__class__.edit.applied_edit_text)
                self.assertEqual(json_ready_version["edit_rationale"],
                                 self.__class__.edit.edit_rationale)
                self.assertEqual(json_ready_version["content_part"],
                                 self.__class__.edit.content_part)
                self.assertEqual(json_ready_version["part_id"],
                                 self.__class__.edit.part_id)
                self.assertEqual(json_ready_version["author_type"],
                                 self.__class__.edit.author_type)
                self.assertIsInstance(json_ready_version["author"], dict)
                self.assertEqual(json_ready_version["author"]["user_id"],
                                 self.__class__.edit.author.user_id)
                self.assertIsInstance(json_ready_version["edit_metrics"], dict)
                self.assertEqual(
                    json_ready_version["edit_metrics"]["original_chars"],
                    self.__class__.edit.edit_metrics.original_chars
                )
                self.assertEqual(
                    json_ready_version["edit_metrics"]["applied_chars"],
                    self.__class__.edit.edit_metrics.applied_chars
                )
                self.assertEqual(
                    json_ready_version["edit_metrics"]["insertions"],
                    self.__class__.edit.edit_metrics.insertions
                )
                self.assertEqual(
                    json_ready_version["edit_metrics"]["deletions"],
                    self.__class__.edit.edit_metrics.deletions
                )
                self.assertEqual(json_ready_version["author_type"],
                                 self.__class__.edit.author_type)
            except AssertionError:
                self.__class__.failure = True
                raise
