import sys
import traceback

from .constants import __NO_PREFIX__
from .exceptions import *
from squyrrel.core.registry.signals import command_loaded_signal, squyrrel_debug_signal



class CommandManager:

    def __init__(self, base_path=None):
        self.base_path = base_path
        self.commands = {}
        #self.add_basic_commands()
        command_loaded_signal.connect(self.on_command_loaded)

    def on_command_loaded(self, *args, **kwargs):
        new_cmd_class_meta = kwargs.get('class_meta') or args[0]
        new_cmd_class = new_cmd_class_meta.class_reference
        self.register_command(
            cmd_cls_meta=new_cmd_class_meta,
            name=new_cmd_class.name,
            prefix=new_cmd_class.command_prefix())

    def register_command(self, cmd_cls_meta, name, prefix=None):
        if name is None:
            print(f'Warning: cmd {cmd_cls_meta.class_name} has name=None. Will not be registered.')
            return
        key = self.convert_prefix_and_name_to_command_key(prefix=prefix, name=name)
        if key in self.commands.keys():
            raise Exception(f'There is already a command on key <{key}>')
        self.commands[key] = cmd_cls_meta

    def convert_prefix_and_name_to_command_key(self, prefix, name):
        return f'{prefix or __NO_PREFIX__}.{name}'

    def convert_command_key_to_prefix_and_name(self, command_key):
        if not '.' in command_key:
            return None, command_key
        try:
            prefix, name = command_key.split('.')
        except Exception as exc:
            raise exc
        return prefix, name

    def fetch_command(self, command_key, **kwargs):
        return self.get_command_class(command_key)(**kwargs)

    def get_command_class(self, command_key):
        prefix, name = self.convert_command_key_to_prefix_and_name(command_key)
        if prefix is None:
            prefix = __NO_PREFIX__
        command_key = self.convert_prefix_and_name_to_command_key(prefix=prefix, name=name)
        try:
            cmd_cls_meta = self.commands[command_key]
        except KeyError:
            raise CommandNotFoundException('Did not find command <{}>'.format(command_key))
        return cmd_cls_meta.class_reference

    # def execute(self, command_key, *args, **kwargs):
    #     command = self.fetch_command(command_key)
    #     return command.execute(*args, **kwargs)

    def execute_from_input(self, prog_name, user_input, **kwargs):
        """The entries in kwargs will be added as attributes to the instantiated command object"""
        user_inputs = user_input.split()
        command_key = user_inputs[0]
        argv = user_inputs[1:]
        command = self.fetch_command(command_key, **kwargs)
        try:
            return command.execute_from_argv(prog_name, command_key, argv)
        except Exception as exc:
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            squyrrel_debug_signal.emit(f'Error on executing command <{command_key}>', tags='error')
            # stacktrace...
            trace = traceback.format_exc()
            # traceback.format_tb(exc_traceback
            squyrrel_debug_signal.emit(trace, tags='error')
            raise exc

    def execute_from_command_line(self, argv=None):
        argv = argv or sys.argv[:]
        # print('running from command line with argv = ', argv)
        try:
            command_key = argv[1]
        except IndexError:
            command_key = 'help'
        command = self.fetch_command(command_key)
        return command.run_from_argv(argv, base_path=self.base_path)