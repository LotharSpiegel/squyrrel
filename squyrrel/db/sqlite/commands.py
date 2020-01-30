from squyrrel.management.base import BaseCommand


class SqliteCommand(BaseCommand):
    prefix = 'sqlite'


class SqliteConnectCommand(SqliteCommand):
    name = 'connect'

    def add_arguments(self, parser):
        parser.add_argument('file', help='Path of the db file')

    def handle(self, *args, **options):
        return 'test successful'