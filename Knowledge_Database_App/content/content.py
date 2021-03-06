"""
Content Piece API

Classes:

    Name, Text, UserData, Content
"""

from datetime import datetime

from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from Knowledge_Database_App.storage.exceptions import (
    InputError, SelectError, MissingDataError)
from Knowledge_Database_App import search as search_api
from Knowledge_Database_App.search import index
from . import content_config as config
from .exceptions import ApplicationError, ContentError


class Name:
    """
    Attributes:
        name_id: Integer.
        name: String.
        name_type: String, expects 'primary' or 'alternate'.
        timestamp: Datetime.
        last_edited_timestamp: Datetime.
    Properties:
        json_ready: Dictionary.
        storage_object: orm.Name object.
    """

    def __init__(self, name_id=None, name=None, name_type=None, 
                 timestamp=None, last_edited_timestamp=None):
        if (not (name_id is None or isinstance(name_id, int)) or
                not (name is None or isinstance(name, str)) or
                not (name_type is None or
                     isinstance(name_type, str)) or
                not (timestamp is None or
                     isinstance(timestamp, datetime)) or
                not (last_edited_timestamp is None or
                     isinstance(last_edited_timestamp, datetime))):
            raise TypeError("Argument of invalid type given!")
        else:
            char_count = len(name) - name.count(" ")
            if (char_count < config.SMALL_PART_MIN_CHARS or
                    char_count > config.SMALL_PART_MAX_CHARS):
                raise ContentError(message="Please provide name(s) containing between "
                    + str(config.SMALL_PART_MIN_CHARS) + " and "
                    + str(config.SMALL_PART_MAX_CHARS) + " characters.")
            self.name_id = name_id
            self.name = name
            self.name_type = name_type
            self.timestamp = timestamp
            self.last_edited_timestamp = last_edited_timestamp

    def __repr__(self):
        return (">Name(name_id={name_id}, name={name}, "
                + "name_type={name_type}, timestamp={timestamp}, "
                + "last_edited_timestamp={last_edited_timestamp})<").format(
            name_id=self.name_id,
            name=self.name,
            name_type=self.name_type,
            timestamp=self.timestamp,
            last_edited_timestamp=self.last_edited_timestamp,
        )

    @classmethod
    def bulk_retrieve(cls, content_ids):
        storage_handler = orm.StorageHandler()
        try:
            name_object_tuples = storage_handler.call(
                select.get_names, content_ids=content_ids)
        except:
            raise
        else:
            return {content_id: Name(name_id=name.name_id, name=name.name,
                                     name_type=name.name_type,
                                     timestamp=name.timestamp)
                    for content_id, name in name_object_tuples}

    @property
    def json_ready(self):
        return {
            "name_id": self.name_id,
            "name": self.name,
            "name_type": self.name_type,
            "timestamp": self.timestamp,
            "last_edited_timestamp": self.last_edited_timestamp,
        }

    @property
    def storage_object(self):
        return orm.Name(name_id=self.name_id, name=self.name,
                        name_type=self.name_type, timestamp=self.timestamp,
                        last_edited_timestamp=self.last_edited_timestamp)


