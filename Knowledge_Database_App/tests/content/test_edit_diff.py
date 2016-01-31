"""
Edit Diff Unit Tests

Currently primarily checks only core functionality of all
functions, not exceptional cases.

Note: Tests are numbered to force a desired execution order.
"""

from unittest import TestCase

from Knowledge_Database_App.content import edit_diff as diff


class EditDiffTest(TestCase):

    def setUp(self):
        self.original_part_text = ("Kylo Ren is the master of the " +
            "Knights of Ren, a Sith, and the son of Leia Organa.")
        self.edit_text = ("Kylo Ren is the master of the " +
            "Knights of Ren, a dark side Force user, and the son of " +
            "Han Solo and Leia Organa.")
        self.further_edit_text = ("Kylo Ren is the master of the " +
            "Knights of Ren, a dark Force user, and the son of " +
            "Han and Leia.")
        self.further_edit_diff = diff.compute_diff(self.edit_text,
                                                   self.further_edit_text)
        self.trivial_edit_diff = diff.compute_diff(
            self.original_part_text, self.original_part_text)
        self.empty_edit_diff = diff.compute_diff(self.original_part_text, "")

    def test_01_compute_diff(self):
        try:
            self.edit_diff = diff.compute_diff(self.original_part_text,
                                               self.edit_text)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(edit_diff, str)
            for line in edit_diff.splitlines():
                self.assertTrue(line.startswith("      ") or
                                line.startswith("+     ") or
                                line.startswith("-     "))

    def test_02_restore(self):
        try:
            original = diff.restore(edit_diff)
            edit = diff.restore(edit_diff, version="edit")
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertEqual(original, self.original_part_text)
            self.assertEqual(edit, self.edit_text)

    def test_03_calculate_metrics(self):
        try:
            insertions, deletions = diff.calculate_metrics(self.edit_diff)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertIsInstance(insertions, int)
            self.assertIsInstance(deletions, int)

    def test_04_conflict(self):
        try:
            conflict1 = diff.conflict(self.edit_diff, self.empty_edit_diff)
            conflict2 = diff.conflict(self.edit_diff, self.trivial_edit_diff)
        except Exception as e:
            self.fail(str(e))
        else:
            self.assertEqual(conflict1, True)
            self.assertEqual(conflict2, False)

    def test_05_merge(self):
        try:
            merged_diff_common = diff.merge([self.edit_diff,
                                             self.trivial_edit_diff,
                                             self.empty_edit_diff])
            merged_diff_nested = diff.merge(
                [self.edit_diff, self.further_edit_text], base="first_diff")
        except Exception as e:
            self.fail(str(e))
        else:
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
                             self.original_part_text)
            self.assertEqual(diff.restore(merged_diff_nested),
                             self.original_part_text)
