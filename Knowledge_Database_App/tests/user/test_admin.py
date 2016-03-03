"""
Admin Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase, skipIf

from Knowledge_Database_App.storage.action_queries import delete_user
from Knowledge_Database_App.user.user import RegisteredUser
from Knowledge_Database_App.user.admin import Admin


class AdminTest(TestCase):

    def setUp(self):
        self.user_name = "Kylo Ren"
        self.email = "kyloren121323@gmail.com"
        self.password = "darthvader123"
        self.failure = False
        self.stored = False

    def tearDown(self):
        if self.stored:
            delete_user(self.admin.user_id, permanently=True)

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_01_create(self):
        try:
            self.admin = Admin(email=self.email, user_name=self.user_name,
                               password=self.password)
            self.admin.register()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.admin.email, self.email)
                self.assertEqual(self.admin.user_name, self.user_name)
                self.assertNotEqual(self.admin.pass_hash, self.password)
                self.assertIsInstance(self.admin.pass_hash_type, str)
                self.assertEqual(self.admin.user_type, "admin")
                self.assertIsNotNone(self.admin.remember_id)
                self.assertIsInstance(self.admin.timestamp, datetime)
                self.assertIsInstance(self.admin.user_id, int)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
            else:
                delete_user(self.admin.user_id, permanently=True)

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_02_promote(self):
        try:
            user = RegisteredUser(email=self.email, password=self.password,
                                  user_name=self.user_name)
            user.register()
            Admin.promote(user.user_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                admin = Admin(user_id=user.user_id)
                self.assertEqual(self.admin, admin)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
            else:
                self.admin = admin
                self.stored = True


    @skipIf(self.failure, "Necessary previous test failed!")
    def test_03_demote(self):
        try:
            self.admin.demote()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                user = RegisteredUser(user_id=self.admin.user_id)
                self.assertEqual(user.user_type, "standard")
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_04_json_ready(self):
        try:
            json_ready_dict = self.admin.json_ready
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_dict["user_id"], self.admin.user_id)
                self.assertEqual(json_ready_dict["user_name"],
                                 self.admin.user_name)
                self.assertEqual(json_ready_dict["user_type"],
                                 self.admin.user_type)
                self.assertEqual(json_ready_dict["email"], self.admin.email)
                self.assertEqual(json_ready_dict["timestamp"],
                                 self.admin.timestamp)
                self.assertEqual(json_ready_dict["deleted_timestamp"],
                                 self.admin.deleted_timestamp)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
