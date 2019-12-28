import pytest

from squyrrel.core.registry.meta import PackageMeta, ModuleMeta


def build_package():
    return PackageMeta(
        package_name='test_package',
        package_path='a/b/c',
        relative_path='b/c',
        package_import_string='a.b.c',
        namespace=None)

def build_module():
    return ModuleMeta(
        package=build_package(),
        module_name='test_module')

def build_class(class_name='TestClass'):
    class TestClass:
        def a_method():
            return 'test'

    TestClass.__name__ = class_name
    return TestClass


def test_add_module_to_package():
    package = build_package()
    package.add_module(module_name='test_module')

    assert package.num_modules == 1
    module = package['test_module']
    assert module.name == 'test_module'
    assert module.package.name == 'test_package'
    assert module.import_string == '{}.test_module'.format(package.import_string)
    assert str(module) == '{}.test_module'.format(package.import_string)

def test_add_class_to_module():
    module = build_module()
    module.add_class(build_class('TestClass'))

    assert module.loaded == False
    assert module.num_classes == 1
    TestClassMeta = module['TestClass']
    assert TestClassMeta is not None
    assert TestClassMeta.class_name == 'TestClass'
    TestClass = TestClassMeta.class_reference
    assert TestClass is not None
    assert TestClass.__name__ == TestClassMeta.class_name

