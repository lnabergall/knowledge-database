"""
Contains the core classes and functions used to interact with the
Postgres database, in particular mapping classes defining the database
scheme. Uses SQLAlchemy.

Functions:

    start_session -
        Starts a session for interacting with the database.
        Returns: session object

Classes:

    Query, StorageHandler, Content, Name, Text, ContentType, Keyword,
    Citation, Edit, Vote, RejectedEdit, User, UserReport

    For all classes X, the attribute 'timestamp' holds the datetime
    of creation.
"""

from sqlalchemy import (create_engine, Column, Integer,
                        DateTime, ForeignKey, Table)
from sqlalchemy import Text as Text_
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm.query import Query as _Query
from sqlalchemy.ext.declarative import declarative_base


KDB_url = "postgresql+psycopg2://postgres:Cetera4247@localhost/kdb_develop"
Base = declarative_base()


def _create_schema():
    engine = create_engine(KDB_url, echo=False)
    Base.metadata.create_all(engine)


def start_session():
    engine = create_engine(KDB_url, echo=False)
    return sessionmaker(bind=engine, query_cls=Query)()


class Query(_Query):
    """Custom SQLAlchemy query class."""

    def values(self):
        """
        Returns an iterable of all scalar element values from rows
        matched by this query.

        Returns:
            List of scalars.
        Raises:
            MultipleValuesFound: If result rows have more than
                one element.
        """
        try:
            return [x for (x,) in self.all()]
        except ValueError as e:
            raise MultipleValuesFound(str(e))


class ActionError(Exception):
    """General exception raised when a database action query fails."""


class StorageHandler:
    """
    Handles queries made to the Postgres database.

    Call a function from select_queries or action_queries using the
    'call' method. The class features built-in session management,
    including handling commits.
    """
    def __init__(self):
        self.session = start_session()

    def call(self, function, *args, **kwargs):
        try:
            output = function(*args, session=self.session, **kwargs)
        except (NameError, ValueError, TypeError) as e:
            raise RuntimeError(str(e))
        except:
            raise
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise ActionError(str(e))
        return output

    def _close(self):
        self.session.close()


# Many-to-Many relationship between Content_Piece and User
content_authors = Table("content_authors", Base.metadata,
    Column("content_id", Integer, ForeignKey("ContentPiece.content_id")),
    Column("user_id", Integer, ForeignKey("User.user_id")),
)


class ContentPiece(Base):
    """
    Attributes:
        content_id: Integer, primary key.
        timestamp: Datetime.
        deleted_timestamp: Datetime.
        first_author_id: Integer, foreign key to User table.
        first_author: User, Many-to-One relationship, backref
            'pieces_created'.
        content_type_id: Integer, foreign key to Content_Type table.
        content_type: ContentType, Many-to-One relationship,
            backref 'pieces'.
        name_id: Integer, foreign key to Name table.
        name: Name, One-to-One relationship, backref 'piece'.
        text_id: Integer, foreign key to Text table.
        text: Text, One-to-One relationship, backref 'piece'.
        authors: list of Users, Many-to-Many relationship,
            backref 'pieces'.
    """
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
    """
    Attributes:
        name_id: Integer, primary key.
        name: String.
        name_type: String, expects 'primary' or 'alternate'.
        timestamp: Datetime.
        content_id: Integer, foreign key to Content_Piece table.
        piece: ContentPiece, Many-to-One relationship, backref
            'alternate_names'.
    """
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
    """
    Attributes:
        text_id: Integer, primary key.
        text: String.
        timestamp: Datetime.
    """
    __tablename__ = "Text"

    text_id = Column(Integer, primary_key=True)
    text = Column(Text_)
    timestamp = Column(DateTime)

    def __repr__(self):
        return "<Text(text={})>".format(self.text)


