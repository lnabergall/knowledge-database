"""
Redis API Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.content import redis_api


class RedisTest(TestCase):

    def setUp(self):
        self.failure = False

    @skipIfTrue("failure")
    def test_01_store_edit(self):
        timestamp = datetime.utcnow()
        try:
            self.edit_id = redis_api.store_edit(-1013, "Kylo Ren is a dark force user.",
                                       "Unlimited power!", "text", -100,
                                       timestamp, timestamp, "U", -333)
        except Exception as e:
            self.fail(str(e))
        else:
            edit = redis_api.get_validation_data(edit_id)["edit"]
            self.assertIsInstance(edit, dict)
            self.assertEqual(edit["edit_id"], edit_id)
            self.assertEqual(edit["content_id"], -1013)
            self.assertEqual(edit["edit_text"], "Kylo Ren is a dark force user.")
            self.assertEqual(edit["edit_rationale"], "Unlimited power!")
            self.assertEqual(edit["content_part"], "text")
            self.assertEqual(edit["part_id"], -100)
            self.assertEqual(edit["timestamp"], timestamp)
            self.assertEqual(edit["start_timestamp"], timestamp)
            self.assertEqual(edit["author_type"], "U")
            self.assertEqual(edit["user_id"], -333)

    @skipIfTrue("failure")
    def test_02_store_vote(self):
        try:
            redis_api.store_vote(self.edit_id, -42, "Y; 2016-01-31 02:33:58.060915")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            votes = redis_api.get_validation_data(self.edit_id)["votes"]
            voted_edit_ids = redis_api.get_edits(voter_id=-42, only_ids=True)
            try:
                self.assertIsInstance(votes, dict)
                self.assertEqual(votes[-42], "Y; 2016-01-31 02:33:58.060915")
                self.assertIn(self.edit_id, voted_edit_ids)
            except AssertionError:
                self.failure = True
                raise

    @skipIfTrue("failure")
    def test_03_get_edits(self):
        try:
            text_edits = redis_api.get_edits(text_id=-100)
            text_edit_ids = redis_api.get_edits(text_id=-100, only_ids=True)
            content_edits = redis_api.get_edits(content_id=-1013)
            user_edits = redis_api.get_edits(user_id=-333)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(text_edits[self.edit_id], dict)
                self.assertEqual(
                    text_edits[self.edit_id]["edit_id"], self.edit_id)
                self.assertIn(self.edit_id, text_edit_ids)
                self.assertIsInstance(content_edits[self.edit_id], dict)
                self.assertEqual(
                    content_edits[self.edit_id]["edit_id"], self.edit_id)
                self.assertIsInstance(user_edits[self.edit_id], dict)
                self.assertEqual(
                    user_edits[self.edit_id]["edit_id"], self.edit_id)
            except AssertionError:
                self.failure = True
                raise

    @skipIfTrue("failure")
    def test_04_get_votes(self):
        try:
            votes = redis_api.get_votes(-1013)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(votes, dict)
                self.assertIsInstance(votes[self.edit_id], dict)
                self.assertEqual(votes[self.edit_id][-42],
                                 "Y; 2016-01-31 02:33:58.060915")
            except AssertionError:
                self.failure = True
                raise

    @skipIfTrue("failure")
    def test_05_get_validation_data(self):
        try:
            validation_data = redis_api.get_validation_data(self.edit_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(validation_data, dict)
                self.assertIsInstance(validation_data["edit"], dict)
                self.assertIsInstance(validation_data["votes"], dict)
                self.assertEqual(
                    validation_data["edit"]["edit_id"], self.edit_id)
                self.assertEqual(validation_data["votes"][-42],
                                 "Y; 2016-01-31 02:33:58.060915")
            except AssertionError:
                self.failure = True
                raise

    @skipIfTrue("failure")
    def test_06_delete_validation_data(self):
        try:
            redis_api.delete_validation_data(-1013, self.edit_id,
                                         -333, -100, "text")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            validation_data = redis_api.get_validation_data(self.edit_id)
            try:
                self.assertIs(validation_data["edit"], None)
                self.assertIs(validation_data["votes"], None)
            except AssertionError:
                self.failure = True
                raise
