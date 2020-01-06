import json
import os
from tkinter import *
# import tkinter.ttk as ttk
from squyrrel.core.registry.config_registry import IConfig


class SmartText(Frame):

    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.create_widgets()
        self.pack_widgets()

    def create_widgets(self, parent=None):
        parent = parent or self
        self.inner_frame = Frame(self, background=None)
        self.vbar = Scrollbar(self)
        self.hbar = Scrollbar(self, orient='horizontal')
        self.text = Text(self.inner_frame, padx=3, wrap='none', border=0)
        self.text.config(yscrollcommand=self.vbar.set)
        self.text.config(xscrollcommand=self.hbar.set)
        self.vbar.config(command=self.text.yview)
        self.hbar.config(command=self.text.xview)
        self.text.config(autoseparators=1)

    def pack_widgets(self):
        self.vbar.pack(side=RIGHT, fill=Y)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.inner_frame.pack(fill=BOTH, expand=YES)
        self.text.pack(side=LEFT, fill=BOTH, expand=YES)

    def append(self, text, tags=None):
        self.text.insert(END, text, tags)
        self.text.mark_set(INSERT, '1.0')
        self.text.see(INSERT)
        self._on_change()

    def set_text(self, text, tags=None):
        self.text.delete('1.0', END)
        self.append(text, tags)

    def get_text(self, start='1.0', end=END):
        return self.text.get(start, end)

    def _on_change(self):
        pass

    def load_theme(self, json_filepath):
        if not os.path.isfile(json_filepath):
            raise Exception(f'Did not find {json_filepath}')
        with open(json_filepath, 'r') as file:
            return json.load(file)

    def apply_theme(self, data):
        for key, value in data.items():
            self.config_option(key, value)

    def config_option(self, key, value):
        method_name = f'config_{key}'
        try:
            method = getattr(self, method_name)
        except AttributeError:
            pass
        method(value)

    def config_font(self, value):
       pass

    def config_bg(self, value):
        self.text.config(background=value)

    def config_fg(self, value):
        self.text.config(foreground=value)

    def config_sel_bg(self, value):
        self.text.tag_config('sel', background=value)

    def config_sel_fg(self, value):
        self.text.tag_config('sel', foreground=value)

    def config_active_line_bg(self, value):
        self.text.tag_config('active_line', background=value)
        self.text.tag_raise('sel')

    def config_active_line_fg(self, value):
        self.text.tag_config('active_line', foreground=value)
        self.text.tag_raise('sel')

    def config_line_numbers_bg(self, value):
        pass

    def config_line_numbers_fg(self, value):
        pass

    def config_line_numbers_active_line_bg(self, value):
        pass

    def config_line_numbers_sel_bg(self, value):
        pass

    def config_cursor_bg(self, value):
        self.text.config(insertbackground=value)

    def config_undo(self, value):
        self.text.config(undo=value)

    def config_wrap(self, value):
        self.text.config(wrap=value)

    #def config_bg(self, value):
    #    pass

    # "font": ["courier", 9, "normal"],
    # "bg": "#131819",
    # "fg": "#c4cfd3",
    # "active_line_bg": "gray18",
    # "sel_bg": "gray37",
    # "sel_fg": "#c4cfd3",
    # "line_numbers_bg": "#131819",
    # "line_numbers_fg": "#c4cfd3",
    # "line_numbers_active_line_bg": "gray18",
    # "line_numbers_sel_bg": "gray37",
    # "cursor_bg": "white"
