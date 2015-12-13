"""

"""

from unittest import TestCase
from datetime import datetime

import Knowledge_Database_App.storage.action_queries as action
import Knowledge_Database_App.storage.orm_core as orm
from . import StorageTest


class ActionQueryTest(TestCase, StorageTest):

    def __init__(self):
        super().__init__()
        self.test_data = {
            "user_id": self.session.query(orm.User.user_id).first(),
            "content_id": self.session.query(
                orm.ContentPiece.content_id).first(),
            "name_id": self.session.query(orm.Name.name_id).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"],
                orm.Name.name_type == "alternate").first(),
            "text_id": self.session.query(orm.Text.text_id).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).first(),
            "keyword_id": self.session.query(orm.Keyword.keyword_id).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).first(),
            "citation_id": self.session.query(orm.Citation.citation_id).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).first(),
            "name": orm.Name(name="The Force", name_type="primary",
                             timestamp=datetime.utcnow()),
            "text": orm.Text(text="The Force surrounds us and penetrates us. " +
                "It binds the galaxy together.", timestamp=datetime.utcnow()),
            "content_type": self.session.query(orm.ContentType).first(),
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
            "edit_text": "This is an edit.",
            "edit_rationale": "Unlimited power.",
            "vote_string": "This is a vote.",
            "voter_ids": self.session.query(orm.User.user_id).join(
                orm.User.pieces).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).all(),
            "user_name": "Vader",
            "email": "vader@empire.gov",
            "pass_hash": "12345",
            "pass_hash_type": "MD5",
            "pass_salt": "123",
        }

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def test_store_content_piece(self):
        timestamp = datetime.utcnow()
        try:
            self.call(action.store_content_piece, self.test_data["user_id"],
                      self.test_data["name"], self.test_data["text"],
                      self.test_data["content_type"], self.test_data["keywords"],
                      timestamp, citations=self.test_data["citations"],
                      alternate_names=self.test_data["alternate_names"])
        except Exception as e:
            self.fail(str(e))
        else:
            results = self.session.query(orm.ContentPiece).join(
                orm.ContentPiece.name).filter(
                orm.Name.name == self.test_data["name"]).all()
            self.assertEqual(len(results), 1)
            content_piece = results[0]
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
                orm.ContentPiece.deleted_timestamp == None).all()
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
                             self.test_data["content_type"])

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
                orm.Name).join(orm.ContentPiece).filter(
                orm.ContentPiece.content_id == self.test_data["content_id"],
                orm.Name.name_type == "alternate").all()
            keywords = self.session.query(orm.Keyword).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).all()
            citations = self.session.query(orm.Citation).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).all()
            self.assertIn(self.test_data["alternate_names"][0].name,
                          [name.name for name in alternate_names])
            self.assertIn(self.test_data["keywords"][0].keyword,
                          [keyword.keyword for keyword in keywords])
            self.assertIn(self.test_data["citations"][0].citation_text,
                          [citation.citation_text for citation in citations])

    def remove_content_part(self):
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
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).all()
            citations = self.session.query(orm.Citation).join(
                orm.ContentPiece).filter(orm.ContentPiece.content_id
                == self.test_data["content_id"]).all()
            alternate_names = self.session.query(
                orm.Name).join(orm.ContentPiece).filter(
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


