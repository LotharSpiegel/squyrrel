from .base import IConfig


class hook:

    def __init__(self, hook, order=None):
        self.hook_name = hook
        self.hook_order = order or 999

    def __call__(self, func):
        #def wrapper(*args, **kwargs):
        #    func(*args, **kwargs)
        #wrapper.hook_name = self.hook_name
        setattr(func, IConfig.HOOK_NAME, self.hook_name)
        setattr(func, IConfig.HOOK_ORDER, self.hook_order)
        #func.__hook_name__ = self.hook_name
        #func.__hook_order__ = self.hook_order
        return func


def exclude_from_logging(func):
    func.__exclude_from_logging__ = True
    return func