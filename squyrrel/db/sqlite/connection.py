import sqlite3

from squyrrel.db.connection import SqlDatabaseConnection


class SqliteConnection(SqlDatabaseConnection):

    def connect(self, filename, select_version=False):
        self.filename = filename

        self.c = sqlite3.connect(self.filename)
        if select_version:
            self.execute('SELECT sqlite_version()')
