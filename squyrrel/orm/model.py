from squyrrel.orm.field import (Field, Relation, ManyToOne,
                                ManyToMany, OneToMany, CongregateField)
from squyrrel.orm.exceptions import RelationNotFoundException
from squyrrel.orm.filter import ManyToOneFilter, ManyToManyFilter
from squyrrel.orm.entity_format import EntityFormat
from squyrrel.sql.references import ColumnReference


class AbstractModel:

    @classmethod
    def attributes(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__')}

    @classmethod
    def attr_dict(cls, field_cls, exclude_cls=CongregateField or None, include_never_select_fields=False):
        if exclude_cls is not None:
            if include_never_select_fields:
                return {k: v for k, v in cls.attributes().items() if
                        isinstance(v, field_cls) and not isinstance(v, exclude_cls)}
            else:
                return {k: v for k, v in cls.attributes().items() if
                        isinstance(v, field_cls) and not isinstance(v, exclude_cls) and not v.never_select}
        if include_never_select_fields:
            return {k: v for k, v in cls.attributes().items() if isinstance(v, field_cls)}
        else:
            return {k: v for k, v in cls.attributes().items() if isinstance(v, field_cls) and not v.never_select}

    @classmethod
    def congregate_attr_dict(cls, include_never_select_fields=False):
        return cls.attr_dict(field_cls=CongregateField, exclude_cls=None, include_never_select_fields=include_never_select_fields)


class Model(AbstractModel):
    table_name = None
    entities_key = None
    entity_key = None
    default_orderby = None
    fulltext_search_columns = None
    duplicate_search_columns = None
    duplicate_exact_columns_matchers = None
    uniqueness_constraints = None
    column_names = None

    @classmethod
    def fields_dict(cls, include_never_select_fields=False):
        return cls.attr_dict(Field, include_never_select_fields=include_never_select_fields)

    @classmethod
    def fields(cls, include_never_select_fields=False):
        return cls.fields_dict(include_never_select_fields=include_never_select_fields).items()

    @classmethod
    def build_select_fields(cls):
        return [ColumnReference(field_name, table=cls.table_name) for field_name in cls.fields_dict().keys()]

    @classmethod
    def congregate_fields(cls):
        return cls.congregate_attr_dict().items()

    @classmethod
    def id_field(cls) -> Field:
        return getattr(cls, cls.id_field_name())

    @classmethod
    def id_field_name(cls) -> str:
        # todo: handle more different cases
        for field_name, field in cls.fields():
            if field.primary_key:
                return field_name
        raise Exception('Model has no primary_key field')

    @classmethod
    def id_column_reference(cls):
        return ColumnReference(cls.id_field_name(), table=cls.table_name)

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
    def get_many_to_one_relation(cls, relation) -> ManyToOne:
        if isinstance(relation, str):
            try:
                return cls.many_to_one_dict().get(relation)
            except KeyError:
                raise Exception(f'Did not find relation {relation} on model {cls.name()}!')
        return relation

    @classmethod
    def get_many_to_many_relation(cls, relation) -> ManyToMany:
        if isinstance(relation, str):
            try:
                return cls.many_to_many_dict().get(relation)
            except KeyError:
                raise Exception(f'Did not find relation {relation} on model {cls.name()}!')
        return relation

    @classmethod
    def get_one_to_many_relation(cls, relation) -> OneToMany:
        if isinstance(relation, str):
            try:
                return cls.one_to_many_dict().get(relation)
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
        return model1_ == model2_

    @classmethod
    def get_relation_by_foreign_model(cls, foreign_model):
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

    def __init__(self, m2m_aggregations=None, **kwargs):
        self.init_fields(**kwargs)
        self.init_congregate_fields()
        self.init_many_to_one_relations(**kwargs)
        self.init_one_to_many_relations(**kwargs)
        self.init_many_to_many_relations()

        self.init_many_to_many_aggregation_values(m2m_aggregations=m2m_aggregations, **kwargs)
        self.init_congregate_field_values()

    # todo: refactor the following init_ methods

    def init_fields(self, **kwargs):
        for field_name, class_field in self.model.fields():
            instance_field = class_field.clone()
            instance_field.value = kwargs.get(field_name, None)
            setattr(self, field_name, instance_field)

    def init_congregate_fields(self):
        for field_name, class_field in self.model.congregate_fields():
            instance_field = class_field.clone()
            setattr(self, field_name, instance_field)

    def init_congregate_field_values(self):
        for field_name, class_field in self.model.congregate_fields():
            instance_field = getattr(self, field_name)
            instance_field.value = self.get_value(instance_field.attr)

    def init_many_to_one_relations(self, **kwargs):
        for relation_name, relation in self.model.many_to_one_relations():
            instance_relation = relation.clone()
            instance_relation.entity = kwargs.get(relation_name, None)
            setattr(self, relation_name, instance_relation)

    def init_one_to_many_relations(self, **kwargs):
        for relation_name, relation in self.model.one_to_many_relations():
            instance_relation = relation.clone()
            if instance_relation.aggregation is None:
                pass  # set entities
            else:
                instance_relation.aggregation_value = kwargs.get(relation_name, None)
                setattr(self, relation_name, instance_relation)

    def init_many_to_many_relations(self):
        for relation_name, relation in self.model.many_to_many_relations():
            instance_relation = relation.clone()
            setattr(self, relation_name, instance_relation)

    def init_many_to_many_aggregation_values(self, m2m_aggregations, **kwargs):
        if m2m_aggregations is None: return
        for relation_name, aggr_column_ref in m2m_aggregations:
            # todo check against m2m relations on self
            relation = getattr(self, relation_name)
            relation.aggregation_value = kwargs[relation_name]

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

    @property
    def id(self) -> str:
        return self.id_field().value

    def as_json(self):
        json_dict = {}
        for field_name, field in self.instance_fields():
            json_dict[field_name] = field.value
        return json_dict

    @property
    def data(self):
        return self.as_json()

    def get_value(self, attribute):
        if '.' in attribute:
            related_entity_name, attr = attribute.split('.')
            try:
                related_entity = getattr(self, related_entity_name)
            except AttributeError:
                raise AttributeError(f'Model {self.model.name()} has no related entity {related_entity_name}')
            return related_entity.get_value(attr)
        try:
            attr = getattr(self, attribute)
        except AttributeError:
            raise AttributeError(f'Attribute {attribute} does not exist on model {self.model.name()}')
        return str(attr)

    @classmethod
    def model_data(cls):
        json_dict = {}
        for field_name, field in cls.fields():
            json_dict[field_name] = field.value
        return json_dict

    @classmethod
    def build_rows(cls, items, max_rows, columns, entity_format=EntityFormat.MODEL):
        rows = []
        if max_rows is None:
            max_rows = len(items)
        # print('build_rows:', max_rows)
        if entity_format == EntityFormat.MODEL:
            for item in items[:max_rows]:
                row = []
                for col in columns:
                    value = item.get_value(attribute=col)
                    # if isinstance(column, ):
                    #     val = column.value
                    # else:
                    #     val = str(column)
                    row.append(value)
                rows.append(row)
        elif entity_format == EntityFormat.JSON:
            for item in items[:max_rows]:
                row = []
                for col in columns:
                    # todo: add sth like format_series() where it outputs series.name for example
                    val = item.get(col, '')
                    # column = getattr(item, col)
                    # val = str(column)
                    # if isinstance(column, CongregateField):
                    #     val = column.value
                    # else:
                    #     val = str(column)
                    row.append(val)
                rows.append(row)
        return rows

    @classmethod
    def get_column_name(cls, column):
        if '.' in column:
            if cls.column_names is None:
                raise AttributeError(f'Model {cls.name()} has no column_names map configured!')
            try:
                return cls.column_names[column]
            except KeyError:
                raise KeyError(f'The column {column} is missing in {cls.name()}.column_names!')
        field = getattr(cls, column)
        try:
            return field.name
        except AttributeError:
            return column

    @classmethod
    def build_column_names(cls, columns):
        return [cls.get_column_name(column) for column in columns]

    @classmethod
    def get_print_column_options(cls, columns):
        print_options = []
        for column in columns:
            try:
                field = getattr(cls, column)
            except AttributeError:
                print_options.append(None)
            else:
                print_options.append(field.print_options)

        return print_options

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

    @classmethod
    def name(cls):
        return cls.__name__

    def __str__(self):
        props = {}
        for field_name, field in self.instance_fields():
            props[field_name] = field.value
        properties = ', '.join([f'{key}={value}' for key, value in props.items()])
        return f'{self.model.name()}({properties})'
