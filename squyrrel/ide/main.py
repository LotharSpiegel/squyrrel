import sys
import pprint
import os
import re

from squyrrel import Squyrrel
# from squyrrel.management.command_manager import CommandManager
from windows import cmd_window_factory, log_window_factory
from squyrrel.core.registry.signals import (squyrrel_debug_signal, squyrrel_error_signal,
    class_loaded_signal, command_loaded_signal)


from shell import on_return, execute_cmd_from_shell


class App:

    def __init__(self, *args, **kwargs):
        # TODO: load user settings from last time
        try:
            self.init_vars()
            self.load_settings()
            self.awake_squyrrel()
            self.init_workers()
            self.load_dependencies()
            self.build_gui()
            self.connect_signals()

            self.run_scripts()
            self.test_db()
        except:
            self.write_log()
            raise
        # self.append_init_debugging()

    def append_init_debugging(self):
        for stamp in self.pop_debugging_signals_cache():
            self.debug(*stamp.args, **stamp.kwargs)

    def init_vars(self):
        self.config = {}
        self.main_window = None

    def load_settings(self):
        self.config['root_path'] = os.getcwd()
        self.config['log_file'] = 'log.txt'

    def awake_squyrrel(self):
        self.squyrrel = Squyrrel() # root_path=self.config['root_path']
        print(sys.path)

    def load_dependencies(self):
        # Squyrrel.load_package(PackageMeta(package_name=squyrrel, package_path=c:\users\lothar\passion\squyrrel\squyrrel, relative_path=squyrrel, import_string=squyrrel))
        self.squyrrel.register_and_load_package('squyrrel/gui')
        self.squyrrel.register_and_load_package('squyrrel/ide')
        class_meta = self.squyrrel.find_class_meta_by_name(class_name='App', package_name='ide', module_name='main')
        class_meta.add_instance(self)

    def init_workers(self):
        cmd_mgr_cls_meta = self.squyrrel.find_class_meta_by_name('CommandManager', package_name='management', module_name='command_manager')
        self.cmd_mgr = self.squyrrel.create_instance(cmd_mgr_cls_meta)
        for stamp in command_loaded_signal.clear_cache():
            # print(str(stamp.kwargs['class_meta']))
            self.cmd_mgr.on_command_loaded(*stamp.args, **stamp.kwargs)

        script_reader_cls_meta = self.squyrrel.find_class_meta_by_name('ScriptReader', package_name='management', module_name='script_reader')
        self.script_reader = self.squyrrel.create_instance(script_reader_cls_meta)

    def write_log(self):
        with open(self.config['log_file'], 'w') as file:
            for stamp in self.pop_debugging_signals_cache():
                file.write(stamp.args[0]+'\n')

    def build_gui(self):
        self.cmd_window = cmd_window_factory(squyrrel=self.squyrrel, parent=None, window_title='Squyrrel CLI')
        self.main_window = self.cmd_window
        self.log_window = log_window_factory(squyrrel=self.squyrrel, parent=self.main_window, window_title='Squyrrel Log')

    def pop_debugging_signals_cache(self):
        return squyrrel_debug_signal.clear_cache()

    def connect_signals(self):
        squyrrel_debug_signal.connect(self.debug)
        class_loaded_signal.connect(self.class_loaded)
        command_loaded_signal.connect(self.command_loaded)
        self.cmd_window.on_return_signal.connect(on_return)

    def debug(self, msg, tags=None):
        self.log_window.text.println(msg, tags=tags)

    def class_loaded(self, class_meta):
        self.debug(f'Loaded class {str(class_meta)}')

    def write_in_shell(self, text, tags=None):
        self.cmd_window.text.append(text, tags=tags)
        self.cmd_window.text.new_line()

    def ghost_cmd(self, cmd_line):
        self.write_in_shell(text=cmd_line)
        execute_cmd_from_shell(squyrrel=self.squyrrel, cmd_line=cmd_line)

    def execute_script(self, path):
        self.write_in_shell(f'Executing script <{path}>..')
        self.vars = {}
        with open(path, 'r') as file:
            self.script_reader.read_script(file.read())

    def start(self):
        self.main_window.mainloop()

    def command_loaded(self, *args, **kwargs):
        self.log_window.text.println('\n\nCOMMAND LOADED\n\n')

    def run_scripts(self):
        pass
        # self.execute_script(path='start.squyrrel')
        # self.execute_script(path='math.squyrrel')
        # self.squyrrel.add_relative_path('c:/users/lothar/passion')

        #self.squyrrel.add_absolute_path('c:\\users\\lothar\\passion')
        #pprint.pprint(sys.path)

        # self.squyrrel.register_and_load_package('mathscript')

    def test_db(self):
        self.squyrrel.register_and_load_package('squyrrel/db')
        sqlite_connection_meta = self.squyrrel.find_class_meta_by_name('SqliteConnection', package_name='sqlite', module_name='connection')
        self.db = self.squyrrel.create_instance(sqlite_connection_meta)
        self.db.connect(filename='kivur_27_12_2019.db')

        sql = 'select * from directors limit 10'
        self.execute_query(sql)

    def execute_query(self, sql, params=None):
        self.db.execute(sql=sql, params=params)
        data = self.db.fetchall()
        for director in data:
            self.debug(director)
        return data

def main():

    # import importlib
    # # import sys
    # # import pprint
    # #sys.path.append('c:/users/lothar/passion\\math')
    # sys.path.append('c:\\users\\lothar\\passion\\math')
    # pprint.pprint(sys.path)
    # # imported_module = importlib.import_module('.regtest', package='squyrrel.management')
    # mod = importlib.import_module('executor', package='math')
    # # print(mod.__file__)


    #sys.path.append('c:\\users\\lothar\\passion\\math')
            #import math
            #imported_module = importlib.import_module('executor', package='....math')


    app = App()
    app.start()

if __name__ == '__main__':
    main()