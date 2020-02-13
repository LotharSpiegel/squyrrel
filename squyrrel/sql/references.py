from enum import Enum


class ColumnReference:
    """
    Typically, a column reference looks like:
        table_name.column_name or even just
        column_name

    Note, that instead of the table_name, we can use an alias (defined in a from clause)
        t.column_name

    Further, the table_name can be qualified by a schema_name


    """

    def __init__(self, name, table=None, alias=None):
        """
        table can be simply a table name (table reference including schema name) or a Table object
        """
        self.name = name
        self.table = table
        self.alias = alias

    def table_name(self):
        if self.table is not None:
            return f'{str(self.table)}.{str(self.name)}'
        return self.name

    def __eq__(self, other):
        if isinstance(other, ColumnReference):
            return self.name == other.name and self.table == other.table
        if isinstance(other, str):
            return self.name == other
        return False

    def __repr__(self):
        """Here, we use str(self.table) rather than repr(self.table)
        to make it possible to pass table and column as str object instead
        of TableReference or ColumnReference objects"""
        if self.alias:
            return f'{self.table_name()} AS {self.alias}'
        return self.table_name()

    def __str__(self):
        return self.__repr__()


class TableReference:

    """
    a table name or a derived table or a join construct
    """
    pass


class TableName(TableReference):

    def __init__(self, name, schema_name=None, alias=None):
        self.name = name
        self.schema_name = schema_name
        self.alias = alias

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


class JoinType(Enum):
    INNER_JOIN = 1
    LEFT_OUTER_JOIN = 2
    RIGHT_OUTER_JOIN = 3
    FULL_OUTER_JOIN = 4
    NATURAL_JOIN = 5
    CROSS_JOIN = 6

join_type = [
    'invalid',
    'INNER JOIN',
    'LEFT OUTER JOIN',
    'RIGHT OUTER JOIN',
    'FULL OUTER JOIN',
    'NATURAL JOIN',
    'CROSS JOIN',
]

# todo remove table1 from JoinConstruct!

class JoinConstruct(TableReference):
    def __init__(self, table1, join_type, table2, join_condition=None):
        """table1 is of type TableReference and table2 is either a simple TableReference
        or a further JoinConstruct"""
        self.table1 = table1
        self.join_type = join_type
        self.table2 = table2
        self.join_condition = join_condition

    def as_lines(self):
        lines = []
        if self.table1 is None:
            pass
        elif isinstance(self.table1, JoinConstruct):
            lines.extend(self.table1.as_lines())
        else:
            lines.append(str(self.table1))
        join_type_descr = join_type[self.join_type.value]
        lines.append(f'{join_type_descr} {str(self.table2)}')
        lines.append(repr(self.join_condition))
        return lines

    def __repr__(self):
        lines = self.as_lines()
        return '\n'.join(lines)

class JoinCondition:
    pass

class OnJoinCondition(JoinCondition):
    def __init__(self, boolean_expr):
        self.boolean_expr = boolean_expr

    def __repr__(self):
        return 'ON {}'.format(repr(self.boolean_expr))

class UsingJoinCondition(JoinCondition):
    def __init__(self, columns_list):
        self.columns_list = columns_list

    def __repr__(self):
        return 'USING {}'.format(str(self.columns_list))

class JoinChain:
    """A more complex sort table reference"""
    def __init__(self, first_table, joins):
        self.joins = joins
        self.joins[0].table1 = first_table
        for i, join in enumerate(joins[1:]):
            join.table1 = None#joins[i-1]

    def __str__(self):
        return 'JoinChain'