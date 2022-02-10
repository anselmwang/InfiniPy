import logging
import os
import pprint
import tkinter as tk
from dataclasses import dataclass

# %%

logger = logging.getLogger(os.path.basename(__file__))
# logger.setLevel(logging.DEBUG)


class RichList(tk.Text):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.tag_configure("arrow", foreground="red")
        self.tag_configure("selected_line", background="seashell2")
        self.tag_configure("match", foreground="dodger blue")

    def bind_data_source(self, searcher):
        self._searchable_records = searcher

    def get_content(self):
        return "\n".join(self._lines)

    def filter(self, query, update_size):
        (
            self._records,
            self._lines,
            self._match_results,
        ) = self._searchable_records.filter(query)
        self._sel_line_no = 0 if len(self._lines) > 0 else -1
        self._update_ui()
        if update_size:
            self._update_size()

    def select_prev(self):
        if self._sel_line_no != -1:
            self._sel_line_no = max(self._sel_line_no - 1, 0)
            self._update_ui()

    def select_next(self):
        if self._sel_line_no != -1:
            self._sel_line_no = min(self._sel_line_no + 1, len(self._lines) - 1)
            self._update_ui()

    def get_selected_record(self):
        if self._sel_line_no != -1:
            return self._records[self._sel_line_no]
        else:
            return None

    @staticmethod
    def _select_line(lines, sel_line_no):
        new_lines = []
        for line_no, line in enumerate(lines):
            if line_no == sel_line_no:
                new_lines.append(f"> {line}")
            else:
                new_lines.append(f"  {line}")
        return new_lines

    def _update_ui(self):
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        result = self._select_line(self._lines, self._sel_line_no)
        self.insert("1.0", "\n".join(result))
        if self._match_results is not None:
            for line_no, (line, line_annotation) in enumerate(
                zip(self._lines, self._match_results)
            ):
                # line_no +1 because tkinter text widget line number starts from 1, not 0
                widget_line_no = line_no + 1
                for tag_span in line_annotation.spans:
                    # +2 because prefix "> "
                    widget_span_start = tag_span.start + 2
                    widget_span_end = tag_span.end + 2
                    self.tag_add(
                        "match",
                        f"{widget_line_no}.{widget_span_start}",
                        f"{widget_line_no}.{widget_span_end}",
                    )

        widget_sel_line_no = self._sel_line_no + 1
        self.tag_add("arrow", f"{widget_sel_line_no}.0", f"{widget_sel_line_no}.1")
        self.tag_add(
            "selected_line", f"{widget_sel_line_no}.0", f"{widget_sel_line_no+1}.0"
        )
        self.config(state=tk.DISABLED)

    def _update_size(self):
        # widget_width = 0
        # widget_height = float(self.index(tk.END))
        widget_width = 100
        widget_height = 18
        for line in self.get("1.0", tk.END).split("\n"):
            if len(line) > widget_width:
                widget_width = len(line) + 1
        self.config(width=widget_width, height=widget_height)
