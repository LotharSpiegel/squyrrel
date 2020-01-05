import os
import sys


from squyrrel.core.registry.config_registry import IConfig
from squyrrel import Squyrrel
# from squyrrel.gui.windows.base import MainWindow


class MainWindowConfig(IConfig):
    class_reference = 'MainWindow'

    @staticmethod
    def config_init_kwargs(kwargs):
        return kwargs

    @staticmethod
    def config(window):
        window.title('Main Window')


class App(object):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.awake_squyrrel()
        self.load_packages()
        self.build_gui()

    def awake_squyrrel(self):
        root_path = os.getcwd()
        self.squyrrel = Squyrrel(root_path=root_path, config_path=None)

    def load_packages(self):
        self.load_gui_package()

    def load_gui_package(self):
        # send signal...then create main window
        self.gui_package = self.squyrrel.register_package('gui')
        self.squyrrel.load_package(self.gui_package,
            ignore_rotten_modules=True,
            load_classes=True, load_subpackages=True,
            load_packages_filter=None)

    def build_gui(self):
        self.gui_windows_package = self.gui_package.find_subpackage('windows')
        base_module = self.gui_windows_package.find_module('base', status='loaded')
        main_window_meta = self.gui_windows_package.find_class_meta_by_name('MainWindow', base_module)
        self.main_window = self.squyrrel.create_instance(main_window_meta)

    def start(self):
        self.main_window.mainloop()


def main():
    app = App()
    app.start()

if __name__ == '__main__':
    main()