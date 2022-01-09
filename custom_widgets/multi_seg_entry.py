
import tkinter as tk
import logging
from tkinter.constants import W
from typing import Callable, List
from enum import Enum


class MultiSegEntryEvent(Enum):
    ActiveSegChange = 0
    ActiveSegFinished = 1
    EntryComplete = 2
    LastSegActivated = 3

MultiSegEntryEventHandler = Callable[[MultiSegEntryEvent, tk.Widget], None]

class MultiSegEntry(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self._active_seg = tk.StringVar(value="")
        self._active_seg.trace_add("write", self._on_active_seg_change)
        self._widgets: List[tk.Widget] = [tk.Entry(self, textvariable=self._active_seg)]
        self._custom_event_dic = {}
        for event in MultiSegEntryEvent:
            self._custom_event_dic[event] = None

        self.set([""])
        
    def set(self, segs: List[str]):
        self._frozen_segs = segs[:-1]
        self._set_active_seg_no_event(segs[-1])
        self._render()

    def get(self):
        return self._frozen_segs + [self._active_seg.get()]

    def focus(self):
        self._widgets[-1].focus()

    def bind(self, event, handler):
        self._widgets[-1].bind(event, handler)

    def custom_bind(self, event: MultiSegEntryEvent, handler: MultiSegEntryEventHandler):
        self._custom_event_dic[event] = handler


    def _set_active_seg_no_event(self, value):
        handler = self._custom_event_dic[MultiSegEntryEvent.ActiveSegChange]
        self._custom_event_dic[MultiSegEntryEvent.ActiveSegChange] = None
        self._active_seg.set(value)
        self._custom_event_dic[MultiSegEntryEvent.ActiveSegChange] = handler
        
    def _on_active_seg_change(self, name, index, mode):
        self._trigger_custom_event(MultiSegEntryEvent.ActiveSegChange)
    
    def _trigger_custom_event(self, ev: MultiSegEntryEvent):
        handler = self._custom_event_dic[ev]
        if handler is not None:
            handler(ev, self)

    def _on_key_tab(self, ev):
        self._finish_active()
        self._trigger_custom_event(MultiSegEntryEvent.ActiveSegFinished)
        
    def _on_key_return(self, ev):
        self._finish_active()
        self._trigger_custom_event(MultiSegEntryEvent.EntryComplete)

    def _on_key_backspace(self, ev):
        if self._active_seg.get() == "" and len(self._frozen_segs) > 0:
            self._activate_last_frozen_seg()
            self._widgets[-1].focus()
            self._trigger_custom_event(MultiSegEntryEvent.LastSegActivated)
            return "break"
            
    def _finish_active(self):
        self._frozen_segs.append(self._active_seg.get())
        self._set_active_seg_no_event("")
        self._render()
        self._widgets[-1].focus()

    def _activate_last_frozen_seg(self):
        self._set_active_seg_no_event(self._frozen_segs[-1])
        self._frozen_segs.pop()
        self._render()
        
    def _render(self):
        for widget in self._widgets[:-1]:
            widget.destroy()
        active_entry = self._widgets[-1]
        active_entry.pack_forget()
        self._widgets = []
        for seg in self._frozen_segs:
            label = tk.Label(self, text=seg, fg="black", bg="seashell2")
            label.pack(side="left", padx=5, pady=5)
            self._widgets.append(label)
        active_entry.pack(fill=tk.X, padx=5, pady=5)
        self._widgets.append(active_entry)
        
        active_entry.icursor(len(self._active_seg.get()))
        active_entry.bind("<Tab>", self._on_key_tab)
        active_entry.bind("<Return>", self._on_key_return)
        active_entry.bind("<BackSpace>", self._on_key_backspace)
    
