from squyrrel.management.base import BaseCommand


class PostgresCommand(BaseCommand):
    prefix = 'postgres'


class PostgresConnectCommand(PostgresCommand):
    name = 'connect'

    __inject__ = {
        '_connection': 'PostgresConnection',
    }

    def add_arguments(self, parser):
        parser.add_argument('user', help='Db user')
        parser.add_argument('pw', help='Db user Password')
        parser.add_argument('db', help='Postgres database name')
        parser.add_argument('host', help='Host', default='127.0.0.1')
        parser.add_argument('port', help='Port', default='5432')

    def handle(self, *args, **options):
        self._connection(user=options.get('user'),
                         pw=options.get('pw'),
                         db=options.get('db'),
                         host=options.get('host'),
                         port=options.get('port'))