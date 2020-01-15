import sys
import traceback

from .commands import HelpCmd, LoadPackageCmd
from squyrrel.core.registry.signals import command_loaded_signal, squyrrel_debug_signal


class CommandManager:

    def __init__(self, base_path=None):
        self.base_path = base_path
        self.commands = {}
        #self.add_basic_commands()
        command_loaded_signal.connect(self.on_command_loaded)

    def on_command_loaded(self, *args, **kwargs):
        new_cmd_class_meta = cls_meta = kwargs.get('class_meta') or args[0]
        new_cmd_class = new_cmd_class_meta.class_reference
        name = new_cmd_class.command_name()
        self.add_command(key=name, cmd=new_cmd_class)

    def add_command(self, key, cmd):
        if key in self.commands.keys():
            raise Exception(f'There is already a command on key <{key}>')
        self.commands[key] = cmd

    # def add_basic_commands(self):
    #     self.add_command('help', HelpCmd)
    #     self.add_command('load-package', LoadPackageCmd)

    def fetch_command(self, command_key):
        cmd_cls = self.commands.get(command_key, None)
        if cmd_cls is None:
            raise Exception('Did not find command <{}>'.format(command_key))
        return cmd_cls()

    def execute(self, command_key, *args, **kwargs):
        command = self.fetch_command(command_key)
        return command.execute(*args, **kwargs)

    def execute_from_input(self, prog_name, user_input, squyrrel=None):
        argv = user_input.split()
        command_key = argv[0]
        command = self.fetch_command(command_key)
        add_kwargs = {
            '_cmd_mgr': self,
            '_squyrrel': squyrrel
        }
        try:
            return command.execute_from_argv(prog_name, command_key, argv[1:], **add_kwargs)
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