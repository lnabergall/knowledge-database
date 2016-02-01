"""
Redis API Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase

from Knowledge_Database_App.content import redis


class RedisTest(TestCase):

    def test_01_store_edit(self):
        timestamp = datetime.utcnow()
        try:
            self.edit_id = redis.store_edit(-1013, "Kylo Ren is a dark force user.",
                                       "Unlimited power!", "text", -100,
                                       timestamp, timestamp, "U", -333)
        except Exception as e:
            self.fail(str(e))
        else:
            edit = redis.get_validation_data(edit_id)["edit"]
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

    def test_02_store_vote(self):
        try:
            redis.store_vote(self.edit_id, -42, "Y; 2016-01-31 02:33:58.060915")
        except Exception as e:
            self.fail(str(e))
        else:
            votes = redis.get_validation_data(self.edit_id)["votes"]
            voted_edit_ids = redis.get_edits(voter_id=-42, only_ids=True)
            self.assertIsInstance(votes, dict)
            self.assertEqual(votes[-42], "Y; 2016-01-31 02:33:58.060915")
            self.assertIn(self.edit_id, voted_edit_ids)

    def test_03_get_edits(self):
        try:
            text_edits = redis.get_edits(text_id=-100)
            text_edit_ids = redis.get_edits(text_id=-100, only_ids=True)
            content_edits = redis.get_edits(content_id=-1013)
            user_edits = redis.get_edits(user_id=-333)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(text_edits[self.edit_id], dict)
            self.assertEqual(text_edits[self.edit_id]["edit_id"], self.edit_id)
            self.assertIn(self.edit_id, text_edit_ids)
            self.assertIsInstance(content_edits[self.edit_id], dict)
            self.assertEqual(
                content_edits[self.edit_id]["edit_id"], self.edit_id)
            self.assertIsInstance(user_edits[self.edit_id], dict)
            self.assertEqual(user_edits[self.edit_id]["edit_id"], self.edit_id)

    def test_04_get_votes(self):
        try:
            votes = redis.get_votes(-1013)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(votes, dict)
            self.assertIsInstance(votes[self.edit_id], dict)
            self.assertEqual(votes[self.edit_id][-42],
                             "Y; 2016-01-31 02:33:58.060915")

    def test_05_get_validation_data(self):
        try:
            validation_data = redis.get_validation_data(self.edit_id)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(validation_data, dict)
            self.assertIsInstance(validation_data["edit"], dict)
            self.assertIsInstance(validation_data["votes"], dict)
            self.assertEqual(validation_data["edit"]["edit_id"], self.edit_id)
            self.assertEqual(validation_data["votes"][-42],
                             "Y; 2016-01-31 02:33:58.060915")

    def test_06_delete_validation_data(self):
        try:
            redis.delete_validation_data(-1013, self.edit_id,
                                         -333, -100, "text")
        except Exception as e:
            self.fail(str(e))
        else:
            validation_data = redis.get_validation_data(self.edit_id)
            self.assertIs(validation_data["edit"], None)
            self.assertIs(validation_data["votes"], None)
