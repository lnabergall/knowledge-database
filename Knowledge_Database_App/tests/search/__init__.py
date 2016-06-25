"""
Base Unit Test classes for handling Elasticsearch index 
resetting before and after unit testing.
"""

from unittest import TestCase

from Knowledge_Database_App.search import index


class ElasticsearchTest(TestCase):

    @classmethod
    def setUpClass(cls):
        print("Elasticsearch setup")
        index._delete_index()
        index._create_index()

    @classmethod
    def tearDownClass(cls):
        print("Elasticsearch teardown")
        index._delete_index()
