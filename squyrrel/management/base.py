"""
- add arg (optional) info to BaseCommand
- if help is None: generate help out of prefix, name and arguments
"""


from argparse import ArgumentParser, HelpFormatter
import os
import sys

from .constants import __NO_PREFIX__
from .exceptions import *


class CommandParser(ArgumentParser):
    pass


class BaseCommand:

    help = ''
    name = None
    prefix = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def command_prefix(cls):
        return getattr(cls, 'prefix', None)

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

    def execute_from_argv(self, prog_name, argv):
        print('execute_from_argv')
        print('argv=', argv)
        parser = self.create_parser(prog_name, command_name=str(self))
        args, cmd_options = self.parse_command_args(parser, argv)
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

    def execute(self, *args, **options):
        return self.handle(*args, **options)

    def handle(self, *args, **options):
        raise NotImplementedError('A subclass of BaseCommand must provide a handle() method')

    @staticmethod
    def _cmd_info(obj):
        if obj.prefix is None or obj.prefix == __NO_PREFIX__:
            cmd_name = obj.name
        else:
            cmd_name = f'{obj.prefix}.{obj.name}'
        if obj.help is None:
            return cmd_name
        return f'{cmd_name}: {obj.help}'

    @classmethod
    def cmd_info(cls):
        return BaseCommand._cmd_info(cls)

    def __str__(self):
        return BaseCommand._cmd_info(self)