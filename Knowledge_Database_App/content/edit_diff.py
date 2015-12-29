"""
Tools to compute diffs for edits and new versions of a content piece.
Uses difflib.

Functions:

    compute_diff, conflict, compute_merge
"""

from difflib import SequenceMatcher


def compute_diff(original_part_text, edit_text):
    part_lines = original_part_text.splitlines()
    edit_lines = edit_text.splitlines()
    part_word_lists = [[word for word in line.split()] for line in part_lines]
    edit_word_lists = [[word for word in line.split()] for line in edit_lines]
    part_words = []
    edit_words = []
    for part_list in part_word_lists:
        for word in part_list:
            part_words.append(word)
        part_words.append("\n")
    for edit_list in edit_word_lists:
        for word in edit_list:
            edit_words.append(word)
        edit_words.append(word)



def conflict(edit_diff1, edit_diff2):



def compute_merge():

