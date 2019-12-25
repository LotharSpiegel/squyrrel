import os
import shutil

from .base import BaseCommand, CommandError
from squyrrel import Squyrrel


class AwakeSquyrrel(BaseCommand):
    help = (
        "Awakes squyrrel"
    )

    def handle(self, **options):
        print('Awaking squyrrel..')
        return Squyrrel()


class LoadPackage(BaseCommand):
    help = (
        "Load package"
    )

    def add_arguments(self, parser):
        parser.add_argument('name', help='Name of the package')
        parser.add_argument('-r', '--root_path', help='Root path', default=os.getcwd())
        parser.add_argument('-p', '--path', help='Optional paths (relative to root_path) to be added to sys.path', nargs='*')

    def handle(self, **options):
        package_name = options.get('name')
        path = options.get('path', None)
        root_path = options.get('root_path')
        self.squyrrel = Squyrrel(root_path)

        if path is not None:
            for p in path:
                self.squyrrel.add_relative_path(p)

        package_meta = self.squyrrel.register_package(package_name)
        self.squyrrel.load_package(package_meta)