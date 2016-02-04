"""
Content Piece Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from math import ceil
from unittest import TestCase

from Knowledge_Database_App.content.content import Content


class ContentPieceTest(TestCase):

    def setUp(self):
        self.first_author_name = "Test Ai"
        self.first_author_id = 1
        self.content_type = "definition"
        self.name = "Kylo Ren"
        self.alternate_names = ["Ben Solo"]
        self.text = ("Kylo Ren is the master of the Knights of Ren, "
                     "a dark side Force user, and the son of " +
                     "Han Solo and Leia Organa.[ref:1]")
        self.keywords = ["Star Wars", "The Force Awakens", "The First Order"]
        self.citations = ["[1] Abrams, J.J. Star Wars: The Force Awakens. 2016."]

    def test_01_create(self):
        try:
            self.piece = Content(
                first_author_name=self.first_author_name,
                first_author_id=self.first_author_id,
                content_type=self.content_type,
                name=self.name,
                alternate_names=self.alternate_names,
                text=self.text,
                keywords=self.keywords,
                citations=self.citations
            )
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertEqual(self.piece.first_author.user_id, self.first_author_id)
            self.assertEqual(self.piece.first_author.user_name,
                             self.first_author_name)
            self.assertEqual(self.piece.content_type, self.content_type)
            self.assertEqual(self.piece.name.name, self.name)
            self.assertEqual(self.piece.name.name_type, "primary")
            self.assertEqual([name.name for name in self.piece.alternate_names],
                             self.alternate_names)
            self.assertEqual(self.piece.text.text, self.text)
            self.assertEqual(self.piece.keywords, self.keywords)
            self.assertEqual(self.piece.citations, self.citations)
            self.assertEqual(self.piece.stored, False)
            self.assertIsInstance(self.piece.timestamp, datetime)

    def test_02_store(self):
        try:
            self.piece.store()
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(self.piece.content_id, int)
            self.assertEqual(self.piece.stored, True)

    def test_03_retrieve(self):
        try:
            piece = Content(content_id=self.piece.content_id)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertEqual(piece.first_author.user_id, self.first_author_id)
            self.assertEqual(piece.first_author.user_name,
                             self.first_author_name)
            self.assertEqual(piece.content_type, self.content_type)
            self.assertEqual(piece.name.name, self.name)
            self.assertEqual(piece.name.name_type, "primary")
            self.assertEqual([name.name for name in piece.alternate_names],
                             self.alternate_names)
            self.assertEqual(piece.text.text, self.text)
            self.assertEqual(piece.keywords, self.keywords)
            self.assertEqual(piece.citations, self.citations)
            self.assertEqual(piece.stored, False)
            self.assertIsInstance(piece.timestamp, datetime)

    def test_04_bulk_retrieve(self):
        arbitrary_user_id = 23
        try:
            arbitrary_user_content, count1 = Content.bulk_retrieve(
                user_id=arbitrary_user_id, page_num=1, return_count=True)
            arbitrary_user_content_ids, count2 = Content.bulk_retrieve(
                user_id=arbitrary_user_id, ids_only=True, return_count=True)
            content, count3 = Content.bulk_retrieve(
                user_id=self.first_author_id, return_count=True)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(count1, int)
            self.assertIsInstance(count2, int)
            self.assertIsInstance(count3, int)
            self.assertTrue(count2-1 <= count1 <= count2)
            self.assertEqual(len(arbitrary_user_content_ids), count2)
            self.assertLessEqual(len(arbitrary_user_content), 10)
            for piece in arbitrary_user_content:
                self.assertIsInstance(piece, Content)
            for content_id in arbitrary_user_content_ids:
                self.assertIsInstance(content_id, int)
            for piece in content:
                self.assertIsInstance(piece, Content)
            self.assertTrue(any([piece.content_id == self.piece.content_id
                                 for piece in content]))

    def test_05_get_content_types(self):
        try:
            content_types = Content.get_content_types()
        except Exception as e:
            self.fail(str(e))
        else:
            for content_type in content_types:
                self.assertIsInstance(content_type, str)

    def test_06_check_uniqueness(self):
        try:
            unique_name = Content.check_uniqueness(
                self.piece.content_id, "Ben Organa", "name")
            copied_name = Content.check_uniqueness(
                self.piece.content_id, self.piece.name.name, "name")
            unique_keyword = Content.check_uniqueness(
                self.piece.content_id, "Skywalker", "keyword")
            copied_keyword = Content.check_uniqueness(
                self.piece.content_id, self.piece.keywords[0], "keyword")
            unique_citation = Content.check_uniqueness(
                self.piece.content_id,
                "Lucas, George. Star Wars: A New Hope. 1977.",
                "citation")
            copied_citation = Content.check_uniqueness(
                self.piece.content_id, self.piece.citations[0], "citation")
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertEqual(unique_name, True)
            self.assertEqual(copied_name, False)
            self.assertEqual(unique_keyword, True)
            self.assertEqual(copied_keyword, False)
            self.assertEqual(unique_citation, True)
            self.assertEqual(copied_citation, False)

    def test_07_filter_by(self):
        try:
            results = Content.filter_by("keyword", self.keywords[0])
        except Exception as e:
            self.fail(str(e))
        else:
            if results["count"] <= 10:
                self.assertTrue(any([
                    result["content_id"] == self.piece.content_id
                    for result in results["results"]
                ]))
            else:
                found = False
                for i in range(ceil(results["count"]/10)):
                    try:
                        results = Content.filter_by(
                            "keyword", self.keywords[0], page_num=i+1)
                    except Exception as e:
                        self.fail(str(e))
                    else:
                        found = any([
                            result["content_id"] == self.piece.content_id
                            for result in results["results"]
                        ])
                self.assertTrue(found)

    def test_08_search(self):
        try:
            results = Content.search("the force awakens")
        except Exception as e:
            self.fail(str(e))
        else:
            if results["count"] <= 10:
                self.assertTrue(any([
                    result["content_id"] == self.piece.content_id
                    for result in results["results"]
                ]))
            else:
                found = False
                for i in range(ceil(results["count"]/10)):
                    try:
                        results = Content.search(
                            "the force awakens", page_num=i+1)
                    except Exception as e:
                        self.fail(str(e))
                    else:
                        found = any([
                            result["content_id"] == self.piece.content_id
                            for result in results["results"]
                        ])
                self.assertTrue(found)

    def test_09_autocomplete(self):
        try:
            keyword_completions = Content.autocomplete(
                "keyword", self.keywords[1].lower()[:8])
            name_completions = Content.autocomplete(
                "name", self.name.lower()[:4])
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertTrue(any([
                completion["completion"] == self.keywords[1]
                for completion in keyword_completions
            ]))
            self.assertTrue(any([
                completion["content_id"] == self.piece.content_id
                for completion in name_completions
            ]))

    def test_10_update(self):
        timestamp = datetime.utcnow()
        try:
            Content.update(self.piece.content_id, "keyword", "add",
                           timestamp, part_text="Skywalker")
        except Exception as e:
            self.fail(str(e))
        else:
            self.piece = Content(content_id=self.piece.content_id)
            self.assertTrue("Skywalker" in self.piece.keywords)

    def test_11_json_ready(self):
        try:
            json_ready_version = self.piece.json_ready
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertEqual(json_ready_version["content_id"],
                             self.piece.content_id)
            self.assertEqual(json_ready_version["timestamp"],
                             str(self.piece.timestamp))
            self.assertEqual(json_ready_version["deleted_timestamp"],
                             self.piece.deleted_timestamp)
            self.assertIsInstance(json_ready_version["first_author"], dict)
            self.assertEqual(json_ready_version["first_author"]["user_name"],
                             self.piece.first_author.user_name)
            self.assertEqual(json_ready_version["name"], dict)
            self.assertEqual(json_ready_version["name"]["name"],
                             self.piece.name.name)
            self.assertEqual(json_ready_version["content_type"],
                             self.piece.content_type)
            self.assertEqual(json_ready_version["text"], dict)
            self.assertEqual(json_ready_version["text"]["text"],
                             self.piece.text.text)
            self.assertEqual(json_ready_version["citations"],
                             self.piece.citations)
            self.assertEqual(json_ready_version["keywords"],
                             self.piece.keywords)
            self.assertEqual(json_ready_version["alternate_names"], list)
            for i in range(len(self.piece.alternate_names)):
                self.assertEqual(
                    json_ready_version["alternate_names"][i]["name"],
                    self.piece.alternate_names[i].name
                )
