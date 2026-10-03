# test_markdown_table.py - unit tests for markdown_table (no Sublime needed).
#
# Copyright 2026 Adam L. Rich
# Licensed under the Apache License, Version 2.0; see LICENSE.
#
# Run from the repository root:  python -m unittest discover -s tests -v

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import markdown_table as mdt  # noqa: E402


def fmt(text, **kwargs):
    return "\n".join(mdt.format_table(text.strip("\n").splitlines(), **kwargs))


class FormatTableTest(unittest.TestCase):

    def test_basic_header_centered_numbers_right(self):
        unformatted = """
| Name | Gender | Age |
|---|---|---|
| Alisa | F | 21 |
| Alex | M | 122 |
"""
        expected = """
| Name  | Gender | Age |
| ----- | ------ | --- |
| Alisa | F      |  21 |
| Alex  | M      | 122 |
""".strip("\n")
        # header cells are centred: 'Name' fits exactly, 'Gender' fits, 'Age' fits
        self.assertEqual(expected, fmt(unformatted))

    def test_header_is_centered(self):
        unformatted = """
| A | Long header |
|---|---|
| wide cell value | x |
"""
        expected = """
|        A        | Long header |
| --------------- | ----------- |
| wide cell value | x           |
""".strip("\n")
        self.assertEqual(expected, fmt(unformatted))

    def test_center_header_off(self):
        unformatted = "| A | Long header |\n|---|---|\n| wide cell value | x |"
        expected = ("| A               | Long header |\n"
                    "| --------------- | ----------- |\n"
                    "| wide cell value | x           |")
        self.assertEqual(expected, fmt(unformatted, center_header=False))

    def test_explicit_alignment_markers_are_kept(self):
        unformatted = """
| L | C | R | N |
|:--|:-:|--:|---|
| a | b | c | d |
| longer | longer | longer | longer |
"""
        expected = """
|   L    |   C    |   R    |   N    |
| :----- | :----: | -----: | ------ |
| a      |   b    |      c | d      |
| longer | longer | longer | longer |
""".strip("\n")
        self.assertEqual(expected, fmt(unformatted))

    def test_numbers_right_can_be_disabled(self):
        unformatted = "| n |\n|---|\n| 1 |\n| 100 |"
        expected = "|  n  |\n| --- |\n| 1   |\n| 100 |"
        self.assertEqual(expected, fmt(unformatted, align_numbers_right=False))

    def test_number_formats(self):
        for cell in ["1", "-2.5", "+3", "1,234.50", ".5", "1e10", "5%", "2."]:
            self.assertTrue(mdt._NUMBER.match(cell), cell)
        for cell in ["abc", "1 2", "--", "inf", "nan", "$5", ""]:
            self.assertFalse(mdt._NUMBER.match(cell), cell)

    def test_short_rows_are_padded(self):
        unformatted = "| a | b | c |\n|---|---|---|\n| 1 |\n| 1 | 2 |"
        expected = ("|  a  |  b  |  c  |\n"
                    "| --- | --- | --- |\n"
                    "|   1 |     |     |\n"
                    "|   1 |   2 |     |")
        self.assertEqual(expected, fmt(unformatted))

    def test_row_without_closing_pipe(self):
        self.assertEqual("|  a  |  b  |\n| --- | --- |\n|   1 |   2 |",
                         fmt("| a | b |\n|---|---|\n| 1 | 2"))

    def test_escaped_pipe_stays_inside_cell(self):
        unformatted = "| a | b |\n|---|---|\n| x \\| y | z |"
        expected = ("|   a    |  b  |\n"
                    "| ------ | --- |\n"
                    "| x \\| y | z   |")
        self.assertEqual(expected, fmt(unformatted))

    def test_wide_characters_use_two_columns(self):
        unformatted = "| name |\n|---|\n| 王小明 |\n| abcdef |"
        expected = ("|  name  |\n"
                    "| ------ |\n"
                    "| 王小明 |\n"
                    "| abcdef |")
        self.assertEqual(expected, fmt(unformatted))
        self.assertEqual(6, mdt.display_width("王小明"))
        self.assertEqual(1, mdt.display_width("é"))  # combining accent

    def test_indented_table_keeps_indent(self):
        unformatted = "  | a | b |\n  |---|---|\n  | 1 | 2 |"
        expected = ("  |  a  |  b  |\n"
                    "  | --- | --- |\n"
                    "  |   1 |   2 |")
        self.assertEqual(expected, fmt(unformatted))

    def test_without_delimiter_row_nothing_is_header(self):
        unformatted = "| aaaa | b |\n| c | dddd |"
        expected = "| aaaa | b    |\n| c    | dddd |"
        self.assertEqual(expected, fmt(unformatted))

    def test_second_row_not_delimiter_when_it_has_text(self):
        unformatted = "| a | b |\n| - | x |"
        self.assertEqual("| a   | b   |\n| -   | x   |", fmt(unformatted))

    def test_idempotent(self):
        text = """
| Name | Score | Notes |
|:--|--:|:-:|
| Alice | 10 | ok |
| 王小明 | 2,500 | wide |
"""
        once = fmt(text)
        self.assertEqual(once, fmt(once))

    def test_line_count_is_preserved(self):
        lines = ["| a |", "|---|", "|", "| b | c |"]
        self.assertEqual(len(lines), len(mdt.format_table(lines)))

    def test_empty_input(self):
        self.assertEqual([], mdt.format_table([]))

    def test_only_pipes(self):
        self.assertEqual(["|", "|"], mdt.format_table(["|", "|"]))


class CursorHelpersTest(unittest.TestCase):
    LINE = "| ab  | c   |  12 |"

    def test_field_at(self):
        self.assertEqual(0, mdt.field_at(self.LINE, 0))
        self.assertEqual(0, mdt.field_at(self.LINE, 3))
        self.assertEqual(0, mdt.field_at(self.LINE, 6))   # before 2nd pipe
        self.assertEqual(1, mdt.field_at(self.LINE, 7))   # after 2nd pipe
        self.assertEqual(2, mdt.field_at(self.LINE, 15))
        self.assertEqual(2, mdt.field_at(self.LINE, len(self.LINE)))

    def test_field_at_ignores_escaped_pipe(self):
        line = "| a \\| b | c |"
        self.assertEqual(0, mdt.field_at(line, 7))
        self.assertEqual(1, mdt.field_at(line, 12))

    def test_cursor_column_is_end_of_text(self):
        self.assertEqual(4, mdt.cursor_column(self.LINE, 0))
        self.assertEqual(9, mdt.cursor_column(self.LINE, 1))
        self.assertEqual(17, mdt.cursor_column(self.LINE, 2))

    def test_cursor_column_empty_cell_and_clamping(self):
        self.assertEqual(2, mdt.cursor_column("|     |", 0))
        self.assertEqual(4, mdt.cursor_column("| ab |", 9))


if __name__ == "__main__":
    unittest.main()
