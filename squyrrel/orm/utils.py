from squyrrel.orm.field import StringField, IntegerField, DateTimeField, BooleanField


def extract_ids(string):
    if string and string[0] == '[':
        string = string[1:-1]
        if not string:
            return []
        ids = string.split(',')
        return [int(id.strip()) for id in ids]
    else:
        return []


def remove_nulls(array):
    return [item for item in array if item]


def sanitize_id_array(model, obj):
    if isinstance(obj, str):
        return extract_ids(obj)
    if isinstance(obj, list):
        if not obj:
            return []
        sanitized_list = [item for item in obj if item]
        first_element = sanitized_list[0]
        if isinstance(first_element, int):
            return obj
        if isinstance(first_element, model):
            return [entity.id for entity in sanitized_list]
        if isinstance(first_element, dict):
            print([entity[model.id_field_name()] for entity in sanitized_list])
            return [entity[model.id_field_name()] for entity in sanitized_list]
    raise ValueError(f"Invalid type <{repr(obj)}> of argument for sanitize_id_array")


def m2m_aggregation_subquery_alias(model, relation_name):
    return f'{model.table_name}_{relation_name}'


def field_to_sql_data_type(field):
    # todo: dynamic method_name pattern
    # at the moment only Sqlite...

    if isinstance(field, StringField):
        return 'TEXT'
    if isinstance(field, IntegerField):
        return 'INTEGER'
    if isinstance(field, DateTimeField):
        return 'TEXT'
    if isinstance(field, BooleanField):
        return 'INTEGER'


#def build_where_clause(model, filter_condition=None, **kwargs):
#    # todo: this is garbage
#    if filter_condition is None:
#        filter_conditions = []
#        for key, value in kwargs.items():
#            filter_conditions.append(
#                Equals.column_as_parameter(ColumnReference(key, table=model.table_name), value))
#        if filter_conditions:
#            return WhereClause(filter_conditions[0])
#        else:
#            return None
#    else:
#        return WhereClause(filter_condition)


