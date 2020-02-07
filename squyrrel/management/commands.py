import inspect
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

class HelpCommand(BaseCommand):
    name = 'help'

    __inject__ = {
        '_cmd_mgr': 'CommandManager',
    }

    def handle(self, *args, **options):
        command_infos = []
        for key in sorted(self._cmd_mgr.commands):
            cmd = self._cmd_mgr.get_command_class(key)
            command_infos.append(cmd.cmd_info())
        commands_info = '\n'.join(command_infos)
        return f"""
-- Squyrrel Command Line Interface --

Available commands:
{commands_info}
"""


class SourceCodeCommand(BaseCommand):
    name = 'source-code'

    __inject__ = {
        '_squyrrel': 'Squyrrel',
    }

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the class or method or module')

    def handle(self, *args, **options):
        name = options.get('name')
        class_meta = self._squyrrel.find_class_meta_by_name(class_name=name, package_name=None, module_name=None)
        return '\n' + inspect.getsource(class_meta.class_reference)


class ClassInfoCommand(BaseCommand):
    name = 'class-info'

    help = ("class-info [class name] -m [module]")

    __inject__ = {
        '_squyrrel': 'Squyrrel',
    }


    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the class')
        # todo: add arg module
        #parser.add_argument('-n', '--name', help='Name of the class')
        # parser.add_argument('-m', '--module', help='Module name', default=None)

    def handle(self, *args, **options):
        class_name = options.get('name')# or args[0]
        module_name = options.get('module', None)
        class_meta = self._squyrrel.find_class_meta_by_name(class_name=class_name, package_name=None, module_name=None)
        return f'{str(class_meta.class_name)}'
