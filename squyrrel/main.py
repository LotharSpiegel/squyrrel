import os
import sys


from squyrrel.core.registry.config_registry import IConfig
from squyrrel.core.registry.signals import squyrrel_debug_signal, squyrrel_error_signal
from squyrrel.core.decorators.config import hook
from squyrrel import Squyrrel
# from squyrrel.gui.windows.base import MainWindow


class MainWindowConfig(IConfig):
    class_reference = 'MainWindow'

    @hook('after init')
    def config(window, **kwargs):
        window.title('Main Window')



class App(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.awake_squyrrel()
        self.load_packages()
        self.build_gui()
        self.pop_debugging_signals_cache()
        self.connect_signals()

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
            # 'after_init_args': [parent],
            'after_init_kwargs': config_kwargs,
        }
        return self.squyrrel.create_instance(class_meta, params)

    def build_gui(self):
        print('build_gui')
        self.main_window = self.gui_factory('windows', 'base', 'MainWindow')
        self.debug_window = self.gui_factory('windows', 'base', 'TextWindow', parent=self.main_window,
                                            config_kwargs={'window_title': 'Debug'})
        text = self.gui_factory('widgets', 'smarttext', 'SmartText', parent=self.debug_window)
        self.debug_window.init_text_widget(text)

    def pop_debugging_signals_cache(self):
        stamps = squyrrel_debug_signal.clear_cache()
        for stamp in stamps:
            self.debug(*stamp.args, **stamp.kwargs)

    def connect_signals(self):
        squyrrel_debug_signal.connect(self.debug)

    def start(self):
        self.main_window.mainloop()

    def debug(self, text):
        debug_text = f'\n{text}'
        self.debug_window.text.append(debug_text)


def main():
    app = App()
    app.start()

if __name__ == '__main__':
    main()