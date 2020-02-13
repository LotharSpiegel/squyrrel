from squyrrel.orm.field import Field, Relation, ManyToOne, ManyToMany, OneToMany


class Model:

    table_name = None
    default_ordering = None

    @classmethod
    def attributes(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}

    @classmethod
    def fields_dict(cls):
        return {k: v for k, v in cls.attributes().items() if isinstance(v, Field)}

    @classmethod
    def fields(cls):
        return cls.fields_dict().items()

    @classmethod
    def id_field_name(cls):
        for field_name, field in cls.fields():
            if field.primary_key:
                return field_name
        raise Exception('Model has no primary_key field')

    @classmethod
    def relations_dict(cls):
        return {k: v for k, v in cls.attributes().items() if isinstance(v, Relation)}

    @classmethod
    def relations(cls):
        return cls.relations_dict().items()

    @classmethod
    def many_to_one_dict(cls):
        return {k: v for k, v in cls.attributes().items() if isinstance(v, ManyToOne)}

    @classmethod
    def many_to_one_relations(cls):
        return cls.many_to_one_dict().items()

    @classmethod
    def one_to_many_dict(cls):
        return {k: v for k, v in cls.attributes().items() if isinstance(v, OneToMany)}

    @classmethod
    def one_to_many_relations(cls):
        return cls.one_to_many_dict().items()

    @classmethod
    def many_to_many_dict(cls):
        return {k: v for k, v in cls.attributes().items() if isinstance(v, ManyToMany)}

    @classmethod
    def many_to_many_relations(cls):
        return cls.many_to_many_dict().items()

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
        for relation_name, relation in self.__class__.many_to_one_relations():
            instance_relation = relation.clone()
            instance_relation.entity = kwargs.get(relation_name, None)
            setattr(self, relation_name, instance_relation)
        for relation_name, relation in self.__class__.one_to_many_relations():
            instance_relation = relation.clone()
            if instance_relation.aggregation is None:
                pass # set entities
            else:
                instance_relation.aggregation_value = kwargs.get(relation_name, None)
                setattr(self, relation_name, instance_relation)

    def __str__(self):
        props = {}
        for field_name, field in self.instance_fields():
            props[field_name] = field.value
        properties = ', '.join([f'{key}={value}' for key, value in props.items()])
        return f'{self.__class__.__name__}({properties})'