
class SqlDatabaseConnection:

    database_error_cls = None
    integrity_error_cls = None

    def __init__(self):
        self.c = None
        self._cursor = None

    def create_cursor(self, *args, **kwargs):
        self._cursor = self.c.cursor(*args, **kwargs)
        return self._cursor

    def close_cursor(self):
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None

    def connect(self, **kwargs):
        raise NotImplementedError

    def close_connection(self):
        if self.c:
            self.c.close()

    def close(self):
        self.close_cursor()
        self.close_connection()

    def execute(self, sql, cursor=None, params=None):
        if cursor is not None:
            self._cursor = cursor
        else:
            self.create_cursor()
        if params is not None:
            self._cursor.execute(sql, params)
        else:
            self._cursor.execute(sql)

    def commit(self):
        self.c.commit()

    def rollback(self):
        self.c.rollback()

    def fetchall(self):
        if self._cursor is None:
            raise Exception('Cursor is None')
        data = self._cursor.fetchall()
        return data

    def fetchone(self):
        if self._cursor is None:
            raise Exception('Cursor is None')
        data = self._cursor.fetchone()
        return data
