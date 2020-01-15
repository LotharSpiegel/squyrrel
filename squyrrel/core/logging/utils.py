

def arguments_tostring(*args, **kwargs):
    kwargs_str = ', '.join(['{}={}'.format(key, repr(value)) for key, value in kwargs.items()])
    if args:
        args_str = ', '.join([repr(arg) for arg in args])
        if kwargs:
            return f'{args_str}, {kwargs_str}'
        else:
            return args_str
    elif kwargs:
        return kwargs_str
    else:
        return ''

def format_func_call(caller_name, func, *args, **kwargs):
    return f'{caller_name}.{func.__name__}({arguments_tostring(*args, **kwargs)})'

def format_return_value(caller_name, func, return_value):
    return f'-> ({caller_name}.{func.__name__}) ->: {repr(return_value)}\n'

def log_call(squyrrel, caller_name, func, tags=None):
    if tags is None:
        tags = 'call'
    def wrapper(*args, **kwargs):
        squyrrel.debug(format_func_call(caller_name, func, *args, **kwargs), tags=tags)
        squyrrel.debug_indent_level += 1
        return_value = func(*args, **kwargs)
        squyrrel.debug(format_return_value(caller_name, func, return_value))
        squyrrel.debug_indent_level -= 1
        return return_value
    wrapper.__name__ = func.__name__
    return wrapper


# todo: functools.wraps (see replace_method Squyrrel)