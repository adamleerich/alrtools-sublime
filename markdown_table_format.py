# markdown_table_format.py - Sublime Text command that formats pipe tables.
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
# NOTICE OF CHANGES: derived from table_plugin.py in SublimeTableEditor
# (https://github.com/vkocubinsky/SublimeTableEditor) by Valery Kocubinsky.
# Reduced to a single command; rewritten for Sublime Text 4 (Python 3.8).

import sublime
import sublime_plugin

from . import markdown_table as mdt

SETTINGS_FILE = "alrtools-sublime.sublime-settings"
STATUS_PREFIX = "alrtools: "


class MarkdownTableFormatCommand(sublime_plugin.TextCommand):
    """Align the pipe table under each cursor.

    Rows are only replaced when their text changes, and the line count never
    changes, so each cursor stays in the same row and cell.
    """

    def run(self, edit):
        view = self.view
        settings = sublime.load_settings(SETTINGS_FILE)
        options = {
            "align_numbers_right": settings.get("align_numbers_right", True),
            "center_header": settings.get("center_header", True),
        }

        # Phase 1: read. Describe every selection as (row, col) positions.
        tables = {}  # (first_row, last_row) -> formatted lines
        carets = []  # one entry per selection
        for sel in view.sel():
            row, col = view.rowcol(sel.begin())
            if not mdt.is_table_row(self._line_text(row)):
                carets.append(("keep", view.rowcol(sel.a), view.rowcol(sel.b)))
                continue
            first, last = self._table_bounds(row)
            if (first, last) not in tables:
                lines = [self._line_text(r) for r in range(first, last + 1)]
                tables[(first, last)] = mdt.format_table(lines, **options)
            field = mdt.field_at(self._line_text(row), col)
            carets.append(("table", row, field, first, last))

        if not tables:
            sublime.status_message(STATUS_PREFIX + "cursor is not in a table")
            return

        # Phase 2: write. Row numbers are stable because line count is fixed.
        for (first, last), new_lines in tables.items():
            for row, new_text in zip(range(first, last + 1), new_lines):
                region = view.line(view.text_point(row, 0))
                if view.substr(region) != new_text:
                    view.replace(edit, region, new_text)

        # Phase 3: restore cursors.
        regions = []
        for caret in carets:
            if caret[0] == "keep":
                (ra, ca), (rb, cb) = caret[1], caret[2]
                regions.append(
                    sublime.Region(view.text_point(ra, ca), view.text_point(rb, cb))
                )
            else:
                _, row, field, first, last = caret
                new_line = tables[(first, last)][row - first]
                pt = view.text_point(row, mdt.cursor_column(new_line, field))
                regions.append(sublime.Region(pt, pt))
        view.sel().clear()
        view.sel().add_all(regions)

        count = len(tables)
        sublime.status_message(
            STATUS_PREFIX
            + "formatted {0} table{1}".format(count, "" if count == 1 else "s")  # noqa: UP030
        )

    def _line_text(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row, 0)))

    def _table_bounds(self, row):
        last_row = self.view.rowcol(self.view.size())[0]
        first = last = row
        while first > 0 and mdt.is_table_row(self._line_text(first - 1)):
            first -= 1
        while last < last_row and mdt.is_table_row(self._line_text(last + 1)):
            last += 1
        return first, last
