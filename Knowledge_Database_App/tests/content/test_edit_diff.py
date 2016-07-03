"""
Edit Diff Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from unittest import TestCase, skipIf

from Knowledge_Database_App.tests import skipIfTrue
from Knowledge_Database_App.content import edit_diff as diff


class EditDiffTest(TestCase):
    failure = False

    @classmethod
    def setUpClass(cls):
        cls.original_part_text = ("Kylo Ren is the master of the " +
            "Knights of Ren, a Sith, and the son of Leia Organa.")
        cls.edit_text = ("Kylo Ren is the master of the " +
            "Knights of Ren, a dark side Force user, and the son of " +
            "Han Solo and Leia Organa.")
        cls.further_edit_text = ("Kylo Ren is the master of the " +
            "Knights of Ren, a dark Force user, and the son of " +
            "Han and Leia.")
        cls.further_edit_diff = diff.compute_diff(cls.edit_text,
                                                  cls.further_edit_text)
        cls.trivial_edit_diff = diff.compute_diff(
            cls.original_part_text, cls.original_part_text)
        cls.empty_edit_diff = diff.compute_diff(cls.original_part_text, "")

    @skipIf(failure, "Previous test failed!")
    def test_01_compute_diff(self):
        try:
            self.__class__.edit_diff = diff.compute_diff(
                self.__class__.original_part_text,
                self.__class__.edit_text)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(self.__class__.edit_diff, str)
                for line in self.__class__.edit_diff.splitlines():
                    self.assertTrue(line.startswith("      ") or
                                    line.startswith("+     ") or
                                    line.startswith("-     "))
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_02_restore(self):
        try:
            original = diff.restore(self.__class__.edit_diff)
            edit = diff.restore(self.__class__.edit_diff, version="edit")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(original, self.__class__.original_part_text)
                self.assertEqual(edit, self.__class__.edit_text)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_03_calculate_metrics(self):
        try:
            insertions, deletions = diff.calculate_metrics(
                self.__class__.edit_diff)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(insertions, int)
                self.assertIsInstance(deletions, int)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_04_conflict(self):
        try:
            conflict1 = diff.conflict(self.__class__.edit_diff, 
                                      self.__class__.empty_edit_diff)
            conflict2 = diff.conflict(self.__class__.edit_diff, 
                                      self.__class__.trivial_edit_diff)
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertEqual(conflict1, True)
                self.assertEqual(conflict2, False)
            except AssertionError:
                self.failure = True
                raise

    @skipIf(failure, "Previous test failed!")
    def test_05_merge(self):
        print("Diff:", self.__class__.edit_diff, "^")
        print("\n")
        print("\n")
        print("Diff:", self.__class__.trivial_edit_diff, "^")
        print("\n")
        print("\n")
        print("Diff:", self.__class__.empty_edit_diff, "^")
        print("\n")
        print("\n")
        try:
            merged_diff_common = diff.merge([self.__class__.edit_diff,
                                             self.__class__.trivial_edit_diff,
                                             self.__class__.empty_edit_diff])
            merged_diff_nested = diff.merge(
                [self.__class__.edit_diff, self.__class__.further_edit_diff], 
                base="first_diff")
        except Exception as e:
            self.failure = True
            self.fail(str(e))
        else:
            try:
                self.assertIsInstance(merged_diff_common, str)
                self.assertIsInstance(merged_diff_nested, str)
                for line in merged_diff_common.splitlines():
                    self.assertTrue(line.startswith("      ") or
                                    line.startswith("+     ") or
                                    line.startswith("-     "))
                for line in merged_diff_nested.splitlines():
                    self.assertTrue(line.startswith("      ") or
                                    line.startswith("+     ") or
                                    line.startswith("-     "))
                self.assertEqual(diff.restore(merged_diff_common),
                                 self.__class__.original_part_text)
                print(merged_diff_nested, "\n")
                print(diff.restore(merged_diff_nested), "\n")
                print(self.__class__.original_part_text, "\n")
                self.assertEqual(diff.restore(merged_diff_nested),
                                 self.__class__.original_part_text)
            except AssertionError:
                self.failure = True
                raise
