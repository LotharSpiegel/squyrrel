


class Field:

    def __init__(self, primary_key=False, not_null=False, unique=False,
                 foreign_key=None):
        self._value = None
        self.primary_key = primary_key
        self.not_null = not_null
        self.unique = unique
        self.foreign_key = foreign_key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def clone(self, **kwargs):
        field_clone = self.__class__(**kwargs)
        # field_clone.value = self._value
        for attr in ('_value', 'primary_key', 'not_null', 'unique', 'foreign_key'):
            setattr(field_clone, attr, getattr(self, attr))
        return field_clone

    def __str__(self):
        return str(self._value) if self._value is not None else ''


class IntegerField(Field):
    pass


class StringField(Field):
    pass


class ForeignKey:

    def __init__(self, model, foreign_field=None):
        self.model = model
        self.foreign_field = foreign_field


class Relation:

    def __init__(self, foreign_model):
        self.foreign_model = foreign_model


class ManyToOne(Relation):

    def __init__(self, foreign_model, foreign_key_field, foreign_model_key_field=None, lazy_load=True):
        super().__init__(foreign_model=foreign_model)
        self.foreign_key_field = foreign_key_field
        if foreign_model_key_field is None:
            self.foreign_model_key_field = self.foreign_key_field
        else:
            self.foreign_model_key_field = foreign_model_key_field
        self.lazy_load = lazy_load
        self._entity = None

    def clone(self):
        kwargs = {
            'foreign_model': self.foreign_model,
            'foreign_key_field': self.foreign_key_field,
            'foreign_model_key_field': self.foreign_model_key_field,
            'lazy_load': self.lazy_load
        }
        return self.__class__(**kwargs)

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, entity):
        self._entity = entity

    def __str__(self):
        return str(self._entity)
