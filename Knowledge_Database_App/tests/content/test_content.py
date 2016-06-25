"""
Content Piece Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from math import ceil
from unittest import TestCase, skipIf
from elasticsearch import Elasticsearch

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.tests.storage import PostgresTest
from Knowledge_Database_App.tests.content.test_redis import RedisTest
from Knowledge_Database_App.tests.search import ElasticsearchTest
from Knowledge_Database_App.content.content import Content
from Knowledge_Database_App.search.index import SearchableContentPiece
from Knowledge_Database_App.storage import orm_core as orm


elastic_engine = Elasticsearch()


class ContentPieceTest(PostgresTest, RedisTest, ElasticsearchTest):
    failure = False

    @classmethod
    def setUpClass(cls):
        PostgresTest.setUpClass.__func__(cls)
        RedisTest.setUpClass.__func__(cls)
        ElasticsearchTest.setUpClass.__func__(cls)
        cls.first_author_id = 1
        cls.first_author_name = cls._session.query(orm.User.user_name).filter(
            orm.User.user_id == 1).scalar()
        cls._session.close()
        cls.content_type = "definition"
        cls.name = "Kylo Ren"
        cls.alternate_names = ["Ben Solo"]
        cls.text = ("Kylo Ren is the master of the Knights of Ren, "
                    "a dark side Force user, and the son of " 
                    "Han Solo and Leia Organa.[ref:1]")
        cls.keywords = ["Star Wars", "The Force Awakens", "The First Order"]
        cls.citations = ["[1] Abrams, J.J. Star Wars: The Force Awakens. 2016."]

    @classmethod
    def tearDownClass(cls):
        PostgresTest.tearDownClass.__func__(cls)
        RedisTest.tearDownClass.__func__(cls)
        ElasticsearchTest.tearDownClass.__func__(cls)
    
    @skipIf(failure, "Previous test failed!")
    def test_01_create(self):
        try:
            self.__class__.piece = Content(
                first_author_name=self.__class__.first_author_name,
                first_author_id=self.__class__.first_author_id,
                content_type=self.__class__.content_type,
                name=self.__class__.name,
                alternate_names=self.__class__.alternate_names,
                text=self.__class__.text,
                keywords=self.__class__.keywords,
                citations=self.__class__.citations
            )
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.__class__.piece.first_author.user_id,
                                 self.__class__.first_author_id)
                self.assertEqual(self.__class__.piece.first_author.user_name,
                                 self.__class__.first_author_name)
                self.assertEqual(self.__class__.piece.content_type, 
                                 self.__class__.content_type)
                self.assertEqual(self.__class__.piece.name.name, 
                                 self.__class__.name)
                self.assertEqual(self.__class__.piece.name.name_type, "primary")
                self.assertEqual([name.name for name in
                                  self.__class__.piece.alternate_names],
                                 self.__class__.alternate_names)
                self.assertEqual(self.__class__.piece.text.text, 
                                 self.__class__.text)
                self.assertEqual(set(self.__class__.piece.keywords), 
                                 set(self.__class__.keywords))
                self.assertEqual(set(self.__class__.piece.citations), 
                                 set(self.__class__.citations))
                self.assertEqual(self.__class__.piece.stored, False)
                self.assertIsInstance(self.__class__.piece.timestamp, datetime)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_02_store(self):
        try:
            self.__class__.piece.store()
            elastic_engine.indices.refresh()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.__class__.piece.content_id, int)
                self.assertEqual(self.__class__.piece.stored, True)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
    
    @skipIf(failure, "Previous test failed!")
    def test_03_retrieve(self):
        try:
            piece = Content(content_id=self.__class__.piece.content_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(piece.first_author.user_id,
                                 self.__class__.first_author_id)
                self.assertEqual(piece.first_author.user_name,
                                 self.__class__.first_author_name)
                self.assertEqual(piece.content_type, self.__class__.content_type)
                self.assertEqual(piece.name.name, self.__class__.name)
                self.assertEqual(piece.name.name_type, "primary")
                self.assertEqual([name.name for name in piece.alternate_names],
                                 self.__class__.alternate_names)
                self.assertEqual(piece.text.text, self.__class__.text)
                self.assertEqual(set(piece.keywords), 
                                 set(self.__class__.keywords))
                self.assertEqual(set(piece.citations), 
                                 set(self.__class__.citations))
                self.assertEqual(piece.stored, True)
                self.assertIsInstance(piece.timestamp, datetime)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
    
    @skipIf(failure, "Previous test failed!")
    def test_04_bulk_retrieve(self):
        arbitrary_user_id = 23
        try:
            arbitrary_user_content, count1 = Content.bulk_retrieve(
                user_id=arbitrary_user_id, page_num=1, return_count=True)
            arbitrary_user_content_ids, count2 = Content.bulk_retrieve(
                user_id=arbitrary_user_id, ids_only=True, return_count=True)
            content, count3 = Content.bulk_retrieve(
                user_id=self.__class__.first_author_id, return_count=True)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
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
                self.assertTrue(any([
                    piece.content_id == self.__class__.piece.content_id
                    for piece in content
                ]))
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_05_get_content_types(self):
        try:
            content_types = Content.get_content_types()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                for content_type in content_types:
                    self.assertIsInstance(content_type, str)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_06_check_uniqueness(self):
        try:
            unique_name = Content.check_uniqueness(
                self.__class__.piece.content_id, 
                "Ben Organa", 
                "name"
            )
            copied_name = Content.check_uniqueness(
                self.__class__.piece.content_id, 
                self.__class__.piece.name.name, 
                "name"
            )
            unique_keyword = Content.check_uniqueness(
                self.__class__.piece.content_id, 
                "Skywalker", 
                "keyword"
            )
            copied_keyword = Content.check_uniqueness(
                self.__class__.piece.content_id, 
                self.__class__.piece.keywords[0], 
                "keyword"
            )
            unique_citation = Content.check_uniqueness(
                self.__class__.piece.content_id,
                "Lucas, George. Star Wars: A New Hope. 1977.",
                "citation"
            )
            copied_citation = Content.check_uniqueness(
                self.__class__.piece.content_id, 
                self.__class__.piece.citations[0], 
                "citation"
            )
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(unique_name, True)
                self.assertEqual(copied_name, False)
                self.assertEqual(unique_keyword, True)
                self.assertEqual(copied_keyword, False)
                self.assertEqual(unique_citation, True)
                self.assertEqual(copied_citation, False)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
    
    @skipIf(failure, "Previous test failed!")
    def test_07_filter_by(self):
        try:
            results = Content.filter_by("content_type", self.__class__.content_type)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            if results["count"] <= 10:
                try:
                    self.assertTrue(any([
                        result["content_id"] == self.__class__.piece.content_id
                        for result in results["results"]
                    ]))
                except AssertionError:
                    self.failure = True
                    raise
            else:
                found = False
                for i in range(ceil(results["count"]/10)):
                    try:
                        results = Content.filter_by(
                            "keyword", self.__class__.keywords[0], page_num=i+1)
                    except Exception as e:
                        self.failure = True
                        self.fail(str(e))
                    else:
                        found = any([
                            result["content_id"] == self.__class__.piece.content_id
                            for result in results["results"]
                        ])
                        if found:
                            break
                try:
                    self.assertTrue(found)
                except AssertionError:
                    self.failure = True
                    raise
                except Exception as e:
                    self.failure = True
                    self.fail(str(e))
          
    @skipIf(failure, "Previous test failed!")
    def test_08_search(self):
        try:
            results = Content.search("the force awakens")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            if results["count"] <= 10:
                try:
                    self.assertTrue(any([
                        result["content_id"] == self.__class__.piece.content_id
                        for result in results["results"]
                    ]))
                except AssertionError:
                    self.failure = True
                    raise
            else:
                found = False
                for i in range(ceil(results["count"]/10)):
                    try:
                        results = Content.search(
                            "the force awakens", page_num=i+1)
                    except Exception as e:
                        self.failure = True
                        self.fail(str(e))
                    else:
                        found = any([
                            result["content_id"] == self.__class__.piece.content_id
                            for result in results["results"]
                        ])
                        if found:
                            break
                try:
                    self.assertTrue(found)
                except AssertionError:
                    self.failure = True
                    raise
                except Exception as e:
                    self.failure = True
                    self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_09_autocomplete(self):
        try:
            keyword_completions = Content.autocomplete(
                "keyword", self.__class__.keywords[1].lower()[:8])
            name_completions = Content.autocomplete(
                "name", self.__class__.name.lower()[:4])
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertTrue(any([
                    completion["completion"] == self.__class__.keywords[1]
                    for completion in keyword_completions
                ]))
                self.assertTrue(any([
                    completion["content_id"] == self.__class__.piece.content_id
                    for completion in name_completions
                ]))
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_10_update(self):
        timestamp = datetime.utcnow()
        try:
            Content.update(self.__class__.piece.content_id, "keyword", "add",
                           timestamp, part_text="Skywalker")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            self.__class__.piece = Content(
                content_id=self.__class__.piece.content_id)
            try:
                self.assertTrue("Skywalker" in self.__class__.piece.keywords)
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_11_json_ready(self):
        try:
            json_ready_version = self.__class__.piece.json_ready
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_version["content_id"],
                                 self.__class__.piece.content_id)
                self.assertEqual(json_ready_version["timestamp"],
                                 str(self.__class__.piece.timestamp))
                self.assertEqual(json_ready_version["deleted_timestamp"],
                                 self.__class__.piece.deleted_timestamp)
                self.assertIsInstance(json_ready_version["first_author"], dict)
                self.assertEqual(json_ready_version["first_author"]["user_name"],
                                 self.__class__.piece.first_author.user_name)
                self.assertIsInstance(json_ready_version["name"], dict)
                self.assertEqual(json_ready_version["name"]["name"],
                                 self.__class__.piece.name.name)
                self.assertEqual(json_ready_version["content_type"],
                                 self.__class__.piece.content_type)
                self.assertIsInstance(json_ready_version["text"], dict)
                self.assertEqual(json_ready_version["text"]["text"],
                                 self.__class__.piece.text.text)
                self.assertEqual(json_ready_version["citations"],
                                 self.__class__.piece.citations)
                self.assertEqual(json_ready_version["keywords"],
                                 self.__class__.piece.keywords)
                self.assertIsInstance(json_ready_version["alternate_names"], list)
                for i in range(len(self.__class__.piece.alternate_names)):
                    self.assertEqual(
                        json_ready_version["alternate_names"][i]["name"],
                        self.__class__.piece.alternate_names[i].name
                    )
            except AssertionError:
                self.failure = True
                raise
            except Exception as e:
                self.failure = True
                self.fail(str(e))
    