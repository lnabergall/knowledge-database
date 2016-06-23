"""
Search Index API

Contains functions and classes used to read and write to the
Elasticsearch cluster. Uses elasticsearch-py-dsl.

Classes:

    SearchableContentPiece

Exceptions:

    IndexAccessError

Functions:

    index_content_piece, update_content_piece, remove_content_piece
"""

from elasticsearch import NotFoundError
from elasticsearch_dsl import (DocType, String, Completion,
                               Index, analyzer, tokenizer, token_filter)
from elasticsearch_dsl.connections import connections

from Knowledge_Database_App.storage.select_queries import InputError
from Knowledge_Database_App.content.redis_api import decode_response


KDB_cluster_url = "localhost:9200"
connections.create_connection(hosts=[KDB_cluster_url])
content = Index("content")


def _create_index():
    content.create()


def _delete_index():
    content.delete(ignore=404)


bigram_analyzer = analyzer(
    "bigram_analyzer",
    type="custom",
    tokenizer="standard",
    filter=[
        "lowercase",
        token_filter("shingle_filter", type="shingle",
                     min_shingle_size=2, max_shingle_size=2)
    ],
)


@content.doc_type
class SearchableContentPiece(DocType):
    """
    Attributes:
        name: String.
        alternate_names: List of strings.
        text: String.
        content_type: String.
        keywords: List of strings.
        citations: List of strings.
    """
    name = String(
        fields={"raw": String(index="not_analyzed")}
    )
    name_suggest = Completion(payloads=True,
                              preserve_separators=False,
                              preserve_position_increments=False)
    alternate_names = String(
        multi=True,
        fields={"raw": String(multi=True, index="not_analyzed")},
        position_increment_gap=100
    )
    alternate_names_suggest = Completion(multi=True, payloads=True,
                                         preserve_separators=False,
                                         preserve_position_increments=False)
    text = String(fields={"bigrams": String(analyzer=bigram_analyzer)})
    content_type = String()
    keywords = String(
        multi=True,
        fields={"raw": String(multi=True, index="not_analyzed")}
    )
    keywords_suggest = Completion(multi=True,
                                  preserve_separators=False,
                                  preserve_position_increments=False)
    citations = String(
        multi=True,
        fields={"raw": String(multi=True, index="not_analyzed")}
    )
    citations_suggest = Completion(multi=True,
                                   preserve_separators=False,
                                   preserve_position_increments=False)

    @classmethod
    def get(cls, *args, **kwargs):
        response = super().get(*args, **kwargs)
        response = decode_response(response)
        return response


class IndexAccessError(NotFoundError):
    """
    General exception raised when an update of a document in the
    Elasticsearch index fails.
    """


def index_content_piece(content_id, name_string, alternate_name_strings,
                        text_string, content_type_string, keyword_strings,
                        citation_strings):
    """
    Args:
        content_id: Integer.
        name_string: String.
        alternate_name_strings: List of strings.
        text_string: String.
        content_type_string: String.
        keyword_strings: List of strings.
        citation_strings: List of strings.
    """
    content_piece = SearchableContentPiece(name=name_string,
        alternate_names=alternate_name_strings, text=text_string,
        content_type=content_type_string, keywords=keyword_strings,
        citations=citation_strings)
    content_piece.name_suggest = {
        "input": name_string,
        "payload": {"content_id": content_id}
    }
    content_piece.alternate_names_suggest = {
        "input": alternate_name_strings,
        "payload": {"content_id": content_id}
    }
    content_piece.keywords_suggest = {"input": keyword_strings}
    content_piece.citations_suggest = {"input": citation_strings}
    content_piece.meta.id = content_id
    content_piece.save()


def add_to_content_piece(content_id, content_part, part_string):
    """
    Args:
        content_id: Integer.
        content_part: String, accepts 'alternate_name', 'keyword',
            or 'citation'.
        part_string: String.
    """
    try:
        content_piece = SearchableContentPiece.get(id=content_id)
    except NotFoundError as e:
        raise IndexAccessError(str(e))
    else:
        if content_part == "alternate_name":
            content_piece.alternate_names.append(part_string)
            content_piece.alternate_names_suggest["input"].append(part_string)
        elif content_part == "keyword":
            content_piece.keywords.append(part_string)
            content_piece.keywords_suggest["input"].append(part_string)
        elif content_part == "citation":
            content_piece.citations.append(part_string)
            content_piece.citations_suggest["input"].append(part_string)
        else:
            raise InputError("Invalid arguments!")
        content_piece.save()

def update_content_piece(content_id, content_part, part_string=None,
                         part_strings=None):
    """
    Args:
        content_id: Integer.
        content_part: String, accepts 'name', 'alternate_name', 'text',
            'content_type', 'keyword', or 'citation'.
        part_string: String.
        part_strings: List of strings.
    """
    try:
        content_piece = SearchableContentPiece.get(id=content_id)
    except NotFoundError as e:
        raise IndexAccessError(str(e))
    else:
        if content_part == "name":
            content_piece.name = part_string
            content_piece.name_suggest = {
                "input": part_string,
                "payload": {"content_id": content_id}
            }
        elif content_part == "alternate_name":
            content_piece.alternate_names = part_strings
            content_piece.alternate_names_suggest = {
                "input": part_strings,
                "payload": {"content_id": content_id}
            }
        elif content_part == "text":
            content_piece.text = part_string
        elif content_part == "content_type":
            content_piece.content_type = part_string
        elif content_part == "keyword":
            content_piece.keywords = part_strings
            content_piece.keywords_suggest = {"input": part_strings}
        elif content_part == "citation":
            content_piece.citations = part_strings
            content_piece.citations_suggest = {"input": part_strings}
        else:
            raise InputError("Invalid arguments!")
        content_piece.save()


def remove_content_piece(content_id):
    """
    Args:
        content_id: Integer.
    """
    try:
        content_piece = SearchableContentPiece.get(id=content_id)
    except NotFoundError as e:
        raise IndexAccessError(str(e))
    else:
        content_piece.delete()
