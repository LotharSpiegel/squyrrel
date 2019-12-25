

class PackageMeta:

    def __init__(self,
                package_name,
                package_path,
                package_import_string,
                namespace):
        self.name = package_name
        self.path = package_path
        self.import_string = package_import_string
        self.namespace = namespace

        self.modules = {}
        self.dependencies = []
        self.failed_dependencies = []

    def add_module(self, module_name):
        # TODO: there can be different modules with same name inside a package
        # (in different subpackages)
        new_module = ModuleMeta(package=self, module_name=module_name)
        self.modules[module_name] = new_module
        return new_module

    def find_registered_module(self, module_name):
        for module_name_, module_meta in self.modules.items():
            if module_name_ == module_name:
                return module_meta
        return None

    @property
    def num_modules(self):
        return len(self.modules)

    def find_class_meta_by_name(self, class_name):
        for module in self.modules.values():
            class_meta = module[class_name]
            if class_meta is not None:
                return class_meta
        return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'PackageMeta(package_name={name}, package_path={path}, import_string={import_string})'.format(
            name=self.name, path=self.path, import_string=self.import_string)

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
        if class_name is None:
            class_name = class_reference.__name__
        new_class = ClassMeta(module=self,
                              class_name=class_name,
                              class_reference=class_reference)
        self.classes[class_reference.__name__] = new_class

    @property
    def num_classes(self):
        return len(self.classes)

    @property
    def import_string(self):
        return '{package_import_string}.{module_name}'.format(
            package_import_string=self.package.import_string, module_name=self.name)

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

    def __str__(self):
        return '{package_name}.{module_name}.{class_name}'.format(
                self.module.package.name, self.module.name, self.class_name)

    def __call__(self, *args, **kwargs):
        return self.class_reference(*args, **kwargs)
