import json
import os
from tkinter import *
# import tkinter.ttk as ttk
from squyrrel.gui.decorators.config import gui_logging


class TextLineNumbers(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        #self.config(borderwidth=0, relief=FLAT)
        self.textwidget = None
        self.bg = 'black'
        self.fg = 'white'
        self.active_line_bg = 'black'
        self.active_line_fg = 'white'
        self.sel_bg = 'black'
        self.sel_fg = 'white'

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill=self.fg)
            i = self.textwidget.index("%s+1line" % i)

START = '1.0'
SEL_FIRST = SEL + '.first'
SEL_LAST = SEL + '.last'

class CustomText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        try:
            result = self.tk.call(cmd)
        except TclError:
            result = None

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result


class SmartText(Frame):

    def __init__(self, parent, **kwargs):
        self.text_class = kwargs.get('text_class', CustomText)
        Frame.__init__(self, parent, **kwargs)
        self.create_widgets()
        self.pack_widgets()
        self.set_bindings()

    def create_widgets(self, parent=None):
        parent = parent or self
        self.inner_frame = Frame(self, background=None)
        self.vbar = Scrollbar(self)
        self.hbar = Scrollbar(self, orient='horizontal')
        self.text = self.text_class(self.inner_frame, padx=3, wrap='none', border=0)
        self.text.config(yscrollcommand=self.vbar.set)
        self.text.config(xscrollcommand=self.hbar.set)
        self.line_number_bar = TextLineNumbers(self.inner_frame, bd=0, highlightthickness=0, width=30)
        #, padx=3, wrap='none', takefocus=0, border=0, background='khaki', state='disabled')
        self.line_number_bar.attach(self.text)
        self.text.config(autoseparators=1)
        self.vbar.config(command=self.text.yview)
        self.hbar.config(command=self.text.xview)
        self.show_line_numbers = True

    def pack_widgets(self):
        self.vbar.pack(side=RIGHT, fill=Y)
        self.hbar.pack(side=BOTTOM, fill=X)
        self._pack_inner_frame()

    def set_bindings(self):
        self.bind("<<Change>>", self._on_change)

    def bind(self, *args, **kwargs):
        self.text.bind(*args, **kwargs)

    def _pack_inner_frame(self):
        self.inner_frame.pack(fill=BOTH, expand=YES)
        if self.show_line_numbers:
            self.line_number_bar.pack(side=LEFT, fill=Y)
        self.text.pack(side=LEFT, fill=BOTH, expand=YES)

    def append(self, text, tags=None, trigger_change=True):
        self.text.insert(END, text, tags)
        self.text.mark_set(INSERT, END)
        self.text.see(INSERT)
        if trigger_change:
            self._on_change()

    def new_line(self, tags=None):
        self.append('\n', tags=None)

    def println(self, text, tags=None):
        self.new_line(tags=None)
        self.append(text, tags=tags)

    def set_text(self, text, tags=None, trigger_change=True):
        self.text.delete('1.0', END)
        self.append(text, tags)
        if trigger_change:
            self._on_change()

    def get_text(self, start='1.0', end=END):
        return self.text.get(start, end)

    def _on_change(self, event=None):
        self.line_number_bar.redraw()

    def load_theme(self, json_filepath):
        if not os.path.isfile(json_filepath):
            raise Exception(f'Did not find {json_filepath}')
        with open(json_filepath, 'r') as file:
            #print(file)
            #print(file.read())
            return json.load(file)

    @gui_logging
    def apply_theme(self, data):
        for key, value in data.items():
            self.config_option(key, value)

    @gui_logging
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
        self.line_number_bar.bg = value
        self.line_number_bar.config(bg=value)

    def config_line_numbers_fg(self, value):
        self.line_number_bar.fg = value

    def config_line_numbers_active_line_bg(self, value):
        self.line_number_bar.active_line_bg = value

    def config_line_numbers_active_line_fg(self, value):
        self.line_number_bar.active_line_fg = value

    def config_line_numbers_sel_bg(self, value):
        self.line_number_bar.sel_bg = value

    def config_line_numbers_sel_fg(self, value):
        self.line_number_bar.sel_fg = value

    def config_cursor_bg(self, value):
        self.text.config(insertbackground=value)

    def config_undo(self, value):
        self.text.config(undo=value)

    def config_wrap(self, value):
        self.text.config(wrap=value)

    def config_tags(self, tags):
        for key, value in tags.items():
            self.text.tag_config(key, value)

    # The next five functions handle the line numbering feature

    def show_line_numbers_widget(self):
        self.show_line_numbers = True
        self.text.pack_forget()
        self.line_number_bar.pack_forget()
        self._pack_inner_frame()

    def hide_line_numbers_widget(self):
        self.show_line_numbers = False
        self.text.pack_forget()
        self.line_number_bar.pack_forget()
        self._pack_inner_frame()

    def on_change_show_line_numbers(self, *args):
        if self.show_line_numbers:
            #self.update_line_numbers()
            self.show_line_numbers_widget()
        else:
            self.hide_line_numbers_widget()

    #def update_line_numbers(self, event=None):
    #    pass

        # line_numbers = self.get_line_numbers()
        # self.line_number_bar.config(state='normal')
        # self.line_number_bar.delete('1.0', 'end')
        # self.line_number_bar.insert('1.0', line_numbers)
        # self.line_number_bar.config(state='disabled')

    def get_line_numbers(self):
        output = ''
        if self.show_line_numbers:
            row, col = self.text.index("end").split('.')
            for i in range(1, int(row)):
                output += str(i)+ '\n'
        return output

    def dlineinfo(self, index):
        return self.text.dlineinfo(index)