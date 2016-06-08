"""
Storage Action Query API Unit Tests

Automatically manages sessions and resets the database between
tests. Currently primarily checks only core functionality of all
functions, not exceptional cases.
"""

from unittest import TestCase
from datetime import datetime
from time import sleep
from contextlib import contextmanager

import Knowledge_Database_App.storage.action_queries as action
import Knowledge_Database_App.storage.select_queries as select
import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class ActionQueryTest(TestCase, StorageTest):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        StorageTest.__init__(self)
        user_id, content_id = self.load_data()
        self.test_data = {
            "user_id": user_id,
            "content_id": content_id,
            "name_id": self.session.query(orm.Name.name_id).join(
                orm.ContentPiece, orm.Name.piece).filter(
                orm.ContentPiece.content_id == content_id,
                orm.Name.name_type == "alternate").first(),
            "text_id": self.session.query(orm.Text.text_id).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == content_id).first(),
            "keyword_id": self.session.query(orm.Keyword.keyword_id).join(
                orm.ContentPiece, orm.Keyword.pieces).filter(
                orm.ContentPiece.content_id == content_id).first(),
            "citation_id": self.session.query(orm.Citation.citation_id).join(
                orm.ContentPieceCitation, orm.Citation.citation_content_pieces).filter(
                orm.ContentPieceCitation.content_id == content_id).first(),
            "name": orm.Name(name="The Force", name_type="primary",
                             timestamp=datetime.utcnow()),
            "text": orm.Text(text="The Force surrounds us and penetrates us. " +
                "It binds the galaxy together.", timestamp=datetime.utcnow()),
            "content_type": orm.ContentType(content_type="theorem"),
            "keywords": [orm.Keyword(keyword="Star Wars",
                                     timestamp=datetime.utcnow()),
                         orm.Keyword(keyword="Invisible force",
                                     timestamp=datetime.utcnow())],
            "citations": [orm.Citation(citation_text="Lucas, George. " +
                                       "Star Wars: A New Hope. 1977.",
                                       timestamp=datetime.utcnow())],
            "alternate_names": [orm.Name(name="Power",
                                         name_type="alternate",
                                         timestamp=datetime.utcnow())],
            "redis_edit_id": -42,
            "edit_text": "This is an edit.",
            "applied_edit_text": "This is an edit.",
            "edit_rationale": "Unlimited power.",
            "vote_string": "This is a vote.",
            "voter_ids": self.session.query(orm.User.user_id).join(
                orm.User.pieces).filter(
                orm.ContentPiece.content_id == content_id).all(),
            "user_name": "Vader",
            "email": "vader@empire.gov",
            "pass_hash": "12345",
            "pass_hash_type": "MD5",
            "pass_salt": "123",
        }

    def load_data(self):
        content_id = self.session.query(orm.ContentPiece.content_id).first()
        user_id = self.session.query(orm.User.user_id).first()
        content_type = self.session.query(orm.ContentType).first()
        timestamp = datetime.utcnow()
        if content_type is None:
            content_type = orm.ContentType(content_type="definition")
        if user_id is None:
            user = orm.User(user_type="admin", user_name="Darth Vader", 
                email="darthvader121323@gmail.com", pass_hash="asdfasdfasdfasdf", 
                pass_hash_type="none", pass_salt="asdf", remember_id=-123,
                timestamp=timestamp)
            self.session.add(user)
            self.session.commit()
            user_id = user.user_id
        if content_id is None:
            content_piece = orm.ContentPiece(timestamp=timestamp, 
                last_edited_timestamp=timestamp)
            user = user if not user_id else self.session.query(orm.User).first()
            content_piece.first_author = user
            content_piece.authors.append(user)
            content_piece.name = orm.Name(name="Emperor Palpatine", 
                name_type="primary", last_edited_timestamp=timestamp, 
                timestamp=timestamp)
            content_piece.alternate_names = [
                orm.Name(name="Darth Sidious", name_type="alternate", 
                         last_edited_timestamp=timestamp, timestamp=timestamp)
                ]
            content_piece.text = orm.Text(text="Emperor Sheev Palpatine was " + 
                "a Dark Lord of the Sith.", last_edited_timestamp=timestamp, 
                timestamp=timestamp)
            content_piece.content_type = content_type
            content_piece.keywords = [
                orm.Keyword(keyword="sith", timestamp=timestamp),
                orm.Keyword(keyword="dark side", timestamp=timestamp)
            ]
            content_piece.citations = [
                orm.Citation(citation_text="Lucas, George. Star Wars:" + 
                             "Revenge of the Sith. 2003.", timestamp=timestamp)
            ]
            self.session.add(content_piece)
            self.session.commit()
            content_id = content_piece.content_id

        return user_id, content_id

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    @contextmanager
    def nested_session(self):
        self.session.begin_nested()
        yield
        self.session.rollback()
    
    def test_store_content_piece(self):
        timestamp = datetime.utcnow()
        try:
            content_id = self.call(action.store_content_piece, self.test_data["user_id"],
                self.test_data["name"], self.test_data["text"],
                self.test_data["content_type"], self.test_data["keywords"],
                timestamp, citations=self.test_data["citations"],
                alternate_names=self.test_data["alternate_names"])
        except Exception as e:
            self.fail(str(e))
        else:
            content_piece = self.session.query(orm.ContentPiece).filter(
                orm.ContentPiece.content_id == content_id).one()
            self.assertEqual(content_piece.text, self.test_data["text"])
            self.assertEqual(content_piece.content_type,
                             self.test_data["content_type"])
            self.assertEqual(content_piece.first_author_id,
                             self.test_data["user_id"])
            self.assertEqual(content_piece.keywords, self.test_data["keywords"])
            self.assertEqual(content_piece.citations, self.test_data["citations"])
            self.assertEqual(content_piece.alternate_names,
                             self.test_data["alternate_names"])
            self.assertEqual(content_piece.timestamp, timestamp)

    def test_delete_content_piece(self):
        deleted_timestamp = datetime.utcnow()
        try:
            self.call(action.delete_content_piece, self.test_data["content_id"],
                      deleted_timestamp)
        except Exception as e:
            self.fail(str(e))
        else:
            results = self.session.query(orm.ContentPiece).filter(
                orm.ContentPiece.content_id == self.test_data["content_id"],
                orm.ContentPiece.deleted_timestamp.is_(None)).all()
            self.assertEqual(results, [])

    def test_update_content_type(self):
        try:
            self.call(action.update_content_type, self.test_data["content_id"],
                      self.test_data["content_type"])
        except Exception as e:
            self.fail(str(e))
        else:
            content_type = self.session.query(orm.ContentType).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).first()
            self.assertEqual(content_type.content_type,
                             self.test_data["content_type"].content_type)

    def test_store_content_part(self):
        try:
            self.call(action.store_content_part,
                      self.test_data["alternate_names"][0],
                      self.test_data["content_id"])
            self.call(action.store_content_part, self.test_data["keywords"][0],
                      self.test_data["content_id"])
            self.call(action.store_content_part, self.test_data["citations"][0],
                      self.test_data["content_id"])
        except Exception as e:
            self.fail(str(e))
        else:
            alternate_names = self.session.query(
                orm.Name).join(orm.ContentPiece, orm.Name.piece).filter(
                orm.ContentPiece.content_id == self.test_data["content_id"],
                orm.Name.name_type == "alternate").all()
            keywords = self.session.query(orm.Keyword).join(
                orm.ContentPiece, orm.Keyword.pieces).filter(
                orm.ContentPiece.content_id == self.test_data["content_id"]).all()
            citations = self.session.query(orm.Citation).join(
                orm.ContentPieceCitation, orm.Citation.citation_content_pieces).filter(
                orm.ContentPieceCitation.content_id == self.test_data["content_id"]).all()
            self.assertIn(self.test_data["alternate_names"][0].name,
                          [name.name for name in alternate_names])
            self.assertIn(self.test_data["keywords"][0].keyword,
                          [keyword.keyword for keyword in keywords])
            self.assertIn(self.test_data["citations"][0].citation_text,
                          [citation.citation_text for citation in citations])

    def test_remove_content_part(self):
        try:
            self.call(action.remove_content_part, self.test_data["content_id"],
                      self.test_data["keyword_id"], "keyword")
            self.call(action.remove_content_part, self.test_data["content_id"],
                      self.test_data["citation_id"], "citation")
            self.call(action.remove_content_part, self.test_data["content_id"],
                      self.test_data["name_id"], "name")
        except Exception as e:
            self.fail(str(e))
        else:
            keywords = self.session.query(orm.Keyword).join(
                orm.ContentPiece, orm.Keyword.pieces).filter(
                orm.ContentPiece.content_id == self.test_data["content_id"]).all()
            citations = self.session.query(orm.Citation).join(
                orm.ContentPieceCitation, 
                orm.Citation.citation_content_pieces).filter(
                orm.ContentPieceCitation.content_id 
                == self.test_data["content_id"]).all()
            alternate_names = self.session.query(
                orm.Name).join(orm.ContentPiece, orm.Name.piece).filter(
                orm.ContentPiece.content_id == self.test_data["content_id"],
                orm.Name.name_type == "alternate").all()
            self.assertNotIn(self.test_data["keyword_id"],
                             [keyword.keyword_id for keyword in keywords])
            self.assertNotIn(self.test_data["citation_id"],
                             [citation.citation_id for citation in citations])
            self.assertNotIn(self.test_data["name_id"],
                             [name.name_id for name in alternate_names])

    def test_update_content_part(self):
        try:
            self.call(action.update_content_part, self.test_data["name_id"],
                      "name", self.test_data["name"].name)
            self.call(action.update_content_part, self.test_data["text_id"],
                      "text", self.test_data["text"].text)
        except Exception as e:
            self.fail(str(e))
        else:
            name_string = self.session.query(orm.Name.name).filter(
                orm.Name.name_id == self.test_data["name_id"]).first()
            text_string = self.session.query(orm.Text.text).filter(
                orm.Text.text_id == self.test_data["text_id"]).first()
            self.assertEqual(name_string, self.test_data["name"].name)
            self.assertEqual(text_string, self.test_data["text"].text)
    
    def test_store_accepted_edit(self):
        timestamp = datetime.utcnow()
        try:
            self.call(action.store_accepted_edit, self.test_data["redis_edit_id"], 
                self.test_data["edit_text"], self.test_data["applied_edit_text"], 
                self.test_data["edit_rationale"], "name", 
                self.test_data["name_id"], self.test_data["content_id"], 
                self.test_data["vote_string"], self.test_data["voter_ids"], 
                timestamp, timestamp, timestamp, "U", self.test_data["user_id"])
            self.call(action.store_accepted_edit, self.test_data["redis_edit_id"]-1,
                self.test_data["edit_text"], self.test_data["applied_edit_text"], 
                self.test_data["edit_rationale"], "text", 
                self.test_data["text_id"], self.test_data["content_id"],
                self.test_data["vote_string"], self.test_data["voter_ids"],
                timestamp, timestamp, timestamp, "U", self.test_data["user_id"])
            self.call(action.store_accepted_edit, self.test_data["redis_edit_id"]-2,
                self.test_data["edit_text"], self.test_data["applied_edit_text"], 
                self.test_data["edit_rationale"], "keyword", 
                self.test_data["keyword_id"], self.test_data["content_id"], 
                self.test_data["vote_string"], self.test_data["voter_ids"], 
                timestamp, timestamp, timestamp, "U", self.test_data["user_id"])
            self.call(action.store_accepted_edit, self.test_data["redis_edit_id"]-3,
                self.test_data["edit_text"], self.test_data["applied_edit_text"], 
                self.test_data["edit_rationale"], "citation", 
                self.test_data["citation_id"], self.test_data["content_id"], 
                self.test_data["vote_string"], self.test_data["voter_ids"], 
                timestamp, timestamp, timestamp, "U", self.test_data["user_id"])
        except Exception as e:
            self.fail(str(e))
        else:
            name_accepted_edits = select.get_accepted_edits(
               name_id=self.test_data["name_id"], session=self.session)
            text_accepted_edits = select.get_accepted_edits(
                text_id=self.test_data["text_id"], session=self.session)
            keyword_accepted_edits = select.get_accepted_edits(
                keyword_id=self.test_data["keyword_id"], session=self.session)
            citation_accepted_edits = select.get_accepted_edits(
                citation_id=self.test_data["citation_id"], session=self.session)
            self.assertIn(self.test_data["edit_text"],
                         [edit.edit_text for edit in name_accepted_edits])
            self.assertIn(self.test_data["edit_text"],
                          [edit.edit_text for edit in text_accepted_edits])
            self.assertIn(self.test_data["edit_text"],
                          [edit.edit_text for edit in keyword_accepted_edits])
            self.assertIn(self.test_data["edit_text"],
                          [edit.edit_text for edit in citation_accepted_edits])
    
    def test_store_rejected_edit(self):
        timestamp = datetime.utcnow()
        try:
            self.call(action.store_rejected_edit, self.test_data["redis_edit_id"]-4,
                self.test_data["edit_text"], self.test_data["edit_rationale"], 
                "name", self.test_data["name_id"], self.test_data["content_id"],
                self.test_data["vote_string"], self.test_data["voter_ids"],
                timestamp, timestamp, "U", self.test_data["user_id"])
            self.call(action.store_rejected_edit, self.test_data["redis_edit_id"]-5,
                self.test_data["edit_text"], self.test_data["edit_rationale"], 
                "text", self.test_data["text_id"], self.test_data["content_id"],
                self.test_data["vote_string"], self.test_data["voter_ids"],
                timestamp, timestamp, "U", self.test_data["user_id"])
            self.call(action.store_rejected_edit, self.test_data["redis_edit_id"]-6,
                self.test_data["edit_text"], self.test_data["edit_rationale"], 
                "keyword", self.test_data["keyword_id"], self.test_data["content_id"],
                self.test_data["vote_string"], self.test_data["voter_ids"],
                timestamp, timestamp, "U", self.test_data["user_id"])
            self.call(action.store_rejected_edit, self.test_data["redis_edit_id"]-7,
                self.test_data["edit_text"], self.test_data["edit_rationale"], 
                "citation", self.test_data["citation_id"], self.test_data["content_id"],
                self.test_data["vote_string"], self.test_data["voter_ids"],
                timestamp, timestamp, "U", self.test_data["user_id"])
        except Exception as e:
            self.fail(str(e))
        else:
            name_rejected_edits = select.get_rejected_edits(
                name_id=self.test_data["name_id"], session=self.session)
            text_rejected_edits = select.get_rejected_edits(
                text_id=self.test_data["text_id"], session=self.session)
            keyword_rejected_edits = select.get_rejected_edits(
                keyword_id=self.test_data["keyword_id"], session=self.session)
            citation_rejected_edits = select.get_rejected_edits(
                citation_id=self.test_data["citation_id"], session=self.session)
            self.assertIn(self.test_data["edit_text"],
                          [edit.edit_text for edit in name_rejected_edits])
            self.assertIn(self.test_data["edit_text"],
                          [edit.edit_text for edit in text_rejected_edits])
            self.assertIn(self.test_data["edit_text"],
                          [edit.edit_text for edit in keyword_rejected_edits])
            self.assertIn(self.test_data["edit_text"],
                          [edit.edit_text for edit in citation_rejected_edits])

    def test_store_new_user(self):
        timestamp = datetime.utcnow()
        remember_id = -467
        try:
            self.call(action.store_new_user, "standard",
                      self.test_data["user_name"], self.test_data["email"],
                      self.test_data["pass_hash"], self.test_data["pass_hash_type"],
                      self.test_data["pass_salt"], remember_id, timestamp)
        except Exception as e:
            self.fail(str(e))
        else:
            try:
                user = select.get_user(email=self.test_data["email"], 
                                       session=self.session)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertEqual(user.user_name, self.test_data["user_name"])
                self.assertEqual(user.pass_hash, self.test_data["pass_hash"])
                self.assertEqual(user.pass_salt, self.test_data["pass_salt"])
                self.assertEqual(user.remember_id, remember_id)

    def test_update_user(self):
        confirmed_timestamp = datetime.utcnow()
        new_remember_token_hash = "abc"
        try:
            self.call(action.update_user, self.test_data["user_id"],
                      new_user_name=self.test_data["user_name"])
            self.call(action.update_user, self.test_data["user_id"],
                      new_email=self.test_data["email"])
            self.call(action.update_user, self.test_data["user_id"],
                      confirmed_timestamp=confirmed_timestamp)
            self.call(action.update_user, self.test_data["user_id"],
                      new_pass_hash=self.test_data["pass_hash"],
                      new_pass_hash_type=self.test_data["pass_hash_type"],
                      new_pass_salt=self.test_data["pass_salt"])
            self.call(action.update_user, self.test_data["user_id"],
                      new_remember_token_hash=new_remember_token_hash,
                      new_remember_hash_type=self.test_data["pass_hash_type"])
        except Exception as e:
            self.fail(str(e))
        else:
            try:
                user = select.get_user(email=self.test_data["email"],
                                       session=self.session)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertEqual(user.user_name, self.test_data["user_name"])
                self.assertEqual(user.pass_hash, self.test_data["pass_hash"])
                self.assertEqual(user.pass_salt, self.test_data["pass_salt"])
                self.assertEqual(user.pass_hash_type,
                                 self.test_data["pass_hash_type"])
                self.assertEqual(user.remember_token_hash, new_remember_token_hash)
                self.assertEqual(user.remember_hash_type,
                                 self.test_data["pass_hash_type"])
                self.assertEqual(user.confirmed_timestamp, confirmed_timestamp)

    def test_store_user_report(self):
        report_text = "This is a report."
        admin_report = "This is an admin report."
        timestamp = datetime.utcnow()
        admin_id = self.session.query(orm.User.user_id).filter(
            orm.User.user_type == "admin").first()
        try:
            self.call(action.store_user_report, self.test_data["content_id"],
                      report_text, "content", admin_report, timestamp,
                      timestamp, admin_id, "U", self.test_data["user_id"])
        except Exception as e:
            self.fail(str(e))
        else:
            try:
                user_reports = select.get_user_reports(
                    content_id=self.test_data["content_id"], session=self.session)
            except Exception as e:
                self.fail(str(e))
            else:
                self.assertIn(report_text, [report.report_text
                                            for report in user_reports])
                self.assertIn(self.test_data["user_id"],
                              [report.author_id for report in user_reports])
