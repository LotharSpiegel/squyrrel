import importlib
import inspect
import os
import sys

from squyrrel.core.registry.exceptions import *
from squyrrel.core.registry.meta import PackageMeta
from squyrrel.core.utils.singleton import Singleton
from squyrrel.core.utils.paths import convert_path_to_import_string


class Squyrrel(metaclass=Singleton):

    def __init__(self, root_path=None):
        self.packages = {}
        self.root_path = root_path
        self.paths = []
        self.add_absolute_path(self.root_path)

    @property
    def num_registered_packages(self):
        return len(self.packages)

    def add_absolute_path(self, absolute_path):
        if absolute_path is None:
            return None
        if not absolute_path in self.paths:
            print('adding path ', absolute_path)
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
        print('register package <{relative_path}>..'.format(relative_path=relative_path))
        full_path = self.get_full_package_path(relative_path)
        if full_path is None:
            raise PackageNotFoundException('registering package with relative path <{relative_path}> failed'.format(
                relative_path=relative_path))
        package_name = os.path.basename(relative_path)
        self.packages[package_name] = PackageMeta(
            package_name=package_name,
            package_path=full_path,
            relative_path=relative_path,
            package_import_string=convert_path_to_import_string(relative_path),
            namespace=None)
        print('Successfully registered package {package_name}'.format(package_name=package_name))
        print('Full path: ', full_path)
        return self.packages[package_name]

    def find_package_by_name(self, name):
        # todo: return array
        for package_name, package_meta in self.packages.items():
            if name == package_name:
                return package_meta
        return None # todo raise exception

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
        print('register module <{module_name}>..'.format(module_name=module_name))
        if not package in self.packages.values():
            raise Exception('package <{package_name}> not registered yet'.format(
                package_name=package.name))
        return package.add_module(module_name=module_name)

    def load_module(self, package, module_name):
        print('load module <{module_name}>..'.format(module_name=module_name))
        module_registered = False

        module = package.find_registered_module(module_name)
        if module is None:
            raise ModuleNotRegisteredException('Error while loading module: Module {} not registered yet'.format(module_name))

        try:
            mod = importlib.import_module(module.import_string)
        except ModuleNotFoundError:
            module.status = 'not found'
            raise
        except Exception as exc:
            module.exception = exc
            print('module <{module_name}> is rotten: {exc}'.format(module_name=module_name, exc=str(exc)))
            raise ModuleRottenException from exc

        module.loaded = True
        return mod

    def load_module_classes(self, module_meta, imported_module):
        print('load classes of module {module}..'.format(module=module_meta))
        mod_imp_str = module_meta.import_string
        classes = {m[0]: m[1] for m in sorted(
            inspect.getmembers(imported_module,
                lambda member: inspect.isclass(member) and member.__module__ == mod_imp_str))}
        for class_name, class_reference in classes.items():
            module_meta.add_class(class_reference=class_reference,
                                  class_name=class_name)
        module_meta.classes_loaded = True
        print('loaded {num_classes} classes in module module {module}'.format(
            num_classes=module_meta.num_classes, module=module_meta))

    def find_class_meta_by_name(self, class_name, package_name=None):
        if package_name is None:
            packages = self.packages.values()
        else:
            package = find_package_by_name(package_name)
            if package is None:
                return None
            packages = [package]
        for package in packages:
            class_meta = package.find_class_meta_by_name(class_name)
            if class_meta is not None:
                return class_meta
        return None

    def load_package(self, package_meta, ignore_rotten_modules=True,
                           load_classes=True, load_subpackages=True):
        modules, sub_dirs = self.inspect_directory(package_meta)
        print('load_package <{package}>...'.format(package=repr(package_meta)))
        print('is package (contains __init__.py):', package_meta.has_init)
        for module in modules:
            module_meta = self.register_module(package_meta, module_name=module)
            try:
                imported_module = self.load_module(package_meta, module_name=module)
            except ModuleRottenException:
                if not ignore_rotten_modules:
                    raise
            if load_classes:
                self.load_module_classes(module_meta=module_meta, imported_module=imported_module)

        #if is_package:
        if not load_subpackages:
            return
        for dir in sub_dirs:
            print('inspecting subdir {} ..'.format(dir))
            relative_dir_path = os.path.join(package_meta.relative_path, dir)
            subpackage_meta = self.register_package(relative_dir_path)
            subpackage_meta = self.load_package(subpackage_meta,
                ignore_rotten_modules=ignore_rotten_modules,
                load_classes=load_classes,
                load_subpackages=load_subpackages)
            if subpackage_meta.has_init:
                print('add subpackage {} to package {}'.format(package_meta.name, subpackage_meta.name))
                package_meta.add_subpackage(subpackage_meta)

        return package_meta

    def find_subpackage(self, name):
        return None