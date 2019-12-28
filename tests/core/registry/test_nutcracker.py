import pytest
from pprint import pprint
import os.path
import sys

from squyrrel.core.registry.nutcracker import Squyrrel
from squyrrel.core.utils.paths import find_first_parent
from squyrrel.core.registry.exceptions import *


def test_nutcracker_is_singleton():
    squyrrel = Squyrrel()
    another_squyrrel = Squyrrel()

    assert id(squyrrel) == id(another_squyrrel)


class TestSquyrrel:

    def setup_method(self, method):
        Squyrrel.kill()
        root_path = find_first_parent(path=os.path.dirname(os.path.abspath(__file__)),
                                      parent='tests')
        self.squyrrel = Squyrrel(root_path=root_path)
        print('root_path: ', self.squyrrel.root_path)

    def test_nutcracker_init(self):
        assert self.squyrrel.num_registered_packages == 0

    def test_get_full_package_path(self):
        pprint(sys.path)
        full_path = self.squyrrel.get_full_package_path(relative_path='test_package')
        assert full_path is not None
        assert full_path.endswith('test_package')

    def test_get_full_package_path_add_path_before(self):
        print('root path: ', self.squyrrel.root_path)
        added = self.squyrrel.add_relative_path('../../../squyrrel')
        print('added path: ', added)
        full_path = self.squyrrel.get_full_package_path(relative_path='core')
        assert full_path is not None
        print('full_path: ', full_path)

    def test_register_package(self):
        package_meta = self.squyrrel.register_package(relative_path='test_package')

        assert self.squyrrel.num_registered_packages == 1
        assert package_meta.name == 'test_package'
        assert package_meta.import_string == 'test_package'
        print('import string:', package_meta.import_string)

    def test_find_package_by_name(self):
        self.squyrrel.register_package(relative_path='test_package')
        package_meta = self.squyrrel.find_package_by_name('test_package')

        assert package_meta is not None
        assert package_meta.name == 'test_package'

    def test_inspect_directory(self):
        package_meta = self.squyrrel.register_package(relative_path='test_package')
        assert package_meta is not None

        modules, sub_dirs = self.squyrrel.inspect_directory(package_meta)
        print('is package:', package_meta.has_init)
        print('Found modules:', modules)
        print('Found subdirs:', sub_dirs)

    def test_register_module(self):
        package = self.squyrrel.register_package(relative_path='test_package')
        module = self.squyrrel.register_module(package, 'module1')
        print('Registered:', module)
        assert package.num_modules == 1
        assert module.import_string == 'test_package.module1'

    # def test_load_module_not_found_raise_exception(self):
    #     package = self.squyrrel.register_package(relative_path='test_package')
    #     with pytest.raises(ModuleNotFoundException):
    #         self.squyrrel.load_module(package, module_name='non_existing_module')

    def test_load_module_not_registered_raise_exception(self):
        package = self.squyrrel.register_package(relative_path='test_package')
        with pytest.raises(ModuleNotRegisteredException):
            self.squyrrel.load_module(package, module_name='module1')

    def test_load_module_raise_module_not_found_error(self):
        package = self.squyrrel.register_package(relative_path='test_package')
        self.squyrrel.register_module(package, module_name='non_existing_module')
        with pytest.raises(ModuleNotFoundError):
            self.squyrrel.load_module(package, module_name='non_existing_module')

    def test_load_rotten_module_raise_error(self):
        package = self.squyrrel.register_package(relative_path='test_package')
        self.squyrrel.register_module(package, module_name='rotten_module')
        with pytest.raises(ModuleRottenException):
            self.squyrrel.load_module(package, module_name='rotten_module')

    def test_load_module(self):
        package = self.squyrrel.register_package(relative_path='test_package')
        self.squyrrel.register_module(package, 'module1')
        self.squyrrel.load_module(package, 'module1')
        assert package['module1'].loaded == True
        assert package['module1'].classes_loaded == False

    def test_load_classes(self):
        package = self.squyrrel.register_package(relative_path='test_package')
        self.squyrrel.register_module(package, 'module1')
        imported_module = self.squyrrel.load_module(package, 'module1')
        self.squyrrel.load_module_classes(package['module1'], imported_module=imported_module)
        assert package['module1'].classes_loaded == True
        assert package['module1'].num_classes == 2

        test_class1_meta = self.squyrrel.find_class_meta_by_name('TestClass1')
        assert test_class1_meta is not None
        test_class1_instance = test_class1_meta()
        assert test_class1_instance.test_attribute == 'set'

    def test_load_package(self):
        package = self.squyrrel.register_package(relative_path='test_package')
        package = self.squyrrel.load_package(package)

        assert len(package.subpackages) == 1
        assert package.find_subpackage('sub_package') is not None


def main():
    root_path = find_first_parent(path=os.path.dirname(os.path.abspath(__file__)),
                                  parent='tests')
    squyrrel = Squyrrel(root_path=root_path)
    squyrrel.add_relative_path('../../../squyrrel')
    package_meta = squyrrel.register_package('test_package')
    squyrrel.load_package(package_meta)

if __name__ == '__main__':
    main()