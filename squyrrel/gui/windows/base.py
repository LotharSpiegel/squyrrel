import os
import tkinter as tk

from squyrrel.core.config.base import IConfig
from squyrrel.core.config.decorators import hook


class MainWindow(tk.Tk):
    pass


class WindowBase(tk.Toplevel):
    pass


class TextWindowBase:

    def __init__(self, parent, **kwargs):
        super().__init__(parent)

    def attach_text_widget(self, text):
        self.text = text
        self.text.pack(fill='both', expand='yes')


class TextWindow(WindowBase, TextWindowBase):
    pass

class TextMainWindow(MainWindow, TextWindowBase):
    pass


class WindowBaseDefaultConfig(IConfig):
    class_reference = WindowBase

    @hook(IConfig.HOOK_AFTER_INIT)
    def config(window, *args, **kwargs):
        window.title(kwargs.get('window_title', ''))
