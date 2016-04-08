"""
User Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.storage.action_queries import delete_user
from Knowledge_Database_App.user.user import RegisteredUser


class UserTest(TestCase):

    def setUp(self):
        self.user_name = "Kylo Ren"
        self.email = "kyloren121323@gmail.com"
        self.password = "darthvader123"
        self.failure = False
        self.stored = False

    def tearDown(self):
        if self.stored:
            delete_user(self.user.user_id, permanently=True)

    @skipIfTrue("failure")
    def test_01_create(self):
        try:
            self.__class__.user = RegisteredUser(
                email=self.email, password=self.password,
                user_name=self.user_name)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.__class__.user.email, self.email)
                self.assertEqual(self.__class__.user.user_name,
                                 self.user_name)
                self.assertNotEqual(self.__class__.user.pass_hash, self.password)
                self.assertIsInstance(self.__class__.user.pass_hash_type, str)
                self.assertEqual(self.__class__.user.user_type, "standard")
                self.assertIsNotNone(self.__class__.user.remember_id)
                self.assertIsInstance(self.__class__.user.timestamp, datetime)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIfTrue("failure")
    def test_02_register(self):
        try:
            self.__class__.confirmation_id = self.__class__.user.register()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.__class__.user.user_id, int)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
            else:
                self.stored = True

    @skipIfTrue("failure")
    def test_03_login(self):
        try:
            user_from_id = RegisteredUser(user_id=self.__class__.user.user_id)
            user_from_login = RegisteredUser(email=self.email,
                                             password=self.password)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.__class__.user, user_from_id)
                self.assertEqual(self.__class__.user, user_from_login)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIfTrue("failure")
    def test_04_process_confirm(self):
        try:
            RegisteredUser.process_confirm(
                self.email, self.__class__.confirmation_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                confirmed_user = RegisteredUser(
                    user_id=self.__class__.user.user_id)
                self.assertIsInstance(
                    confirmed_user.confirmed_timestamp, datetime)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
            else:
                self.__class__.user = confirmed_user

    @skipIfTrue("failure")
    def test_05_remember_user(self):
        try:
            user_with_remember = RegisteredUser(
                email=self.email, password=self.password, remember_user=True)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                user = RegisteredUser(
                    remember_id=user_with_remember.remember_id,
                    remember_token=user_with_remember.remember_token)
                self.assertEqual(user, self.__class__.user)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIfTrue("failure")
    def test_06_update(self):
        new_email = "bensolo121323@gmail.com"
        new_user_name = "Ben Solo"
        new_password = "hansolo123"
        try:
            RegisteredUser.update(self.__class__.user.user_id,
                                  new_user_name=new_user_name)
            RegisteredUser.update(self.__class__.user.user_id,
                                  new_email=new_email)
            RegisteredUser.update(self.__class__.user.user_id,
                                  new_password=new_password)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.__class__.user = RegisteredUser(
                    user_id=self.__class__.user.user_id)
                self.assertEqual(self.__class__.user.email, new_email)
                self.assertEqual(self.__class__.user.user_name, new_user_name)
                user_logged_in = RegisteredUser(email=new_email,
                                                password=new_password)
                self.assertEqual(user_logged_in, self.__class__.user)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIfTrue("failure")
    def test_07_json_ready(self):
        try:
            json_ready_dict = self.__class__.user.json_ready
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_dict["user_id"],
                                 self.__class__.user.user_id)
                self.assertEqual(json_ready_dict["user_name"],
                                 self.__class__.user.user_name)
                self.assertEqual(json_ready_dict["user_type"],
                                 self.__class__.user.user_type)
                self.assertEqual(json_ready_dict["email"],
                                 self.__class__.user.email)
                self.assertEqual(json_ready_dict["timestamp"],
                                 self.__class__.user.timestamp)
                self.assertEqual(json_ready_dict["deleted_timestamp"],
                                 self.__class__.user.deleted_timestamp)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIfTrue("failure")
    def test_08_delete(self):
        try:
            RegisteredUser.delete(self.__class__.user.user_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                deleted_user = RegisteredUser(user_id=self.__class__.user.user_id)
                self.assertIsInstance(deleted_user.deleted_timestamp, datetime)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
