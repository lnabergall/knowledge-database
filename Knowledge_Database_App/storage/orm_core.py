"""
Contains the core classes and functions used to interact with the
Postgres database, in particular mapping classes defining the database
scheme. Uses SQLAlchemy.

Functions:

    create_scheme -
        Creates the database scheme from the ORM classes.

    start_session -
        Starts a session for interacting with the database.
        Returns: session object

Classes:

    StorageHandler, Content, Name, Text, ContentType, Keyword, Citation,
    Edit, Vote, RejectedEdit, User, UserReport

    For all classes X, the attribute 'timestamp' holds the datetime
    of creation.
"""

from sqlalchemy import (create_engine, Column, Integer,
                        DateTime, ForeignKey, Table)
from sqlalchemy import Text as Text_
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import action_queries
from select_queries import Query


KDB_url = "postgresql+psycopg2://postgres:Cetera4247@localhost/kdb_develop"
Base = declarative_base()


def create_scheme():
    engine = create_engine(KDB_url, echo=False)
    Base.metadata.create_all(engine)


def start_session():
    engine = create_engine(KDB_url, echo=False)
    return sessionmaker(bind=engine, query_cls=Query)()


class StorageHandler:
    """
    Class which handles queries made to the Postgres database.

    Call a function from select_queries or action_queries using the
    'run' method. The class features built-in session management, including
    handling commits.
    """
    def __init__(self):
        self.session = start_session()

    def run(self, function, *args, **kwargs):
        try:
            output = function(*args, session=self.session, **kwargs)
        except (NameError, ValueError, TypeError) as e:
            raise RuntimeError(str(e))
        if function.__name__ in dir(action_queries):
            self.session.commit()
        self.session.close()
        return output


# Many-to-Many relationship between Content_Piece and User
content_authors = Table("content_authors", Base.metadata,
    Column("content_id", Integer, ForeignKey("ContentPiece.content_id")),
    Column("user_id", Integer, ForeignKey("User.user_id")),
)


class ContentPiece(Base):
    __tablename__ = "Content_Piece"

    content_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    deleted_timestamp = Column(DateTime)

    # Many-to-One relationships
    first_author_id = Column(Integer, ForeignKey("User.user_id"))
    first_author = relationship("User", backref="pieces_created")

    content_type_id = Column(Integer, ForeignKey("Content_Type.content_type_id"))
    content_type = relationship("ContentType", backref="pieces")

    # One-to-One relationships
    name_id = Column(Integer, ForeignKey("Name.name_id"))
    name = relationship("Name", backref=backref("piece", uselist=False))

    text_id = Column(Integer, ForeignKey("Text.text_id"))
    text = relationship("Text", backref=backref("piece", uselist=False))

    # Many-to-Many relationships:
    authors = relationship("User", secondary=content_authors, backref="pieces")


class Name(Base):
    """name_type: 'primary' or 'alternate'."""

    __tablename__ = "Name"

    name_id = Column(Integer, primary_key=True)
    name = Column(Text_)
    name_type = Column(Text_)
    timestamp = Column(DateTime)

    # Many-to-One relationships
    content_id = Column(Integer, ForeignKey("Content_Piece.content_id"))
    piece = relationship("ContentPiece", backref="alternate_names")

    def __repr__(self):
        return "<Name(name={}, name_type={})>".format(self.name, self.name_type)


class Text(Base):
    __tablename__ = "Text"

    text_id = Column(Integer, primary_key=True)
    text = Column(Text_)
    timestamp = Column(DateTime)

    def __repr__(self):
        return "<Text(text={})>".format(self.text)


class ContentType(Base):
    __tablename__ = "Content_Type"

    content_type_id = Column(Integer, primary_key=True)
    content_type = Column(Text_, unique=True)

    def __repr__(self):
        return "<ContentType(type={})>".format(self.type)


# Many-to-Many relationship between Keyword and ContentPiece
content_keywords = Table("content_keywords", Base.metadata,
    Column("keyword_id", Integer, ForeignKey("Keyword.keyword_id")),
    Column("content_id", Integer, ForeignKey("Content_Piece.content_id")),
)


class Keyword(Base):
    __tablename__ = "Keyword"

    keyword_id = Column(Integer, primary_key=True)
    keyword = Column(Text_, unique=True, index=True)
    timestamp = Column(DateTime)

    # Many-to-Many relationships
    pieces = relationship("ContentPiece", secondary=content_keywords, 
                          backref="keywords")

    def __repr__(self):
        return "<Keyword(keyword={})>".format(self.keyword)


# Many-to-Many relationship between Citation and ContentPiece
content_citations = Table("content_citations", Base.metadata,
    Column("citation_id", Integer, ForeignKey("Citation.citation_id")),
    Column("content_id", Integer, ForeignKey("Content_Piece.content_id")),
)


class Citation(Base):
    __tablename__ = "Citation"

    citation_id = Column(Integer, primary_key=True)
    citation_text = Column(Text_, unique=True)
    timestamp = Column(DateTime)

    # Many-to-Many relationships
    pieces = relationship("ContentPiece", secondary=content_citations,
                          backref="citations")

    def __repr__(self):
        return "<Citation(citation_text={})>".format(self.citation_text)


