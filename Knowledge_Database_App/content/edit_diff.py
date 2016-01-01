"""
Tools to compute diffs of edits and new versions of a content piece.
Uses difflib.

Functions:

    compute_diff, restore, conflict, merge
"""

from difflib import SequenceMatcher

from Knowledge_Database_App.storage.select_queries import InputError


class DiffComputationError(Exception):
    """
    General exception to raise when computation of a diff-related
    function fails, indicating an implementation error.
    """


def compute_diff(original_part_text, edit_text):
    r"""
    Computes a word-oriented diff representing an edit as a
    sequence of deletions and insertions. Does not preserve
    whitespace.

    Args:
        original_part_text: String.
        edit_text: String.

    Returns:
        String.

    Example:

        >>> original_text = "Hello, my name is Lukas.\nI like to take"
                             + "long rides\non the beach."
        >>> new_text = "Hello, my name is not Ben.\nI don't like to take"
                        + "long rides\non the beach."
        >>> print(compute_diff(original_text, new_text))
              Hello, my name is
        -     Lukas.
        +     not Ben.
              I
        +     don't
              like to take long rides on the beach.
    """
    # Separate into words and linebreaks.
    part_words = original_part_text.split()
    edit_words = edit_text.split()
    edit_word_lists = [line.split() for line in edit_text.splitlines()]
    edit_linebreak_indices = []
    for i, line in enumerate(edit_word_lists):
        if i == 0:
            edit_linebreak_indices.append(len(line))
        else:
            edit_linebreak_indices.append(
                len(line) + edit_linebreak_indices[-1])

    # Now compute word-oriented opcodes.
    opcodes_with_replace = SequenceMatcher(
        a=part_words, b=edit_words, autojunk=False).get_opcodes()
    opcodes = []
    for operation in opcodes_with_replace:
        if operation[0] == "replace":
            opcodes.append(("delete", operation[1], operation[2],
                            operation[3], operation[3]))
            opcodes.append(("insert", operation[1], operation[1],
                            operation[3], operation[4]))
        else:
            opcodes.append(operation)

    # Convert the opcodes into a single-string diff
    diff = ""
    for i, operation in enumerate(opcodes):
        if operation[0] == "delete":
            diff += "-     " + " ".join(
                part_words[operation[1] : operation[2]]) + " \n"
        elif operation[0] == "insert":
            diff += "+     " + " ".join(
                edit_words[operation[3] : operation[4]]) + " \n"
        elif operation[0] == "equal":
            diff += "      " + " ".join(
                edit_words[operation[3] : operation[4]]) + " \n"

    return diff


def restore(diff, version="original"):
    """
    Args:
        version: String, accepts 'original' and 'edited'.
            Defaults to 'original'.
    Returns:
        Non-diffed part text string, either the original or edited version.
    """
    if version == "original":
        part_text = ""
        for line in diff.splitlines():
            if line.startswith("-") or line.startswith(" "):
                part_text += line[6:]
    elif version == "edit":
        part_text = ""
        for line in diff.splitlines():
            if line.startswith("+") or line.startswith(" "):
                part_text += line[6:]
    else:
        raise InputError("Invalid arguments!")

    return part_text


def conflict(diff1, diff2):
    """
    Args:
        diff1: String, specifically expects an edit diff.
        diff2: String, specifically expects an edit diff that has
            the same original text as diff1.
    Returns:
        Boolean indicating whether the edit diffs could
        semantically conflict on merging.
    """
    equal_sections = []
    changed_sections = []
    previous_line = ""
    for line in diff1.splitlines():
        if line.startswith(" "):
            if previous_line.startswith(" "):
                equal_sections[-1] += line[6:]
            else:
                equal_sections.append(line[6:])
        else:
            if previous_line.startswith(" "):
                changed_sections.append(line[6:])
            else:
                changed_sections[-1] += line[6:]
        previous_line = line
    for line in diff2.splitlines():


