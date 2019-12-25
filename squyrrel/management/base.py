from argparse import ArgumentParser, HelpFormatter
import os
import sys


class CommandError(Exception):
    pass


class CommandParser(ArgumentParser):
    pass


class BaseCommand:

    help = ''

    def __init__(self, stdout=None, stderr=None):
        pass

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = CommandParser(
            prefix_chars='-',
            prog='{} {}'.format(os.path.basename(prog_name), subcommand),
            description=self.help or None,
            # formatter_class=
            #missing_args_message=
            #called_from_command_line=
            **kwargs)

        parser.add_argument('--traceback',
            action='store_true',
            help='Raise on CommandError exceptions')
        self.add_arguments(parser) # possibility for subclasses to add arguments
        return parser

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def run_from_argv(self, argv, base_path=None):
        self._called_from_command_line = True
        parser = self.create_parser(prog_name=argv[0], subcommand=argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        cmd_options['base_path'] = base_path

        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise
            if isinstance(e, CommandError):
                print(str(e)) # --> Logging

            sys.exit(1)
        finally:
            # try:
            #     connections.close_all()
            # except ImproperlyConfigured:
            #     pass
            pass

    def execute(self, *args, **options):
        output = self.handle(*args, **options)
        # if output:
        #     self.stdout.write(output)
        return output

    def handle(self, *args, **options):
        raise NotImplementedError('A subclass of BaseCommand must provide a handle() method')
