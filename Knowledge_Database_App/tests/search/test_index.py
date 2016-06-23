"""
Search Index API Unit Tests

Currently primarily tests only core functionality of all
functions, not exceptional cases.
"""

from unittest import TestCase, skipIf

from Knowledge_Database_App.search import index
from Knowledge_Database_App.tests.search import ElasticsearchTest


class SearchIndexTest(ElasticsearchTest):
    failure = False

    @skipIf(failure, "Previous test failed!")
    def test_01_index_content_piece(self):
        try:
            index.index_content_piece(121, "Kylo Ren", 
                ["Ben Solo", "Ben Skywalker"], 
                "Kylo Ren is a member of the Knights of Ren.",
                "definition", ["jedi", "First Order", "Snoke"],
                ["Abrams, J.J. The Force Awakens. 2015."])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                content_piece = index.SearchableContentPiece.get(
                    id=121, ignore=404)
                self.assertIsNot(content_piece, None)
                if content_piece is not None:
                    self.assertEqual(int(content_piece.meta.id), 121)
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
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_02_add_to_content_piece(self):
        try:
            index.add_to_content_piece(121, "alternate_name", "Jedi Killer")
            index.add_to_content_piece(121, "keyword", "Knights of Ren")
            index.add_to_content_piece(121, "citation", 
                "Lucas, George. Star Wars: Return of the Jedi. 1983.")
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                content_piece = index.SearchableContentPiece.get(id=121, ignore=404)
                if content_piece is not None:
                    self.assertIn("Jedi Killer", content_piece.alternate_names)
                    self.assertIn("Knights of Ren", content_piece.keywords)
                    self.assertIn(
                        "Lucas, George. Star Wars: Return of the Jedi. 1983.",
                        content_piece.citations)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_02_update_content_piece(self):
        try:
            index.update_content_piece(121, "name", part_string="Ben Solo")
            index.update_content_piece(121, "alternate_name", 
                part_strings=["Kylo Ren"])
            index.update_content_piece(121, "text", 
                part_string="Ben Solo is the brother of Rey.")
            index.update_content_piece(121, "content_type", 
                part_string="conjecture")
            index.update_content_piece(121, "keyword", 
                part_strings=["star wars", "jedi"])
            index.update_content_piece(121, "citation",
                part_strings=["Abrams, J.J. Star Wars: Episode VII. 2015"])
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                content_piece = index.SearchableContentPiece.get(id=121, ignore=404)
                if content_piece is not None:
                    self.assertEqual(int(content_piece.meta.id), 121)
                    self.assertEqual(content_piece.name, "Ben Solo")
                    self.assertEqual(content_piece.alternate_names, ["Kylo Ren"])
                    self.assertEqual(content_piece.text,
                                     "Ben Solo is the brother of Rey.")
                    self.assertEqual(content_piece.content_type, "conjecture")
                    self.assertEqual(content_piece.keywords, ["star wars", "jedi"])
                    self.assertEqual(content_piece.citations,
                                     ["Abrams, J.J. Star Wars: Episode VII. 2015"])
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))

    @skipIf(failure, "Previous test failed!")
    def test_03_remove_content_piece(self):
        try:
            index.remove_content_piece(121)
        except Exception as e:
            self.__class__.failure = True
            self.fail(str(e))
        else:
            try:
                content_piece = index.SearchableContentPiece.get(
                    id=121, ignore=404)
                self.assertIs(content_piece, None)
            except AssertionError:
                self.__class__.failure = True
                raise
            except Exception as e:
                self.__class__.failure = True
                self.fail(str(e))
