


class Field:

    def __init__(self, primary_key=False, not_null=False, unique=False):
        self._value = None
        self.primary_key = primary_key
        self.not_null = not_null
        self.unique = unique

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def clone(self, **kwargs):
        field_clone = self.__class__(**kwargs)
        # field_clone.value = self._value
        for attr in ('_value', 'primary_key', 'not_null', 'unique'):
            setattr(field_clone, attr, getattr(self, attr))
        return field_clone


class IntegerField(Field):
    pass


class StringField(Field):
    pass