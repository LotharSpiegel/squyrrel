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


class SmartTextDefaultConfig(IConfig):
    class_reference = SmartText
