from squyrrel.orm.field import (Field, Relation, ManyToOne,
    ManyToMany, OneToMany, StringField, CongregateField)
from squyrrel.orm.exceptions import RelationNotFoundException
from squyrrel.orm.filter import ManyToOneFilter, ManyToManyFilter, StringFieldFilter


class AbstractModel:

    @classmethod
    def attributes(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}

    @classmethod
    def attr_dict(cls, field_cls, exclude_cls=CongregateField):
        if exclude_cls is not None:
            return {k: v for k, v in cls.attributes().items() if isinstance(v, field_cls) and not isinstance(v, exclude_cls)}
        return {k: v for k, v in cls.attributes().items() if isinstance(v, field_cls)}

    @classmethod
    def congregate_attr_dict(cls):
        return cls.attr_dict(field_cls=CongregateField, exclude_cls=None)


class Model(AbstractModel):

    table_name = None
    default_orderby = None
    fulltext_search_columns = None

    @classmethod
    def fields_dict(cls):
        return cls.attr_dict(Field)

    @classmethod
    def fields(cls):
        return cls.fields_dict().items()

    @classmethod
    def congregate_fields(cls):
        return cls.congregate_attr_dict().items()

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
    def get_many_to_one_relation(cls, relation):
        if isinstance(relation, str):
            try:
                return cls.many_to_one_dict().get(relation)
            except KeyError:
                raise Exception(f'Did not find relation {relation} on model {cls.name()}!')
        return relation

    @classmethod
    def get_many_to_many_relation(cls, relation):
        if isinstance(relation, str):
            try:
                return cls.many_to_many_dict().get(relation)
            except KeyError:
                raise Exception(f'Did not find relation {relation} on model {cls.name()}!')
        return relation

    @classmethod
    def compare_models(cls, model1, model2):
        if isinstance(model1, str):
            model1_ = model1
        else:
            model1_ = model1.__name__
        if isinstance(model2, str):
            model2_ = model2
        else:
            model2_ = model2.__name__
        print('compare_models')
        print(model1_)
        print(model2_)
        return model1_ == model2_

    @classmethod
    def get_relation_by_foreign_model(cls, foreign_model):
        print('get_relation_by_foreign_model')
        for relation_name, relation in cls.relations_dict().items():
            if cls.compare_models(relation.foreign_model, foreign_model):
                return relation_name, relation
        raise RelationNotFoundException(foreign_model=foreign_model, model=cls.__name__)

    @classmethod
    def get_relation_by_fk_id_column(cls, fk_id_column):
        for relation_name, relation in cls.relations_dict().items():
            if isinstance(relation, OneToMany):
                # todo: solve diff., has no foreign_key_field attr
                continue
            if relation.foreign_key_field == fk_id_column:
                return relation_name, relation
        raise RelationNotFoundException(fk_id_column=fk_id_column)

    def __init__(self, **kwargs):
        #print('model.init', kwargs)
        self.init_fields(**kwargs)
        self.init_congregate_fields(**kwargs)
        self.init_many_to_one_relations(**kwargs)
        self.init_one_to_many_relations(**kwargs)
        self.init_many_to_many_relations(**kwargs)

    # todo: refactor the following init_ methods

    def init_fields(self, **kwargs):
        for field_name, class_field in self.model.fields():
            instance_field = class_field.clone()
            instance_field.value = kwargs.get(field_name, None)
            setattr(self, field_name, instance_field)

    def init_congregate_fields(self, **kwargs):
        for field_name, class_field in self.model.congregate_fields():
            instance_field = class_field.clone()
            instance_field.value = kwargs.get(field_name, None)
            setattr(self, field_name, instance_field)

    def init_many_to_one_relations(self, **kwargs):
        for relation_name, relation in self.model.many_to_one_relations():
            instance_relation = relation.clone()
            instance_relation.entity = kwargs.get(relation_name, None)
            setattr(self, relation_name, instance_relation)

    def init_one_to_many_relations(self, **kwargs):
        for relation_name, relation in self.model.one_to_many_relations():
            instance_relation = relation.clone()
            if instance_relation.aggregation is None:
                pass # set entities
            else:
                instance_relation.aggregation_value = kwargs.get(relation_name, None)
                setattr(self, relation_name, instance_relation)

    def init_many_to_many_relations(self, **kwargs):
        for relation_name, relation in self.model.many_to_many_relations():
            instance_relation = relation.clone()
            setattr(self, relation_name, instance_relation)

    def instance_fields_dict(self):
        fields = {}
        for field_name in self.model.fields_dict().keys():
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

    @classmethod
    def build_many_to_one_filter(cls, model, name, relation, load_all=False):
        return ManyToOneFilter(
            model=model,
            name=name,
            relation=relation,
            load_all=load_all)

    @classmethod
    def build_many_to_many_filter(cls, model, name, relation):
        return ManyToManyFilter(
            model=model,
            name=name,
            relation=relation)

    @classmethod
    def build_filter(cls, model, name, field_name):
        field = model.get_field(field_name)
        if isinstance(field, StringField):
            return StringFieldFilter(name=name, model=model, field_name=field_name)
        return None

    @classmethod
    def build_rows(cls, items, max_rows, columns):
        rows = []
        if max_rows is None:
            max_rows = len(items)
        print('build_rows:', max_rows)
        for item in items[:max_rows]:
            row = []
            for col in columns:
                column = getattr(item, col)
                val = str(column)
                # if isinstance(column, CongregateField):
                #     val = column.value
                # else:
                #     val = str(column)
                row.append(val)
            rows.append(row)
        return rows

    @classmethod
    def get_column_name(cls, column):
        col = getattr(cls, column)
        try:
            return col.name
        except AttributeError:
            return column

    @classmethod
    def build_column_names(cls, columns):
        return [cls.get_column_name(column) for column in columns]

    @classmethod
    def filters(cls):
        return []

    @classmethod
    def many_to_one_filters(cls):
        return [filter for filter in cls.filters() if isinstance(filter, ManyToOneFilter)]

    @classmethod
    def many_to_many_filters(cls):
        return [filter for filter in cls.filters() if isinstance(filter, ManyToManyFilter)]

    @classmethod
    def get_filter(cls, column_name):
        for filter in cls.filters():
            if column_name == filter.key:
                return filter
        return None

    @classmethod
    def get_many_to_one_filter(cls, foreign_model):
        for filter in cls.many_to_one_filters():
            if filter.foreign_model == foreign_model:
                return filter
        return None

    @classmethod
    def get_many_to_many_filter(cls, foreign_model):
        for filter in cls.many_to_many_filters():
            if filter.foreign_model == foreign_model:
                return filter
        return None

    def __str__(self):
        props = {}
        for field_name, field in self.instance_fields():
            props[field_name] = field.value
        properties = ', '.join([f'{key}={value}' for key, value in props.items()])
        return f'{self.model.__name__}({properties})'