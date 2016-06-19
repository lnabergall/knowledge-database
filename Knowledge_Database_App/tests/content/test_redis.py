"""
Redis API Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase, skipIf

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.content import redis_api


class RedisTest(TestCase):

    @classmethod
    def setUpClass(cls):
        print("Redis setup")
        redis_api._reset_db()

    @classmethod
    def tearDownClass(cls):
        print("Redis teardown")
        redis_api._reset_db()


class RedisAPITest(RedisTest):
    failure = False

    @classmethod
    def setUpClass(cls):
        RedisTest.setUpClass.__func__(cls)
        timestamp = datetime.utcnow()
        cls.test_data = {
            "content_id": -1013,
            "edit_text": "Kylo Ren is a dark force user.",
            "edit_rationale": "Unlimited power!",
            "content_part": "text",
            "part_id": -100,
            "timestamp": timestamp,
            "start_timestamp": timestamp,
            "author_type": "U",
            "user_id": -333,
            "email": "kyloren121323@gmail.com",
            "confirmation_id_hash": "1212121212asdf",
            "expire_timestamp": datetime.utcnow(),
            "voter_id": -42,
            "vote_and_time": "Y; 2016-01-31 02:33:58.060915",
            "report_text": "Mission report: December 16, 1991.",
            "report_type": "content",
            "admin_id": -1212,
        }

    @skipIf(failure, "Previous test failed!")
    def test_01_store_edit(self):
        try:
            self.__class__.edit_id = redis_api.store_edit(
                self.__class__.test_data["content_id"], 
                self.__class__.test_data["edit_text"], 
                self.__class__.test_data["edit_rationale"], 
                self.__class__.test_data["content_part"], 
                self.__class__.test_data["part_id"], 
                self.__class__.test_data["timestamp"], 
                self.__class__.test_data["start_timestamp"], 
                self.__class__.test_data["author_type"], 
                self.__class__.test_data["user_id"]
            )
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                edit = redis_api.get_validation_data(
                    self.__class__.edit_id)["edit"]
                self.assertIsInstance(edit, dict)
                self.assertEqual(edit["edit_id"], self.__class__.edit_id)
                self.assertEqual(edit["content_id"], 
                                 self.__class__.test_data["content_id"])
                self.assertEqual(edit["edit_text"], 
                                 self.__class__.test_data["edit_text"])
                self.assertEqual(edit["edit_rationale"], 
                                 self.__class__.test_data["edit_rationale"])
                self.assertEqual(edit["content_part"], 
                                 self.__class__.test_data["content_part"])
                self.assertEqual(edit["part_id"], 
                                 self.__class__.test_data["part_id"])
                self.assertEqual(edit["timestamp"], 
                                 self.__class__.test_data["timestamp"])
                self.assertEqual(edit["start_timestamp"], 
                                 self.__class__.test_data["start_timestamp"])
                self.assertEqual(edit["author_type"], 
                                 self.__class__.test_data["author_type"])
                self.assertEqual(edit["user_id"], 
                                 self.__class__.test_data["user_id"])
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_02_store_vote(self):
        try:
            redis_api.store_vote(self.__class__.edit_id, 
                                 self.__class__.test_data["voter_id"], 
                                 self.__class__.test_data["vote_and_time"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                votes = redis_api.get_validation_data(
                    self.__class__.edit_id)["votes"]
                voted_edit_ids = redis_api.get_edits(
                    voter_id=self.__class__.test_data["voter_id"], only_ids=True)
                self.assertIsInstance(votes, dict)
                self.assertEqual(votes[self.__class__.test_data["voter_id"]], 
                                 self.__class__.test_data["vote_and_time"])
                self.assertIn(self.__class__.edit_id, voted_edit_ids)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_03_store_confirm(self):
        try:
            redis_api.store_confirm(self.__class__.test_data["email"],
                self.__class__.test_data["confirmation_id_hash"],
                self.__class__.test_data["expire_timestamp"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                confirmation_info = redis_api.get_confirm_info(
                    self.__class__.test_data["email"])
                self.assertIn(self.__class__.test_data["confirmation_id_hash"], 
                    confirmation_info)
                self.assertIsInstance(confirmation_info[
                    self.__class__.test_data["confirmation_id_hash"]], datetime)
                self.assertEqual(confirmation_info[
                    self.__class__.test_data["confirmation_id_hash"]], 
                    self.__class__.test_data["expire_timestamp"])
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))    

    @skipIf(failure, "Previous test failed!")
    def test_04_get_confirm_info(self):
        try:
            confirmation_info = redis_api.get_confirm_info(
                self.__class__.test_data["email"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(confirmation_info, dict)
                self.assertIn(self.__class__.test_data["confirmation_id_hash"], 
                    confirmation_info)
                self.assertIsInstance(confirmation_info[
                    self.__class__.test_data["confirmation_id_hash"]], datetime)
                self.assertEqual(confirmation_info[
                    self.__class__.test_data["confirmation_id_hash"]], 
                    self.__class__.test_data["expire_timestamp"])
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_05_expire_confirm(self):
        try:
            redis_api.expire_confirm(self.__class__.test_data["email"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                confirmation_info = redis_api.get_confirm_info(
                    self.__class__.test_data["email"])
                self.assertFalse(confirmation_info)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_06_store_report(self):
        try:
            self.__class__.report_id = redis_api.store_report(
                self.__class__.test_data["content_id"], 
                self.__class__.test_data["report_text"],
                self.__class__.test_data["report_type"],
                self.__class__.test_data["admin_id"],
                self.__class__.test_data["timestamp"], 
                self.__class__.test_data["author_type"], 
                self.__class__.test_data["user_id"] 
            )
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                report_dict = redis_api.get_reports(
                    report_id=self.__class__.report_id)
                self.assertEqual(report_dict["report_id"], 
                    self.__class__.report_id)
                self.assertEqual(report_dict["content_id"], 
                    self.__class__.test_data["content_id"])
                self.assertEqual(report_dict["report_text"], 
                    self.__class__.test_data["report_text"])
                self.assertEqual(report_dict["report_type"], 
                    self.__class__.test_data["report_type"])
                self.assertEqual(report_dict["admin_id"], 
                    self.__class__.test_data["admin_id"])
                self.assertEqual(report_dict["timestamp"], 
                    self.__class__.test_data["timestamp"])
                self.assertEqual(report_dict["author_type"], 
                    self.__class__.test_data["author_type"])
                self.assertEqual(report_dict["author_id"], 
                    self.__class__.test_data["user_id"])
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_07_get_reports(self):
        try:
            report_dict = redis_api.get_reports(
                report_id=self.__class__.report_id)
            content_report_dicts = redis_api.get_reports(
                content_id=self.__class__.test_data["content_id"])
            user_report_dicts = redis_api.get_reports(
                user_id=self.__class__.test_data["user_id"])
            admin_report_dicts = redis_api.get_reports(
                admin_id=self.__class__.test_data["admin_id"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(report_dict, dict)
                self.assertEqual(report_dict["report_id"], 
                    self.__class__.report_id)
                self.assertEqual(report_dict["content_id"], 
                    self.__class__.test_data["content_id"])
                self.assertEqual(report_dict["report_text"], 
                    self.__class__.test_data["report_text"])
                self.assertEqual(report_dict["report_type"], 
                    self.__class__.test_data["report_type"])
                self.assertEqual(report_dict["admin_id"], 
                    self.__class__.test_data["admin_id"])
                self.assertEqual(report_dict["timestamp"], 
                    self.__class__.test_data["timestamp"])
                self.assertEqual(report_dict["author_type"], 
                    self.__class__.test_data["author_type"])
                self.assertEqual(report_dict["author_id"], 
                    self.__class__.test_data["user_id"])
                self.assertIsInstance(content_report_dicts, list)
                for report_dict_ in content_report_dicts:
                    self.assertIsInstance(report_dict_, dict)
                self.assertIsInstance(user_report_dicts, list)
                for report_dict_ in user_report_dicts:
                    self.assertIsInstance(report_dict_, dict)
                self.assertIsInstance(admin_report_dicts, list)
                for report_dict_ in admin_report_dicts:
                    self.assertIsInstance(report_dict_, dict)
                self.assertIn(report_dict, content_report_dicts)
                self.assertIn(report_dict, user_report_dicts)
                self.assertIn(report_dict, admin_report_dicts)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_08_get_admin_assignments(self):
        try:
            admin_assignments = redis_api.get_admin_assignments(
                [self.__class__.test_data["admin_id"]])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(admin_assignments, dict)
                self.assertEqual(len(admin_assignments.keys()), 1)
                self.assertIn(self.__class__.test_data["admin_id"], 
                              admin_assignments)
                assigned_reports = admin_assignments[
                    self.__class__.test_data["admin_id"]]
                self.assertIsInstance(assigned_reports, list)
                for report_id in assigned_reports:
                    self.assertIsInstance(report_id, int)
                self.assertIn(self.__class__.report_id, assigned_reports)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_09_delete_report(self):
        try:
            redis_api.delete_report(self.__class__.report_id)
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                report_dict = redis_api.get_reports(
                    report_id=self.__class__.report_id)
                self.assertFalse(report_dict)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_10_get_edits(self):
        try:
            text_edits = redis_api.get_edits(
                text_id=self.__class__.test_data["part_id"])
            text_edit_ids = redis_api.get_edits(
                text_id=self.__class__.test_data["part_id"], only_ids=True)
            content_edits = redis_api.get_edits(
                content_id=self.__class__.test_data["content_id"])
            user_edits = redis_api.get_edits(
                user_id=self.__class__.test_data["user_id"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(text_edits[self.__class__.edit_id], dict)
                self.assertEqual(text_edits[self.__class__.edit_id]["edit_id"], 
                                 self.__class__.edit_id)
                self.assertIn(self.__class__.edit_id, text_edit_ids)
                self.assertIsInstance(content_edits[self.__class__.edit_id], dict)
                self.assertEqual(content_edits[self.__class__.edit_id]["edit_id"], 
                                 self.__class__.edit_id)
                self.assertIsInstance(user_edits[self.__class__.edit_id], dict)
                self.assertEqual(user_edits[self.__class__.edit_id]["edit_id"], 
                                 self.__class__.edit_id)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_11_get_votes(self):
        try:
            votes = redis_api.get_votes(self.__class__.test_data["content_id"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(votes, dict)
                self.assertIsInstance(votes[self.__class__.edit_id], dict)
                self.assertEqual(
                    votes[self.__class__.edit_id][self.__class__.test_data["voter_id"]],
                    self.__class__.test_data["vote_and_time"]
                )
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_12_get_validation_data(self):
        try:
            validation_data = redis_api.get_validation_data(self.__class__.edit_id)
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(validation_data, dict)
                self.assertIsInstance(validation_data["edit"], dict)
                self.assertIsInstance(validation_data["votes"], dict)
                self.assertEqual(
                    validation_data["edit"]["edit_id"], self.__class__.edit_id)
                self.assertEqual(
                    validation_data["votes"][self.__class__.test_data["voter_id"]],
                    self.__class__.test_data["vote_and_time"]
                )
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_13_delete_validation_data(self):
        try:
            redis_api.delete_validation_data(
                self.__class__.test_data["content_id"], 
                self.__class__.edit_id, 
                self.__class__.test_data["user_id"], 
                self.__class__.test_data["part_id"], 
                self.__class__.test_data["content_part"]
            )
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                validation_data = redis_api.get_validation_data(self.__class__.edit_id)
                self.assertFalse(validation_data["edit"])
                self.assertFalse(validation_data["votes"])
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))
