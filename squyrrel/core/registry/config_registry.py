from squyrrel.core.utils.singleton import Singleton


class ConfigRegistry(metaclass=Singleton):

    class_configs = {}

    def add_config(self, config_cls, name, bases, attrs):
        if not 'config_init_kwargs' in attrs:
            config_cls.config_init_kwargs = lambda kwargs: kwargs
        print('\n\nadd_config, attrs=' + str(attrs))
        try:
            class_reference = attrs['class_reference']
        except KeyError:
            raise Exception(f'{name} is missing attribute `class_reference`')
        if class_reference is None:
            return
        if isinstance(class_reference, str):
            class_name = class_reference
        else:
            class_name = class_reference.__name__
        if class_name in self.class_configs:
            self.class_configs[class_name].append(config_cls)
        else:
            self.class_configs[class_name] = [config_cls]

    def get_config(self, class_name, profile_name=None):
        configs = self.class_configs.get(class_name, None)
        if configs is None:
            return None
        for config in configs:
            if profile_name is None:
                return config
            if hasattr(config, 'profile_name'):
                if profile_name == config.profile_name:
                    return config


class IConfigRegistry(type): # Singleton(type)

    def __new__(cls, name, bases, attrs):
        # when e.g. squyrrel loads module,
        # this is called
        print('\n\nIConfigRegistry.__new__!!!')
        print('name:', name)

        config_class = super().__new__(cls, name, bases, attrs)

        # can add class attribute here
        # can add this class to squyrrel
        print(attrs) # enthält class_name, init, config
        if name != 'IConfig':
            ConfigRegistry().add_config(config_class, name, bases, attrs)
        return config_class


class IConfig(object, metaclass=IConfigRegistry):

    class_reference = None