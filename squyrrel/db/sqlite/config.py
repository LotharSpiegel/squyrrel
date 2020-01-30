from squyrrel.core.config.base import IConfig
from squyrrel.core.config.decorators import hook
from squyrrel.core.registry.signals import squyrrel_debug_signal
from squyrrel.core.registry.logging import debug
from squyrrel.core.logging.utils import log_call


class SqliteConnectionConfig(IConfig):

    class_reference = 'SqliteConnection'

    # @hook(IConfig.HOOK_AFTER_INIT)
    # def connect_signals(squyrrel, **kwargs):
    #     squyrrel_debug_signal.connect(debug)

    @hook(IConfig.HOOK_AFTER_INIT)
    def install_logging(conn, **kwargs):
        squyrrel = kwargs['squyrrel']
        squyrrel.debug('Setup logging of SqliteConnection methods..')

        method_names = set(attrib for attrib in dir(conn) if callable(getattr(conn, attrib)))
        method_names = [method_name for method_name in method_names if not method_name.startswith('__')]

        for method_name in method_names:
            method = getattr(conn, method_name)
            if not hasattr(method, '__exclude_from_logging__'):
                setattr(conn, method_name, log_call(squyrrel, caller_name='SqliteConnection', func=method))
