from squyrrel.orm.field import Field


class Model:

    table_name = None

    @classmethod
    def fields_dict(cls):
        attributes = {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}
        return {k: v for k, v in attributes.items() if isinstance(v, Field)}

    @classmethod
    def fields(cls):
        return cls.fields_dict().items()

    @classmethod
    def id_field_name(cls):
        for field_name, field in cls.fields():
            if field.primary_key:
                return field_name
        raise Exception('Model has no primary_key field')

    def instance_fields_dict(self):
        fields = {}
        for field_name in self.__class__.fields_dict().keys():
            fields[field_name] = getattr(self, field_name)
        return fields

    def instance_fields(self):
        return self.instance_fields_dict().items()

    def __init__(self, **kwargs):
        for field_name, class_field in self.__class__.fields():
            instance_field = class_field.clone()
            instance_field.value = kwargs.get(field_name, None)
            setattr(self, field_name, instance_field)

    def __str__(self):
        props = {}
        for field_name, field in self.instance_fields():
            props[field_name] = field.value
        properties = ', '.join([f'{key}={value}' for key, value in props.items()])
        return f'{self.__class__.__name__}({properties})'