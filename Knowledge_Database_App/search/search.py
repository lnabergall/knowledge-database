"""
Search Query API

Contains functions used to query the Elasticsearch cluster.
Uses elasticsearch-py-dsl.

Functions:

    search, filter_by, autocomplete
"""
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match, Term, Q

from Knowledge_Database_App.storage.exceptions import InputError
from .index import SearchableContentPiece


def search(query_string, page_num=1):
    """
    Args:
        query_string: String.
        page_num: Positive integer. Defaults to 1.

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
            "content_part": string,
            "keywords": list of strings,
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
    bigram_query = Q({
        "match": {
            "text.bigrams" : {
                "query": query_string, "boost": 0.4}
            }
        }
    )
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
    content_search = content_search.highlight_options(order="score")
    content_search = content_search.highlight(
        "text", fragment_size=150, number_of_fragments=3, no_match_size=150)
    content_search = content_search.highlight("name", number_of_fragments=0)
    content_search = content_search.highlight(
        "alternate_names", number_of_fragments=0)
    response = content_search.execute()
    query_result = {"count": response.hits.total, "results": []}
    for hit in response:
        highlighted_name = None
        highlighted_alt_name = None
        if "name" in dir(hit.meta.highlight):
            highlighted_name = hit.meta.highlight.name
        if "alternate_names" in dir(hit.meta.highlight):
            highlighted_alt_name = hit.meta.highlight.alternate_names
        body = {
            "score": hit.meta.score,
            "content_id": int(hit.meta.id),
            "name": hit.name,
            "alternate_names": hit.alternate_names,
            "content_part": hit.content_type,
            "keywords": hit.keywords,
            "highlights": {
                "name": highlighted_name,
                "alternate_names": highlighted_alt_name,
                "text": hit.meta.highlight.text
            }
        }
        query_result["results"].append(body)

    return query_result


def filter_by(content_part, part_string, page_num=1):
    """
    Args:
        content_part: String, accepts 'keyword', 'content_type', 'name',
            or 'citation'.
        part_string: String.
        page_num: Positive integer. Defaults to 1.

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
            "text_fragment": 200 character string fragment,
        }
    """
    search = SearchableContentPiece.search()
    search = search[10*(page_num-1) : 10*page_num]
    if content_part == "keyword":
        query = Q("bool", filter=[Q("term", keywords=part_string)])
    elif content_part == "content_type":
        query = Q("bool", filter=[Q("term", content_type=part_string)])
    elif content_part == "citation":
        query = Q("bool", filter=[Q("term", citations=part_string)])
    elif content_part == "name":
        query = (Q("bool", filter=[Q("term", name=part_string)]) |
                 Q("bool", filter=[Q("term", alternate_names=part_string)]))
    else:
        raise InputError("Missing arguments!")
    search = search.query(query)
    response = search.execute()
    results = {"count": response.hits.total, "results": []}
    for hit in response:
        body = {
            "score": hit.meta.score,
            "content_id": int(hit.meta.id),
            "name": hit.name,
            "alternate_names": hit.alternate_names,
            "text_fragment": hit.text[:201],
        }
        results["results"].append(body)

    return results


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
            completion={"field": "name_suggest", "fuzzy": True, "size": 10}
        ).suggest(
            "alt_suggestions", query_string,
            completion={"field": "alternate_names_suggest",
                        "fuzzy": True, "size": 10}
        )
    elif content_part == "keyword":
        autocomplete_search = autocomplete_search.suggest(
            "suggestions", query_string,
            completion={"field": "keywords_suggest", "fuzzy": True, "size": 10}
        )
    elif content_part == "citation":
        autocomplete_search = autocomplete_search.suggest(
            "suggestions", query_string,
            completion={"field": "citations_suggest", "fuzzy": True, "size": 10}
        )
    else:
        raise InputError("Invalid argument!")

    # Execute the search and reformat the result.
    response = autocomplete_search.execute()
    completions = []
    if response:
        if len(response.suggest.suggestions) > 1:
            raise NotImplementedError
        if content_part == "name":
            for result in response.suggest.suggestions:
                for suggestion in result.options:
                    completions.append({
                        "completion": suggestion.text,
                        "content_id": int(suggestion.payload.content_id)
                    })
        elif content_part == "keyword" or content_part == "citation":
            for result in response.suggest.suggestions:
                for suggestion in result.options:
                    completions.append({"completion": suggestion.text})

    return completions

# TODO: Implement and combine name and alternate name suggestions,
# likely via a combined 'names' field on SearchableContentPiece 
