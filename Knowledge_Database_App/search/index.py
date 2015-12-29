"""
Search Index API

Contains functions and classes used to read and write to the
Elasticsearch cluster. Uses elasticsearch-py-dsl.

Classes:

    SearchableContentPiece

Exceptions:

    IndexAccessError

Functions:

    index_content_piece, update_content_piece, delete_content_piece
"""

from elasticsearch import NotFoundError
from elasticsearch_dsl import (DocType, String, Completion,
                               Index, analyzer, tokenizer)
from elasticsearch_dsl.connections import connections

from Knowledge_Database_App.storage.select_queries import InputError


KDB_cluster_url = "127.0.0.1:9200"
connections.create_connection(hosts=[KDB_cluster_url])
content = Index("content")


def _create_index():
    # Call only once.
    content.create()


bigram_analyzer = analyzer("bigram_analyzer", tokenizer=tokenizer(
    "bigram", "shingle", min_shingle_size=2, max_shingle_size=2),
    filter=["lowercase"],
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
        fields={"raw": String(index="not_analyzed")},
        properties={"suggest": Completion(payloads=True,
                                          preserve_separators=False,
                                          preserve_position_increments=False)}
    )
    alternate_names = String(
        multi=True,
        fields={"raw": String(multi=True, index="not_analyzed")},
        properties={"suggest": Completion(multi=True, payloads=True,
                                          preserve_separators=False,
                                          preserve_position_increments=False)},
        position_offset_gap=100
    )
    text = String(fields={"bigrams": String(analyzer=bigram_analyzer)})
    content_type = String()
    keywords = String(
        multi=True,
        fields={"raw": String(multi=True, index="not_analyzed")},
        properties={"suggest": Completion(multi=True, payloads=True,
                                          preserve_separators=False,
                                          preserve_position_increments=False)}
    )
    citations = String(
        multi=True,
        fields={"raw": String(multi=True, index="not_analyzed")},
        properties={"suggest": Completion(multi=True, payloads=True,
                                          preserve_separators=False,
                                          preserve_position_increments=False)}
    )


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
    content_piece.name.suggest = {
        "input": name_string,
        "payload": {"content_id": content_id}
    }
    content_piece.alternate_names.suggest = {
        "input": alternate_name_strings,
        "payload": {"content_id": content_id}
    }
    content_piece.keywords.suggest = {"input": keyword_strings}
    content_piece.citations.suggest = {"input": citation_strings}
    content_piece.meta.id = content_id
    content_piece.save()


def update_content_piece(content_id, content_part, part_string=None,
                        part_strings=None):
    """
    Args:
        content_id: Integer.
        content_part: String, accepts 'name', 'text', 'content_type',
            'keyword', or 'citation'.
        part_string: String. Defaults to None.
        part_strings: List of strings. Defaults to None.
    """
    try:
        content_piece = SearchableContentPiece.get(id=content_id)
    except NotFoundError as e:
        raise IndexAccessError(str(e))
    else:
        if content_part == "name":
            if part_string is not None:
                content_piece.name = part_string
                content_piece.name.suggest = {
                    "input": part_string,
                    "payload": {"content_id": content_id}
                }
            elif part_strings is not None:
                content_piece.alternate_names = part_strings
                content_piece.alternate_names.suggest = {
                    "input": part_strings,
                    "payload": {"content_id": content_id}
                }
            else:
                raise InputError("Invalid arguments!")
        elif content_part == "text":
            if part_string is not None:
                content_piece.text = part_string
            else:
                raise InputError("Invalid arguments!")
        elif content_part == "content_type":
            if part_string is not None:
                content_piece.content_type = part_string
            else:
                raise InputError("Invalid arguments!")
        elif content_part == "keyword":
            if part_strings is not None:
                content_piece.keywords = part_strings
                content_piece.keywords.suggest = {"input": part_strings}
            else:
                raise InputError("Invalid arguments!")
        elif content_part == "citation":
            if part_strings is not None:
                content_piece.citations = part_strings
                content_piece.citations.suggest = {"input": part_strings}
            else:
                raise InputError("Invalid arguments!")
        else:
            raise InputError("Invalid arguments!")


def delete_content_piece(content_id):
    """
    Args:
        content_id: Integer.
    """
    try:
        content_piece = SearchableContentPiece(id=content_id)
    except NotFoundError as e:
        raise IndexAccessError(str(e))
    else:
        content_piece.delete()
