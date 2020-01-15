from squyrrel import Squyrrel


def gui_factory(module_name, class_name, gui_package=None, subpackage=None,
            parent=None, init_kwargs=None, config_kwargs=None):
    squyrrel = Squyrrel()
    if gui_package is None:
        gui_package = squyrrel.get_package('gui')
    if subpackage is None:
        package_meta = gui_package
    else:
        package_meta = gui_package.find_subpackage(subpackage)
    class_meta = package_meta.find_class_meta_by_name(class_name, module_name)

    params = {
        'init_args': [parent],
        'init_kwargs': init_kwargs,
        # 'after_init_args': [parent],
        'after_init_kwargs': config_kwargs,
    }
    return squyrrel.create_instance(class_meta, params)