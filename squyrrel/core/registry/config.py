from squyrrel.core.config.base import IConfig
from squyrrel.core.config.decorators import hook
from squyrrel.core.registry.signals import squyrrel_debug_signal
from squyrrel.core.registry.logging import debug
from squyrrel.core.logging.utils import log_call


class SquyrrelDefaultConfig(IConfig):

    class_reference = 'Squyrrel'

    exclude_subpackages_from_registration = ()
    exclude_subpackages_from_loading = ('gui', 'sql')

    @hook(IConfig.HOOK_REPLACE)
    def _load_package_filter(squyrrel, package_meta):
        if squyrrel.loading:
            if package_meta.name in SquyrrelDefaultConfig.exclude_subpackages_from_loading:
                return False
        return True

    @hook(IConfig.HOOK_REPLACE)
    def _register_package_filter(squyrrel, package_name):
        if squyrrel.loading:
            if package_name in SquyrrelDefaultConfig.exclude_subpackages_from_registration:
                return False
        return True

    @hook(IConfig.HOOK_AFTER_INIT)
    def connect_signals(squyrrel, **kwargs):
        squyrrel_debug_signal.connect(debug)

    @hook(IConfig.HOOK_AFTER_INIT)
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