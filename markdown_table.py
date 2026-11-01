# markdown_table.py - format GitHub Flavored Markdown (GFM) pipe tables.
#
# Copyright 2012-2016 Valery Kocubinsky (original SublimeTableEditor)
# Modifications Copyright 2026 Adam L. Rich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# NOTICE OF CHANGES: this file is a heavily modified derivative of
# SublimeTableEditor (https://github.com/vkocubinsky/SublimeTableEditor) by
# Valery Kocubinsky. The multi-syntax table editor was reduced to a single
# pure-Python formatter for pipe tables. See NOTICE.

"""Pure-Python (no Sublime dependency) GFM pipe table formatter.

A pipe table looks like::

    | Name  | Age |
    |-------|----:|
    | Alice |  21 |

Only tables whose rows start with ``|`` are recognised. Pipes inside a cell
must be escaped as ``\\|``.
"""

import re
import unicodedata
from typing import List, Optional, Tuple

LEFT = "left"
RIGHT = "right"
CENTER = "center"

MIN_COLUMN_WIDTH = 3

_DELIMITER_CELL = re.compile(r"^:?-+:?$")
_NUMBER = re.compile(r"^[+-]?(?:\d[\d,]*(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?%?$")
_TABLE_ROW = re.compile(r"^\s*\|")


def is_table_row(line: str) -> bool:
    """True if the line looks like a pipe table row (starts with ``|``)."""
    return _TABLE_ROW.match(line) is not None


def display_width(text: str) -> int:
    """Number of monospace terminal columns the text occupies.

    East Asian wide/fullwidth characters take two columns, combining and
    other zero-width characters take none.
    """
    width = 0
    for ch in text:
        if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
            continue
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def _pipe_positions(line: str) -> List[int]:
    """Character offsets of every unescaped ``|`` in the line."""
    positions = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "|":
            positions.append(i)
        i += 1
    return positions


def split_row(line: str) -> Tuple[str, List[str]]:
    """Split a table row into (indentation, stripped cell texts)."""
    body = line.lstrip()
    prefix = line[: len(line) - len(body)]
    cells = []  # type: List[str]
    start = 0
    positions = _pipe_positions(body)
    if positions and positions[0] == 0:
        positions = positions[1:]
        start = 1
    for pos in positions:
        cells.append(body[start:pos])
        start = pos + 1
    tail = body[start:]
    if tail.strip():  # row without a closing pipe
        cells.append(tail)
    return prefix, [c.strip() for c in cells]


def _pad(text: str, width: int, align: str) -> str:
    extra = max(width - display_width(text), 0)
    if align == RIGHT:
        return " " * extra + text
    if align == CENTER:
        left = extra // 2
        return " " * left + text + " " * (extra - left)
    return text + " " * extra


def _delimiter_alignment(cell: str) -> Optional[str]:
    left, right = cell.startswith(":"), cell.endswith(":")
    if left and right:
        return CENTER
    if left:
        return LEFT
    if right:
        return RIGHT
    return None


def _delimiter_cell(align: Optional[str], width: int) -> str:
    if align == CENTER:
        return ":" + "-" * (width - 2) + ":"
    if align == LEFT:
        return ":" + "-" * (width - 1)
    if align == RIGHT:
        return "-" * (width - 1) + ":"
    return "-" * width


def format_table(
    lines: List[str], align_numbers_right: bool = True, center_header: bool = True
) -> List[str]:
    """Return the lines of a pipe table, aligned and padded.

    The number of lines never changes. Short rows are padded with empty
    cells. ``:--``, ``:-:`` and ``--:`` delimiter markers set column
    alignment; unmarked columns are right-aligned when every non-empty body
    cell is a number (if ``align_numbers_right``), otherwise left-aligned.
    The header row is centred when a delimiter row follows it (if
    ``center_header``).
    """
    if not lines:
        return []

    prefix = lines[0][: len(lines[0]) - len(lines[0].lstrip())]
    rows = [split_row(line)[1] for line in lines]
    column_count = max(len(r) for r in rows)
    if column_count == 0:
        return [prefix + "|" for _ in lines]

    delimiter_index = None  # type: Optional[int]
    if len(rows) > 1 and rows[1] and all(_DELIMITER_CELL.match(c) for c in rows[1]):
        delimiter_index = 1

    explicit = [None] * column_count  # type: List[Optional[str]]
    if delimiter_index is not None:
        for col, cell in enumerate(rows[delimiter_index]):
            explicit[col] = _delimiter_alignment(cell)

    text_rows = [i for i in range(len(rows)) if i != delimiter_index]
    body_rows = [i for i in text_rows if not (delimiter_index is not None and i == 0)]

    alignment = []  # type: List[str]
    widths = []  # type: List[int]
    for col in range(column_count):
        cells = [rows[i][col] if col < len(rows[i]) else "" for i in text_rows]
        widths.append(max([MIN_COLUMN_WIDTH] + [display_width(c) for c in cells]))
        align = explicit[col]
        if align is None:
            body = [
                rows[i][col] for i in body_rows if col < len(rows[i]) and rows[i][col]
            ]
            numeric = bool(body) and all(_NUMBER.match(c) for c in body)
            align = RIGHT if (align_numbers_right and numeric) else LEFT
        alignment.append(align)

    out = []
    for i, row in enumerate(rows):
        if i == delimiter_index:
            cells = [
                _delimiter_cell(explicit[c], widths[c]) for c in range(column_count)
            ]
        else:
            is_header = delimiter_index is not None and i == 0 and center_header
            cells = [
                _pad(
                    row[c] if c < len(row) else "",
                    widths[c],
                    CENTER if is_header else alignment[c],
                )
                for c in range(column_count)
            ]
        out.append(prefix + "| " + " | ".join(cells) + " |")
    return out


def field_at(line: str, column: int) -> int:
    """Index of the table cell containing character offset ``column``."""
    positions = _pipe_positions(line)
    before = sum(1 for p in positions if p < column)
    return max(min(before - 1, len(positions) - 2), 0)


def cursor_column(line: str, field: int) -> int:
    """Character offset just after the text of cell ``field`` in ``line``.

    For an empty cell, the offset of the first space inside the cell.
    """
    positions = _pipe_positions(line)
    if len(positions) < 2:
        return len(line)
    field = max(0, min(field, len(positions) - 2))
    left, right = positions[field], positions[field + 1]
    content = line[left + 1 : right].rstrip()
    if content.strip():
        return left + 1 + len(content)
    return left + 2
