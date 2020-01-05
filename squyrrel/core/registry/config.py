from squyrrel.core.registry.config_registry import IConfig


class SquyrrelDefaultConfig(IConfig):

    class_reference = 'Squyrrel'

    def _load_packages_filter(squyrrel, package_meta):
        if package_meta.name == 'sql':
            return False
        return True