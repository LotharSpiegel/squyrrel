

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
        return f'WHERE {str(self.condition)}'


class OrderByClause:
    pass


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
        self.items = args

    def item_to_string(self, item):
        if isinstance(item, str):
            return str(item)
        return repr(item)

    def items_tostring(self):

        return ', '.join([self.item_to_string(item) for item in self.items])

    def __repr__(self):
        return f'SELECT {self.items_tostring()}'