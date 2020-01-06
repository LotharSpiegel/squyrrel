

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
        self.loaded = False

    def add_module(self, module_name):
        # TODO: there can be different modules with same name inside a package
        # (in different subpackages)
        new_module = ModuleMeta(package=self, module_name=module_name)
        new_module.status = 'registered'
        self.modules[module_name] = new_module
        return new_module

    def find_module(self, module_name, status=None):
        # todo handle case when there is more than one module with the same name
        if status is None:
            status = 'registered'
        for module_name_, module_meta in self.modules.items():
            if module_name_ == module_name:
                if module_meta.status == status:
                    return module_meta
                else:
                    raise Exception(f'Found module with name <{module_name}>, but its status is `{module_meta.status}`, not `{status}`!')
        raise Exception(f'Did not find module with name <{module_name}>')

    def add_subpackage(self, package_meta):
        self.subpackages.append(package_meta)
        package_meta.parent = self

    def find_subpackage(self, package_name):
        for subpackage in self.subpackages:
            if subpackage.name == package_name:
                return subpackage
        raise Exception(f'Did not find subpackage with name <{package_name}>!')

    @property
    def num_modules(self):
        return len(self.modules)

    def find_class_meta_by_name(self, class_name, module_name=None, module_status=None):
        module_meta = None
        if module_status is None: module_status = 'loaded'
        if module_name is not None:
            module_meta = self.find_module(module_name, status=module_status)
        if module_meta is None:
            for module_meta in self.modules.values():
                class_meta = module_meta[class_name]
                if class_meta is not None:
                    return class_meta
        else:
            class_meta = module_meta[class_name]
            if class_meta is not None:
                return class_meta
        raise Exception(f'Did not find class with name <{class_name}>!')

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
        return '{module_str}.{class_name}'.format(
                module_str=str(self.module), class_name=self.class_name)

    def __call__(self, *args, **kwargs):
        return self.class_reference(*args, **kwargs)
