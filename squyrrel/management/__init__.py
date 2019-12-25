
from .commands import AwakeSquyrrel, LoadPackage


commands = {
    'awake': AwakeSquyrrel,
    'load_package': LoadPackage,
}


class SquyrrelCommandManager:

    def __init__(self, argv=None, base_path=None):
        self.argv = argv or sys.argv[:]
        self.base_path = base_path

    def fetch_command(self, subcommand):
        cmd_cls = commands.get(subcommand, None)
        if cmd_cls is None:
            # raise Exception('Did not find subcommand <{}>'.format(subcommand))
            return None
        return cmd_cls()

    def execute(self):
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'

        if subcommand == 'help':
            print('help..')
        else:
            command = self.fetch_command(subcommand)
            if command is None:
                print('Did not find command <{}>'.format(subcommand))
            else:
                command.run_from_argv(self.argv, base_path=self.base_path)


def execute_from_command_line(argv=None, base_path=None):
    cmd_mgr = SquyrrelCommandManager(argv=argv, base_path=base_path)
    cmd_mgr.execute()