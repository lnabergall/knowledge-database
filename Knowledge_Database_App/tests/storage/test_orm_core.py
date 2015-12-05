
from unittest import TestCase

import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class ORMTest(TestCase, StorageTest):

    def setUp(self):
        super().setup()

    def tearDown(self):
        super().teardown()

    def test_schema(self):
        try:
            orm.create_schema()
        except Exception as e:
            self.fail(str(e))