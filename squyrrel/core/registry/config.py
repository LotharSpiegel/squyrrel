from squyrrel.core.registry.config_registry import IConfig
from squyrrel.core.decorators.config import hook
from squyrrel.core.registry.signals import squyrrel_debug_signal
from squyrrel.core.registry.logging import debug
from squyrrel.core.logging.utils import log_call


class SquyrrelDefaultConfig(IConfig):

    class_reference = 'Squyrrel'

    def _load_packages_filter(squyrrel, package_meta):
        if package_meta.name == 'sql':
            return False
        return True

    @hook('after init')
    def connect_signals(squyrrel, **kwargs):
        squyrrel_debug_signal.connect(debug)

    @hook('after init')
    def install_logging(squyrrel, **kwargs):
        #squyrrel = kwargs['squyrrel']
        squyrrel.debug('Setup logging of Squyrrel methods..')

        method_names = set(attrib for attrib in dir(squyrrel) if callable(getattr(squyrrel, attrib)))
        method_names = [method_name for method_name in method_names if not method_name.startswith('__')]

        for method_name in method_names:
            method = getattr(squyrrel, method_name)
            if not hasattr(method, '__exclude_from_logging__'):
                setattr(squyrrel, method_name, log_call(squyrrel, caller_name='Squyrrel', func=method))
            # squyrrel.replace_method(instance=squyrrel, method_name=method_name, new_method=log_call_method)

            # print('replaced {}'.format(method_name))