"""
Search Query API

Contains functions used to query the Elasticsearch cluster.
Uses elasticsearch-py-dsl.

Functions:

    search, autocomplete
"""

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match

from Knowledge_Database_App.storage.select_queries import InputError
from index import SearchableContentPiece


def search(query_string, page_num):
    """
    Args:
        query_string: String.
        page_num: Positive integer.

    Returns:
        A dictionary of the form

        {"count": int, "results": result_list},

        where "count" holds a count of the number of results returned by
        the search and result_list is a list, sorted in descending order
        by query matching score, containing dict elements of the form:

        {
            "score": float,
            "content_id": int,
            "name": string,
            "alternate_names": list of strings,
            "highlights": {
                "name": string or None,
                "alternate_names": list of strings and Nones,
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
    content_search = content_search[10*(page_num-1) : 10*page_num]
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
            },
            "query_weight": 2,
            "rescore_query_weight": 1
        }
    }
    content_search = Search.from_dict(search_dict)

    # Request highlighting, execute the search, and return the result.
    content_search = content_search.highlight(
        "text", fragment_size=150, number_of_fragments=3, no_match_size=150)
    content_search = content_search.highlight("name", number_of_fragments=0)
    content_search = content_search.highlight(
        "alternate_names", number_of_fragments=0)
    response = content_search.execute()
    query_result = {"count": response.hits.total, "results": []}
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
        query_result["results"].append(body)

    return query_result


def autocomplete(content_part, query_string):
    """
    Args:
        content_part: String, accepts 'name', 'keyword', or 'citation'.
        query_string: String.

    Returns:
        A list. If content_part == 'name', contains dict
        elements of the form:

        {"completion": completed string, "content_id": int}

        Otherwise, contains dict elements of the form:

        {"completion": completed string}
    """
    # Setup autocomplete search.
    autocomplete_search = SearchableContentPiece.search()
    if content_part == "name":
        autocomplete_search = autocomplete_search.suggest(
            "suggestions", query_string,
            completion={"field": "name.suggest", "fuzzy": True, "size": 10}
        ).suggest(
            "alt_suggestions", query_string,
            completion={"field": "alternate_names.suggest",
                        "fuzzy": True, "size": 10}
        )
    elif content_part == "keyword":
        autocomplete_search = autocomplete_search.suggest(
            "suggestions", query_string,
            completion={"field": "keywords.suggest", "fuzzy": True, "size": 10}
        )
    elif content_part == "citation":
        autocomplete_search = autocomplete_search.suggest(
            "suggestions", query_string,
            completion={"field": "citations.suggest", "fuzzy": True, "size": 10}
        )
    else:
        raise InputError("Invalid argument!")

    # Execute the search and reformat the result.
    response = autocomplete_search.execute()
    completions = []
    if content_part == "name":
        suggestions = response.suggest.suggestions.options \
            + response.suggest.alt_suggestions.options
        for suggestion in suggestions:
            completions.append({
                "completion": suggestion.text,
                "content_id": suggestion.payload.content_id
            })
    elif content_part == "keyword" or content_part == "citation":
        for suggestion in response.suggest.suggitions.options:
            completions.append({"completion": suggestion.text})

    return completions