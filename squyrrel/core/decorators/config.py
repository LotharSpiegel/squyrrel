
class hook:

    def __init__(self, hook_name):
        self.hook_name = hook_name

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
        wrapper.hook_name = self.hook_name
        return wrapper


# def hook(func, *args, **kwargs):
#     def wrapper(*args, **kwargs):
#         func(*args, **kwargs)

#     wrapper.__hook__ =
#     wrapper.__name__ = func.__name__
#     return wrapper