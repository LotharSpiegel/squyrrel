from datetime import datetime

from squyrrel.sql.table import TableName


# todo: make Relation(Clonable)
class Clonable:

    clone_attributes = []

    def clone(self, **kwargs):
        field_clone = self.__class__(**kwargs)
        for attr in self.clone_attributes:
            setattr(field_clone, attr, getattr(self, attr))
        return field_clone


class Field(Clonable):

    clone_attributes = ['_value', 'primary_key', 'not_null', 'unique', 'foreign_key',
                    'default_ascending', 'name']

    def __init__(self, primary_key=False, not_null=False, unique=False,
                 foreign_key=None, default_ascending=True, name=None):
        self._value = None
        self.primary_key = primary_key
        self.not_null = not_null
        self.unique = unique
        self.foreign_key = foreign_key
        self.default_ascending = default_ascending
        self.name = name

    @property
    def value(self):
        return self._value

    @property
    def nice_value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.set_value(value)

    def set_value(self, value):
        self._value = value

    def __str__(self):
        value = self.nice_value
        return str(value) if value is not None else ''


class IntegerField(Field):
    pass


class BooleanField(Field):

    clone_attributes = Field.clone_attributes + ['nice_true', 'nice_false']

    def __init__(self, *args, **kwargs):
        self.nice_true = kwargs.pop('nice_true', 'true')
        self.nice_false = kwargs.pop('nice_false', 'false')
        super().__init__(*args, **kwargs)

    @property
    def nice_value(self):
        return self.nice_true if self.value else self.nice_false


class StringField(Field):
    pass


class CongregateField(Field):

    def __init__(self, *args, **kwargs):
        self.attr = kwargs.pop('attr', None)
        super().__init__(*args, **kwargs)


class DateTimeField(Field):

    DEFAULT_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
    DEFAULT_TIMESTAMP_PYTHON_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    DEFAULT_ANCIENT = '1970-1-1 00:00:00'

    def __init__(self, *args, **kwargs):
        # actually, only needed for sqlite (which does not have a proper DateTime object, but uses Text for dates and times)
        # therefore todo: make this into SqliteDateTimeField
        self.timestamp_format = kwargs.pop('timestamp_format', self.DEFAULT_TIMESTAMP_FORMAT)
        self.ancient = kwargs.pop('ancient', self.DEFAULT_ANCIENT)
        super().__init__(*args, **kwargs)

    def set_value(self, value):
        print('set_value')
        print(value)
        if isinstance(value, datetime):
            self._value = value.strftime(self.timestamp_format)
        elif value == 'now':
            self._value = self.now()
        else:
            self._value = value

    def now(self):
        return datetime.now().strftime(self.timestamp_format)

    def ancient_datetime(self):
        return datetime.strptime(self.ancient, self.timestamp_format)

    def convert_to_python_datetime(self):
        return self.__class__.as_python_datetime(self.value, self.timestamp_format)

    @classmethod
    def as_python_datetime(cls, value, timestamp_format=None):
        print('value', value)
        print('timestamp_format:', timestamp_format)
        return datetime.strptime(value, timestamp_format or cls.DEFAULT_TIMESTAMP_FORMAT)


class ForeignKey:

    def __init__(self, model, foreign_field=None):
        self.model = model
        self.foreign_field = foreign_field


class Relation:

    def __init__(self, foreign_model, name=None):
        self.foreign_model = foreign_model
        self.name = name


class ManyToOne(Relation):

    def __init__(self, foreign_model, foreign_key_field,
                foreign_model_key_field=None, update_search_column=None,
                load_all=False, lazy_load=True, name=None):
        super().__init__(foreign_model=foreign_model, name=name)
        self.foreign_key_field = foreign_key_field
        if foreign_model_key_field is None:
            self.foreign_model_key_field = self.foreign_key_field
        else:
            self.foreign_model_key_field = foreign_model_key_field
        self.update_search_column = update_search_column
        self.lazy_load = lazy_load
        self.load_all = load_all
        self._entity = None

    def clone(self):
        kwargs = {
            'foreign_model': self.foreign_model,
            'foreign_key_field': self.foreign_key_field,
            'foreign_model_key_field': self.foreign_model_key_field,
            'update_search_column': self.update_search_column,
            'lazy_load': self.lazy_load,
            'load_all': self.load_all,
            'name': self.name
        }
        return self.__class__(**kwargs)

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, entity):
        self._entity = entity

    def __getattr__(self, name):
        return getattr(self.entity, name)

    def __str__(self):
        return str(self._entity)


class ManyToMany(Relation):
    """docstring for ManyToMany"""

    def __init__(self, foreign_model, junction_table,
                foreign_key_field, lazy_load=True, aggregation=None,
                name=None):
        super().__init__(foreign_model=foreign_model, name=name)
        self.foreign_key_field = foreign_key_field
        self.junction_table = TableName.build(junction_table)
        self.lazy_load = lazy_load
        self.aggregation = aggregation
        self._entities = None
        self._aggregation_value = None

    def clone(self):
        kwargs = {
            'foreign_model': self.foreign_model,
            'junction_table': self.junction_table,
            'foreign_key_field': self.foreign_key_field,
            'lazy_load': self.lazy_load,
            'aggregation': self.aggregation,
            'name': self.name
            # _aggregation_value?
        }
        return self.__class__(**kwargs)

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, entities):
        self._entities = entities

    @property
    def aggregation_value(self):
        return self._aggregation_value

    @aggregation_value.setter
    def aggregation_value(self, value):
        self._aggregation_value = value

    def __iter__(self):
        if self.entities is None:
            return iter([])
        return iter(self.entities)

    def __str__(self):
        if self.aggregation is not None:
            return str(self._aggregation_value) if self._aggregation_value is not None else ''
        return '' # todo: represent entities, durch komma getrennt, same for OneToMany


class OneToMany(Relation):

    def __init__(self, foreign_model, lazy_load=True, aggregation=None, name=None):
        super().__init__(foreign_model=foreign_model, name=name)
        self.lazy_load = lazy_load
        self.aggregation = aggregation
        self._entities = None
        self._aggregation_value = None

    def clone(self):
        kwargs = {
            'foreign_model': self.foreign_model,
            'lazy_load': self.lazy_load,
            'aggregation': self.aggregation,
            'name': self.name,
            # _aggregation_value?
        }
        return self.__class__(**kwargs)

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, entities):
        self._entities = entities

    @property
    def aggregation_value(self):
        return self._aggregation_value

    @aggregation_value.setter
    def aggregation_value(self, value):
        self._aggregation_value = value

    def __iter__(self):
        if self.entities is None:
            return iter([])
        return iter(self.entities)

    def __str__(self):
        if self.aggregation is not None:
            return str(self._aggregation_value) if self._aggregation_value is not None else ''
        return '' # todo: represent entities, durch komma getrennt