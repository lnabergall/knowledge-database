"""
Search Query API
"""

from elasticsearch_dsl.query import MultiMatch, Q

from Knowledge_Database_App.storage.select_queries import InputError
from index import SearchableContentPiece


def search(query_string):
    """
    Args:
        query_string: String.
    """
    query = MultiMatch(
        query=query_string,
        type="cross_fields",
        fields=["name^5", "alternate_names^5", "text^1",
                "content_type^3", "keywords^2", "citations^1"]
    )
    bigram_query = Q("rescore_query")
    search = SearchableContentPiece.search().query(query)


def auto_complete(content_part, query_string):
    """
    Args:
        content_part: String, accepts 'name', 'keyword', or 'citation'.
        query_string: String.
    """

