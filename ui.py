# %%
import functools
import logging
import os
import sys
import tkinter as tk
import traceback
from logging.handlers import TimedRotatingFileHandler
from pprint import pformat, pprint
from typing import Callable, List

import app_common
from custom_widgets.multi_seg_entry import MultiSegEntry, MultiSegEntryEvent
from custom_widgets.rich_list import RichList
from search import ListSearcher, StrSearcher
from sh_cmd import Cmd, Op
from sh_package import launcher, package_manager
from sh_package.launcher import window
from space_key import SpaceKeyNode, SpaceKeyNodeListSearcher

sys.path.insert(0, app_common.PROJ_HOME)

import package_config
import space_key_config

logFormatter = logging.Formatter("%(asctime)s %(name)s:%(levelname)s:%(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

logger = logging.getLogger(os.path.basename(__file__))
# logger.setLevel(logging.INFO)

os.makedirs(app_common.PROJ_HOME, exist_ok=True)
fileHandler = TimedRotatingFileHandler(
    app_common.LOG_PATH, encoding="utf-8", when="d", interval=1, backupCount=10
)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

logger.debug(space_key_config.__file__)

# %%


class SpaceFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self._space_root = space_key_config.root_node

        self._constructed_cmd = None
        self._cur_node = None

        self._cmd_val = tk.StringVar(value="")
        self._cmd = tk.Entry(self, textvariable=self._cmd_val)
        self._cmd.pack(fill=tk.X)
        self._cmd.focus()

        self._intellisense_list = RichList(self, name="cmd_list")
        self._intellisense_list.pack(fill=tk.BOTH)

        self.init_fill()

        self._cmd.bind("<Control-k>", lambda ev: self._intellisense_list.select_prev())
        self._cmd.bind("<Up>", lambda ev: self._intellisense_list.select_prev())
        self._cmd.bind("<Control-j>", lambda ev: self._intellisense_list.select_next())
        self._cmd.bind("<Down>", lambda ev: self._intellisense_list.select_next())
        self._cmd.bind("<Return>", self._on_key_return)
        self._cmd_val.trace_add("write", self._on_change)

    def init_fill(self):
        self._constructed_cmd = []
        self._cur_node = self._space_root
        self._refresh()

    def focus(self):
        self._cmd.focus()

    def _refresh(self):
        self._cmd_val.set("")
        searcher = SpaceKeyNodeListSearcher(self._cur_node.children)
        self._intellisense_list.bind_data_source(searcher)
        self._intellisense_list.filter(self._cmd_val.get(), update_size=True)

    def _on_key_return(self, ev):
        record: SpaceKeyNode = self._intellisense_list.get_selected_record()
        self._select(record.key)

    def _on_change(self, name, index, mode):
        key = self._cmd_val.get()
        # _on_change could trigger due to use input, can also trigger when
        # 1. refocus the window by hotkey and set `_cmd_val` to empty
        # 2. enter a new level of menu, set `_cmd_val` to empty
        if key != "":
            self._select(key)

    def _select(self, key):
        if not self._cur_node.is_valid_next_key(key):
            root.wm_state("iconic")
            return
        self._cur_node = self._cur_node.walk_to(key)
        if self._cur_node.is_leaf():
            logger.info(f"Invoke {self._cur_node.key}:{self._cur_node.comment}")
            self._cur_node.op_func()
            # Should not withdraw here. whether withdraw should determined by the op_func.
            # For example, a calculator doesn't need to withdraw
            # root.withdraw()
        else:
            self._constructed_cmd.append(key)
            self._refresh()


# %%
class CmdFrame(tk.Frame):
    def __init__(self, master: tk.Tk, constructed_cmd: Cmd):
        super().__init__(master)

        self._app = master
        self._constructed_cmd = constructed_cmd
        self._link_to_op = tk.Label(self, fg="blue", cursor="hand2", anchor="w")
        self._help_text = tk.Text(self)
        self._help_text.tag_configure("cur_parameter", foreground="red")
        self._cmd = MultiSegEntry(self)
        self._cmd.pack(fill=tk.X)
        self._cmd.focus()
        self._intellisense_list = RichList(self, name="win_list")
        self._intellisense_list.pack(fill=tk.BOTH)

        self.set()

        self._cmd.bind("<Control-k>", lambda ev: self._intellisense_list.select_prev())
        self._cmd.bind("<Up>", lambda ev: self._intellisense_list.select_prev())
        self._cmd.bind("<Control-j>", lambda ev: self._intellisense_list.select_next())
        self._cmd.bind("<Down>", lambda ev: self._intellisense_list.select_next())
        self._cmd.bind("<Control-y>", self._on_copy)
        self._cmd.bind("<Control-o>", self._on_describe_op)
        self._cmd.custom_bind(MultiSegEntryEvent.ActiveSegChange, self._on_change)
        self._cmd.custom_bind(
            MultiSegEntryEvent.ActiveSegFinished, self._on_active_seg_finished
        )
        self._cmd.custom_bind(
            MultiSegEntryEvent.LastSegActivated, self._on_last_seg_activated
        )
        self._cmd.custom_bind(MultiSegEntryEvent.EntryComplete, self._on_entry_complete)
        self._link_to_op.bind("<Button-1>", self._on_describe_op)

    def focus(self):
        self._cmd.focus()

    def set(self, input_cmd_segs=[""]):
        logger.debug(f"cmd_frame.set({input_cmd_segs})")
        self._cmd.set(input_cmd_segs)
        self._update_help()
        self._update_intellisense_list()

    def set_and_execute(self, input_cmd_segs=[""]):
        self.set(input_cmd_segs)
        self._execute_cmd()

    def _on_copy(self, ev):
        self._app.clipboard_clear()
        content = self._intellisense_list.get_content()
        self._app.clipboard_append(content)

    def _update_intellisense_list(self, searcher=None):
        segs = self._cmd.get()
        query = segs[-1]
        logger.debug(f"update intellisense list with query: {repr(query)}")
        if searcher is None:
            searcher = self._constructed_cmd.get_intellisense_searcher()
        self._intellisense_list.bind_data_source(searcher)
        self._intellisense_list.filter(query, update_size=True)

    def _execute_cmd(self):
        try:
            ret = self._constructed_cmd.execute()
            if ret is None:
                # succeed, no return value
                root.wm_state("iconic")
            elif ret is not None and not isinstance(ret, ListSearcher):
                # succeed, show return value
                if not isinstance(ret, str):
                    ret = pformat(ret)
                ret = StrSearcher(ret.split("\n"))
                self._update_intellisense_list(ret)
            else:
                # need more arguments
                self._update_intellisense_list(ret)
        except:
            # fail, print stack trace
            exception_stack_trace = traceback.format_exc()
            ret = StrSearcher(exception_stack_trace.split("\n"))
            self._update_intellisense_list(ret)
            logger.error(f"Failed to execute {self._constructed_cmd}: ")
            logger.error(exception_stack_trace)

    def _on_change(self, ev: MultiSegEntryEvent, widget: MultiSegEntry):
        self._intellisense_list.filter(widget.get()[-1], update_size=True)

    def _finish_current_seg(self):
        record = self._intellisense_list.get_selected_record()
        if record is None:
            # if the query user typed doesn't match any record, simply save the raw user text
            record = self._cmd.get()[-2]
        self._constructed_cmd.append(record)
        self._update_help()

    def _update_help(self):
        (
            file_path,
            line_no,
            help_message,
            para_start,
            para_end,
        ) = self._constructed_cmd.get_help()
        help_text = self._help_text
        link_to_symbol = self._link_to_op
        if file_path is None:
            help_text.pack_forget()
        else:
            link_to_symbol.config(text=f"{file_path}:{line_no}")
            link_to_symbol.pack(fill=tk.X)
        if help_message is None:
            link_to_symbol.forget()
        else:
            help_text.config(state=tk.NORMAL)
            help_text.delete("1.0", tk.END)
            help_text.insert("1.0", help_message)
            if para_start is not None:
                help_text.tag_add("cur_parameter", f"1.{para_start}", f"1.{para_end}")
            help_text.config(state=tk.DISABLED)
            widget_height = float(help_text.index(tk.END))
            widget_width = 100
            for line in help_text.get("1.0", tk.END).split("\n"):
                if len(line) > widget_width:
                    widget_width = len(line) + 1
            help_text.config(width=widget_width, height=widget_height)
            help_text.pack(fill=tk.X)

    def _on_active_seg_finished(self, ev: MultiSegEntryEvent, widget: MultiSegEntry):
        self._finish_current_seg()
        self._update_intellisense_list()

    def _on_last_seg_activated(self, ev: MultiSegEntryEvent, widget: MultiSegEntry):
        self._constructed_cmd.pop()
        self._update_help()
        self._update_intellisense_list()

    def _on_entry_complete(self, ev: MultiSegEntryEvent, widget: MultiSegEntry):
        self._finish_current_seg()
        self._execute_cmd()

    def _on_describe_op(self, ev):
        link_text: str = self._link_to_op.cget("text")
        file_path, line_no = link_text.rsplit(":", 1)
        line_no = int(line_no)
        launcher.open_with_vscode(
            app_common.PROJ_NAME,
            file_path,
            functools.partial(
                package_config.launcher.open_folder_with_vscode,
                app_common.SOURCE_CODE_ROOT,
            ),
            line_no,
        )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(app_common.PROJ_NAME)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"+{int(0.25*screen_width)}+{int(0.25*screen_height)}")
        self.bind("<Escape>", self.hide)
        self.bind("<Control-g>", self.restart)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._space_frame = SpaceFrame(self)
        self._space_frame.pack()

        self._constructed_cmd = Cmd(
            package_manager.build_op_list(package_config), package_manager
        )
        self._cmd_frame = CmdFrame(self, self._constructed_cmd)

    def invoke_cmd_frame(
        self, func: Callable = None, args: List = [], is_execute=False
    ):
        """When `func` is None, just show the cmd frame

        Args:
            func (Callable, optional): [description]. Defaults to None.
            args (List, optional): [description]. Defaults to [].
            is_execute (bool, optional): [description]. Defaults to False.
        """
        self._space_frame.pack_forget()
        self._cmd_frame.pack()
        self._cmd_frame.focus()
        if func is not None:
            self._constructed_cmd.set(func, args)
            input_cmd_segs = [self._constructed_cmd.get_op().name] + [
                str(seg) for seg in args
            ]
        else:
            self._constructed_cmd.clear()
            input_cmd_segs = []
        input_cmd_segs += [""]
        if is_execute:
            self._cmd_frame.set_and_execute(input_cmd_segs)
        else:
            self._cmd_frame.set(input_cmd_segs)

    def restart(self, ev):
        self._space_frame.pack()
        self._cmd_frame.pack_forget()
        self._space_frame.focus()
        self._space_frame.init_fill()
        # self._cmd_frame.set()
        # self.invoke_cmd_frame(launcher.goto_browser, [], is_execute=False)

    def hide(self, ev):
        if str(ev.widget == "."):
            self.wm_state("iconic")

    def on_closing(self):
        logger.info("on_closing")
        logger.info("Closing the root window is not allowed.")
        self.wm_state("iconic")
        # self.destroy()


root = App()
app_common.register_invoke_cmd_frame(root.invoke_cmd_frame)
root.mainloop()

logger.info("after main loop")

# %%
