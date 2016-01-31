"""
Search Index API Unit Tests

Currently primarily tests only core functionality of all
functions, not exceptional cases.
"""

from unittest import TestCase

from Knowledge_Database_App.search.index import (SearchableContentPiece,
    index_content_piece, update_content_piece, delete_content_piece)


class SearchIndexTest(TestCase):

    def setUp(self):
        self._test_index_content_piece()

    def tearDown(self):
        self._test_delete_content_piece()

    def _test_index_content_piece(self):
        index_content_piece(121, "Kylo Ren", ["Ben Solo", "Ben Skywalker"],
                            "Kylo Ren is a member of the Knights of Ren.",
                            "definition", ["jedi", "First Order", "Snoke"],
                            ["Abrams, J.J. The Force Awakens. 2015."])
        content_piece = SearchableContentPiece.get(id=121, ignore=404)
        self.assertIsNot(content_piece, None)
        if content_piece is not None:
            self.assertEqual(content_piece.id, 121)
            self.assertEqual(content_piece.name, "Kylo Ren")
            self.assertEqual(content_piece.alternate_names,
                             ["Ben Solo", "Ben Skywalker"])
            self.assertEqual(content_piece.text,
                             "Kylo Ren is a member of the Knights of Ren.")
            self.assertEqual(content_piece.content_type, "definition")
            self.assertEqual(content_piece.keywords,
                             ["jedi", "First Order", "Snoke"])
            self.assertEqual(content_piece.citations,
                             ["Abrams, J.J. The Force Awakens. 2015."])

    def test_update_content_piece(self):
        try:
            update_content_piece(121, "name", part_string="Ben Solo")
            update_content_piece(121, "name", part_strings=["Kylo Ren"])
            update_content_piece(121, "text", "Ben Solo is the brother of Rey.")
            update_content_piece(121, "content_type", "conjecture")
            update_content_piece(121, "keyword", ["star wars", "jedi"])
            update_content_piece(121, "citation",
                                 ["Abrams, J.J. Star Wars: Episode VII. 2015"])
        except Exception as e:
            self.fail(str(e))
        else:
            content_piece = SearchableContentPiece.get(id=121, ignore=404)
            if content_piece is not None:
                self.assertEqual(content_piece.id, 121)
                self.assertEqual(content_piece.name, "Ben Solo")
                self.assertEqual(content_piece.alternate_names, ["Kylo Ren"])
                self.assertEqual(content_piece.text,
                                 "Ben Solo is the brother of Rey.")
                self.assertEqual(content_piece.content_type, "conjecture")
                self.assertEqual(content_piece.keywords, ["star wars", "jedi"])
                self.assertEqual(content_piece.citations,
                                 ["Abrams, J.J. Star Wars: Episode VII. 2015"])

    def _test_delete_content_piece(self):
        try:
            delete_content_piece(121)
        except Exception as e:
            self.fail(str(e))
        else:
            content_piece = SearchableContentPiece.get(id=121, ignore=404)
            self.assertIs(content_piece, None)
