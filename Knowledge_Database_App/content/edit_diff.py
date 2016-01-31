"""
Tools to compute diffs of edits and new versions of a content piece.
Uses difflib.

Exceptions:

    DiffComputationError

Functions:

    compute_diff, restore, calculate_metrics, conflict, merge
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
        version: String, accepts 'original' and 'edit'.
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


def calculate_metrics(diff):
    """
    Args:
        diff: String, specifically expects an edit diff.
    Returns:
        2-tuple containing the number of characters inserted
        and characters deleted, not including whitespace.
    """
    insertions = 0
    deletions = 0
    for line in diff:
        if line.startswith("+"):
            insertions += len(line) - 1 - line.count(" ")
        elif line.startswith("-"):
            deletions += len(line) - 1 - line.count(" ")

    return insertions, deletions


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
    # Locate all the edited sentences in the original text.
    sentence_edit_indicators1 = []
    for i, line in enumerate(diff1.splitlines()):
        if not line.startswith("+"):
            periods = [j for j in range(len(line)) if line[j] == "."
                       and line[j-1:j+1] != "\."]
        else:
            sentence_edit_indicators1[-1] = True
        if line.startswith(" "):
            sentence_edit_indicators1.extend([False]*len(periods))
        elif line.startswith("-"):
            sentence_edit_indicators1.extend([True]*len(periods))
    sentence_edit_indicators2 = []
    for i, line in enumerate(diff2.splitlines()):
        if not line.startswith("+"):
            periods = [j for j in range(len(line)) if line[j] == "."
                       and line[j-1:j+1] != "\."]
        else:
            sentence_edit_indicators2[-1] = True
        if line.startswith(" "):
            sentence_edit_indicators2.extend([False]*len(periods))
        elif line.startswith("-"):
            sentence_edit_indicators2.extend([True]*len(periods))

    # Then search for conflicts by looking for a sentence
    # with edits in both diffs.
    if list(filter(lambda pair: pair[0] and pair[1], zip(
            sentence_edit_indicators1, sentence_edit_indicators2))):
        return True
    else:
        return False


# throw in quick path for edits involving only one insertion
# or one deletion...
def _compute_combined_diff(first_diff, later_diff, base="common"):
    """
    Args:
        first_diff: String, specifically expects an edit diff.
        later_diff: String, specifically expects an edit diff that was
            accepted later than first_diff and has the same original text
            as first_diff.
        base: String, accepts 'common' and 'first_diff', the latter
            indicating that later_diff represents an edit of first_diff.
    Returns:
        The merged diff string with both diffs applied.
    """
    # Get splits of the original version of the first diff
    # at all edit points.
    first_diff_lines = first_diff.splitlines()
    first_diff_splits = []
    partial_original = ""
    reverse_partial_original = restore(first_diff, version="original")
    for i, line in enumerate(first_diff_lines):
        first_diff_splits.append(
                (partial_original, reverse_partial_original))
        if ((base == "common" and not line.startswith("+")) or
                (base == "first_diff" and not line.startswith("-"))):
            partial_original += line[6:]
            reverse_partial_original = reverse_partial_original[len(line[6:]):]

    # Get splits of the original version of the later diff
    # at the insertion points and indices at the deletion points.
    later_diff_lines = later_diff.splitlines()
    later_diff_insertion_splits, later_diff_insertions = [], []
    partial_original = ""
    reverse_partial_original = restore(later_diff, version="original")
    original_text_index_offset = 0
    later_diff_index_dict = {}
    for i, line in enumerate(later_diff_lines):
        if line.startswith("-"):
            later_diff_index_dict.update({
                i : [original_text_index_offset+j for j in range(6, len(line))]
            })
        if line.startswith("+"):
            later_diff_insertion_splits.append(
                (partial_original, reverse_partial_original))
            later_diff_insertions.append(line)
        else:
            partial_original += line[6:]
            reverse_partial_original = reverse_partial_original[len(line)-6:]
            original_text_index_offset += len(line)-6

    # Merge insertions of the later diff into the first diff
    merged_diff_lines = first_diff_lines
    index_offset = 0
    for (partial1, partial2), line in zip(
            later_diff_insertion_splits, later_diff_insertions):
        if line.startswith("+") and base == "first_diff":
            line = "+" + line   # To distinguish later_diff insertions
        match_index, min_offset = min(enumerate(
            len(partial1) - len(first_diff_p) for first_diff_p,
            first_diff_pr in first_diff_splits if first_diff_p1 in partial1),
            key=lambda pair: pair[1])
        if min_offset == 0:
            merged_diff_lines.insert(match_index+index_offset, line)
            index_offset += 1
        elif min_offset == len(first_diff_lines[match_index])-6:
            merged_diff_lines.insert(match_index+1+index_offset, line)
            index_offset += 1
        elif 0 < min_offset < len(first_diff_lines[match_index])-6:
            if first_diff_lines[match_index].startswith("+"):
                if base == "common":
                    raise DiffComputationError(
                        "An error was encountered while merging two diffs.")
                elif base == "first_diff":
                    part1 = first_diff_lines[match_index][:min_offset]
                    if part1[-1] != " ":
                        part1 += " "
                    if first_diff_lines[match_index][min_offset:].startswith(" "):
                        part2 = "+    " + first_diff_lines[match_index][min_offset:]
                    else:
                        part2 = "+     " + first_diff_lines[match_index][min_offset:]
                    del merged_diff_lines[match_index+index_offset]
                    merged_diff_lines.insert(match_index+index_offset, part1)
                    merged_diff_lines.insert(match_index+1+index_offset, line)
                    merged_diff_lines.insert(match_index+2+index_offset, part2)
                    index_offset += 2
                else:
                    raise action.InputError("Invalid argument!")
            elif first_diff_lines[match_index].startswith("-"):
                if base == "first_diff":
                    raise DiffComputationError(
                        "An error was encountered while merging two diffs.")
                else:
                    merged_diff_lines.insert(match_index+1+index_offset, line)
                    index_offset += 1
            else:
                part1 = first_diff_lines[match_index][:min_offset]
                if part1[-1] != " ":
                    part1 += " "
                if first_diff_lines[match_index][min_offset:].startswith(" "):
                    part2 = "     " + first_diff_lines[match_index][min_offset:]
                else:
                    part2 = "      " + first_diff_lines[match_index][min_offset:]
                del merged_diff_lines[match_index+index_offset]
                merged_diff_lines.insert(match_index+index_offset, part1)
                merged_diff_lines.insert(match_index+1+index_offset, line)
                merged_diff_lines.insert(match_index+2+index_offset, part2)
                index_offset += 2
        else:
            raise DiffComputationError(
                "An error was encountered while merging two diffs.")

    # Merge deletions of the later diff into the first diff
    original_text_index_offset = 0
    merged_diff_index_dict = {}
    for i, line in enumerate(merged_diff_lines):
        if (not line.startswith("+") or
                (line.startswith("+ ") and base == "first_diff")):
            merged_diff_index_dict.update({
                original_text_index_offset+j : (i, j)
                for j in range(6, len(line))
            })
            original_text_index_offset += len(line)-6
    index_offset = 0
    for i, line in enumerate(later_diff_lines):
        if line.startswith("-"):
            original_indices = later_diff_index_dict[i]
            pairs = [merged_diff_index_dict[j] for j in original_indices]
            first_line_index, start_subindex = min(pairs)
            last_line_index, finish_subindex = max(pairs)
            first_line_index += index_offset
            start_subindex += index_offset
            last_line_index += index_offset
            finish_subindex += index_offset
            for j in range(first_line_index, last_line_index+1):
                merged_line = merged_diff_lines[j]
                if j == first_line_index:
                    if (merged_line.startswith(" ") or
                            (merged_line.startswith("+ ") and base == "first_diff")):
                        same_part = merged_line[:start_subindex]
                        if not same_part.endswith(" "):
                            same_part += " "
                        deleted_part = merged_line[start_subindex:]
                        if deleted_part.startswith(" "):
                            deleted_part = "-    " + deleted_part
                        else:
                            deleted_part = "-     " + deleted_part
                        del merged_diff_lines[j]
                        merged_diff_lines.insert(j, same_part)
                        merged_diff_lines.insert(j+1, deleted_part)
                elif j == last_line_index:
                    if (merged_line.startswith(" ") or
                            (merged_line.startswith("+ ") and base == "first_diff")):
                        same_part = merged_line[finish_subindex+1:]
                        if same_part.startswith(" "):
                            if base == "common":
                                same_part = "     " + same_part
                            else:
                                same_part = "+    " + same_part
                        else:
                            if base == "common":
                                same_part = "      " + same_part
                            else:
                                same_part = "+     " + same_part
                        deleted_part = merged_line[:finish_subindex+1]
                        deleted_part[0] = "-"
                        if not deleted_part.endswith(" "):
                            deleted_part += " "
                        del merged_diff_lines[j]
                        merged_diff_lines.insert(j, deleted_part)
                        merged_diff_lines.insert(j+1, same_part)
                else:
                    if (merged_line.startswith(" ") or
                            (merged_line.startswith("+ ") and base == "first_diff")):
                        merged_diff_lines[j][0] = "-"

    # If applicable, recombine insertions.
    if base == "first_diff":
        previous_line = ""
        new_line = ""
        splintered_merged_diff_lines = merged_diff_lines
        merged_diff_lines = []
        for i, line in enumerate(splintered_merged_diff_lines):
            if previous_line.startswith("+") and line.startswith("+"):
                if line.startswith("++"):
                    new_line += line[7:]
                else:
                    new_line += line[6:]
                if i == len(splintered_merged_diff_lines)-1:
                    merged_diff_lines.append(new_line)
            elif not previous_line.startswith("+") and line.startswith("+"):
                new_line = line
                if i == len(splintered_merged_diff_lines)-1:
                    merged_diff_lines.append(new_line)
            else:
                merged_diff_lines.append(new_line)
                new_line = line

    return "\n".join(merged_diff_lines)


def merge(chronologically_ascending_diffs, base="common"):
    """
    Args:
        chronologically_ascending_diffs: List of diffs of edits of the
            same original text, or, if base == "first_diff", with ith diff
            specifying the original text of the (i+1)th diff, sorted in
            ascending chronological order.
        base: String, accepts 'common' and 'first_diff'.
    Returns:
        The merged diff string of the part text with all edits applied.
    """
    base_diff = chronologically_ascending_diffs[0]
    merged_diff = base_diff
    initial = True
    for diff in chronologically_ascending_diffs[1:]:
        merged_diff = _compute_combined_diff(merged_diff, diff, base=base)

    return merged_diff
