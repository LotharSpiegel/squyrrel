from squyrrel.core.registry.exceptions import *
from squyrrel.core.context import Context


class PackageMeta:

    def __init__(self,
                package_name,
                package_path,
                relative_path,
                package_import_string,
                namespace):
        self.name = package_name
        self.path = package_path
        self.relative_path = relative_path
        self.import_string = package_import_string
        self.namespace = namespace

        self.modules = {}
        self.dependencies = []
        self.failed_dependencies = []
        self.subpackages = []
        self.parent = None
        self.has_init = False
        self.registered = False
        self.loaded = False
        self.status = None

    def add_module(self, module_name, status='registered'):
        # TODO: there can be different modules with same name inside a package
        # (in different subpackages)
        new_module = ModuleMeta(package=self, module_name=module_name)
        new_module.status = status
        self.modules[module_name] = new_module
        return new_module

    def find_module(self, module_name, status=None):
        """ Goes through all loaded modules and compares their name with `module_name` """
        # todo handle case when there is more than one module with the same name
        # todo: add options

        for module_name_, module_meta in self.modules.items():
            if module_name_ == module_name:
                if status is None:
                    return module_meta
                if module_meta.status == status:
                    return module_meta
                else:
                    if status == 'registered':
                        raise ModuleNotRegisteredException(f'Found module with name <{module_name}>, but its status is `{module_meta.status}`, not `{status}`!')
        raise ModuleNotFoundException(f'Did not find module with name <{module_name}>')

    def add_subpackage(self, package_meta):
        self.subpackages.append(package_meta)
        package_meta.parent = self

    def find_subpackage(self, package_name):
        for subpackage in self.subpackages:
            if subpackage.name == package_name:
                return subpackage
        sub_packages = ', '.join([sub_package.name for sub_package in self.subpackages])
        msg = f'Did not find subpackage with name <{package_name}>! Subpackages: {sub_packages}'
        raise PackageNotFoundException(msg)

    @property
    def num_modules(self):
        return len(self.modules)

    def find_class_meta_by_name(self, class_name, module_name=None, module_meta=None, module_status=None, raise_not_found=True):
        if module_status is None: module_status = 'loaded'
        if module_meta is None:
            if module_name is None:
                modules = self.modules.values()
            else:
                modules = [self.find_module(module_name=module_name, status=module_status)]
        else:
            modules = [module_meta]

        for module_meta in modules:
            class_meta = module_meta[class_name]
            if class_meta is not None:
                return class_meta
        if raise_not_found:
            raise ClassNotFoundException(f'Did not find class with name <{class_name}>!')
        else:
            return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'PackageMeta(package_name={name}, package_path={path}, relative_path={rel_path}, import_string={import_string})'.format(
            name=self.name, path=self.path, rel_path=self.relative_path, import_string=self.import_string)

    def __getitem__(self, module_name):
        return self.modules.get(module_name, None)

    def __eq__(self, other):
        if not isinstance(other, PackageMeta):
            return False
        return other.name == self.name and other.path == self.path


class ModuleMeta:

    def __init__(self, package, module_name):
        # instead of package_name, reference to package?
        self.package = package
        self.name = module_name
        self.loaded = False
        self.exception = None
        self.status = None
        self.classes = {}
        self.classes_loaded = False

    def add_class(self, class_reference, class_name=None):
        #todo: check if class_reference already existing
        # if so, raise ClassAlreadyAddedException!
        if class_name is None:
            class_name = class_reference.__name__
        new_class = ClassMeta(module=self,
                              class_name=class_name,
                              class_reference=class_reference)
        self.classes[class_reference.__name__] = new_class
        return new_class

    def find_class_by_reference(self, class_reference):
        raise NotImplementedError

    @property
    def num_classes(self):
        return len(self.classes)

    @property
    def import_string(self):
        return '{package_import_string}.{module_name}'.format(
            package_import_string=self.package.import_string, module_name=self.name)

    def __repr__(self):
        return f'ModuleMeta(package={self.package}, module_name={self.name})'

    def __str__(self):
        return self.import_string
        #return '{package_import_string}.{module_name}'.format(
        #    package_name=self.package.import_string, module_name=self.name)

    def __getitem__(self, class_name):
        return self.classes.get(class_name, None)

    def __eq__(self, other):
        if not isinstance(other, ModuleMeta):
            return False
        return other.package_name == self.package_name \
            and other.module_name == self.module_name


class ClassMeta:

    def __init__(self,
                module,
                class_name,
                class_reference):
        self.module = module
        self.class_name = class_name
        self.class_reference = class_reference
        self.instances = []

    def get_all_bases(self):
        return self.class_reference.__bases__

    @staticmethod
    def get_all_ancestors(cls, bases=None):
        bases = bases or []
        bases.append(cls)
        for cls in cls.__bases__:
            ClassMeta.get_all_ancestors(cls, bases)
        return tuple(bases)

    def has_ancestor(self, cls):
        """Returns True if self.class_reference has cls as ancestor or equals cls"""
        return cls in ClassMeta.get_all_ancestors(self.class_reference)

    def add_instance(self, instance):
        self.instances.append(instance)

    def remove_instance(self, instance):
        self.instances.remove(instance)

    def delete_instance(self, instance):
        # todo: test!!
        del instance

    def get_first_instance(self):
        return self.instances[0]

    def __str__(self):
        return '{module_str}.{class_name}'.format(
                module_str=str(self.module), class_name=self.class_name)

    def __call__(self, *args, **kwargs):
        return self.class_reference(*args, **kwargs)


class PythonContext(Context):

    def build(self, squyrrel):
        for package_name, package_meta in squyrrel.packages.items():
            self.add(package_name, package_meta)
        return self
