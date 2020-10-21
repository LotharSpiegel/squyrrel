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

    @property
    def reference(self):
        if self.table is not None:
            return f'{str(self.table)}.{str(self.name)}'
        return self.name

    @property
    def params(self):
        return []

    @property
    def columns(self):
        return [self]

    def __eq__(self, other):
        if isinstance(other, ColumnReference):
            return self.name == other.name and self.table == other.table
        if isinstance(other, str):
            return self.reference == other
        return False

    def __hash__(self):
        return hash(self.reference)

    def __repr__(self):
        """Here, we use str(self.table) rather than repr(self.table)
        to make it possible to pass table and column as str object instead
        of TableReference or ColumnReference objects"""
        if self.alias:
            return f'{self.reference} AS {self.alias}'
        return self.reference

    def __str__(self):
        return self.__repr__()


class TableReference:
    """
    a table name or a derived table or a join construct
    """
    pass