class Text:
    """
    Attributes:
        text_id: Integer.
        text: String.
        timestamp: Datetime.
        last_edited_timestamp: Datetime.
    Properties:
        json_ready: Dictionary.
        storage_object: orm.Name object.
    """

    def __init__(self, text_id=None, text=None, timestamp=None, 
                 last_edited_timestamp=None):
        if (not (text_id is None or isinstance(text_id, int)) or
                not (text is None or isinstance(text, str)) or
                not (timestamp is None or
                     isinstance(timestamp, datetime)) or
                not (last_edited_timestamp is None or
                     isinstance(last_edited_timestamp, datetime))):
            raise TypeError("Argument of invalid type given!")
        else:
            char_count = len(text) - text.count(" ")
            if (char_count < config.LARGE_PART_MIN_CHARS or
                    char_count > config.LARGE_PART_MAX_CHARS):
                raise ContentError(message="Please provide a text body containing "
                    " between " + str(config.LARGE_PART_MIN_CHARS) + " and "
                    + str(config.LARGE_PART_MAX_CHARS) + " characters.")
            self.text_id = text_id
            self.text = text
            self.timestamp = timestamp
            self.last_edited_timestamp = last_edited_timestamp

    def __repr__(self):
        return (">Text(text_id={text_id}, text={text}, "
                + "timestamp={timestamp}, "
                + "last_edited_timestamp={last_edited_timestamp})<").format(
            text_id=self.text_id,
            text=self.text,
            timestamp=self.timestamp,
            last_edited_timestamp=self.last_edited_timestamp,
        )

    @property
    def json_ready(self):
        return {
            "text_id": self.text_id,
            "text": self.text,
            "timestamp": self.timestamp,
            "last_edited_timestamp": self.last_edited_timestamp,
        }

    @property
    def storage_object(self):
        return orm.Text(text_id=self.text_id, text=self.text,
                        timestamp=self.timestamp, 
                        last_edited_timestamp=self.last_edited_timestamp)


class UserData:
    """
    Attributes:
        user_id: Integer.
        user_name: String.
    Properties:
        json_ready: Dictionary.
    Instance Methods:
        load_email
    """

    def __init__(self, user_id=None, user_name=None, email=None):
        if (not (user_id is None or isinstance(user_id, int)) or
                not (user_name is None or
                     isinstance(user_name, str))):
            raise TypeError("Argument of invalid type given!")
        else:
            self.user_id = user_id
            self.user_name = user_name
            self.email = email

    def __repr__(self):
        return ">UserData(user_id={user_id}, user_name={user_name})<".format(
            user_id=self.user_id,
            user_name=self.user_name,
        )

    def load_info(self):
        try:
            user_id, self.user_name, self.email = orm.StorageHandler().call(
                select.get_user_info, user_id=self.user_id)
        except:
            raise

    @classmethod
    def bulk_retrieve(cls, user_data_objects=None, content_id=None):
        args = locals()
        storage_handler = orm.StorageHandler()
        if user_data_objects is not None:
            user_ids = [user.user_id for user in user_data_objects]
            try:
                info_tuples = storage_handler.call(
                    select.get_user_info, user_ids=user_ids)
            except:
                raise
        elif content_id is not None:
            try:
                info_tuples = storage_handler.call(
                    select.get_user_info, content_id=content_id)
            except:
                raise
        else:
            raise InputError("No arguments provided.",
                             message="No data provided.",
                             inputs=args)

        return [UserData(user_id=tup[0], user_name=tup[1], email=tup[2])
                for tup in info_tuples]

    @property
    def json_ready(self):
        return {"user_id": self.user_id, "user_name": self.user_name}


