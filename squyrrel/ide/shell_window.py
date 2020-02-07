
from .gui import gui_factory
from squyrrel.gui.windows.base import TextMainWindow
from squyrrel.core.signals import Signal
from squyrrel.core.config.base import IConfig
from squyrrel.core.config.decorators import hook
from squyrrel.core.registry.signals import squyrrel_debug_signal
from squyrrel.core.logging.utils import arguments_tostring




class ShellWindow(TextMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text = gui_factory(module_name='smarttext', subpackage='widgets', class_name='SmartText', parent=self)
        self.attach_text_widget(text)
        self.on_return_signal = Signal('shell_on_return',
            before_emit_hook=lambda *args, **kwargs: squyrrel_debug_signal.emit(f'Signal[shell_on_return]({arguments_tostring(*args, **kwargs)})', tags='signal'))
        text.bind("<Return>", self.on_return)

    def on_return(self, event=None):
        cmd_line = self.text.get_text("insert-1c linestart", "insert-1c lineend")
        self.on_return_signal.emit(user_input=cmd_line)


class ShellWindowConfig(IConfig):
    class_reference = ShellWindow

    @hook(IConfig.HOOK_AFTER_INIT)
    def config(window, *args, **kwargs):
        window.title(kwargs.get('window_title', 'Squyrrel CLI'))