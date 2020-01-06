import importlib
import inspect
import os
import sys

from squyrrel.core.registry.exceptions import *
from squyrrel.core.registry.exception_handler import ExceptionHandler
from squyrrel.core.registry.meta import PackageMeta
from squyrrel.core.registry.config_registry import ConfigRegistry
from squyrrel.core.registry.signals import squyrrel_debug_signal, squyrrel_error_signal
from squyrrel.core.utils.singleton import Singleton
from squyrrel.core.utils.paths import convert_path_to_import_string
from squyrrel.core.decorators.config import exclude_from_logging
from squyrrel.core.logging.utils import arguments_tostring
from squyrrel.core.constants import *


class Squyrrel(metaclass=Singleton):

    config_module_name = 'config'

    def __init__(self, root_path=None, config_path=None):
        self.packages = {}
        self.root_path = root_path
        self.paths = []
        self.add_absolute_path(self.root_path)
        self.debug_indent_level = 0

        self.squyrrel_package = self.register_package('squyrrel')

        self.active_profile = None
        self.module_import_exception_handler = ExceptionHandler() # traceback_limit=

        self.load_config(config_path)
        self.load_package(self.squyrrel_package)

    @exclude_from_logging
    def format_debug_output(self, text):
        return '{indent}{text}'.format(indent=self.debug_indent_level*'\t',
                                       text=text)

    @exclude_from_logging
    def debug(self, message, tags=None):
        debug_text = self.format_debug_output(message)
        squyrrel_debug_signal.emit(debug_text, tags=tags)

    @exclude_from_logging
    def error(self, message):
        error_text = self.format_debug_output(message)
        squyrrel_debug_signal.emit(error_text, tags='error')


    def activate_profile(self, profile_name):
        self.active_profile = profile_name

    def load_config(self, config_path):
        #self.squyrrel_config_module = self.register_module(self.squyrrel_package,
        #    module_name=self.config_module_name)
        #self.load_module(self.squyrrel_package, self.config_module_name)
        #squyrrel_config = self.find_class_meta_by_name('SquyrrelConfig')
        # find class by annotation!
        if config_path is None:
            from .config import SquyrrelDefaultConfig
            config_cls = SquyrrelDefaultConfig
        else:
            raise Exception('Not implemented')
        self.config_instance(instance=self, cls=Squyrrel, config_cls=config_cls)

    def config_instance(self, instance, cls, config_cls, exclude_dunders=True, params=None):
        # config_methods = inspect.getmembers(config_class, predicate=inspect.ismethod)
        # squyrrel_methods = inspect.getmembers(Squyrrel, predicate=inspect.ismethod)
        # print('config methods:')
        # print(config_methods)
        # print('squyrrel_methods methods:')
        # print(squyrrel_methods)
        replace_methods = config_cls.get_hook_methods('replace', exclude_dunders=exclude_dunders)
        for method_name in replace_methods:
            if hasattr(cls, method_name):
                self.replace_method(instance=instance, method_name=method_name, new_method=getattr(config_cls, method_name))

        # afterInit hook
        after_init_methods = config_cls.get_hook_methods(HOOK_AFTER_INIT)
        if params is None:
            params = {}
        after_init_args = params.get('after_init_args', []) or []
        after_init_kwargs = params.get('after_init_kwargs', {}) or {}
        if not 'squyrrel' in after_init_kwargs and instance != self:
            after_init_kwargs['squyrrel'] = self
        for method in after_init_methods:
            self.debug(f'after init hook for {instance.__class__.__name__}: {config_cls.__class__.__name__}.{method.__name__}')
            method(instance, *after_init_args, **after_init_kwargs)
            #try:
            #    method(instance, *after_init_args, **after_init_kwargs)
            #except TypeError as exc:
            #    arguments = arguments_tostring(*after_init_args, **after_init_kwargs)
            #    add_message = (f'. Wrong arguments for calling <{config_cls.__name__}.{method.__name__}>; Used: {arguments}')
                # self.debug(str(exc) + add_message)
                # todo: -> self.error
            #    raise type(exc)(str(exc) + add_message).with_traceback(sys.exc_info()[2])# from exc

    def replace_method(self, instance, method_name, new_method):
        setattr(instance, method_name, lambda *args, **kwargs: new_method(instance, *args, **kwargs))

    @property
    def num_registered_packages(self):
        return len(self.packages)

    def add_absolute_path(self, absolute_path):
        if absolute_path is None:
            return None
        if not absolute_path in self.paths:
            # print('adding path ', absolute_path)
            self.paths.append(absolute_path)
            if not absolute_path in sys.path:
                sys.path.append(absolute_path)
        return absolute_path

    def add_relative_path(self, relative_path):
        """relative_path is meant to be relative to Squyrrel.root_path"""
        if self.root_path is None:
            return None
        absolute_path = os.path.abspath(os.path.join(self.root_path, relative_path))
        return self.add_absolute_path(absolute_path)

    def get_full_package_path(self, relative_path):
        paths_tried = []
        for path in sys.path:
            check_path = os.path.join(path, relative_path)
            paths_tried.append(check_path)
            if os.path.exists(check_path):
                return check_path
        paths = '\n'.join(paths_tried)
        print('Did not find package <{relative_path}>. Tried the following paths: \n{paths}'.format(
            relative_path=relative_path, paths=paths))
        return None

    def register_package(self, relative_path):
        # possibly add check with find_package_by_name
        self.debug(f'register package/dir <{relative_path}>..')
        full_path = self.get_full_package_path(relative_path)
        if full_path is None:
            raise PackageNotFoundException('registering package/dir with relative path <{relative_path}> failed'.format(
                relative_path=relative_path))
        package_name = os.path.basename(relative_path)
        self.packages[package_name] = PackageMeta(
            package_name=package_name,
            package_path=full_path,
            relative_path=relative_path,
            package_import_string=convert_path_to_import_string(relative_path),
            namespace=None)
        self.debug(f'Successfully registered package/dir {package_name}')
        self.debug('Full path: ' + full_path)
        return self.packages[package_name]

    def find_package_by_name(self, name):
        # todo: return array
        for package_name, package_meta in self.packages.items():
            if name == package_name:
                return package_meta
        raise PackageNotFoundException(name)

    def inspect_directory(self, package_meta):
        modules = []
        for root, sub_dirs, files in os.walk(package_meta.path):
            for file in files:
                file_name, file_ext = os.path.splitext(file)
                if file_ext == '.py':
                    modules.append(file_name)
            package_meta.has_init = '__init__.py' in files
            break
        return modules, sub_dirs

    # def get_module_import_string(self, package_meta, module_name):
    #     return '{package_path}.{}'

    def register_module(self, package, module_name):
        if package is None:
            raise Exception('package is None')
        self.debug('register module <{module_name}>..'.format(module_name=module_name))
        if not package in self.packages.values():
            raise Exception('package <{package_name}> not registered yet'.format(
                package_name=package.name))
        return package.add_module(module_name=module_name)

    def load_module(self, package, module_name, load_classes=True):
        self.debug('load module <{module_name}>..'.format(module_name=module_name))
        module_registered = False

        module_meta = package.find_module(module_name, status='registered')
        # if module_meta is None:
        #     raise ModuleNotRegisteredException('Error while loading module: Module {} not registered yet'.format(module_name))

        try:
            imported_module = importlib.import_module(module_meta.import_string)
        except ModuleNotFoundError:
            module_meta.status = 'not found'
            raise
        except Exception as exc:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            module_meta.exception = (exc_type, exc_value, exc_traceback)
            self.module_import_exception_handler.handle(module_meta, exc_type, exc_value, exc_traceback)
            module_meta.status = 'rotten'
            raise ModuleRottenException from exc

        if load_classes:
            self.load_module_classes(module_meta=module_meta, imported_module=imported_module)

        module_meta.status = 'loaded'
        module_meta.loaded = True

    def load_class(self, module_meta, class_name, class_reference):
        self.debug('add class {}'.format(class_name))
        module_meta.add_class(class_reference=class_reference,
                              class_name=class_name)
        #if hasattr(class_reference, 'is_class_config'):
        #    if class_reference.is_class_config:
        #        self.add_config()
        #is_class_config

    def load_module_classes(self, module_meta, imported_module):
        self.debug('load classes of module {module}..'.format(module=module_meta))
        mod_imp_str = module_meta.import_string
        classes = {m[0]: m[1] for m in sorted(
                inspect.getmembers(
                    imported_module,
                    lambda member: inspect.isclass(member) and member.__module__ == mod_imp_str)
        )}
        for class_name, class_reference in classes.items():
            self.load_class(module_meta, class_name, class_reference)
        module_meta.classes_loaded = True
        self.debug('loaded {num_classes} classes in module module {module}'.format(
            num_classes=module_meta.num_classes, module=module_meta))

    def find_class_meta_by_name(self, class_name, package_name=None):
        if package_name is None:
            packages = self.packages.values()
        else:
            packages = [self.find_package_by_name(package_name)]
        for package in packages:
            class_meta = package.find_class_meta_by_name(class_name, raise_not_found=False)
            if class_meta is not None:
                return class_meta
        raise ClassNotFoundException(f'Did not find class with name <{class_name}>!')

    def _load_packages_filter(self, package_meta):
        return True

    def load_package(self, package_meta, ignore_rotten_modules=True,
                           load_classes=True, load_subpackages=True,
                           load_packages_filter=None):
        self.debug('load package <{package}>...'.format(package=repr(package_meta)))

        if load_packages_filter is None:
            load_packages_filter = self._load_packages_filter
        if not load_packages_filter(package_meta):
            self.debug(f'package {str(package_meta)} did not pass filter')
            return package_meta

        modules, sub_dirs = self.inspect_directory(package_meta)
        self.debug(f'is package (contains __init__.py): {package_meta.has_init}')
        for module in modules:
            module_meta = self.register_module(package_meta, module_name=module)
            try:
                self.load_module(package_meta, module_name=module, load_classes=load_classes)
            except ModuleRottenException:
                if not ignore_rotten_modules:
                    raise

        if not load_subpackages:
            return
        for dir in sub_dirs:
            self.debug('Inspecting subdir {} ..'.format(dir))
            relative_dir_path = os.path.join(package_meta.relative_path, dir)
            subpackage_meta = self.register_package(relative_dir_path)
            subpackage_meta = self.load_package(subpackage_meta,
                ignore_rotten_modules=ignore_rotten_modules,
                load_classes=load_classes,
                load_subpackages=load_subpackages)
            if subpackage_meta.has_init:
                self.debug('add subpackage {} to package {}'.format(package_meta.name, subpackage_meta.name))
                package_meta.add_subpackage(subpackage_meta)

        package_meta.loaded = True
        return package_meta

    def find_subpackage(self, name):
        return None

    def create_instance(self, class_meta, params=None):
        self.debug(f'\ncreate_instance of class <{class_meta.class_name}>')
        config_cls = self.get_class_config(class_meta=class_meta)

        if params is None:
            params = {}
        init_args = params.get('init_args', None)
        init_kwargs = params.get('init_kwargs', None)

        init_kwargs_methods = config_cls.get_hook_methods(HOOK_INIT_KWARGS)
        for method in init_kwargs_methods:
            init_kwargs = method(init_kwargs or {})

        instance = class_meta(*(init_args or []), **(init_kwargs or {}))
        if config_cls is not None:
            self.debug(f'config class: {config_cls.__name__}')
            ##configured_kwargs = class_config.config_init_kwargs(kwargs)
            self.config_instance(instance=instance, cls=class_meta.class_reference, config_cls=config_cls, params=params)
            # config_cls.config(instance, *args, **configured_kwargs)
        return instance

    def get_class_config(self, class_meta):
        class_name = class_meta.class_name
        return ConfigRegistry().get_config(class_name, profile_name=self.active_profile)