# throw in quick path for edits involving only one insertion
# or one deletion, for conflict function too...
def _compute_combined_diff(first_diff, later_diff):
    """
    Args:
        first_diff: String, specifically expects an edit diff.
        later_diff: String, specifically expects an edit diff that was
            accepted later than first_diff and has the same original text
            as first_diff.
    Returns:
        The merged diff string with both diffs applied.
    """
    # Get splits of the original version of the first diff
    # at all edit points.
    first_diff_lines = first_diff.splitlines()
    first_diff_splits = []
    partial_original = ""
    reverse_partial_original = restore(first_diff, version="original")
    for line in first_diff_lines:
        first_diff_splits.append(
                (partial_original, reverse_partial_original))
        if not line.startswith("+"):
            partial_original += line[6:]
            reverse_partial_original = reverse_partial_original[len(line[6:]):]

    # Get splits of the original version of the later diff
    # at the insertion points.
    later_diff_insertion_splits = []
    later_diff_deletion_splits = []
    later_diff_insertions = []
    later_diff_deletions = []
    partial_original = ""
    reverse_partial_original = restore(later_diff, version="original")
    for line in later_diff.splitlines():
        if line.startswith("-"):
            later_diff_deletion_splits.append(
                (partial_original, reverse_partial_original))
            later_diff_deletions.append(line)
        if line.startswith("+"):
            later_diff_insertion_splits.append(
                (partial_original, reverse_partial_original))
            later_diff_insertions.append(line)
        else:
            partial_original += line[6:]
            reverse_partial_original = reverse_partial_original[len(line[6:]):]

    # Merge insertions of the later diff into the first diff
    merged_diff_lines = first_diff_lines
    index_offset = 0
    index_offset_dict = {}
    for (partial1, partial2), line in zip(
            later_diff_insertion_splits, later_diff_insertions):
        match_index, min_offset = min(enumerate(
            len(partial1) - len(first_diff_p) for first_diff_p,
            first_diff_pr in first_diff_splits if first_diff_p1 in partial1),
            key=lambda pair: pair[1])
        if min_offset == 0:
            merged_diff_lines.insert(match_index+index_offset, line)
            index_offset += 1
            index_offset_dict[match_index] = index_offset
        elif min_offset == len(first_diff_lines[match_index])-6:
            merged_diff_lines.insert(match_index+1+index_offset, line)
            index_offset += 1
            index_offset_dict[match_index+1] = index_offset
        elif 0 < min_offset < len(first_diff_lines[match_index])-6:
            if first_diff_lines[match_index].startswith("+"):
                raise DiffComputationError(
                    "An error was encountered while merging two diffs.")
            elif first_diff_lines[match_index].startswith("-"):
                merged_diff_lines.insert(match_index+1+index_offset, line)
                index_offset += 1
                index_offset_dict[match_index+1] = index_offset
            else:
                part1 = first_diff_lines[match_index][:min_offset]
                if part1[-1] != " ":
                    part1 += " "
                if first_diff_lines[match_index][min_offset:].startswith(" "):
                    part2 = "     " + first_diff_lines[match_index][min_offset:]
                else:
                    part2 = "      " + first_diff_lines[match_index][min_offset:]
                del merged_diff_lines[match_index]
                merged_diff_lines.insert(match_index+index_offset, part1)
                merged_diff_lines.insert(match_index+1+index_offset, line)
                merged_diff_lines.insert(match_index+2+index_offset, part2)
                index_offset += 2
                index_offset_dict[match_index] = index_offset
        else:
            raise DiffComputationError(
                "An error was encountered while merging two diffs.")

    # Merge deletions of the later diff into the first diff
    index_offset = 0
    for (partial1, partial2), line in zip(
            later_diff_deletion_splits, later_diff_deletions):
        match_index, min_offset = min(enumerate(
            len(partial1) - len(first_diff_p) for first_diff_p,
            first_diff_pr in first_diff_splits if first_diff_p1 in partial1),
            key=lambda pair: pair[1])
        offset_match_index = match_index + index_offset + max(filter(
            lambda index: index <= match_index, index_offset_dict.keys()))
        if min_offset == 0:
            if first_diff_lines[match_index].startswith("+"):
                merged_diff_lines
        elif min_offset == len(first_diff_lines[match_index])-6:



def merge(chronologically_ascending_diffs):
    """
    Args:
        chronologically_ascending_diffs: List of diffs of edits of the
            same original text sorted in ascending chronological order.
    Returns:
        The merged version string of the part text with all edits applied.
    """
    base_diff = chronologically_ascending_diffs[0]
    merged_diff = base_diff
    initial = True
    for diff in chronologically_ascending_diffs[1:]:
        if initial:
            merged_diff = _compute_combined_diff(base_diff, diff)
        else:
            merged_diff = _compute_combined_diff(merged_diff, diff)

    return restore(merged_diff, version="edited")
