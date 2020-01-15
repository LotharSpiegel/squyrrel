from squyrrel.core.utils.singleton import Singleton


class ConfigRegistry(metaclass=Singleton):

    class_configs = {}

    def add_config(self, config_cls, name, bases, attrs):
        # if not 'config_init_kwargs' in attrs:
        #     config_cls.config_init_kwargs = lambda kwargs: kwargs
        # if not 'config' in attrs:
        #     config_cls.config = lambda instance, *args, **kwargs: None
        # print('\n\nadd_config, attrs=' + str(attrs))
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

        config_class = super().__new__(cls, name, bases, attrs)

        # can add class attribute here
        # can add this class to squyrrel
        # print(attrs) # enthält class_name, init, config
        if name != 'IConfig':
            ConfigRegistry().add_config(config_class, name, bases, attrs)
        return config_class


class IConfig(object, metaclass=IConfigRegistry):

    HOOK_NAME = '__hook_name__'
    HOOK_ORDER = '__hook_order__'

    # hooks:
    HOOK_AFTER_INIT = 'HOOK_AFTER_INIT'
    HOOK_INIT_KWARGS = 'HOOK_INIT_KWARGS'
    HOOK_REPLACE = 'HOOK_REPLACE'

    class_reference = None

    @classmethod
    def get_method_names(cls, exclude_dunders=True):
        attribs = dir(cls)
        method_names = set(attrib for attrib in attribs if callable(getattr(cls, attrib)))

        #print('all method names:', method_names)

        for base in cls.__bases__:
            base_method_names = set(attrib for attrib in dir(base) if callable(getattr(base, attrib)))
            # print(f'base: {base.__name__} has:', base_method_names)
            for m in base_method_names:
                if m in method_names:
                    method_names.remove(m)
            #method_names = method_names.difference(set(attrib for attrib in attribs if callable(getattr(base, attrib))))

        #print('only mine:', method_names)

        if exclude_dunders:
            method_names = [method_name for method_name in method_names if not method_name.startswith('__')]
            #methods = filter(lambda method: not method.startswith("__"), methods)
        return method_names

    @classmethod
    def get_methods(cls, exclude_dunders=True):
        return [getattr(cls, method_name) for method_name in cls.get_method_names(exclude_dunders=exclude_dunders)]
    # methods = cls.get_methods(exclude_dunders=exclude_dunders)
    # print(methods)
    # for method in methods:
    #     print(type(method))
    #     print(method)
    #     setattr(method, 'hook', 'hook')
    #     if hasattr(method, 'hook'):
    #         print('method has hook!')
    # return [method for method in methods if hasattr(method, 'hook') and method.hook == 'replace']

    @classmethod
    def get_hook_methods(cls, hook, exclude_dunders=True):
        methods = cls.get_methods(exclude_dunders=exclude_dunders)
        hook_methods = [method for method in methods if
            hasattr(method, cls.HOOK_NAME) and getattr(method, cls.HOOK_NAME) == hook]
        hook_methods.sort(key=lambda method: getattr(method, cls.HOOK_ORDER))
        return hook_methods
