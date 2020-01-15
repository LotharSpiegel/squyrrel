import pytest
from pprint import pprint
import os.path
import sys

from squyrrel import Squyrrel
from squyrrel.core.utils.paths import find_first_parent
from squyrrel.core.registry.exceptions import *
from squyrrel.core.config.base import IConfigRegistry


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
        num_registered_packages = self.squyrrel.num_registered_packages
        package_meta = self.squyrrel.register_package(relative_path='test_package')

        assert self.squyrrel.num_registered_packages == num_registered_packages + 1
        assert package_meta.name == 'test_package'
        assert package_meta.import_string == 'test_package'
        print('import string:', package_meta.import_string)

    def test_find_package_by_name(self):
        self.squyrrel.register_package(relative_path='test_package')
        package_meta = self.squyrrel.find_package_by_name('test_package')

        assert package_meta is not None
        assert package_meta.name == 'test_package'

    def test_find_package_by_name_when_not_existing_raises_exception(self):
        with pytest.raises(PackageNotFoundException):
            self.squyrrel.find_package_by_name('not_existing_package')

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
        package.add_module('not_registered_module', status='foo')

        with pytest.raises(ModuleNotRegisteredException):
            self.squyrrel.load_module(package, module_name='not_registered_module')

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
        self.squyrrel.load_module(package, 'module1', load_classes=False)
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

    def test_squyrrel_class_instance_factory_and_config(self):
        # todo: divide into several tests
        print('\n\tStart test_squyrrel_class_instance_factory_and_config')
        package = self.squyrrel.register_package(relative_path='test_package')
        package = self.squyrrel.load_package(package)

        sub_package = self.squyrrel.find_package_by_name('sub_package')
        module = sub_package.find_module('config_factory_module', status='loaded')
        A_meta = sub_package.find_class_meta_by_name('A', module_meta=module)
        X2_meta = sub_package.find_class_meta_by_name('X2', module_meta=module)
        Y2_meta = sub_package.find_class_meta_by_name('Y2', module_meta=module)

        A_config = self.squyrrel.get_class_config(class_meta=A_meta)
        assert A_config is not None

        instance = A_meta()
        self.squyrrel.config_instance(
            instance=instance,
            cls=A_meta.class_reference,
            config_cls=A_config
        )
        assert instance.test_property == 'config 2'

        assert A_meta.class_name == 'A'

        A_instance = A_meta()

        assert A_instance.quack() == 'x = X1, y = Y1'

        assert Y2_meta.class_name == 'Y2'
        X2_instance = X2_meta()
        Y2_instance = Y2_meta()
        A_instance = A_meta(x=X2_instance, y=Y2_instance)

        assert A_instance.quack() == 'x = X2, y = Y2'

        # now with squyrrel create_instance factory method

        A_instance = self.squyrrel.create_instance(A_meta)

        assert A_instance.quack() == 'x = X2, y = Y2'

        # AConfig2_meta = sub_package.find_class_meta_by_name('AConfig2', module)
        # assert AConfig2_meta is not None

        assert A_instance.test_property == 'config 2'

def main():
    root_path = find_first_parent(path=os.path.dirname(os.path.abspath(__file__)),
                                  parent='tests')
    squyrrel = Squyrrel(root_path=root_path)
    squyrrel.add_relative_path('../../../squyrrel')
    package_meta = squyrrel.register_package('test_package')
    squyrrel.load_package(package_meta)

if __name__ == '__main__':
    main()