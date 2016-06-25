"""
Base Unit Test classes for handling PostgreSQL database
resetting before and after unit testing. 
"""

from datetime import datetime
from unittest import TestCase

from Knowledge_Database_App.storage import action_queries
from Knowledge_Database_App.storage import orm_core as orm


class PostgresTest(TestCase):

    @classmethod
    def setUpClass(cls):
        print("Postgres setup")
        orm._reset_database()
        cls._session = orm.start_session()
        cls.load_data()
        cls._session.close()

    @classmethod
    def load_data(cls):
        content_id = cls._session.query(orm.ContentPiece.content_id).first()
        user_id = cls._session.query(orm.User.user_id).first()
        content_type = cls._session.query(orm.ContentType).first()
        timestamp = datetime.utcnow()
        if content_type is None:
            content_type = orm.ContentType(content_type="definition")
        if user_id is None:
            user = orm.User(user_type="admin", user_name="Darth Vader", 
                email="darthvader121323@gmail.com", pass_hash="asdfasdfasdfasdf", 
                pass_hash_type="none", pass_salt="asdf", remember_id=-123,
                timestamp=timestamp)
            cls._session.add(user)
            cls._session.commit()
            user_id = user.user_id
        if content_id is None:
            content_piece = orm.ContentPiece(timestamp=timestamp, 
                last_edited_timestamp=timestamp)
            user = user if not user_id else cls._session.query(orm.User).first()
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
                "a Dark Lord of the Sith who ruled the Galactic Empire.", 
                last_edited_timestamp=timestamp, timestamp=timestamp)
            content_piece.content_type = content_type
            content_piece.keywords = [
                orm.Keyword(keyword="sith", timestamp=timestamp),
                orm.Keyword(keyword="dark side", timestamp=timestamp)
            ]
            content_piece.citations = [
                orm.Citation(citation_text="Lucas, George. Star Wars: " + 
                             "Revenge of the Sith. 2003.", timestamp=timestamp)
            ]
            cls._session.add(content_piece)
            cls._session.commit()
            content_id = content_piece.content_id

        return user_id, content_id

    @classmethod
    def tearDownClass(cls):
        print("Postgres teardown")
        orm.session_factory.close_all()
        orm._reset_database()


class StorageTest(orm.StorageHandler):
    """
    Base class for storage tests. Automatically manages sessions and
    resets the Postgres database after each test.
    """

    def setup(self):
        self.session = orm.start_session()
        self.session.begin_nested()
        user_id = self.session.query(orm.User.user_id).first()
        content_id = self.session.query(orm.ContentPiece.content_id).first()
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

    def call(self, function, *args, **kwargs):
        if function.__name__ in dir(action_queries):
            self.session.begin_nested()
        return super().call(function, *args, **kwargs)

    def teardown(self):
        self.session.rollback()
        self._close()
