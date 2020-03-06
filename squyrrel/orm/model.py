from squyrrel.orm.field import Field, Relation, ManyToOne, ManyToMany, OneToMany


class Model:

    table_name = None
    default_ordering = None
    fulltext_search_columns = None

    @classmethod
    def name(cls):
        return cls.__name__

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
        # todo: handle more different cases
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

    @classmethod
    def get_field(cls, field_name):
        return cls.fields_dict().get(field_name)

    @classmethod
    def get_relation(cls, relation_name):
        return cls.relations_dict().get(relation_name)

    @classmethod
    def get_relation_by_fk_id_column(cls, fk_id_column):
        for relation_name, relation in cls.relations_dict().items():
            if relation.foreign_key_field == fk_id_column:
                return relation_name, relation
        return None

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

    def instance_fields_dict(self):
        fields = {}
        for field_name in self.__class__.fields_dict().keys():
            fields[field_name] = getattr(self, field_name)
        return fields

    @property
    def model(self):
        return self.__class__

    def instance_fields(self):
        return self.instance_fields_dict().items()

    def id_field(self):
        return getattr(self, self.model.id_field_name())

    @property
    def id(self):
        return self.id_field().value

    def as_json(self):
        json_dict = {}
        for field_name, field in self.instance_fields():
            json_dict[field_name] = field.value
        return json_dict

    @property
    def data(self):
        return self.as_json()

    def __str__(self):
        props = {}
        for field_name, field in self.instance_fields():
            props[field_name] = field.value
        properties = ', '.join([f'{key}={value}' for key, value in props.items()])
        return f'{self.__class__.__name__}({properties})'