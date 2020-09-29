from squyrrel.core.signals import Signal
from squyrrel.core.registry.signals import class_loaded_signal
from squyrrel.orm.model import Model


def model_filter(*args, **kwargs):
    cls_meta = kwargs.get('class_meta') or args[0]
    return cls_meta.has_ancestor(Model)


model_loaded_signal = class_loaded_signal.filtered(model_filter)
