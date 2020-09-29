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
