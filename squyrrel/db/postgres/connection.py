import psycopg2

from squyrrel.db.connection import SqlDatabaseConnection


class PostgresConnection(SqlDatabaseConnection):

    database_error_cls = psycopg2.Error

    def connect(self, user, password, database, host="127.0.0.1", port=5432, select_version=False, **kwargs):

        if isinstance(port, int):
            port = str(port)

        self.c = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=database)
        # Print PostgreSQL Connection properties
        # print (self.c.get_dsn_parameters(),"\n")

        if select_version:
            # Print PostgreSQL version
            self.execute("SELECT version();")
            record = self.fetchone()
            print("You are connected to - ", record,"\n")
