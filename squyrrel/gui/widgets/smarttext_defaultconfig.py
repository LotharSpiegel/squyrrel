from squyrrel.core.logging.utils import log_call
from squyrrel.core.registry.config_registry import IConfig
from squyrrel.core.decorators.config import hook
from squyrrel.core.constants import HOOK_AFTER_INIT


class SmartTextDefaultConfig(IConfig):
    class_reference = 'SmartText'

    @hook(HOOK_AFTER_INIT, order=1)
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

    @hook(HOOK_AFTER_INIT, order=2)
    def config(widget, **kwargs):
        json_filepath = 'gui/widgets/themes/grey_scale.json'
        data = widget.load_theme(json_filepath)
        widget.apply_theme(data)