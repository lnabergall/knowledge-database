"""
User Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase, skipIf

from Knowledge_Database_App.user.user import RegisteredUser


class UserTest(TestCase):

    def setUp(self):
        self.user_name = "Kylo Ren"
        self.email = "kyloren@gmail.com"
        self.password = "darthvader123"
        self.failure = False
        self.stored = False

    def tearDown(self):
        if not self.failure:
            pass

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_01_create(self):
        try:
            self.user = RegisteredUser(
                email=self.email, password=self.password,
                user_name=self.user_name)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(user.email, self.email)
                self.assertEqual(user.user_name, self.user_name)
                self.assertNotEqual(user.pass_hash, self.password)
                self.assertIsInstance(user.pass_hash_type, str)
                self.assertEqual(user.user_type, "standard")
                self.assertIsNotNone(user.remember_id)
                self.assertIsInstance(user.timestamp, datetime)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_02_register(self):
        try:
            self.confirmation_id = self.user.register()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.user.user_id, int)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_03_login(self):
        try:
            user_from_id = RegisteredUser(user_id=self.user.user_id)
            user_from_login = RegisteredUser(email=self.email,
                                             password=self.password)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.user, user_from_id)
                self.assertEqual(self.user, user_from_login)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_04_process_confirm(self):
        try:
            RegisteredUser.process_confirm(self.email, self.confirmation_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                confirmed_user = RegisteredUser(user_id=self.user.user_id)
                self.assertIsInstance(confirmed_user.confirmed_timestamp, datetime)
            except AssertionError:
                self.failure = True
                raise
            else:
                self.user = confirmed_user

    @skipIf(self.failure, "Necessary previous test failed!")
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
                    remember_id=self.user_with_remember.remember_id,
                    remember_token=self.user_with_remember.remember_token)
                self.assertEqual(user, self.user)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_06_update(self):
        try:
            pass
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                pass
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_07_json_ready(self):
        try:
            pass
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                pass
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_08_delete(self):
        try:
            pass
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                pass
            except AssertionError:
                self.failure = True
                raise
