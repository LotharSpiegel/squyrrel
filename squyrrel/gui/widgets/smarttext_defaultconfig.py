import os.path

from squyrrel.core.logging.utils import log_call
from squyrrel.core.config.base import IConfig
from squyrrel.core.config.decorators import hook
from squyrrel.gui.widgets.smarttext import CustomText


class SmartTextDefaultConfig(IConfig):
    class_reference = 'SmartText'

    @hook(IConfig.HOOK_INIT_KWARGS)
    def config_init_kwargs(kwargs):
        kwargs['text_class'] = CustomText

    @hook(IConfig.HOOK_AFTER_INIT, order=1)
    def setup_logging(widget, **kwargs):
        squyrrel = kwargs['squyrrel']
        squyrrel.debug('Setup logging of SmartText methods..')

        method_names = set(attrib for attrib in dir(widget) if callable(getattr(widget, attrib)))
        method_names = [method_name for method_name in method_names if not method_name.startswith('__')]

        for method_name in method_names:
            method = getattr(widget, method_name)
            if hasattr(method, '__include_in_gui_logging__'):
                print(method)
                setattr(widget, method_name, log_call(squyrrel, caller_name=widget.__class__.__name__, func=method, tags="gui_call"))

    @hook(IConfig.HOOK_AFTER_INIT, order=2)
    def config(widget, **kwargs):
        json_filepath = os.path.dirname(__file__)
        json_filepath += '/themes/grey_scale.json'
        data = widget.load_theme(json_filepath)
        widget.apply_theme(data)