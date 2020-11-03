from squyrrel.orm.wizzard import QueryWizzard
from squyrrel.sql.clauses import InsertClause, ValuesClause
from squyrrel.sql.query import BatchInsertQuery, InsertQuery, CreateManyToManyJunctionTableQuery


class MigrationManager:

    def __init__(self, qw: QueryWizzard):
        self.qw = qw
        self.queries = {}

    def add_query_key(self, key):
        if key in self.queries:
            raise ValueError(f'{key} already exists in query schema')
        self.queries[key] = list()

    def add_query(self, key, query):
        try:
            self.queries[key].append(query)
        except KeyError:
            raise KeyError(f'{key} does not exists in query schema')

    def add_queries(self, key, queries):
        try:
            self.queries[key].extend(queries)
        except KeyError:
            raise KeyError(f'{key} does not exists in query schema')

    def add_create_query(self, key, model, if_not_exists=False):
        self.add_query(key, query=self.qw.build_create_table_query(model, if_not_exists=if_not_exists))

    def write_queries_to_file(self, key, file):
        for query in self.queries[key]:
            file.write('\n' + repr(query) + '\n')

    def build_db_m2m_tables(self, key, models):
        junction_tables = []
        for model in models:
            for m2m_relation_name, m2m_relation in model.many_to_many_relations():
                junction_table_name = m2m_relation.junction_table.name
                if junction_table_name in junction_tables:
                    continue
                query = CreateManyToManyJunctionTableQuery(model1=model,
                                                           model2=self.qw.get_model(m2m_relation.foreign_model),
                                                           junction_table_name=m2m_relation.junction_table)
                junction_tables.append(junction_table_name)
                self.add_query(key, query)

    def build_db_schema(self, key, models, if_not_exists=False, build_m2m_junction_tables=True):
        self.add_query_key(key)
        for model in models:
            self.add_create_query(key, model, if_not_exists=if_not_exists)
        if build_m2m_junction_tables:
            self.build_db_m2m_tables(key, models=models)

    def add_insert(self, key, model, columns, values):
        insert_clause = InsertClause(model.table_name, columns)
        values_clause = ValuesClause(values)
        self.add_query(key, InsertQuery(model.table_name, insert_clause=insert_clause, values_clause=values_clause))

    def add_batch_inserts(self, key, table_name, columns, rows, rows_per_batch=500):
        insert_clause = InsertClause(table_name, columns)

        num_rows_total = len(rows)
        if num_rows_total < 1:
            return None
        if num_rows_total < rows_per_batch:
            rows_per_batch = num_rows_total

        chunks = [rows[x:x+rows_per_batch] for x in range(0, num_rows_total, rows_per_batch)]

        queries = [
            BatchInsertQuery(table_name, insert_clause=insert_clause, rows=chunk) for chunk in chunks
        ]
        self.add_queries(key, queries)
