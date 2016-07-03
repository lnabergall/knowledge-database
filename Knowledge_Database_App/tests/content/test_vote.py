"""
Content Vote Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase, skipIf

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.tests.storage import PostgresTest
from Knowledge_Database_App.tests.content.test_redis import RedisTest
from Knowledge_Database_App.tests.search import ElasticsearchTest
from Knowledge_Database_App.storage.select_queries import SelectError
from Knowledge_Database_App.content.content import Content
from Knowledge_Database_App.content.edit import Edit
from Knowledge_Database_App.content.vote import AuthorVote


class ContentVoteTest(PostgresTest, RedisTest, ElasticsearchTest):
    failure = False

    @classmethod
    def setUpClass(cls):
        PostgresTest.setUpClass.__func__(cls)
        RedisTest.setUpClass.__func__(cls)
        ElasticsearchTest.setUpClass.__func__(cls)
        cls.first_author_id = 1
        cls.piece = Content.bulk_retrieve(
            user_id=cls.first_author_id)[0]
        cls.content_id = cls.piece.content_id
        cls.start_timestamp = datetime.utcnow()
        cls.edit_text = ("Kylo Ren is the master of the Knights of Ren, "
                         "a dark Force user, apprentice of Supreme Leader "
                         "Snoke, and the son of Han Solo and Leia Organa.[ref:1]")
        cls.edit_rationale = "Unlimited power!"
        cls.content_part = "text"
        cls.part_id = cls.piece.text.text_id
        cls.edit = Edit(
            content_id=cls.content_id,
            edit_text=cls.edit_text,
            edit_rationale=cls.edit_rationale,
            content_part=cls.content_part,
            part_id=cls.part_id,
            original_part_text=cls.piece.text.text,
            author_type="U",
            author_id=cls.first_author_id,
            start_timestamp=cls.start_timestamp,
        )
        cls.edit.start_vote()

    @classmethod
    def tearDownClass(cls):
        PostgresTest.tearDownClass.__func__(cls)
        RedisTest.tearDownClass.__func__(cls)
        ElasticsearchTest.tearDownClass.__func__(cls)

    @skipIf(failure, "Previous test failed!")
    def test_01_create(self):
        try:
            self.__class__.vote = AuthorVote(
                "in-progress", self.__class__.edit.edit_id, 
                "Y", self.__class__.first_author_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.__class__.vote.vote_status, "in-progress")
                self.assertEqual(self.__class__.vote.edit_id, 
                                 self.__class__.edit.edit_id)
                self.assertEqual(self.__class__.vote.vote, "Y")
                self.assertEqual(self.__class__.vote.close_timestamp, None)
                self.assertEqual(self.__class__.vote.author.user_id, 
                                 self.__class__.first_author_id)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_02_save(self):
        try:
            self.__class__.vote.save()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                edit_votes = AuthorVote.bulk_retrieve(
                    "in-progress", edit_id=self.__class__.edit.edit_id)
            except Exception as e:
                self.failure = True
                self.fail(str(e))
            else:
                try:
                    self.assertTrue(edit_votes)
                    found = False
                    for vote in edit_votes:
                        if (vote.author.user_id == 
                                self.__class__.vote.author.user_id):
                            found = True
                            self.assertEqual(vote.author.user_id,
                                             self.__class__.vote.author.user_id)
                            self.assertEqual(vote.vote, self.__class__.vote.vote)
                            self.assertEqual(vote.vote_status, 
                                             self.__class__.vote.vote_status)
                            self.assertEqual(vote.timestamp, 
                                             self.__class__.vote.timestamp)
                    self.assertTrue(found)
                except AssertionError:
                    self.failure = True
                    raise

    @skipIf(failure, "Previous test failed!")
    def test_03_vote_summary(self):
        # Tests complete vote summary formatting process,
        # including both serialization and deserialization.
        try:
            vote_summary = AuthorVote.get_vote_summary([self.__class__.vote])
            vote_dict = AuthorVote.unpack_vote_summary(vote_summary)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(
                    vote_dict[self.__class__.first_author_id][0], "Y")
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_04_bulk_retrieve(self):
        try:
            edit_votes = AuthorVote.bulk_retrieve(
                "in-progress", edit_id=self.__class__.edit.edit_id)
            with self.assertRaises(SelectError):
                edit_ended_votes = AuthorVote.bulk_retrieve(
                    "ended", edit_id=self.__class__.edit.edit_id,
                    validation_status="accepted")
            content_votes = AuthorVote.bulk_retrieve(
                "in-progress", content_id=self.__class__.content_id)
            content_ended_votes = AuthorVote.bulk_retrieve(
                "ended", content_id=self.__class__.content_id,
                validation_status="accepted")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertNotIn(self.__class__.edit.edit_id, content_ended_votes)
                self.assertEqual(edit_votes[0].author.user_id,
                                 self.__class__.vote.author.user_id)
                self.assertEqual(edit_votes[0].vote, self.__class__.vote.vote)
                self.assertEqual(edit_votes[0].vote_status,
                                 self.__class__.vote.vote_status)
                self.assertEqual(edit_votes[0].timestamp, 
                                 self.__class__.vote.timestamp)
                vote = content_votes[self.__class__.edit.edit_id][0]
                self.assertEqual(vote.author.user_id, 
                                 self.__class__.vote.author.user_id)
                self.assertEqual(vote.vote, self.__class__.vote.vote)
                self.assertEqual(vote.vote_status, 
                                 self.__class__.vote.vote_status)
                self.assertEqual(vote.timestamp, self.__class__.vote.timestamp)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_05_votes_needed(self):
        try:
            votes_needed_dict = AuthorVote.votes_needed(
                self.__class__.first_author_id, 
                content_ids=[self.__class__.content_id])
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertFalse(self.__class__.edit.edit_id in
                                 votes_needed_dict[self.__class__.content_id])
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_06_json_ready(self):
        try:
            json_ready_version = self.__class__.vote.json_ready
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_version["edit_id"],
                                 self.__class__.vote.edit_id)
                self.assertEqual(json_ready_version["vote_status"],
                                 self.__class__.vote.vote_status)
                self.assertEqual(json_ready_version["timestamp"],
                                 str(self.__class__.vote.timestamp))
                self.assertEqual(json_ready_version["close_timestamp"],
                                 self.__class__.vote.close_timestamp)
                self.assertEqual(
                    json_ready_version[self.__class__.first_author_id], "Y")
            except AssertionError:
                self.failure = True
                raise
