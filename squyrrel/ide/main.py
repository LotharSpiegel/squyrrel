import os

from squyrrel import Squyrrel
from squyrrel.management.command_manager import CommandManager
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
            self.init_cmd_mgr()
            self.awake_squyrrel()
            self.load_dependencies()
            self.build_gui()
            self.connect_signals()
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

    def init_cmd_mgr(self):
        self.cmd_mgr = CommandManager()

    def awake_squyrrel(self):
        self.squyrrel = Squyrrel() # root_path=self.config['root_path']

    def load_dependencies(self):
        # Squyrrel.load_package(PackageMeta(package_name=squyrrel, package_path=c:\users\lothar\passion\squyrrel\squyrrel, relative_path=squyrrel, import_string=squyrrel))
        self.squyrrel.register_and_load_package('squyrrel/gui')
        self.squyrrel.register_and_load_package('squyrrel/ide')
        class_meta = self.squyrrel.find_class_meta_by_name(class_name='App', package_name='ide', module_name='main')
        class_meta.add_instance(self)

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
        class_loaded_signal.connect(self.debug)
        command_loaded_signal.connect(self.command_loaded)
        self.cmd_window.on_return_signal.connect(on_return)

    def debug(self, msg, tags=None):
        self.log_window.text.println(msg, tags=tags)

    def write_in_shell(self, text, tags=None):
        self.cmd_window.text.append(text, tags=tags)
        self.cmd_window.text.new_line()

    def ghost_cmd(self, cmd_line):
        self.write_in_shell(text=cmd_line)
        execute_cmd_from_shell(squyrrel=self.squyrrel, cmd_line=cmd_line)

    def start(self):
        self.write_in_shell('Start Squyrrel CLI (version=0.1.0)')
        self.ghost_cmd(cmd_line='s.report')
        self.main_window.mainloop()

    def command_loaded(self, msg):
        self.log_window.text.println('\n\nCOMMAND LOADED\n\n')


def main():
    app = App()
    app.start()

if __name__ == '__main__':
    main()