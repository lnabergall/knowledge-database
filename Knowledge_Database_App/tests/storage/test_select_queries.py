
from unittest import TestCase

import Knowledge_Database_App.storage.select_queries as select
import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class SelectQueryTest(TestCase, StorageTest):

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def get_sample_ids(self):
        ids = self.session.query(
            orm.ContentPiece.content_id,
            orm.User.user_id,
            orm.Text.text_id,
            orm.Name.name_id,
            orm.Citation.citation_id,
            orm.Keyword.keyword_id,
            orm.AcceptedEdit.edit_id,
            orm.RejectedEdit.edit_id,
            orm.Vote.vote_id,
            orm.UserReport.report_id).first()
        if not ids:
            return
        else:
            return {
                "content_id": ids[0],
                "user_id": ids[1],
                "text_id": ids[2],
                "name_id": ids[3],
                "citation_id": ids[4],
                "keyword_id": ids[5],
                "accepted_edit_id": ids[6],
                "rejected_edit_id": ids[7],
                "vote_id": ids[8],
                "report_id": ids[9],
            }

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
        ids = self.get_sample_ids()
        if not ids:
            return
        else:
            results = []
            try:
                results.append(self.call(select.get_accepted_edits,
                                         content_id=ids["content_id"]))
                results.append(self.call(select.get_accepted_edits,
                                         edit_id=ids["accepted_edit_id"]))
                results.append(self.call(select.get_accepted_edits,
                                         user_id=ids["user_id"]))
                results.append(self.call(select.get_accepted_edits,
                                         text_id=ids["text_id"]))
                results.append(self.call(select.get_accepted_edits,
                                         name_id=ids["name_id"]))
                results.append(self.call(select.get_accepted_edits,
                                         citation_id=ids["citation_id"]))
                results.append(self.call(select.get_accepted_edits,
                                         keyword_id=ids["keyword_id"]))
            except Exception as e:
                self.fail(str(e))
            else:
                for i in range(len(results)):
                    if i == 1:
                        self.assertIsInstance(results[i], orm.AcceptedEdit)
                        continue
                    self.assertIsInstance(results[i], list)
                    if results[i]:
                        self.assertIsInstance(results[i][-1], orm.AcceptedEdit)

    def test_get_rejected_edits(self):
        ids = self.get_sample_ids()
        if not ids:
            return
        else:
            results = []
            try:
                results.append(self.call(select.get_rejected_edits,
                                         content_id=ids["content_id"]))
                results.append(self.call(select.get_rejected_edits,
                                         edit_id=ids["rejected_edit_id"]))
                results.append(self.call(select.get_rejected_edits,
                                         user_id=ids["user_id"]))
                results.append(self.call(select.get_rejected_edits,
                                         text_id=ids["text_id"]))
                results.append(self.call(select.get_rejected_edits,
                                         name_id=ids["name_id"]))
                results.append(self.call(select.get_rejected_edits,
                                         citation_id=ids["citation_id"]))
                results.append(self.call(select.get_rejected_edits,
                                         keyword_id=ids["keyword_id"]))
            except Exception as e:
                self.fail(str(e))
            else:
                for i in range(len(results)):
                    if i == 1:
                        self.assertIsInstance(results[i], orm.RejectedEdit)
                        continue
                    self.assertIsInstance(results[i], list)
                    if results[i]:
                        self.assertIsInstance(results[i][-1], orm.RejectedEdit)

    def test_user_votes(self):
        id_tuple = self.session.query(orm.User.user_id).first()
        if not id_tuple:
            return
        else:
            try:
                votes = self.call(select.get_user_votes, id_tuple[0])
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(votes, list)
                if votes:
                    self.assertIsInstance(votes[-1], orm.Vote)

    def test_get_accepted_votes(self):
        ids = self.get_sample_ids()
        if not ids:
            return
        else:
            results = []
            try:
                results.append(self.call(select.get_accepted_votes,
                                         content_id=ids["content_id"]))
                results.append(self.call(select.get_accepted_votes,
                                         edit_id=ids["accepted_edit_id"]))
                results.append(self.call(select.get_accepted_votes,
                                         vote_id=ids["vote_id"]))
                results.append(self.call(select.get_accepted_votes,
                                         user_id=ids["user_id"]))
            except Exception as e:
                self.fail(str(e))
            else:
                for i in range(len(results)):
                    if i == 1 or 1 == 2:
                        self.assertIsInstance(results[i], orm.Vote)
                    else:
                        self.assertIsInstance(results[i], list)
                        self.assertIsInstance(results[i][-1], orm.Vote)

    def test_get_rejected_votes(self):
        ids = self.get_sample_ids()
        if not ids:
            return
        else:
            results = []
            try:
                results.append(self.call(select.get_rejected_votes,
                                         content_id=ids["content_id"]))
                results.append(self.call(select.get_rejected_votes,
                                         edit_id=ids["rejected_edit_id"]))
                results.append(self.call(select.get_rejected_votes,
                                         vote_id=ids["vote_id"]))
                results.append(self.call(select.get_rejected_votes,
                                         user_id=ids["user_id"]))
            except Exception as e:
                self.fail(str(e))
            else:
                for i in range(len(results)):
                    if i == 1 or 1 == 2:
                        self.assertIsInstance(results[i], orm.Vote)
                    else:
                        self.assertIsInstance(results[i], list)
                        self.assertIsInstance(results[i][-1], orm.Vote)
