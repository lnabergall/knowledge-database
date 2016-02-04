"""
Content Vote Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from datetime import datetime
from unittest import TestCase, skipIf

from Knowledge_Database_App.content.content import Content
from Knowledge_Database_App.content.edit import Edit
from Knowledge_Database_App.content.vote import AuthorVote


class ContentVoteTest(TestCase):

    def setUp(self):
        self.failure = False
        self.first_author_id = 1
        user_content_pieces = Content.bulk_retrieve(user_id=self.first_author_id)
        if self.name in [piece.name.name for piece in user_content_pieces]:
            self.piece = filter(lambda piece: piece.name.name == self.name,
                                user_content_pieces)[0]
        else:
            self.failure = True
            return
        self.content_id = self.piece.content_id
        self.start_timestamp = datetime.utcnow()
        self.edit_text = ("Kylo Ren is the master of the Knights of Ren, "
                          "a dark Force user, apprentice of Supreme Leader "
                          "Snoke, and the son of Han Solo and Leia Organa.[ref:1]")
        self.edit_rationale = "Unlimited power!"
        self.content_part = "text"
        self.part_id = self.piece.text.text_id
        self.failure = False
        self.edit = Edit(
            content_id=self.content_id,
            edit_text=self.edit_text,
            edit_rationale=self.edit_rationale,
            content_part=self.content_part,
            part_id=self.part_id,
            original_part_text=self.text,
            author_type="U",
            author_id=self.first_author_id,
            start_timestamp=self.start_timestamp,
        )
        self.edit.start_vote()

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_01_create(self):
        try:
            self.vote = AuthorVote("in-progress", self.edit.edit_id,
                                   "Y", self.first_author_id)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(self.vote.vote_status, "in-progress")
                self.assertEqual(self.vote.edit_id, self.edit.edit_id)
                self.assertEqual(self.vote.vote, "Y")
                self.assertEqual(self.vote.close_timestamp, None)
                self.assertEqual(self.vote.author.user_id, self.first_author_id)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_02_vote_summary(self):
        # Tests complete vote summary formatting process,
        # including both serialization and deserialization.
        try:
            vote_summary = AuthorVote.get_vote_summary([self.vote])
            vote_dict = AuthorVote.unpack_vote_summary(vote_summary)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(vote_dict[self.first_author_id][0], "Y")
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_03_bulk_retrieve(self):
        try:
            edit_votes = AuthorVote.bulk_retrieve(
                "in-progress", edit_id=self.edit.edit_id)
            edit_ended_votes = AuthorVote.bulk_retrieve(
                "ended", edit_id=self.edit.edit_id)
            content_votes = AuthorVote.bulk_retrieve(
                "in-progress", content_id=self.content_id)
            content_ended_votes = AuthorVote.bulk_retrieve(
                "ended", content_id=self.content_id,
                validation_status="accepted")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertFalse(edit_ended_votes)
                self.assertFalse(content_ended_votes[self.edit.edit_id])
                self.assertEqual(edit_votes[0].author.user_id,
                                 self.vote.author.user_id)
                self.assertEqual(edit_votes[0].vote, self.vote.vote)
                self.assertEqual(edit_votes[0].vote_status,
                                 self.vote.vote_status)
                self.assertEqual(edit_votes[0].timestamp, self.vote.timestamp)
                vote = content_votes[self.edit.edit_id][0]
                self.assertEqual(vote.author.user_id, self.vote.author.user_id)
                self.assertEqual(vote.vote, self.vote.vote)
                self.assertEqual(vote.vote_status, self.vote.vote_status)
                self.assertEqual(vote.timestamp, self.vote.timestamp)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_04_votes_needed(self):
        try:
            votes_needed_dict = AuthorVote.votes_needed(
                self.first_author_id, content_ids=[self.content_id])
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertTrue(self.edit.edit_id in
                                votes_needed_dict[self.content_id])
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_05_json_ready(self):
        try:
            json_ready_version = self.vote.json_ready
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(json_ready_version["edit_id"],
                                 self.vote.edit_id)
                self.assertEqual(json_ready_version["vote_status"],
                                 self.vote.vote_status)
                self.assertEqual(json_ready_version["timestamp"],
                                 str(self.vote.timestamp))
                self.assertEqual(json_ready_version["close_timestamp"],
                                 self.vote.close_timestamp)
                self.assertEqual(json_ready_version[self.first_author_id], "Y")
            except AssertionError:
                self.failure = True
                raise

    @skipIf(self.failure, "Necessary previous test failed!")
    def test_06_save(self):
        try:
            self.vote.save()
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                edit_votes = AuthorVote.bulk_retrieve(
                    "in-progress", edit_id=self.edit.edit_id)
                edit_ended_votes = AuthorVote.bulk_retrieve(
                    "ended", edit_id=self.edit.edit_id)
                content_votes = AuthorVote.bulk_retrieve(
                    "in-progress", content_id=self.content_id)
                content_ended_votes = AuthorVote.bulk_retrieve(
                    "ended", content_id=self.content_id,
                    validation_status="accepted")
            except Exception as e:
                self.failure = True
                self.fail(str(e))
            else:
                try:
                    self.assertFalse(edit_votes)
                    self.assertFalse(content_votes[self.edit.edit_id])
                    self.assertEqual(edit_ended_votes[0].author.user_id,
                                     self.vote.author.user_id)
                    self.assertEqual(edit_ended_votes[0].vote, self.vote.vote)
                    self.assertEqual(edit_ended_votes[0].vote_status,
                                     self.vote.vote_status)
                    self.assertEqual(edit_ended_votes[0].timestamp,
                                     self.vote.timestamp)
                    vote = content_ended_votes[self.edit.edit_id][0]
                    self.assertEqual(vote.author.user_id,
                                     self.vote.author.user_id)
                    self.assertEqual(vote.vote, self.vote.vote)
                    self.assertEqual(vote.vote_status, self.vote.vote_status)
                    self.assertEqual(vote.timestamp, self.vote.timestamp)
                except AssertionError:
                    self.failure = True
                    raise
