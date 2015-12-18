"""
Search Query API
"""

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match

from index import SearchableContentPiece


def search(query_string):
    """
    Args:
        query_string: String.
    Returns:
        A dict of the form:

        {
            "score": float,
            "content_id": int,
            "name": string,
            "alternate_names": list of strings,
            "highlights": {
                "name": string or None,
                "alternate_names": list of strings,
                "text": list of strings
            }
        }
    """
    # First apply two rounds of match queries.
    query = MultiMatch(
        query=query_string,
        type="cross_fields",
        fields=["name^5", "alternate_names^5", "text^1",
                "content_type^3", "keywords^2", "citations^1"]
    )
    bigram_query = Match(query=query_string, fields=["text.bigrams"], boost=0.4)
    content_search = SearchableContentPiece.search()
    content_search = content_search.query(query).query(bigram_query)

    # Then rescore the top results with a fuzzy phrase match.
    search_dict = content_search.to_dict()
    search_dict["rescore"] = {
        "window_size": 50,
        "query": {
            "rescore_query": {
                "bool": {
                    "should": [
                        {"match_phrase": {
                            "text": {"query": query_string, "slop": 50}}},
                        {"match_phrase": {
                            "name": {"query": query_string, "slop": 10}}},
                        {"match_phrase": {
                            "alternate_names": {
                                "query": query_string, "slop": 10}}}
                    ]
                }
            }
        }
    }
    content_search = Search.from_dict(search_dict)

    # Apply highlighting, execute the search, and return the result.
    content_search = content_search.highlight(
        "text", fragment_size=150, number_of_fragments=3)
    content_search = content_search.highlight("name", number_of_fragments=0)
    content_search = content_search.highlight(
        "alternate_names", number_of_fragments=0)
    response = content_search.execute()
    query_result = []
    for hit in response:
        body = {
            "score": hit.meta.score,
            "content_id": hit.meta.id,
            "name": hit.name,
            "alternate_names": hit.alternate_names,
            "highlights": {
                "name": hit.meta.highlight.name,
                "alternate_names": hit.meta.highlight.alternate_names,
                "text": hit.meta.highlight.text
            }
        }
        query_result.append(body)

    return query_result

def auto_complete(content_part, query_string):
    """
    Args:
        content_part: String, accepts 'name', 'keyword', or 'citation'.
        query_string: String.
    """
