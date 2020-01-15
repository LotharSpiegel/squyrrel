import os
import shutil

from .base import BaseCommand, CommandError
# from squyrrel.core.registry.nutcracker import Squyrrel


# class AwakeSquyrrel(BaseCommand):
#     help = (
#         "Awakes squyrrel"
#     )

#     def handle(self, **options):
#         print('Awaking squyrrel..')
#         return Squyrrel()

class HelpCmd(BaseCommand):

    name = 'help'

    def handle(self, *args, **options):

        # squyrrel = options['squyrrel']
        cmd_mgr = options['_cmd_mgr']
        command_infos = []
        for key in sorted(cmd_mgr.commands):
            cmd = cmd_mgr.commands[key]
            if cmd.help:
                command_infos.append(f'{key}: {cmd.help}')
            else:
                command_infos.append(key)
        commands_info = '\n'.join(command_infos)
        return f"""
-- Squyrrel Command Line Interface --

Available commands:
{commands_info}
"""


class ClassInfoCmd(BaseCommand):

    name = 'class-info'

    help = (
        "class-info [class name] -m [module]"
    )

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the class')
        #parser.add_argument('-n', '--name', help='Name of the class')
        # parser.add_argument('-m', '--module', help='Module name', default=None)

    def handle(self, *args, **options):
        class_name = options.get('name')# or args[0]
        module_name = options.get('module', None)
        squyrrel = options.get('_squyrrel')
        class_meta = squyrrel.find_class_meta_by_name(class_name=class_name, package_name=None, module_name=None)
        output = f'{str(class_meta.class_name)}'
        return output


class ListPackagesCmd(BaseCommand):
    name = 'lp'
    help = ("lp: List all packages (registered, loaded")

    @property
    def column_lengths(self):
        return (30, 10, 10)

    @property
    def column_headers(self):
        return ('Name', 'Status', '# Modules')

    def column_spaces(self, entries):
        return [length - len(entry) for entry, length in zip(entries, self.column_lengths())]

    def row(self, entries):
        return '|'.join(['{entry}{space}'.format(
            entry=entry, space=space*' ') for entry, space in zip(entries, self.column_spaces(entries))])

    def table_header(self):
        return self.row(self.column_headers)

    def table_body(self, packages):
        return '\n'.join([self.row((package.name, package.status, str(package.num_modules))) for package in packages])

    def packages_to_table(self, packages):
        return f"""
Packages:
{self.table_header()}
{self.table_body(packages)}
"""

    def handle(self, *args, **options):
        squyrrel = options.get('_squyrrel')
        packages = squyrrel.packages
        return self.packages_to_table(packages)


class LoadPackageCmd(BaseCommand):
    name = 'load-package'

    help = (
        "load-package [package name] -r [root_path] -p [path]"
    )

    def add_arguments(self, parser):
        parser.add_argument('name', help='Name of the package')
        parser.add_argument('-r', '--root_path', help='Root path', default=os.getcwd())
        parser.add_argument('-p', '--path', help='Optional paths (relative to root_path) to be added to sys.path', nargs='*')
        parser.add_argument('-c', '--config', help='Config file')

    def handle(self, *args, **options):
        package_name = options.get('name')
        path = options.get('path', None)
        root_path = options.get('root_path')
        self.squyrrel = Squyrrel(root_path, config_path=options.get('config', None))

        if path is not None:
            for p in path:
                self.squyrrel.add_relative_path(p)

        package_meta = self.squyrrel.register_package(package_name)

        self.squyrrel.load_package(package_meta,
            ignore_rotten_modules=True,
            load_classes=True, load_subpackages=True)
        self.report()

    def report(self):
        print('finished')
        # self.squyrrel