class ContentType(Base):
    """
    Attributes:
        content_type_id: Integer, primary key.
        content_type: String, constrained to be unique.
    """
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
    """
    Attributes:
        keyword_id: Integer, primary key.
        keyword: String, indexed and constrained to be unique.
        timestamp: Datetime.
        pieces: list of ContentPieces, Many-to-Many relationship,
            backref 'content_keywords'.
    """
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
    """
    Attributes:
        citation_id: Integer, primary key.
        citation_text: String, constrained to be unique.
        timestamp: Datetime.
        pieces: list of ContentPieces, Many-to-Many relationship,
            backref 'citations'.
    """
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
    Attributes:
        edit_id: Integer, primary key.
        edit_text: String.
        edit_rational: String.
        content_part: String, expects 'name', 'text', 'keyword',
            or 'citation'.
        timestamp: Datetime.
        acc_timestamp: Datetime of acceptance of the edit.
        author_type: String, expects 'U' for registered users, IP address
            for anonymous users.
        author_id: Integer, foreign key to User table.
        author: User, Many-to-One relationship, backref 'accepted_edits'.
        content_id: Integer, foreign key to Content_Piece table.
        piece: ContentPiece, Many-to-One relationship, backref
            'accepted_edits'.
        name_id: Integer, foreign key to Name table.
        name: Name, Many-to-One relationship, backref 'accepted_edits'.
        text_id: Integer, foreign key to Name table.
        text: Text, Many-to-One relationship, backref 'accepted_edits'.
        keyword_id: Integer, foreign key to Keyword table.
        keyword: Keyword, Many-to-One relationship, backref
            'accepted_edits'.
        citation_id: Integer, foreign key to Citation table.
        citation: Citation, Many-to-One relationship, backref
            'accepted_edits'.
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
    Attributes:
        vote_id: Integer, primary key.
        vote: String.
        content_part: String, expects 'name', 'text', 'keyword',
            or 'citation'.
        timestamp: Datetime.
        close_timestamp: Datetime of the closing of the vote.
        accepted_edit_id: Integer, foreign key to Accepted_Edit table.
        accepted_edit: AcceptedEdit, One-to-One relationship, backref 'vote'.
        rejected_edit_id: Integer, foreign key to Rejected_Edit table.
        rejected_edit: RejectedEdit, One-to-One relationship, backref 'vote'.
        voters: list of Users, Many-to-Many relationship, backref 'votes'.
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
    Attributes:
        edit_id: Integer, primary key.
        edit_text: String.
        edit_rational: String.
        content_part: String, expects 'name', 'text', 'keyword',
            or 'citation'.
        timestamp: Datetime.
        rej_timestamp: Datetime of rejection of the edit.
        author_type: String, expects 'U' for registered users, IP address
            for anonymous users.
        author_id: Integer, foreign key to User table.
        author: User, Many-to-One relationship, backref 'accepted_edits'.
        content_id: Integer, foreign key to Content_Piece table.
        piece: ContentPiece, Many-to-One relationship, backref
            'accepted_edits'.
        name_id: Integer, foreign key to Name table.
        name: Name, Many-to-One relationship, backref 'accepted_edits'.
        text_id: Integer, foreign key to Name table.
        text: Text, Many-to-One relationship, backref 'accepted_edits'.
        keyword_id: Integer, foreign key to Keyword table.
        keyword: Keyword, Many-to-One relationship, backref
            'accepted_edits'.
        citation_id: Integer, foreign key to Citation table.
        citation: Citation, Many-to-One relationship, backref
            'accepted_edits'.
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
    """
    Attributes:
        user_id: Integer, primary key.
        user_type: String, expects 'admin' or 'standard'.
        user_name: String, indexed.
        email: String, indexed and constrained to be unique.
        confirmed_timestamp: Datetime.
        pass_hash: String, indexed and constrained to be unique.
        pass_hash_type: String.
        pass_salt: String, indexed and constrained to be unique.
        remember_id: Integer, indexed and constrained to be unique.
        remember_token_hash: String, indexed and constrained to be unique.
        timestamp: Datetime.
        deleted_timestamp: Datetime.
    """

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
    Attributes:
        report_id: Integer, primary key.
        report_text: String.
        report_type: String, expects 'content' or 'authors'.
        author_type: String, expects 'U' for registered users,
            IP address for anonymous users.
        admin_report: String.
        timestamp: Datetime.
        res_timestamp: Datetime of resolution of the report by
            the assigned admin.
        author_id: Integer, foreign key to User table.
        author: User, Many-to-One relationship, backref 'reports'.
        admin_id: Integer, foreign key to User table.
        admin: User, Many-to-One relationship, backref 'reports_resolved'.
        content_id: Integer, foreign key to Content_Piece table.
        piece: ContentPiece, Many-to-One relationship, backref
            'user_reports'.
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
    piece = relationship("ContentPiece", backref="user_reports")
