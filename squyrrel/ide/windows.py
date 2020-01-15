

def window_factory(squyrrel, package_name, window_cls_name, module_name, parent=None, init_kwargs=None, config_kwargs=None):
    package = squyrrel.get_package(package_name)
    window_cls_meta = package.find_class_meta_by_name(window_cls_name, module_name)
    params = {
        'init_args': [parent],
        'init_kwargs': init_kwargs,
        # 'after_init_args': [parent],
        'after_init_kwargs': config_kwargs,
    }
    return squyrrel.create_instance(window_cls_meta, params)

def cmd_window_factory(squyrrel, parent, window_title):
    return window_factory(squyrrel,
            package_name='ide',
            window_cls_name='ShellWindow',
            module_name='shell_window',
            parent=parent,
            config_kwargs={'window_title': window_title})

def log_window_factory(squyrrel, parent, window_title):
    return window_factory(squyrrel,
            package_name='ide',
            window_cls_name='LogWindow',
            module_name='log_window',
            parent=parent,
            config_kwargs={'window_title': window_title})