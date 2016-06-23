"""
Search Query API Unit Tests

Currently primarily tests only core functionality of all
functions, not exceptional cases.
"""

from unittest import TestCase

from Knowledge_Database_App import search as search_api
from Knowledge_Database_App.tests.search import ElasticsearchTest


class SearchQueryTest(ElasticsearchTest):

    def test_search(self):
        try:
            response = search_api.search("the", page_num=1)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(response, dict)
            self.assertIsInstance(response["count"], int)
            results_page1 = response["results"]
            self.assertIsInstance(results_page1, list)
            if results_page1:
                self.assertGreater(response["count"], 0)
                self.assertIsInstance(results_page1[-1], dict)
                self.assertIsInstance(results_page1[-1]["score"], float)
                self.assertIsInstance(results_page1[-1]["content_id"], int)
                self.assertIsInstance(results_page1[-1]["name"], str)
                self.assertIsInstance(results_page1[-1]["alternate_names"], list)
                self.assertIsInstance(results_page1[-1]["alternate_names"][-1], str)
                if results_page1[-1]["highlights"]["name"] is not None:
                    self.assertIsInstance(
                        results_page1[-1]["highlights"]["name"], str)
                self.assertIsInstance(
                    results_page1[-1]["highlights"]["alternate_names"], list)
                if results_page1[-1]["highlights"]["alternate_names"][-1] is not None:
                    self.assertIsInstance(
                        results_page1[-1]["highlights"]["alternate_names"][-1], str)
                self.assertIsInstance(results_page1[-1]["highlights"]["text"], list)
                self.assertIsInstance(
                    results_page1[-1]["highlights"]["text"][-1], str)
            else:
                self.assertEqual(response["count"], 0)

    def test_filter_by(self):
        try:
            name_response = search_api.filter_by("name", "lem", page_num=1)
            content_type_response = search_api.filter_by(
                "name", "def", page_num=1)
            keyword_response = search_api.filter_by("name", "zeta", page_num=1)
            citation_response = search_api.filter_by("name", "mat", page_num=1)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(name_response, dict)
            self.assertIsInstance(content_type_response, dict)
            self.assertIsInstance(keyword_response, dict)
            self.assertIsInstance(citation_response, dict)
            name_results = name_response["results"]
            content_type_results = content_type_response["results"]
            keyword_results = keyword_response["results"]
            citation_results = citation_response["results"]
            self.assertIsInstance(name_results, list)
            self.assertIsInstance(content_type_results, list)
            self.assertIsInstance(keyword_results, list)
            self.assertIsInstance(citation_results, list)
            if name_results:
                self.assertGreater(name_response["count"], 0)
                self.assertIsInstance(name_results[-1], dict)
                self.assertIsInstance(name_results[-1]["score"], float)
                self.assertIsInstance(name_results[-1]["content_id"], int)
                self.assertIsInstance(name_results[-1]["name"], str)
                self.assertIsInstance(name_results[-1]["alternate_names"], list)
                for name in name_results[-1]["alternate_names"]:
                    self.assertIsInstance(name, str)
                self.assertIsInstance(name_results[-1]["text_fragment"], str)
            else:
                self.assertEqual(name_response["count"], 0)

            if content_type_results:
                self.assertGreater(content_type_response["count"], 0)
                self.assertGreater(content_type_response["count"], 0)
                self.assertIsInstance(content_type_results[-1], dict)
                self.assertIsInstance(content_type_results[-1]["score"], float)
                self.assertIsInstance(content_type_results[-1]["content_id"], int)
                self.assertIsInstance(content_type_results[-1]["name"], str)
                self.assertIsInstance(
                    content_type_results[-1]["alternate_names"], list)
                for name in content_type_results[-1]["alternate_names"]:
                    self.assertIsInstance(name, str)
                self.assertIsInstance(
                    content_type_results[-1]["text_fragment"], str)
            else:
                self.assertEqual(content_type_response["count"], 0)
            if keyword_results:
                self.assertGreater(keyword_response["count"], 0)
                self.assertGreater(keyword_response["count"], 0)
                self.assertIsInstance(keyword_results[-1], dict)
                self.assertIsInstance(keyword_results[-1]["score"], float)
                self.assertIsInstance(keyword_results[-1]["content_id"], int)
                self.assertIsInstance(keyword_results[-1]["name"], str)
                self.assertIsInstance(
                    keyword_results[-1]["alternate_names"], list)
                for name in keyword_results[-1]["alternate_names"]:
                    self.assertIsInstance(name, str)
                self.assertIsInstance(keyword_results[-1]["text_fragment"], str)
            else:
                self.assertEqual(keyword_response["count"], 0)
            if citation_results:
                self.assertGreater(citation_response["count"], 0)
                self.assertGreater(citation_response["count"], 0)
                self.assertIsInstance(citation_results[-1], dict)
                self.assertIsInstance(citation_results[-1]["score"], float)
                self.assertIsInstance(citation_results[-1]["content_id"], int)
                self.assertIsInstance(citation_results[-1]["name"], str)
                self.assertIsInstance(
                    citation_results[-1]["alternate_names"], list)
                for name in citation_results[-1]["alternate_names"]:
                    self.assertIsInstance(name, str)
                self.assertIsInstance(
                    citation_results[-1]["text_fragment"], str)
            else:
                self.assertEqual(citation_response["count"], 0)

    def test_autocomplete(self):
        try:
            name_completions = search_api.autocomplete("name", "lem")
            keyword_completions = search_api.autocomplete("keyword", "zeta")
            citation_completions = search_api.autocomplete("citation", "mat")
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(name_completions, list)
            self.assertIsInstance(keyword_completions, list)
            self.assertIsInstance(citation_completions, list)
            if name_completions:
                self.assertIsInstance(name_completions[-1], dict)
                self.assertIsInstance(name_completions[-1]["completion"], str)
                self.assertIsInstance(name_completions[-1]["content_id"], int)
            if keyword_completions:
                self.assertIsInstance(keyword_completions[-1], dict)
                self.assertIsInstance(keyword_completions[-1]["completion"], str)
            if citation_completions:
                self.assertIsInstance(citation_completions[-1], dict)
                self.assertIsInstance(citation_completions[-1]["completion"], str)
