"""
Storage Select Query API Unit Tests

Automatically manages sessions and resets the database between
tests. Currently primarily checks only core functionality of all
functions, not exceptional cases.
"""

from unittest import TestCase

import Knowledge_Database_App.storage.select_queries as select
import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class SelectQueryTest(TestCase, StorageTest):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        StorageTest.__init__(self)

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
        id_ = self.session.query(orm.ContentPiece.content_id).first()
        if not id_:
            return
        else:
            try:
                content_piece = self.call(select.get_content_piece, id_)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(content_piece, orm.ContentPiece)
                self.assertEqual(content_piece.content_id, id_)

    def test_get_alternate_names(self):
        id_ = self.session.query(orm.ContentPiece.content_id).first()
        if not id_:
            return
        else:
            try:
                alternate_names = self.call(
                    select.get_alternate_names, id_)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(alternate_names, list)
                if alternate_names:
                    self.assertIsInstance(alternate_names[-1], orm.Name)

    def test_get_keyword(self):
        keyword_string = self.session.query(orm.Keyword.keyword).first()
        if not keyword_string:
            return
        else:
            try:
                keyword = self.call(select.get_keyword, keyword_string)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(keyword, orm.Keyword)
                self.assertEqual(keyword.keyword, keyword_string)

    def test_get_citation(self):
        citation_string = self.session.query(orm.Citation.citation_text).first()
        if not citation_string:
            return
        else:
            try:
                citation = self.call(select.get_citation, citation_string)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(citation, orm.Citation)
                self.assertEqual(citation.citation_text, citation_string)

    def test_get_content_type(self):
        content_type_string = self.session.query(
            orm.ContentType.content_type).first()
        if not content_type_string:
            return
        else:
            try:
                content_type = self.call(select.get_content_type,
                                         content_type_string)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(content_type, orm.ContentType)
                self.assertEqual(content_type.content_type, content_type_string)

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
        id_ = self.session.query(orm.User.user_id).first()
        if not id_:
            return
        else:
            try:
                votes = self.call(select.get_user_votes, id_)
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

    def test_get_user_encrypt_info(self):
        email = self.session.query(orm.User.email).first()
        remember_id = self.session.query(orm.User.remember_id).first()
        if not email:
            return
        else:
            try:
                info_with_email = self.call(select.get_user_encrypt_info,
                                            email=email)
                info_with_id = self.call(select.get_user_encrypt_info,
                                         remember_id=remember_id)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(info_with_email, tuple)
                self.assertIsInstance(info_with_id, tuple)
                self.assertIsInstance(info_with_email[0], (str, type(None)))
                self.assertIsInstance(info_with_email[1], (str, type(None)))
                self.assertIsInstance(info_with_email[2], (str, type(None)))
                self.assertIsInstance(info_with_id[0], (str, type(None)))
                self.assertIsInstance(info_with_id[1], (str, type(None)))
                self.assertIsInstance(info_with_id[2], (str, type(None)))

    def test_get_user(self):
        parameters = self.session.query(orm.User.user_id, orm.User.email,
                                        orm.User.pass_hash, orm.User.remember_id,
                                        orm.User.remember_token_hash).first()
        if not parameters:
            return
        else:
            user_id, email, pass_hash, remember_id, remember_token_hash \
                = parameters
            try:
                user_from_email = self.call(select.get_user, email=email,
                                            pass_hash=pass_hash)
                user_from_remember = self.call(select.get_user,
                    remember_id=remember_id,
                    remember_token_hash=remember_token_hash)
                user_from_id = self.call(select.get_user, user_id=user_id)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(user_from_email, orm.User)
                self.assertIsInstance(user_from_remember, orm.User)
                self.assertIsInstance(user_from_id, orm.User)
                self.assertEqual(user_from_email, user_from_remember)
                self.assertEqual(user_from_remember, user_from_id)

    def test_get_user_emails(self):
        ids = self.get_sample_ids()
        if not ids:
            return
        else:
            try:
                emails = self.call(select.get_user_emails,
                                   content_id=ids["content_id"])
                email_accepted = self.call(select.get_user_emails,
                    accepted_edit_id=ids["accepted_edit_id"])
                email_rejected = self.call(select.get_user_emails,
                    rejected_edit_id=ids["rejected_edit_id"])
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIsInstance(emails, list)
                self.assertIsInstance(emails[-1], str)
                self.assertIn("@", emails[-1])
                self.assertIsInstance(email_accepted, str)
                self.assertIn("@", email_accepted)
                self.assertIsInstance(email_rejected, str)
                self.assertIn("@", email_rejected)

    def test_get_user_reports(self):
        ids = self.get_sample_ids()
        admin_id = self.session.query(orm.User.user_id).filter(
                orm.User.user_type == "admin").first()
        if not ids or not admin_id:
            return
        else:
            results = []
            try:
                results.append(self.call(select.get_user_reports,
                                         content_id=ids["content_id"]))
                results.append(self.call(select.get_user_reports,
                                         report_id=ids["report_id"]))
                results.append(self.call(select.get_user_reports,
                                         user_id=ids["user_id"]))
                results.append(self.call(select.get_user_reports,
                                         admin_id=admin_id))
            except Exception as e:
                self.fail(str(e))
            else:
                for i in range(len(results)):
                    if i == 1:
                        self.assertIsInstance(results[i], orm.UserReport)
                    else:
                        self.assertIsInstance(results[i], list)
                        self.assertIsInstance(results[i][-1], orm.UserReport)
