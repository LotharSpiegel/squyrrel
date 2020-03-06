"""
Todo: register/unregister package: more refined than storing with key = package_name
(should also depend on path or other metrics)

"""


from functools import wraps
import importlib
import inspect
import os
import sys

from squyrrel.core.registry.exceptions import *
from squyrrel.core.registry.exception_handler import ExceptionHandler
from squyrrel.core.registry.meta import PackageMeta, ClassMeta
from squyrrel.core.registry.signals import (squyrrel_debug_signal, squyrrel_error_signal,
    class_loaded_signal)
from squyrrel.core.utils.singleton import Singleton
from squyrrel.core.utils.paths import convert_path_to_import_string, find_first_parent
from squyrrel.core.config.base import ConfigRegistry, IConfig
from squyrrel.core.config.decorators import exclude_from_logging
from squyrrel.core.logging.utils import arguments_tostring


__SQUYRREL_PACKAGE_NAME__ = 'squyrrel'



class Squyrrel(metaclass=Singleton):

    config_module_name = 'config'

    def __init__(self, root_path=None, config_class=None):

        self.initialize(root_path=root_path, config_class=config_class)

        self.load_squyrrel_package()

        print(f'Squyrrel ({id(self)}) awakened')

    def initialize(self, root_path=None, config_class=None):
        self.packages = {}
        self.root_path = root_path or self.get_squyrrel_package_root_path()
        self.paths = []
        self.loading = False
        self.add_absolute_path(self.root_path)
        self.debug_indent_level = 0
        self.context = None
        self.active_profile = None
        self.last_report = None
        self.module_import_exception_handler = ExceptionHandler() # traceback_limit=
        self.load_config(config_class)

    def load_squyrrel_package(self):
        num_packages_before = self.num_registered_packages
        self.loading = True
        self.squyrrel_package = self.register_package(__SQUYRREL_PACKAGE_NAME__)
        self.load_package(self.squyrrel_package)
        self.loading = False
        self.build_context()
        self.report(num_packages_before)

    def reload_squyrrel_package(self):
        # make backup copy of squyrrel package?
        self.unregister_package(self.squyrrel_package)
        self.load_squyrrel_package()

    def get_squyrrel_package_root_path(self):
        return find_first_parent(__file__, __SQUYRREL_PACKAGE_NAME__)

    def build_context(self):
        pass

    def report(self, num_packages_before):
        filtered_packages = [str(package) for package in self.squyrrel_package.subpackages if (package.registered and not package.loaded)]
        self.last_report = f"""
Loaded squyrrel package.
Loaded {self.num_registered_packages - num_packages_before} (sub)packages.
Packages registered: {', '.join([str(package) for package in self.squyrrel_package.subpackages])}
Packages not loaded (because they were filtered): {', '.join(filtered_packages)}
"""
        self.debug(self.last_report)

    @exclude_from_logging
    def format_debug_output(self, text):
        return '{indent}{text}'.format(indent=self.debug_indent_level*'\t', text=text)

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

    def load_config(self, config_cls):
        #self.squyrrel_config_module = self.register_module(self.squyrrel_package,
        #    module_name=self.config_module_name)
        #self.load_module(self.squyrrel_package, self.config_module_name)
        #squyrrel_config = self.find_class_meta_by_name('SquyrrelConfig')
        # find class by annotation!
        if config_cls is None:
            from .config import SquyrrelDefaultConfig
            config_cls = SquyrrelDefaultConfig
        self.config_instance(instance=self, cls=Squyrrel, config_cls=config_cls)

    def config_instance(self, instance, cls, config_cls, exclude_dunders=True, params=None):
        # config_methods = inspect.getmembers(config_class, predicate=inspect.ismethod)
        # squyrrel_methods = inspect.getmembers(Squyrrel, predicate=inspect.ismethod)
        # print('config methods:')
        # print(config_methods)
        # print('squyrrel_methods methods:')
        # print(squyrrel_methods)
        replace_methods = config_cls.get_hook_methods(IConfig.HOOK_REPLACE, exclude_dunders=exclude_dunders)
        for method in replace_methods:
            method_name = method.__name__
            if hasattr(cls, method_name):
                self.replace_method(instance=instance, method_name=method_name, new_method=method)

        # afterInit hook
        after_init_methods = config_cls.get_hook_methods(IConfig.HOOK_AFTER_INIT)
        if params is None:
            params = {}
        after_init_args = params.get('after_init_args', []) or []
        after_init_kwargs = params.get('after_init_kwargs', {}) or {}
        if not 'squyrrel' in after_init_kwargs and instance != self:
            after_init_kwargs['squyrrel'] = self
        for method in after_init_methods:
            self.debug(f'After init hook for {instance.__class__.__name__}: {config_cls.__class__.__name__}.{method.__name__}')
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
        @wraps(getattr(instance, method_name))
        def wrapper(*args, **kwargs):
            return new_method(instance, *args, **kwargs)
        setattr(instance, method_name, wrapper)

    @property
    def num_registered_packages(self):
        return len(self.packages)

    def get_package(self, package_name):
        try:
            package = self.packages[package_name]
        except KeyError:
            raise Exception(f'Package with name <{package_name}> not registered!')
        return package

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
        for path in sys.path: #TODO: self.paths
            check_path = os.path.join(path, relative_path)
            paths_tried.append(check_path)
            if os.path.exists(check_path):
                return check_path
        paths = '\n'.join(paths_tried)
        self.debug('Did not find package <{relative_path}>. Tried the following paths: \n{paths}'.format(
            relative_path=relative_path, paths=paths))
        print('sys.path:')
        print(sys.path)
        return None

    def find_package_by_name(self, name):
        # todo: return array
        for package_name, package_meta in self.packages.items():
            if name == package_name:
                return package_meta
        raise PackageNotFoundException(name)

    def get_registered_package(self, name):
        try:
            return self.find_package_by_name(name)
        except PackageNotFoundException:
            return self.register_package(name)

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
        self.debug('Register module <{module_name}>..'.format(module_name=module_name))
        if not package in self.packages.values():
            raise Exception('Package <{package_name}> not registered yet'.format(
                package_name=package.name))
        return package.add_module(module_name=module_name)

    def load_module(self, module_name, package=None, load_classes=True):

        module_registered = False

        if package is None:
            module_meta = ModuleMeta(package=None, module_name=module_name)
        else:
            if package.status == 'registered':
                module_meta = package.add_module(module_name=module_name)
            else:
                module_meta = package.find_module(module_name, status='registered')

        self.debug(f'Load module <{module_meta.import_string}>')

        # if module_meta is None:
        #     raise ModuleNotRegisteredException('Error while loading module: Module {} not registered yet'.format(module_name))
        # sys.path.append('c:\\users\\lothar\\passion\\math')
        try:
            # TODO: enable relative import (pass package='example' to import_module...)
            imported_module = importlib.import_module(module_meta.import_string)#, package=package.import_string)
        except ModuleNotFoundError:
            module_meta.status = 'not found'
            print('package:', package.import_string)
            print('module:', module_meta.import_string)

            # imported_module = importlib.import_module('.'+module_name, package=package.import_string)


            raise
        except Exception as exc:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            module_meta.exception = (exc_type, exc_value, exc_traceback)
            self.module_import_exception_handler.handle(module_meta, exc_type, exc_value, exc_traceback)
            module_meta.status = 'rotten'
            raise ModuleRottenException(f'Module {str(module_meta)} contains errors') from exc

        if load_classes:
            self.load_module_classes(module_meta=module_meta, imported_module=imported_module)

        module_meta.status = 'loaded'
        module_meta.loaded = True

    def load_class(self, module_meta, class_name, class_reference):
        self.debug('add class {}'.format(class_name))
        new_class_meta = module_meta.add_class(class_reference=class_reference,
                              class_name=class_name)
        class_loaded_signal.emit(class_meta=new_class_meta)
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

    def find_class_meta_by_name(self, class_name, package_name=None, module_name=None):
        # TODO: handle module_name
        if package_name is None:
            packages = self.packages.values()
        else:
            packages = [self.find_package_by_name(package_name)]
        for package in packages:
            class_meta = package.find_class_meta_by_name(class_name, raise_not_found=False)
            if class_meta is not None:
                return class_meta
        raise ClassNotFoundException(f'Did not find class with name <{class_name}>!')

    def _register_package_filter(self, package_name):
        return True

    def _load_package_filter(self, package_meta):
        return True

    def register_and_load_package(self, relative_path):
        package_meta = self.register_package(relative_path)
        return self.load_package(package_meta)

    def unregister_package(self, package_meta):
        # todo: refine package_key (method on PackageMeta, eventually hash code or uid)
        if not package_meta.loaded:
            return
        for subpackage in package_meta.subpackages:
            self.unregister_package(subpackage)
        package_key = package_meta.name
        del self.packages[package_key]

    def package_already_registered(self, package_name):
        #TODO:refine with path, ..
        return package_name in self.packages.keys()

    def register_package(self, relative_path, register_package_filter=None, raise_when_already_registered=False):
        # possibly add check with find_package_by_name
        self.debug(f'Register package <{relative_path}>..')
        full_path = self.get_full_package_path(relative_path)
        if full_path is None:
            raise PackageNotFoundException('registering package/dir with relative path <{relative_path}> failed'.format(
                relative_path=relative_path))
        package_name = os.path.basename(relative_path)
        if package_name == '__pycache__':
            pass
        elif self.package_already_registered(package_name=package_name):
            if raise_when_already_registered:
                raise Exception(f'There is already a package with name <{package_name}> registered!')
            return self.packages[package_name]

        package_meta = PackageMeta(
            package_name=package_name,
            package_path=full_path,
            relative_path=relative_path,
            package_import_string=convert_path_to_import_string(relative_path),
            namespace=None)

        if register_package_filter is None:
            register_package_filter = self._register_package_filter
        if not register_package_filter(package_name):
            self.debug(f'Package {package_name} did not pass register filter')
            print(f'Package {package_name} did not pass register filter')
            package_meta.status = 'excluded by filter'
            return package_meta

        package_meta.status = 'registered'
        package_meta.registered = True
        self.packages[package_name] = package_meta
        self.debug(f'Successfully registered package/dir {package_name}')
        self.debug('Full path: ' + full_path)
        return self.packages[package_name]

    @property
    def loaded_packages(self):
        return [package for package in self.packages if package.loaded]
        return self._loaded_packages

    def load_package(self, package_meta, ignore_rotten_modules=False,
                           load_classes=True, load_subpackages=True,
                           load_package_filter=None, raise_when_already_loaded=False):
        self.debug('Load package <{package}>...'.format(package=repr(package_meta)))

        if package_meta.loaded:
            if raise_when_already_loaded:
                raise Exception(f'Package <{str(package_meta)}> is already loaded!')
            return package_meta

        modules, subdirs = self.inspect_directory(package_meta)
        self.debug(f'..is package (contains __init__.py): {package_meta.has_init}')

        if load_package_filter is None:
            load_package_filter = self._load_package_filter
        if not load_package_filter(package_meta):
            self.debug(f'Package {str(package_meta)} did not pass loading filter')
            print(f'Package {str(package_meta)} did not pass loading filter')
            package_meta.status = 'excluded by filter'
            return package_meta

        self.register_and_load_modules(
            package_meta=package_meta,
            modules=modules,
            ignore_rotten_modules=ignore_rotten_modules,
            load_classes=load_classes)

        package_meta.status = 'loaded'
        package_meta.loaded = True

        if not load_subpackages:
            return package_meta

        self.register_and_load_subpackages(
            package_meta=package_meta,
            subdirs=subdirs,
            ignore_rotten_modules=ignore_rotten_modules,
            load_classes=load_classes)

        return package_meta

    def register_and_load_modules(self, package_meta, modules, load_classes=True, ignore_rotten_modules=False):
        for module in modules:
            module_meta = self.register_module(package_meta, module_name=module)
            try:
                self.load_module(package=package_meta, module_name=module, load_classes=load_classes)
            except ModuleRottenException:
                if not ignore_rotten_modules:
                    raise

    def register_and_load_subpackages(self, package_meta, subdirs, ignore_rotten_modules=False, load_classes=True):
        for dir in subdirs:
            self.debug('Inspecting subdir {} ..'.format(dir))
            relative_dir_path = os.path.join(package_meta.relative_path, dir)
            subpackage_meta = self.register_package(relative_dir_path)
            if subpackage_meta.status == 'excluded by filter':
                continue
            subpackage_meta = self.load_package(subpackage_meta,
                ignore_rotten_modules=ignore_rotten_modules,
                load_classes=load_classes,
                load_subpackages=True)
            if subpackage_meta.has_init:
                self.debug('Add subpackage {} to package {}'.format(subpackage_meta.name, package_meta.name))
                package_meta.add_subpackage(subpackage_meta)

    def find_subpackage(self, name):
        return None

    def apply_init_kwargs_hook(self, init_kwargs, config_cls=None):
        if config_cls is not None:
            init_kwargs_methods = config_cls.get_hook_methods(IConfig.HOOK_INIT_KWARGS)
            for method in init_kwargs_methods:
                init_kwargs = method(init_kwargs or {})
        return init_kwargs

    def create_instance(self, class_meta, params=None, add_object=True):
        # todo: replace params by **params
        self.debug(f'\nCreate_instance of class <{class_meta.class_name}>')
        config_cls = self.get_class_config(class_meta=class_meta)

        if params is None:
            params = {}
        init_args = params.get('init_args', None)
        init_kwargs = params.get('init_kwargs', None)

        init_kwargs = self.apply_init_kwargs_hook(init_kwargs, config_cls=config_cls)

        instance = class_meta(*(init_args or []), **(init_kwargs or {}))

        if config_cls is not None:
            self.debug(f'config class: {config_cls.__name__}')
            self.config_instance(instance=instance, cls=class_meta.class_reference, config_cls=config_cls, params=params)

        if add_object:
            class_meta.add_instance(instance)

        return instance

    def get_object(self, class_name_or_meta, package_name=None, module_name=None,
                    create_instance_when_not_found=True, params=None):
        # todo: refine searching criteria
        print('get_object:', class_name_or_meta)

        if isinstance(class_name_or_meta, ClassMeta):
            class_meta = class_name_or_meta
        else:
            class_meta = self.find_class_meta_by_name(class_name, package_name=package_name, module_name=module_name)
        try:
            return class_meta.get_first_instance()
        except IndexError:
            if create_instance_when_not_found:
                return self.create_instance(class_meta, params=params, add_object=True)
            else:
                raise ObjectNotFoundError(f'No object of class <{str(class_meta)}> stored!')

    def get_class_config(self, class_meta):
        class_name = class_meta.class_name
        return self.config_registry.get_config(class_name, profile_name=self.active_profile)

    @property
    def config_registry(self):
        """Returns singleton ConfigRegistry() which handles association of
        classes and config class"""
        return ConfigRegistry()

    def load_orm_packages(self):
        for package in ('sql', 'db', 'orm'):
            self.register_and_load_package(package)