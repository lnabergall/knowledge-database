"""
Content Piece API
"""


from datetime import datetime

from Knowledge_Database_App import email
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from Knowledge_Database_App import search as search_api
from Knowledge_Database_App.search import index

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

    @property
    def json_ready(self):
        return {
            "name_id": self.name_id,
            "name": self.name,
            "name_type": self.name_type,
            "timestamp": self.timestamp,
        }

    @property
    def storage_object(self):
        return orm.Name(name_id=self.name_id, name=self.name,
                        name_type=self.name_type, timestamp=self.timestamp)


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

    @property
    def json_ready(self):
        return {
            "text_id": self.text_id,
            "text": self.text,
            "timestamp": self.timestamp
        }

    @property
    def storage_object(self):
        return orm.Text(text_id=self.text_id, text=self.text,
                        timestamp=self.timestamp)


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

    @property
    def json_ready(self):
        return {"user_id": self.user_id, "user_name": self.user_name}


class Content:

    storage_handler = orm.StorageHandler()

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

    def __init__(self, content_id=None, first_author_name=None,
                 first_author_id=None, content_type=None, name=None,
                 alternate_names=None, text=None, keywords=None,
                 citations=None, content_piece=None):
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
            content_piece: ContentPiece object.
        """
        if content_id is not None:
            try:
                content_piece = self.storage_handler.call(
                    select.get_content_piece, content_id=content_id)
            except:
                raise
            else:
                self._transfer(content_piece)
                self.stored = True
        elif content_piece is not None:
            self._transfer(content_piece)
            self.stored = True
        else:
            if (not first_author_id or not first_author_name or
                    not content_type or not name or not text or not keywords):
                raise action.InputError("Required arguments not provided!")
            self.timestamp = datetime.utcnow()
            self.first_author = UserData(user_id=first_author_id,
                                         user_name=first_author_name)
            self.authors = [self.first_author]
            self.content_type = content_type
            self.name = Name(name=name, name_type="primary",
                             timestamp=self.timestamp)
            self.alternate_names = [Name(name=name, name_type="alternate",
                                         timestamp=self.timestamp)
                                    for name in alternate_names]
            self.text = Text(text=text, timestamp=self.timestamp)
            self.keywords = keywords
            self.citations = citations
            self.stored = False

    def _transfer(self, content_piece):
        """
        Transfers the data in a ContentPiece object to this Content object.

        Args:
            content_piece: ContentPiece object.
        """
        self.content_id = content_piece.content_id
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
        """
        Args:
            user_id: Integer. Defaults to None.
        Returns:
            List of Content objects.
        """
        if user_id is not None:
            try:
                content_pieces = self.storage_handler.call(
                    select.get_content_pieces, user_id=user_id)
            except:
                raise
            else:
                content = [Content(content_piece=content_piece)
                           for content_piece in content_pieces]
                return content
        else:
            return []

    @classmethod
    def get_content_types(cls):
        """
        Returns:
            List of content type strings.
        """
        try:
            content_types = self.storage_handler.call(select.get_content_types)
            content_types = [content_type.content_type
                             for content_type in content_types]
        except:
            raise
        else:
            return content_types

    @classmethod
    def check_uniqueness(cls, content_id, part_string, content_part):
        """
        Args:
            content_id: Integer.
            part_string: String.
            content_part: String, accepts 'name', 'keyword', or 'citation'.
        Returns:
            Boolean indicating whether the name, keyword, or citation is
            unique among the content piece's (identified by content_id)
            names (incl. alternate names), keywords, or citations,
            respectively.
        """
        if content_part == "name":
            try:
                name = self.storage_handler.call(select.get_name, content_id)
                alternate_names = self.storage_handler.call(
                    select.get_alternate_names, content_id)
            except:
                raise
            else:
                return (part_string != name.name and part_string
                        not in [name.name for name in alternate_names])
        elif content_part == "keyword":
            try:
                keywords = self.storage_handler.call(select.get_keywords,
                                                     content_id)
            except:
                raise
            else:
                return part_string not in [keyword.keyword
                                           for keyword in keywords]
        elif content_part == "citation":
            try:
                citations = self.storage_handler.call(select.get_citations,
                                                      content_id)
            except:
                raise
            else:
                return part_string not in [citation.citation_text
                                           for citation in citations]
        else:
            raise action.InputError("Invalid argument!")

    @classmethod
    def filter_by(cls, keyword=None, content_type=None,
                  citation=None, page_num=1):
        """
        Args:
            keyword: String. Defaults to None.
            content_type: String. Defaults to None.
            citation: String. Defaults to None.
        Returns:
            Dictionary of results.
        """
        try:
            if keyword is not None:
                results = search_api.filter_by(keyword_string=keyword,
                                               page_num=page_num)
            elif content_type is not None:
                results = search_api.filter_by(content_type_string=content_type,
                                               page_num=page_num)
            elif citation is not None:
                results = search_api.filter_by(citation_string=citation,
                                               page_num=page_num)
            else:
                raise action.InputError("No arguments!")
        except:
            raise
        else:
            for result in results["results"]:
                del result["score"]
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
            for result in results["results"]:
                del result["score"]
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
                except select.SelectError:
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
                except select.SelectError:
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
    def update(cls, content_id, content_part, update_type,
               part_text=None, part_id=None):
        """
        Args:
            content_id: Integer.
            content_part: String, orm.Name, orm.Keyword, orm.Citation,
                or orm.ContentType. As a string, expects 'name',
                'alternate_name', 'text', 'keyword', or 'citation'.
            update_type: String, accepts 'modify', 'add', or 'remove'.
            part_text: String. Defaults to None.
            part_id: Integer. Defaults to None.
        """
        if part_id is None and update_type == "modify":
            try:
                self.storage_handler.call(action.update_content_type,
                                          content_id, content_part)
                index.update_content_piece(content_id, "content_type",
                                           content_part.content_type)
            except:
                raise
        elif update_type == "add":
            try:
                self.storage_handler.call(action.store_content_part,
                                          content_part, content_id)
                if isinstance(content_part, orm.Name):
                    index.add_to_content_piece(content_id, "alternate_name",
                                               content_part.name)
                elif isinstance(content_part, orm.Keyword):
                    index.add_to_content_piece(content_id, "keyword",
                                               content_part.keyword)
                elif isinstance(content_part, orm.Citation):
                    index.add_to_content_piece(content_id, "citation",
                                               content_part.citation_text)
                else:
                    raise action.InputError("Invalid argument!")
            except:
                raise
        elif part_id is not None and update_type == "remove":
            try:
                self.storage_handler.call(action.remove_content_part,
                                          content_id, part_id, content_part)
                if content_part == "alternate_name":
                    alternate_names = self.storage_handler.call(
                        select.get_alternate_names, content_id)
                    alternate_names = [name.name for name in alternate_names]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=alternate_names)
                elif content_part == "keyword":
                    keywords = self.storage_handler.call(select.get_keywords,
                                                         content_id)
                    keywords = [keyword.keyword for keyword in keywords]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=keywords)
                elif content_part == "citation":
                    citations = self.storage_handler.call(
                        select.get_citations, content_id)
                    citations = [citation.citation_text
                                 for citation in citations]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=citations)
                else:
                    raise action.InputError("Invalid argument!")
            except:
                raise
        elif part_id is not None and update_type == "modify":
            try:
                if content_part == "name" or content_part == "alternate_name":
                    self.storage_handler.call(action.update_content_part,
                                              part_id, "name", part_text)
                else:
                    self.storage_handler.call(action.update_content_part,
                                              part_id, content_part, part_text)
                if content_part == "name" or content_part == "text":
                    index.update_content_piece(content_id, content_part,
                                               part_string=part_text)
                elif content_part == "alternate_name":
                    alternate_names = self.storage_handler.call(
                        select.get_alternate_names, content_id)
                    alternate_names = [name.name for name in alternate_names]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=alternate_names)
                elif content_part == "keyword":
                    keywords = self.storage_handler.call(select.get_keywords,
                                                         content_id)
                    keywords = [keyword.keyword for keyword in keywords]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=keywords)
                elif content_part == "citation":
                    citations = self.storage_handler.call(
                        select.get_citations, content_id)
                    citations = [citation.citation_text
                                 for citation in citations]
                    index.update_content_piece(content_id, content_part,
                                               part_strings=citations)
                else:
                    raise action.InputError("Invalid argument!")
            except:
                raise
        else:
            raise action.InputError("Invalid arguments!")

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
                        if authors is not None else None),
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


# Automatically parsing content piece text for matches to the
# names (incl. alternate names) of other content pieces and
# and then adding in a hyperlink (likely in some separate
# field distinct from the actual text).
