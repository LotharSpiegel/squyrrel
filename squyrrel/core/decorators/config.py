from squyrrel.core.constants import HOOK_NAME, HOOK_ORDER


class hook:

    def __init__(self, hook, order=None):
        self.hook_name = hook
        self.hook_order = order or 999

    def __call__(self, func):
        #def wrapper(*args, **kwargs):
        #    func(*args, **kwargs)
        #wrapper.hook_name = self.hook_name
        setattr(func, HOOK_NAME, self.hook_name)
        setattr(func, HOOK_ORDER, self.hook_order)
        #func.__hook_name__ = self.hook_name
        #func.__hook_order__ = self.hook_order
        return func


def exclude_from_logging(func):
    func.__exclude_from_logging__ = True
    return func


# def hook(func, *args, **kwargs):
#     def wrapper(*args, **kwargs):
#         func(*args, **kwargs)

#     wrapper.__hook__ =
#     wrapper.__name__ = func.__name__
#     return wrapper