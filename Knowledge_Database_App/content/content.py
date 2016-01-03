"""
Content Piece API
"""


from datetime import datetime

from Knowledge_Database_App import email
from Knowledge_Database_App.storage import (select_queries as select,
                                            action_queries as action)
from Knowledge_Database_App.search import index, search
from .celery import celery_app


class Name:

    def __init__(self, name_id=None, name=None,
                 name_type=None, timestamp=None):
        if (not (isinstance(name_id, None) or isinstance(name_id, int)) or
                not (isinstance(name, None) or isinstance(name, str)) or
                not (isinstance(name_type, None) or
                     isinstance(name_type, str)) or
                not (isinstance(timestamp, None) or
                     isinstance(timestamp, datetime))):
            raise TypeError("Argument of invalid type given!")
        else:
            self.name_id = name_id
            self.name = name
            self.name_type = name_type
            self.timestamp = timestamp

    def __repr__(self):
        return (">Name(name_id={name_id}, name={name}, "
                + "name_type={name_type}, timestamp={timestamp})<").format(
            name_id=self.name_id,
            name=self.name,
            name_type=self.name_type,
            timestamp=self.timestamp,
        )


class Text:

    def __init__(self, text_id=None, text=None, timestamp=None):
        if (not (isinstance(text_id, None) or isinstance(text_id, int)) or
                not (isinstance(text, None) or isinstance(text, str)) or
                not (isinstance(timestamp, None) or
                     isinstance(timestamp, datetime))):
            raise TypeError("Argument of invalid type given!")
        else:
            self.text_id = text_id
            self.text = text
            self.timestamp = timestamp

    def __repr__(self):
        return (">Text(text_id={text_id}, text={text}, "
                + "timestamp={timestamp})<").format(
            text_id=self.text_id,
            text=self.text,
            timestamp=self.timestamp,
        )


class UserData:

    def __init__(self, user_id=None, user_name=None):
        if (not (isinstance(user_id, None) or isinstance(user_id, int)) or
                not (isinstance(user_name, None) or
                     isinstance(user_name, str))):
            raise TypeError("Argument of invalid type given!")
        else:
            self.user_id = user_id
            self.user_name = user_name

    def __repr__(self):
        return ">UserData(user_id={user_id}, user_name={user_name})<".format(
            user_id=self.user_id,
            user_name=self.user_name,
        )


class MissingDataError(Exception):
    """General exception to raise when required data is missing."""


class Content:

    content_id = None           # Integer.
    timestamp = None            # Datetime.
    deleted_timestamp = None    # Datetime.
    first_author = None         # UserData object.
    authors = None              # List of UserData objects.
    content_type = None         # String.
    name = None                 # Name object.
    alternate_names = None      # List of Name objects.
    text = None                 # Text object.
    keywords = None             # String.
    citations = None            # String.
    notification = None

    def __init__(self, content_id=None, first_author=None,
                 content_type=None, name=None, alternate_names=None,
                 text=None, keywords=None, citations=None):
        """
        Args:
            content_id: Integer.
            first_author: UserData object.
            content_type: String.
            name: Name object.
            alternate_names: List of Name objects.
            text: Text object.
            keywords: List of Strings.
            citations: List of Strings.
        """
        if content_id is not None:
            try:
                content_piece = select.get_content_piece(content_id=content_id)
            except:
                raise
            else:
                self.content_id = content_id
                self._transfer(content_piece)
        else:
            if (not first_author or not content_type or not name or
                    not text or not keywords):
                raise MissingDataError("Required arguments not provided!")
            self.timestamp = datetime.utcnow()
            self.first_author = first_author
            self.authors = [first_author]
            self.content_type = content_type
            self.name = name
            self.alternate_names = alternate_names
            self.text = text
            self.keywords = keywords
            self.citations = citations

    def _transfer(self, content_piece):
        """
        Transfers the data in a ContentPiece object to this Content object.

        Args:
            content_piece: ContentPiece object.
        """
        self.timestamp = content_piece.timestamp
        self.deleted_timestamp = content_piece.deleted_timestamp
        self.first_author = UserData(
            user_id=content_piece.first_author.user_id,
            user_name=content_piece.first_author.user_name)
        self.authors = [UserData(user_id=author.user_id,
                                 user_name=author.user_name)
                        for author in content_piece.authors]
        self.content_type = content_piece.content_type
        self.name = Name(name_id=content_piece.name.name_id,
                         name=content_piece.name.name,
                         name_type=content_piece.name.name_type,
                         timestamp=content_piece.name.timestamp)
        self.alternate_names = [Name(name_id=name.name_id,
                                     name=name.name,
                                     name_type=name.name_type,
                                     timestamp=name.timestamp)
                                for name in content_piece.alternate_names]
        self.text = Text(text_id=content_piece.text.text_id,
                         text=content_piece.text.text,
                         timestamp=content_piece.text.timestamp)
        self.keywords = content_piece.keywords
        self.citations = content_piece.citations

    @classmethod
    def bulk_retrieve(cls, user_id=None):
        if user_id is not None:
            pass
        else:
            return []

    @classmethod
    def get_content_types(cls):
        pass

    @classmethod
    def search(cls):
        pass

    @classmethod
    def autocomplete(cls):
        pass

    def save(self):
        pass

    def update(self):
        pass

    def _delete(self):
        pass

    def serialize(self):
        pass
