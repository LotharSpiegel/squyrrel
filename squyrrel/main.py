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
    def config_after_init(window, *args, **kwargs):
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

    def gui_factory(self, subpackage, module_name, class_name, parent=None, init_kwargs=None, config_kwargs=None):
        package_meta = self.gui_package.find_subpackage(subpackage)
        class_meta = package_meta.find_class_meta_by_name(class_name, module_name)

        params = {
            'init_args': [parent],
            'init_kwargs': init_kwargs,
            'after_init_kwargs': config_kwargs,
        }
        return self.squyrrel.create_instance(class_meta, params)

    def build_gui(self):
        self.main_window = self.gui_factory('windows', 'base', 'MainWindow')
        self.debug_window = self.gui_factory('windows', 'base', 'TextWindow', parent=self.main_window,
                                            config_kwargs={'window_title': 'Debug'})
        text = self.gui_factory('widgets', 'smarttext', 'SmartText', parent=self.debug_window)
        self.debug_window.init_text_widget(text)

    def test(self):
        self.debug_window.text.set_text('Veniam do deserunt amet ea incididunt sunt occaecat in occaecat officia incididunt ad duis velit voluptate labore sit exercitation minim dolor irure quis non.')

    def start(self):
        self.main_window.mainloop()


def main():
    app = App()
    app.start()

if __name__ == '__main__':
    main()