class AcceptedEdit(Base):
    """
    content_part: 'name', 'text', 'keyword', or 'citation'.
    author_type: 'U' for registered users, IP address for anonymous users.
    acc_timestamp: datetime of acceptance of the edit.
    """

    __tablename__ = "Accepted_Edit"

    edit_id = Column(Integer, primary_key=True)
    edit_text = Column(Text_)
    edit_rationale = Column(Text_)
    content_part = Column(Text_)
    timestamp = Column(DateTime)
    acc_timestamp = Column(DateTime)
    author_type = Column(Text_)

    # Many-to-One relationships
    author_id = Column(Integer, ForeignKey("User.user_id"))
    author = relationship("User", backref="accepted_edits")

    content_id = Column(Integer, ForeignKey("Content_Piece.content_id"))
    piece = relationship("ContentPiece", backref="accepted_edits")

    name_id = Column(Integer, ForeignKey("Name.name_id"))
    name = relationship("Name", backref="accepted_edits")

    text_id = Column(Integer, ForeignKey("Text.text_id"))
    text = relationship("Text", backref="accepted_edits")

    keyword_id = Column(Integer, ForeignKey("Keyword.keyword_id"))
    keyword = relationship("Keyword", backref="accepted_edits")

    citation_id = Column(Integer, ForeignKey("Citation.citation_id"))
    citation = relationship("Citation", backref="accepted_edits")


# Many-to-Many relationship between Vote and User
user_votes = Table("user_votes", Base.metadata,
    Column("vote_id", Integer, ForeignKey("Vote.vote_id")),
    Column("user_id", Integer, ForeignKey("User.user_id")),
)


class Vote(Base):
    """
    content_part: 'name', 'text', 'keyword', or 'citation'.
    close_timestamp: datetime of the closing of the vote.
    """

    __tablename__ = "Vote"

    vote_id = Column(Integer, primary_key=True)
    vote = Column(Text_)
    content_part = Column(Text_)
    timestamp = Column(DateTime)
    close_timestamp = Column(DateTime)

    # One-to-One relationships
    accepted_edit_id = Column(Integer, ForeignKey("Accepted_Edit.edit_id"))
    accepted_edit = relationship(
        "AcceptedEdit", backref=backref("vote", uselist=False))

    rejected_edit_id = Column(Integer, ForeignKey("Rejected_Edit.edit_id"))
    rejected_edit = relationship(
        "RejectedEdit", backref=backref("vote", uselist=False))

    # Many-to-Many relationships
    voters = relationship("User", secondary=user_votes, backref="votes")


class RejectedEdit(Base):
    """
    content_part: 'name', 'text', 'keyword', or 'citation'.
    author_type: 'U' for registered users, IP address for anonymous users.
    rej_timestamp: datetime of rejection of the edit.
    """

    __tablename__ = "Rejected_Edit"

    edit_id = Column(Integer, primary_key=True)
    edit_text = Column(Text_)
    edit_rationale = Column(Text_)
    content_part = Column(Text_)
    timestamp = Column(DateTime)
    rej_timestamp = Column(DateTime)
    author_type = Column(Text_)

    # Many-to-One relationships
    author_id = Column(Integer, ForeignKey("User.user_id"))
    author = relationship("User", backref="rejected_edits")

    content_id = Column(Integer, ForeignKey("Content_Piece.content_id"))
    piece = relationship("ContentPiece", backref="accepted_edits")

    name_id = Column(Integer, ForeignKey("Name.name_id"))
    name = relationship("Name", backref="rejected_edits")

    text_id = Column(Integer, ForeignKey("Text.text_id"))
    text = relationship("Text", backref="rejected_edits")

    keyword_id = Column(Integer, ForeignKey("Keyword.keyword_id"))
    keyword = relationship("Keyword", backref="accepted_edits")

    citation_id = Column(Integer, ForeignKey("Citation.citation_id"))
    citation = relationship("Citation", backref="accepted_edits")


class User(Base):
    """user_type: 'admin' or 'standard'."""

    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True)
    user_type = Column(Text_)
    user_name = Column(Text_, index=True)
    email = Column(Text_, unique=True, index=True)
    confirmed_timestamp = Column(DateTime)
    pass_hash = Column(Text_, unique=True, index=True)
    pass_hash_type = Column(Text_)
    pass_salt = Column(Text_, unique=True, index=True)
    remember_id = Column(Integer, unique=True, index=True)
    remember_token_hash = Column(Text_, unique=True, index=True)
    remember_hash_type = Column(Text_)
    timestamp = Column(DateTime)
    deleted_timestamp = Column(DateTime)

    def __repr__(self):
        return "<User(user_name={}, user_type={})>".format(
            self.user_name, self.user_type)


class UserReport(Base):
    """
    author_type: 'U' for registered users, IP address for anonymous users.
    report_type: 'content' or 'authors'.
    res_timestamp: datetime of resolution of
                   the report by the assigned admin.
    """

    __tablename__ = "User_Report"

    report_id = Column(Integer, primary_key=True)
    report_text = Column(Text_)
    report_type = Column(Text_)
    author_type = Column(Text_)
    admin_report = Column(Text_)
    timestamp = Column(DateTime)
    res_timestamp = Column(DateTime)

    # Many-to-One relationships
    author_id = Column(Integer, ForeignKey("User.user_id"))
    author = relationship("User", backref="reports")

    admin_id = Column(Integer, ForeignKey("User.user_id"))
    admin = relationship("User", backref="reports_resolved")

    content_id = Column(Integer, ForeignKey("Content_Piece.content_id"))
    content = relationship("ContentPiece", backref="user_reports")
