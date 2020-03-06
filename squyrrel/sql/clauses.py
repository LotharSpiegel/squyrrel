from squyrrel.sql.expressions import (StringLiteral, NumericalLiteral,
    Equals, Parameter)
from squyrrel.sql.references import ColumnReference


class FromClause:
    """FROM table_reference
    where table_reference can be: a table name,
    a derived table (such as a subquery) or a joni construct.
    Instead of a table name,there can be a comma separated list of multiple tabl (interpreted as cross join)
    """
    def __init__(self, table_reference):
        self.table_reference = table_reference

    def __repr__(self):
        return f'FROM {str(self.table_reference)}'


class WhereClause:

    def __init__(self, condition):
        self.condition = condition

    def __repr__(self):
        return f'WHERE {repr(self.condition)}'

    @property
    def params(self):
        return self.condition.params


class OrderByClause:
    def __init__(self, expr, ascending):
        self.expr = expr
        self.ascending = ascending

    def __repr__(self):
        asc = 'ASC' if self.ascending else 'DESC'
        return f'ORDER BY {repr(self.expr)} {asc}'


class HavingClause:
    def __init__(self, condition):
        self.condition = condition

    def __repr__(self):
        return f'HAVING {str(self.condition)}'


class SelectClause:
    def __init__(self, *args):
        """every arg can be any of the following:
        a column name, a ColumnReference object or a Literal object
        """
        self.items = list(args)

    def item_to_string(self, item):
        if isinstance(item, str):
            return str(item)
        return repr(item)

    def items_tostring(self):
        return ', '.join([self.item_to_string(item) for item in self.items])

    def __repr__(self):
        return f'SELECT {self.items_tostring()}'


class GroupByClause:
    def __init__(self, *args):
        """every arg can be any of the following:
        a column name, a ColumnReference object or a Literal object
        """
        self.items = args

    def item_to_string(self, item):
        if isinstance(item, str):
            return str(item)
        return repr(item)

    def items_tostring(self):
        return ', '.join([self.item_to_string(item) for item in self.items])

    def __repr__(self):
        return f'GROUP BY {self.items_tostring()}'

def get_clauses(self):
        clauses = [self.select_clause, self.from_clause]


class Pagination:

    def __init__(self, page_size, page_number=None):
        self.page_size = int(page_size)
        if page_number is None:
            self.offset = None
        else:
            self.offset = (int(page_number) - 1) * self.page_size

    def __repr__(self):
        if self.offset is None:
            return f'LIMIT {self.page_size}'
        return f'LIMIT {self.page_size} OFFSET {self.offset}'



#### UPDATE STATEMENT ###


class UpdateClause:

    def __init__(self, table_name):
        self.table_name = table_name

    def __repr__(self):
        return f'UPDATE {str(self.table_name)}'


class SetClause:
    """used in UPDATE query"""

    def __init__(self, **kwargs):
        self.updates = []
        for key, value in kwargs.items():
            self.updates.append(
                Equals(lhs=ColumnReference(key),
                       rhs=Parameter(value))
            )

    @property
    def params(self):
        return [update.rhs.value for update in self.updates]

    def __repr__(self):
        updates = ', '.join([repr(update) for update in self.updates])
        return f'SET {updates}'


class InsertClause:

    def __init__(self, table, columns):
        self.table = table
        self.columns = columns

    def __repr__(self):
        # todo: convert self.table into tablereference in case it is str and use repr()
        cols = ', '.join(self.columns)
        return f'INSERT INTO {self.table} ({cols})'


class DeleteClause:

    def __init__(self, table):
        self.table = table

    def __repr__(self):
        # todo: convert self.table into tablereference in case it is str and use repr()
        return f'DELETE FROM {self.table}'


class ValuesClause:

    def __init__(self, values):
        self.values = values

    @property
    def params(self):
        return [param.value for param in self.values]

    def __repr__(self):
        vals = ', '.join(repr(value) for value in self.values)
        return f'VALUES ({vals})'