from squyrrel.core.signals import Signal
from squyrrel.management.base import BaseCommand

squyrrel_error_signal = Signal('squyrrel_error_signal')
squyrrel_debug_signal = Signal('squyrrel_debug_signal')

class_loaded_signal = Signal('class_loaded_signal')


def command_filter(*args, **kwargs):
    cls_meta = kwargs.get('class_meta') or args[0]
    return cls_meta.has_ancestor(BaseCommand)


command_loaded_signal = class_loaded_signal.filtered(command_filter)
