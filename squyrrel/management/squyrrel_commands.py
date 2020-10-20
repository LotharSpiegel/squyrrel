import os

from .base import BaseCommand, CommandError



class SquyrrelCommand(BaseCommand):
    prefix = 's'

    __inject__ = {
        '_squyrrel': 'Squyrrel',
    }


class SquyrrelReloadCommand(SquyrrelCommand):
    name = 'reload'
    help = ("Reloads the squyrrel library")

    def handle(self, *args, **options):
        self._squyrrel.reload_squyrrel_package()


class SquyrrelHelpCommand(SquyrrelCommand):
    name = 'help'

    def handle(self, *args, **options):
        return 'SquyrrelHelpCommand executed!'


def cell_len(value):
    return len(value) if value is not None else 0


class SquyrrelListPackagesCommand(SquyrrelCommand):
    """ Todo:cut off to long entries in cell with .."""

    name = 'lp'
    help = ("List all packages (registered, loaded) by squyrrel")

    @property
    def column_lengths(self):
        return (30, 10, 10)

    @property
    def column_headers(self):
        return ('Name', 'Status', '# Modules')

    def column_spaces(self, entries):
        return [length - cell_len(entry) for entry, length in zip(entries, self.column_lengths)]

    def row(self, entries, sep=''):
        return sep.join(['{entry}{space}'.format(
            entry=entry, space=space*' ') for entry, space in zip(entries, self.column_spaces(entries))])

    def table_header(self):
        header_row = self.row(self.column_headers, sep='|')
        header_separation = '-'*len(header_row)
        return f'{header_row}\n{header_separation}\n'

    def table_body(self, packages):
        return '\n'.join([self.row((package.name, package.status, str(package.num_modules))) for package in packages])

    def packages_to_table(self, packages):
        return f'\n{self.table_header()}\n{self.table_body(packages)}'

    def handle(self, *args, **options):
        packages = self._squyrrel.packages.values()
        return self.packages_to_table(packages)


class SquyrrelReportCommand(SquyrrelCommand):
    name = 'report'

    def handle(self, *args, **options):
        return self._squyrrel.last_report


class SquyrrelLoadPackageCommand(SquyrrelCommand):
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
        # TODO: reconfig squyrrel...
        #self.squyrrel = Squyrrel(root_path, config_path=options.get('config', None))

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