class Content:
    """
    Attributes:
        content_id: Integer. Defaults to None.
        timestamp: Datetime. Defaults to None.
        last_edited_timestamp: Datetime. Defaults to None.
        deleted_timestamp: Datetime. Defaults to None.
        first_author: UserData object. Defaults to None.
        authors: List of UserData objects. Defaults to None.
        content_type: String. Defaults to None.
        name: Name object. Defaults to None.
        alternate_names: List of Name objects. Defaults to None.
        text: Text object. Defaults to None.
        keywords: List of Strings. Defaults to None.
        citations: List of Strings. Defaults to None.
        notification: String. Defaults to None.

    Properties:
        json_ready: Dictionary.

    Instance Methods:
        _transfer, store, _delete

    Class Methods:
        bulk_retrieve, get_content_types, check_uniqueness, filter_by,
        search, autocomplete, update
    """

    storage_handler = orm.StorageHandler()

    content_id = None               # Integer.
    timestamp = None                # Datetime.
    last_edited_timestamp = None    # Datetime.
    deleted_timestamp = None        # Datetime.
    first_author = None             # UserData object.
    authors = None                  # List of UserData objects.
    content_type = None             # String.
    name = None                     # Name object.
    alternate_names = None          # List of Name objects.
    text = None                     # Text object.
    keywords = None                 # List of Strings.
    citations = None                # List of Strings.
    notification = None

    def __init__(self, content_id=None, accepted_edit_id=None,
                 rejected_edit_id=None, first_author_id=None,
                 content_type=None, name=None, alternate_names=None,
                 text=None, keywords=None, citations=None,
                 content_piece=None):
        """
        Args:
            content_id: Integer.
            accepted_edit_id: Integer.
            rejected_edit_id: Integer.
            first_author_id: Integer.
            content_type: String.
            name: String.
            alternate_names: List of Strings.
            text: String.
            keywords: List of Strings.
            citations: List of Strings.
            content_piece: ContentPiece object.
        """
        args = locals()
        if (content_id is not None or accepted_edit_id is not None or
                rejected_edit_id is not None):
            try:
                content_piece = self.storage_handler.call(
                    select.get_content_piece, content_id=content_id,
                    accepted_edit_id=accepted_edit_id,
                    rejected_edit_id=rejected_edit_id)
            except:
                raise
            else:
                self._transfer(content_piece)
                self.stored = True
        elif content_piece is not None:
            self._transfer(content_piece)
            self.stored = True
        else:
            if (not first_author_id or not content_type or not name or
                    not text or not keywords):
                raise InputError("Invalid argument(s) provided.",
                                 message="Insufficient data provided.",
                                 inputs=args)
            self.timestamp = datetime.utcnow()
            self.last_edited_timestamp = self.timestamp
            self.first_author = UserData(user_id=first_author_id)
            self.authors = [self.first_author]
            self.content_type = content_type
            self.name = Name(name=name, name_type="primary",
                             timestamp=self.timestamp, 
                             last_edited_timestamp=self.timestamp)
            self.alternate_names = [
                Name(name=alt_name, name_type="alternate",
                     timestamp=self.timestamp, 
                     last_edited_timestamp=self.last_edited_timestamp)
                for alt_name in list(set(alternate_names))
                if alt_name and alt_name != self.name.name
            ]
            self.text = Text(text=text, timestamp=self.timestamp, 
                             last_edited_timestamp=self.timestamp)
            self.keywords = list(set(keywords))
            self.citations = list(set(citations))
            Content._check_legal(name, alternate_names, text, keywords, citations)
            self.stored = False

    @staticmethod
    def _check_legal(name, alternate_names, text, keywords, citations):
        """
        Checks that all content parts are legal, that is, satisfy
        the content requirements.

        Args:
            name: String.
            alternate_names: List of strings.
            text: String.
            keywords: List of strings.
            citations: List of strings.
        """
        names = [name] + alternate_names
        if any([config.SMALL_PART_MAX_CHARS <
                len(alt_name) - alt_name.count(" ") or
                config.SMALL_PART_MIN_CHARS >
                len(alt_name) - alt_name.count(" ")
                for alt_name in names]):
            raise ContentError(message="Please provide name(s) containing "
                "between " + str(config.SMALL_PART_MIN_CHARS) + " and "
                + str(config.SMALL_PART_MAX_CHARS) + " characters.")
        if (config.LARGE_PART_MAX_CHARS < len(text) - text.count(" ") or
                config.LARGE_PART_MIN_CHARS > len(text) - text.count(" ")):
            raise ContentError(message="Please provide a text body containing "
                "between " + str(config.LARGE_PART_MIN_CHARS) + " and "
                + str(config.LARGE_PART_MAX_CHARS) + " characters.")
        if any([config.LARGE_PART_MAX_CHARS <
                len(citation) - citation.count(" ") or
                config.SMALL_PART_MIN_CHARS >
                len(citation) - citation.count(" ")
                for citation in citations]):
            raise ContentError(message="Please provide citation(s) containing "
                "between " + str(config.SMALL_PART_MIN_CHARS) + " and "
                + str(config.SMALL_PART_MAX_CHARS) + " characters.")
        if any([config.SMALL_PART_MAX_CHARS <
                len(keyword) - keyword.count(" ") or
                config.SMALL_PART_MIN_CHARS >
                len(keyword) - keyword.count(" ")
                for keyword in keywords]):
            raise ContentError(message="Please provide keyword(s) containing "
                "between " + str(config.SMALL_PART_MIN_CHARS) + " and "
                + str(config.SMALL_PART_MAX_CHARS) + " characters.")

    def _transfer(self, content_piece):
        """
        Transfers the data in a ContentPiece object to this Content object.

        Args:
            content_piece: ContentPiece object.
        """
        self.content_id = content_piece.content_id
        self.timestamp = content_piece.timestamp
        self.last_edited_timestamp = content_piece.last_edited_timestamp
        self.deleted_timestamp = content_piece.deleted_timestamp
        self.first_author = UserData(
            user_id=content_piece.first_author.user_id,
            user_name=content_piece.first_author.user_name)
        self.authors = [UserData(user_id=author.user_id,
                                 user_name=author.user_name)
                        for author in content_piece.authors]
        self.content_type = content_piece.content_type.content_type
        self.name = Name(
            name_id=content_piece.name.name_id,
            name=content_piece.name.name,
            name_type=content_piece.name.name_type,
            timestamp=content_piece.name.timestamp,
            last_edited_timestamp=content_piece.name.last_edited_timestamp
        )
        self.alternate_names = [Name(name_id=name.name_id,
                                     name=name.name,
                                     name_type=name.name_type,
                                     timestamp=name.timestamp,
                                     last_edited_timestamp=name.last_edited_timestamp)
                                for name in content_piece.alternate_names]
        self.text = Text(
            text_id=content_piece.text.text_id,
            text=content_piece.text.text,
            timestamp=content_piece.text.timestamp,
            last_edited_timestamp=content_piece.text.last_edited_timestamp
        )
        self.keywords = [keyword.keyword for keyword in content_piece.keywords]
        self.citations = [citation.citation_text 
                          for citation in content_piece.citations]

    @classmethod
    def bulk_retrieve(cls, sort="created_at", content_part=None, user_id=None,
                      page_num=0, return_count=False, ids_only=False):
        """
        Args:
            sort: String, accepts 'created_at' or 'last_edited_at'.
                Defaults to 'created_at'.
            content_part: String, accepts 'keyword', 'content_type', 'name',
                or 'citation'. Defaults to None.
            user_id: Integer. Defaults to None.
            page_num: Integer. Defaults to 0.
            return_count: Boolean. Defaults to False.
            ids_only: Boolean. Defaults to False.
        Returns:
            List of Content objects.
        """
        if user_id is not None:
            try:
                content_pieces = cls.storage_handler.call(
                    select.get_content_pieces, user_id=user_id)
            except:
                raise
            else:
                content = [Content(content_piece=content_piece)
                           for content_piece in content_pieces]
                content = sorted(content,
                    key=lambda piece: piece.last_edited_timestamp,
                    reverse=True)
                content_count = len(content)
                if ids_only:
                    content = [content_piece.content_id
                               for content_piece in content]
                if page_num != 0 and return_count:
                    return content[10*(page_num-1) : 10*page_num], content_count
                elif page_num != 0:
                    return content[10*(page_num-1) : 10*page_num]
                elif return_count:
                    return content, content_count
                else:
                    return content
        else:
            try:
                if page_num < 1:
                    raise InputError("Invalid argument(s) provided.",
                                     message="Invalid data provided.",
                                     inputs={"page_num": page_num})
                content_pieces = cls.storage_handler.call(
                    select.get_content_pieces, sort=sort,
                    content_part=content_part, page_num=page_num)
                content = [Content(content_piece=content_piece)
                           for content_piece in content_pieces]
            except:
                raise
            else:
                return content

    @classmethod
    def get_parts(cls, content_part, page_num=None, per_page=None):
        """
        Args:
            content_part: String, accepts 'content_type', 'keyword',
                or 'citation'.
            page_num: Integer. Defaults to None.
            per_page: Integer. Defaults to None.
        Returns:
            List of content part strings.
        """
        try:
            if content_part == "content_type":
                content_types = cls.storage_handler.call(select.get_content_types)
                content_types = [content_type.content_type
                                 for content_type in content_types]
                return content_types
            elif content_part == "keyword":
                keywords = cls.storage_handler.call(
                    select.get_keywords, page_num=page_num, per_page=per_page)
                keywords = [keyword.keyword for keyword in keywords]
                return keywords
            elif content_part == "citation":
                citations = cls.storage_handler.call(
                    select.get_citations, page_num=page_num, per_page=per_page)
                citations = [citation.citation_text for citation in citations]
                return citations
            else:
                raise InputError("Invalid argument(s) provided.",
                                 message="Invalid data provided.",
                                 inputs={"content_part": content_part})
        except:
            raise

    @classmethod
    def check_uniqueness(cls, content_id, part_string, content_part):
        """
        Args:
            content_id: Integer.
            part_string: String.
            content_part: String, accepts 'name', 'alternate_name', 
                keyword', or 'citation'.
        Returns:
            Boolean indicating whether the name, keyword, or citation is
            unique among the content piece's (identified by content_id)
            names (incl. alternate names), keywords, or citations,
            respectively.
        """
        if content_part == "name" or content_part == "alternate_name":
            try:
                name = cls.storage_handler.call(
                    select.get_names, content_id=content_id)
                alternate_names = cls.storage_handler.call(
                    select.get_alternate_names, content_id)
            except:
                raise
            else:
                return (part_string != name.name and part_string
                        not in [name.name for name in alternate_names])
        elif content_part == "keyword":
            try:
                keywords = cls.storage_handler.call(select.get_keywords,
                                                    content_id)
            except:
                raise
            else:
                return part_string not in [keyword.keyword
                                           for keyword in keywords]
        elif content_part == "citation":
            try:
                citations = cls.storage_handler.call(select.get_citations,
                                                     content_id)
            except:
                raise
            else:
                return part_string not in [citation.citation_text
                                           for citation in citations]
        else:
            raise InputError("Invalid argument(s) provided.",
                             message="Invalid data provided.",
                             inputs={"content_part": content_part})

    @classmethod
    def filter_by(cls, content_part, part_string, page_num=1):
        """
        Args:
            content_part: String, accepts 'keyword', 'content_type',
                'name', or 'citation'.
            part_string: String.
            page_num: Positive integer. Defaults to None.
        Returns:
            Dictionary of results.
        """
        try:
            results = search_api.filter_by(content_part, part_string,
                                           page_num=page_num)
        except:
            raise
        else:
            for i in range(len(results["results"])):
                try:
                    del results["results"][i]["score"]
                except KeyError:
                    pass
            return results

    @classmethod
    def search(cls, query, page_num=1):
        """
        Args:
            query: String.
            page_num: Integer. Defaults to 1.
        Returns:
            Dictionary of results.
        """
        try:
            results = search_api.search(query, page_num)
        except:
            raise
        else:
            for i in range(len(results["results"])):
                del results["results"][i]["score"]
            return results

    @classmethod
    def autocomplete(cls, content_part, query):
        """
        Args:
            content_part: String, expects 'name', 'keyword', or 'citation'.
            query: String.
        Returns:
            List of completion dictionaries.
        """
        try:
            completions = search_api.autocomplete(content_part, query)
        except:
            raise
        else:
            return completions

    def store(self):
        if self.stored:
            return
        else:
            keywords_for_storage = []
            for keyword_string in self.keywords:
                try:
                    keyword = self.storage_handler.call(select.get_keyword,
                                                        keyword_string)
                except SelectError:
                    keyword = orm.Keyword(keyword=keyword_string,
                                          timestamp=self.timestamp)
                    keywords_for_storage.append(keyword)
                except:
                    raise
                else:
                    keywords_for_storage.append(keyword)
            citations_for_storage = []
            for citation_string in self.citations:
                try:
                    citation = self.storage_handler.call(select.get_citation,
                                                         citation_string)
                except SelectError:
                    citation = orm.Citation(citation_text=citation_string,
                                            timestamp=self.timestamp)
                    citations_for_storage.append(citation)
                except:
                    raise
                else:
                    citations_for_storage.append(citation)
            try:
                content_id = self.storage_handler.call(
                    action.store_content_piece,
                    self.first_author.user_id,
                    self.name.storage_object,
                    self.text.storage_object,
                    self.storage_handler.call(select.get_content_type,
                                              self.content_type),
                    keywords_for_storage,
                    self.timestamp,
                    citations=citations_for_storage,
                    alternate_names=[name.storage_object
                                     for name in self.alternate_names],
                )
                index.index_content_piece(
                    content_id,
                    self.name.name,
                    [name.name for name in self.alternate_names],
                    self.text.text,
                    self.content_type,
                    self.keywords,
                    self.citations if self.citations is not None else []
                )
            except:
                raise
            else:
                self.content_id = content_id
                self.stored = True

    @classmethod
    def update(cls, content_id, content_part, update_type, timestamp,
               part_text=None, part_id=None, edited_citations=None):
        """
        Args:
            content_id: Integer.
            content_part: String, expects 'name', 'alternate_name',
                'text', 'content_type', 'keyword', or 'citation'.
            update_type: String, accepts 'modify', 'add', or 'remove'.
            timestamp: Datetime.
            part_text: String or orm.Name. Defaults to None.
            part_id: Integer. Defaults to None.
            edited_citations: List of orm.Citation objects.
                Defaults to None.
        """
        args = locals()
        if content_part == "content_type" and update_type == "modify":
            try:
                content_type = select.get_content_type(part_text)
                cls.storage_handler.call(action.update_content_type,
                                          content_id, content_type)
                index.update_content_piece(content_id, content_part,
                    part_string=content_type.content_type)
            except:
                raise
        elif update_type == "add":
            try:
                if isinstance(part_text, orm.Name):
                    cls.storage_handler.call(action.store_content_part,
                                             part_text, content_id)
                    index.add_to_content_piece(content_id, "alternate_name",
                                               content_part.name)
                elif content_part == "keyword" and part_text is not None:
                    try:
                        keyword = cls.storage_handler.call(
                            select.get_keyword, part_text)
                    except SelectError:
                        keyword = orm.Keyword(keyword=part_text,
                                              timestamp=timestamp)
                    cls.storage_handler.call(action.store_content_part,
                                             keyword, content_id)
                    index.add_to_content_piece(content_id, content_part,
                                               keyword.keyword)
                elif content_part == "citation" and part_text is not None:
                    try:
                        citation = cls.storage_handler.call(
                            select.get_citation, part_text)
                    except SelectError:
                        citation = orm.Citation(citation_text=part_text,
                                                timestamp=timestamp)
                    cls.storage_handler.call(
                        action.store_content_part, citation, content_id,
                        edited_citations=edited_citations)
                    index.add_to_content_piece(content_id, content_part,
                                               citation.citation_text)
                else:
                    raise InputError("Invalid argument(s) provided.",
                                     message="Invalid data provided.",
                                     inputs=args)
            except:
                raise
        elif part_id is not None and update_type == "remove":
            try:
                cls.storage_handler.call(action.remove_content_part,
                                         content_id, part_id, content_part)
                if content_part == "alternate_name":
                    alternate_names = cls.storage_handler.call(
                        select.get_alternate_names, content_id)
                    alternate_names = [name.name for name in alternate_names]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=alternate_names)
                elif content_part == "keyword":
                    keywords = cls.storage_handler.call(
                        select.get_keywords, content_id)
                    keywords = [keyword.keyword for keyword in keywords]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=keywords)
                elif content_part == "citation":
                    citations = cls.storage_handler.call(
                        select.get_citations, content_id)
                    citations = [citation.citation_text
                                 for citation in citations]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=citations)
                else:
                    raise InputError("Invalid argument(s) provided.",
                                     message="Invalid data provided.",
                                     inputs=args)
            except:
                raise
        elif part_id is not None and update_type == "modify":
            try:
                if content_part == "name" or content_part == "alternate_name":
                    cls.storage_handler.call(action.update_content_part,
                                             part_id, "name", part_text)
                elif content_part == "text":
                    cls.storage_handler.call(action.update_content_part,
                                             part_id, content_part, part_text)
                if content_part == "name" or content_part == "text":
                    index.update_content_piece(content_id, content_part,
                                               part_string=part_text)
                elif content_part == "alternate_name":
                    alternate_names = cls.storage_handler.call(
                        select.get_alternate_names, content_id)
                    alternate_names = [name.name for name in alternate_names]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=alternate_names)
                elif content_part == "keyword":
                    try:
                        cls.update(content_id, content_part, "remove", part_id)
                    except MissingDataError:
                        pass
                    cls.update(content_id, content_part,
                               "add", timestamp, part_text=part_text)
                    keywords = cls.storage_handler.call(
                        select.get_keywords, content_id)
                    keywords = [keyword.keyword for keyword in keywords]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=keywords)
                elif content_part == "citation":
                    try:
                        cls.update(content_id, content_part, "remove", part_id)
                    except MissingDataError:
                        other_edits = cls.storage_handler.call(
                            select.get_citations, content_id,
                            edited_citation_id=part_id)
                        if len(other_edits) != 1:
                            raise ApplicationError(error_data=other_edits,
                                message="Multiple citations found. "
                                "Cannot resolve citation ambiguity.")
                        else:
                            previous_citation = other_edits[0]
                            edited_citations = ([previous_citation] +
                                previous_citation.edited_citations)
                            cls.update(content_id, content_part, "remove",
                                       previous_citation.citation_id)
                    cls.update(content_id, content_part, "add", timestamp,
                        part_text=part_text, edited_citations=edited_citations)
                    citations = cls.storage_handler.call(
                        select.get_citations, content_id)
                    citations = [citation.citation_text
                                 for citation in citations]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=citations)
                else:
                    raise InputError("Invalid argument(s) provided.",
                                     message="Invalid data provided.",
                                     inputs={"content_part": content_part})
            except:
                raise
        else:
            raise InputError("Invalid argument(s) provided.",
                             message="Invalid data provided.",
                             inputs=args)

    def _delete(self):
        if not self.stored:
            return
        else:
            deleted_timestamp = datetime.now()
            try:
                self.storage_handler.call(action.delete_content_piece,
                                          self.content_id, deleted_timestamp)
                index.remove_content_piece(self.content_id)
            except:
                raise
            else:
                self.deleted_timestamp = deleted_timestamp

    @property
    def json_ready(self):
        return {
            "content_id": self.content_id,
            "timestamp": (str(self.timestamp)
                          if self.timestamp is not None else None),
            "deleted_timestamp": (str(self.deleted_timestamp)
                if self.deleted_timestamp is not None else None),
            "first_author": (self.first_author.json_ready
                             if self.first_author is not None else None),
            "authors": ([author.json_ready for author in self.authors]
                        if self.authors is not None else None),
            "content_type": self.content_type,
            "name": self.name.json_ready if self.name is not None else None,
            "alternate_names": ([name.json_ready for name in self.alternate_names]
                                if self.alternate_names is not None else None),
            "text": self.text.json_ready if self.text is not None else None,
            "keywords": self.keywords,
            "citations": self.citations,
            "notification": self.notification,
            "stored": self.stored,
        }


# TODO:
# Automatically parsing content piece text for matches to the
# names (incl. alternate names) of other content pieces and
# and then adding in a hyperlink (likely in some separate
# field distinct from the actual text).
