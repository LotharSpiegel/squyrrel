from squyrrel.db.connection import SqlDatabaseConnection


class DummyConnection(SqlDatabaseConnection):

    def connect(self):
        print('DummyConnection: connect')
