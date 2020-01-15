
from gui import gui_factory
from squyrrel.gui.windows.base import TextWindow
from squyrrel.core.config.base import IConfig
from squyrrel.core.config.decorators import hook


class LogWindow(TextWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text = gui_factory(module_name='smarttext', subpackage='widgets', class_name='SmartText', parent=self)
        self.attach_text_widget(text)


class LogWindowConfig(IConfig):
    class_reference = LogWindow

    @hook(IConfig.HOOK_AFTER_INIT)
    def config(window, *args, **kwargs):
        window.title(kwargs.get('window_title', 'Squyrrel Log'))