from squyrrel.core.registry.config_registry import IConfig
from squyrrel.core.decorators.config import hook
from squyrrel.core.registry.signals import squyrrel_debug_signal
from squyrrel.core.registry.logging import debug


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

def format_func_call(func, *args, **kwargs):
    return f'Squyrrel.{func.__name__}({arguments_tostring(*args, **kwargs)})'

def log_call(squyrrel, func):
    def wrapper(*args, **kwargs):
        squyrrel.debug(format_func_call(func, *args, **kwargs))
        squyrrel.debug_indent_level += 1
        return_value = func(*args, **kwargs)
        squyrrel.debug_indent_level -= 1
        return return_value
    wrapper.__name__ = func.__name__
    return wrapper

class SquyrrelDefaultConfig(IConfig):

    class_reference = 'Squyrrel'

    def _load_packages_filter(squyrrel, package_meta):
        if package_meta.name == 'sql':
            return False
        return True

    @hook('after init')
    def connect_signals(squyrrel):
        squyrrel_debug_signal.connect(debug)

    @hook('after init')
    def install_logging(squyrrel):
        squyrrel.debug('Setup logging of Squyrrel methods..')

        method_names = set(attrib for attrib in dir(squyrrel) if callable(getattr(squyrrel, attrib)))
        method_names = [method_name for method_name in method_names if not method_name.startswith('__')]

        for method_name in method_names:
            method = getattr(squyrrel, method_name)
            if not hasattr(method, '__exclude_from_logging__'):
                setattr(squyrrel, method_name, log_call(squyrrel, method))
            # squyrrel.replace_method(instance=squyrrel, method_name=method_name, new_method=log_call_method)

            # print('replaced {}'.format(method_name))