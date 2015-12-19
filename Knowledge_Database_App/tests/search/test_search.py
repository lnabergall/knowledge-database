"""
Search Query API Unit Tests

Currently primarily tests only core functionality of all
functions, not exceptional cases.
"""

from unittest import TestCase

from Knowledge_Database_App.search import search, autocomplete

class SearchQueryTestCase(TestCase):

    def test_search(self):
        results_page1 = search("the", 1)
        self.assertIsInstance(results_page1, list)
        if results_page1:
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

    def test_autocomplete(self):
        try:
            name_completions = autocomplete("name", "lem")
            keyword_completions = autocomplete("keyword", "zeta")
            citation_completions = autocomplete("citation", "mat")
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
