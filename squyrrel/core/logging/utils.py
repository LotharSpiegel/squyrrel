

def arguments_tostring(*args, **kwargs):
    kwargs_str = ', '.join(['{}={}'.format(key, str(value)) for key, value in kwargs.items()])
    if args:
        args_str = ', '.join([str(arg) for arg in args])
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

def log_call(squyrrel, caller_name, func):
    def wrapper(*args, **kwargs):
        squyrrel.debug(format_func_call(caller_name, func, *args, **kwargs))
        squyrrel.debug_indent_level += 1
        return_value = func(*args, **kwargs)
        squyrrel.debug_indent_level -= 1
        #if caller_name != 'Squyrrel':
        #    print('log', func)
        return return_value
    wrapper.__name__ = func.__name__
    return wrapper