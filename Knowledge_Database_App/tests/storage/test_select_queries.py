
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
        if not id_tuple:
            return
        else:
            try:
                content_piece = self.call(select.get_content_piece, id_tuple[0])
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(content_piece, orm.ContentPiece)
                self.assertEquals(content_piece.content_id, id_tuple[0])

    def test_get_alternate_names(self):
        id_tuple = self.session.query(orm.ContentPiece.content_id).first()
        if not id_tuple:
            return
        else:
            try:
                alternate_names = self.call(
                    select.get_alternate_names, id_tuple[0])
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(alternate_names, list)
                if alternate_names:
                    self.assertIsInstance(alternate_names[-1], orm.Name)

    def test_get_content_types(self):
        try:
            content_types = self.call(select.get_content_types)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(content_types, list)
            if content_types:
                self.assertIsInstance(content_types[-1], orm.ContentType)

    def test_get_accepted_edits(self):
        ids = self.session.query(orm.ContentPiece.content_id,
            orm.AcceptedEdit.edit_id, orm.User.user_id, orm.Text.text_id,
            orm.Name.name_id, orm.Citation.citation_id,
            orm.Keyword.keyword_id).first()
        if not ids:
            return
        else:
            results = []
            try:
                results.append(self.call(select.get_accepted_edits,
                                         content_id=ids[0]))
                results.append(self.call(select.get_accepted_edits,
                                         edit_id=ids[1]))
                results.append(self.call(select.get_accepted_edits,
                                         user_id=ids[2]))
                results.append(self.call(select.get_accepted_edits,
                                         text_id=ids[3]))
                results.append(self.call(select.get_accepted_edits,
                                         name_id=ids[4]))
                results.append(self.call(select.get_accepted_edits,
                                         citation_id=ids[5]))
                results.append(self.call(select.get_accepted_edits,
                                         keyword_id=ids[6]))
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(results[1], orm.AcceptedEdit)
                self.assertIsInstance(results[0], list)
                if results[0]:
                    self.assertIsInstance(results[0][-1], orm.AcceptedEdit)
                for i in range(2, len(results)):
                    self.assertIsInstance(results[i], list)
                    if results[i]:
                        self.assertIsInstance(results[i][-1], orm.AcceptedEdit)
