from squyrrel.sql.references import TableReference
from squyrrel.sql.join import JoinConstruct, JoinType


class TableName(TableReference):

    def __init__(self, name, schema_name=None, alias=None):
        self.name = name
        self.schema_name = schema_name
        self.alias = alias

    def join(self, join_type, table2, join_condition):
        return JoinConstruct(
            table1=self,
            join_type=JoinType.LEFT_OUTER_JOIN,
            table2=table2,
            join_condition=join_condition
        )

    @property
    def table_name(self):
        if self.schema_name is not None:
            return f'{str(self.schema_name)}.{str(self.name)}'
        return self.name

    def __repr__(self):
        if self.alias:
            return '{} AS {}'.format(self.table_name, self.alias)
        else:
            return str(self.table_name)

    @classmethod
    def build(cls, table_ref):
        if isinstance(table_ref, str):
            return cls(name=table_ref)
        else:
            return table_ref