import os
import tkinter as tk

from squyrrel.core.registry.config_registry import IConfig
from squyrrel.core.decorators.config import hook


class MainWindow(tk.Tk):
    pass


class TextWindow(tk.Toplevel):

    def __init__(self, parent, **kwargs):
        super().__init__(parent)

    def init_text_widget(self, text):
        self.text = text
        self.text.pack(fill='both', expand='yes')


class TextWindowDefaultConfig(IConfig):
    class_reference = TextWindow

    @hook('after init')
    def config(window, *args, **kwargs):
        window.title(kwargs.get('window_title', ''))
