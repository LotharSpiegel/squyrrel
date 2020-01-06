
class hook:

    def __init__(self, hook_name):
        self.hook_name = hook_name

    def __call__(self, func):
        #def wrapper(*args, **kwargs):
        #    func(*args, **kwargs)
        #wrapper.hook_name = self.hook_name
        func.hook_name = self.hook_name
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