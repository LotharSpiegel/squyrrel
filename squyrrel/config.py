


class SquyrrelConfig:

    def _load_packages_filter(squyrrel, package_meta):
        if package_meta.name == 'sql':
            return False
        return True

        # idea: lazy load package: in __init__: squyrrel_config = {
                 #   lazy_load: True
                # }