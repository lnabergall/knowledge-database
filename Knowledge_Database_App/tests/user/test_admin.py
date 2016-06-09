"""
Admin Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase, skipIf

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.storage.action_queries import delete_user
from Knowledge_Database_App.user.user import RegisteredUser
from Knowledge_Database_App.user.admin import Admin


class AdminTest(TestCase):
    failure = False
    stored = False

    @classmethod
    def setUpClass(cls):
        cls.user_name = "Kylo Ren"
        cls.email = "kyloren121323@gmail.com"
        cls.password = "darthvader123"

    @classmethod
    def tearDownClass(cls):
        if cls.stored:
            Admin.storage_handler.call(
                delete_user, cls.admin.user_id, permanently=True)

    @skipIf(failure, "Previous test failed!")
    def test_01_create(self):
        try:
            self.__class__.admin = Admin(email=self.__class__.email,
                                         user_name=self.__class__.user_name,
                                         password=self.__class__.password)
            self.admin.register()
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.__class__.admin.email,
                                 self.__class__.email)
                self.assertEqual(self.__class__.admin.user_name,
                                 self.__class__.user_name)
                self.assertNotEqual(self.__class__.admin.pass_hash,
                                    self.__class__.password)
                self.assertIsInstance(self.__class__.admin.pass_hash_type, str)
                self.assertEqual(self.__class__.admin.user_type, "admin")
                self.assertIsNotNone(self.__class__.admin.remember_id)
                self.assertIsInstance(self.__class__.admin.timestamp, datetime)
                self.assertIsInstance(self.__class__.admin.user_id, int)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))
            else:
                delete_user(self.__class__.admin.user_id, permanently=True)

    @skipIf(failure, "Previous test failed!")
    def test_02_promote(self):
        try:
            user = RegisteredUser(email=self.__class__.email,
                                  password=self.__class__.password,
                                  user_name=self.__class__.user_name)
            user.register()
            Admin.promote(user.user_id)
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                admin = Admin(user_id=user.user_id)
                self.assertEqual(self.__class__.admin, admin)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))
            else:
                self.__class__.admin = admin
                self.__class__.stored = True

    @skipIf(failure, "Previous test failed!")
    def test_03_demote(self):
        try:
            self.__class__.admin.demote()
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                user = RegisteredUser(user_id=self.__class__.admin.user_id)
                self.assertEqual(user.user_type, "standard")
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_04_json_ready(self):
        try:
            json_ready_dict = self.__class__.admin.json_ready
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_dict["user_id"],
                                 self.__class__.admin.user_id)
                self.assertEqual(json_ready_dict["user_name"],
                                 self.__class__.admin.user_name)
                self.assertEqual(json_ready_dict["user_type"],
                                 self.__class__.admin.user_type)
                self.assertEqual(json_ready_dict["email"],
                                 self.__class__.admin.email)
                self.assertEqual(json_ready_dict["timestamp"],
                                 self.__class__.admin.timestamp)
                self.assertEqual(json_ready_dict["deleted_timestamp"],
                                 self.__class__.admin.deleted_timestamp)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))
