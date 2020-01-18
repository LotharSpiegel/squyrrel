


class SqlDatabaseConnection:

    def __init__(self):
        self.c = None
        self._cursor = None

    def cursor(self, *args, **kwargs):
        self._cursor = self.c.cursor(*args, **kwargs)
        return self._cursor

    def connect(self, **kwargs):
        raise NotImplementedError

    def execute(self, sql, cursor=None, params=None):
        cursor = cursor or self.cursor()
        if params is not None:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

