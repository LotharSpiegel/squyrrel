from argparse import ArgumentParser, HelpFormatter
import os
import sys

from .exceptions import ArgumentParserException


class CommandError(Exception):
    pass


class CommandParser(ArgumentParser):
    pass


class BaseCommand:

    help = ''
    name = None

    def __init__(self, stdout=None, stderr=None):
        pass

    @classmethod
    def command_name(cls):
        return getattr(cls, 'name', cls.__name__)

    def create_parser(self, prog_name, command_name, **kwargs):
        parser = CommandParser(
            prefix_chars='-',
            prog='{} {}'.format(os.path.basename(prog_name), command_name),
            description=self.help or None,
            # formatter_class=
            #missing_args_message=
            #called_from_command_line=
            **kwargs)
        # parser.add_argument('--traceback',
        #     action='store_true',
        #     help='Raise on CommandError exceptions')
        self.add_arguments(parser) # possibility for subclasses to add arguments
        return parser

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def parse_command_args(self, parser, argv):
        try:
            options = parser.parse_args(argv)
            print('options:', options)
        except:
            raise ArgumentParserException(command=self)
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        # cmd_options['base_path'] = self.base_path
        print('args=',args)
        print('cmd_options=', cmd_options)
        return args, cmd_options

    def execute_from_argv(self, prog_name, command_name, argv, **kwargs):
        print('execute_from_argv')
        print('argv=', argv)
        parser = self.create_parser(prog_name, command_name=command_name)
        args, cmd_options = self.parse_command_args(parser, argv)
        cmd_options.update(kwargs)
        return self.execute(*args, **cmd_options)

    def run_from_argv(self, argv, base_path=None):
        self._called_from_command_line = True

        try:
            parser = self.create_parser(prog_name=argv[0], command_name=argv[1])
        except IndexError:
            raise Exception('Command missing')

        args, cmd_options = self.parse_command_args(parser, argv[2:])

        try:
            return self.execute(*args, **cmd_options)
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
