
from unittest import TestCase

import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class ORMTest(TestCase, StorageTest):

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def test_schema(self):
        try:
            orm._create_schema()
        except Exception as e:
            self.fail(str(e))
