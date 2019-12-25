import os.path


def convert_path_to_import_string(path):
    """Replaces all occurencies of '/' by '.'"""
    contains_slashes = False
    path = path.replace('\\\\', '/')
    path = path.replace('\\', '/')
    if not '/' in path:
        return path

    folders = path.strip().split('/')
    num_parents = 0
    if not folders[-1]:
        folders.pop(-1)
    for i, folder in enumerate(folders):
        if folder == '..':
            num_parents += 1
    if folders[0] == '.':
        relative_path = True
    else:
        relative_path = False
    folders_ = []
    for folder in folders:
        if not folder.startswith('.'):
            folders_.append(folder)

    if num_parents:
        base_path = '.'.join([(num_parents)*'.', '.'.join(folders_)])
    else:
        base_path = '.'.join(folders_)
    if relative_path and num_parents == 0:
        return '.' + base_path
    return base_path

def find_first_parent(path, parent):
    last_base = None
    base, tail = os.path.split(path)
    while (base != last_base):
        if tail == parent:
            return os.path.join(base, tail)
        last_base = base
        base, tail = os.path.split(base)
    return None