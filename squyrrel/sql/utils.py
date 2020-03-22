from squyrrel.sql.references import ColumnReference


def sanitize_column_reference(column_reference):
    if isinstance(column_reference, str):
        if '.' in column_reference:
            table, column = column_reference.split('.')
            column_reference = ColumnReference(column, table=table)
        else:
            raise Exception('Missing table in column reference')
    return column_reference