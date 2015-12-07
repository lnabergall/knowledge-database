
from unittest import TestCase

import Knowledge_Database_App.storage.select_queries as select
import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class SelectQueryTest(TestCase, StorageTest):

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def test_get_content_piece(self):
        id_tuple = self.session.query(orm.ContentPiece.content_id).first()
        if id_tuple is None:
            return
        else:
            try:
                content_piece = self.call(select.get_content_piece, id_tuple[0])
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(content_piece, orm.ContentPiece)
                self.assertEquals(content_piece.content_id, id_tuple[0])
