from typing import List

from squyrrel.orm.field import StringField, BooleanField


class FieldFilter:

    def __init__(self, name: str, model, value=None, display_name: str = None, description: str = None, negate: bool = False):
        self.name = name
        self.model = model
        self.description = description
        self.display_name = display_name
        self.negate = negate
        self._value = value

    @property
    def model_name(self):
        if isinstance(self.model, str):
            return self.model
        else:
            return self.model.name()

    @property
    def value(self):
        return self._value

    def to_dict(self):
        data = {
            'name': self.name,
            'value': self.value,
            'description': self.description,
            'negate': self.negate
        }
        return data


# todo: refactor BooleanFieldFilter und StringFieldFilter: both descend from
# new class FieldValueFilter


class BooleanFieldFilter(FieldFilter):

    def __init__(self, name, model, field_name, value=None, description: str = None, display_name: str = None):
        if not hasattr(model, 'get_field'):
            raise ValueError('Invalid model')
        if not isinstance(model.get_field(field_name), BooleanField):
            raise ValueError(f'Invalid field_name <{field_name}> for model {model.name()}')
        super().__init__(name=name, model=model, value=value, description=description, display_name=display_name)
        self.field_name = field_name

    def clone(self, value):
        return BooleanFieldFilter(
            name=self.name,
            model=self.model,
            field_name=self.field_name,
            value=value
        )

    @property
    def key(self):
        return self.field_name

    @property
    def value(self):
        return self._value

    def to_dict(self):
        return {
            'name': self.name,
            'fieldName': self.field_name,
            'value': self.value,
            'description': self.description,
            'negate': self.negate
        }

    # todo: implement json.JSONEncoder instead

    def __str__(self):
        return f'{self.name} = {self.value}'


class StringFieldFilter(FieldFilter):

    def __init__(self, name, model, field_name, value=None, description: str = None, display_name: str = None, negate: bool = False):
        if not hasattr(model, 'get_field'):
            raise ValueError('Invalid model')
        if not isinstance(model.get_field(field_name), StringField):
            raise ValueError(f'Invalid field_name <{field_name}> for model {model.name()}')
        super().__init__(name=name, model=model, value=value, description=description, display_name=display_name, negate=negate)
        self.field_name = field_name

    def clone(self, value):
        return StringFieldFilter(
            name=self.name,
            model=self.model,
            field_name=self.field_name,
            value=value
    )

    @property
    def key(self):
        return self.field_name

    @property
    def value(self):
        return self._value

    def to_dict(self):
        return {
            'name': self.name,
            'fieldName': self.field_name,
            'value': self.value,
            'description': self.description,
            'negate': self.negate
        }

    # todo: implement json.JSONEncoder instead

    def __str__(self):
        return f'{self.name} = {self.value}'


#class CoalesceFilter(FieldFilter):
#
#    def __init__(self, name, model, description: str = None):
#        super().__init__(name=name, model=model, description=description)
#
#    def __str__(self):
#        return ''


# todo: inherit relationfilter from clonable!! (see field)


class RelationFilter(FieldFilter):
    conjunction = 'AND'

    def __init__(self,
                 name,
                 model,
                 relation,
                 value=None,
                 entities=None,
                 load_all=False,
                 description: str = None,
                 display_name: str = None,
                 negate: bool = False):
        # todo: entities?
        if isinstance(relation, str) and hasattr(model, 'get_relation'):
            self._relation = model.get_relation(relation)
        else:
            self._relation = relation
        super().__init__(name=name,
                         model=model,
                         value=value,
                         description=description,
                         display_name=display_name if display_name is not None else self._relation.name,
                         negate=negate)
        self._entities = None
        self.load_all = load_all
        self.select_options = None

    def clone(self, value, entities=None, relation=None):
        field_clone = self.__class__(
            name=self.name,
            model=self.model,
            value=value,
            relation=relation or self._relation,
            load_all=self.load_all)
        # for attr in self.clone_attributes:
        #    setattr(field_clone, attr, getattr(self, attr))
        field_clone.entities = entities
        return field_clone

    @property
    def foreign_model(self):
        return self._relation.foreign_model

    @property
    def key(self):
        if hasattr(self._relation, 'foreign_key_field'):
            return self._relation.foreign_key_field
        return str(self._relation)

    @property
    def entities(self):
        return self._entities

    @entities.setter
    def entities(self, value):
        self._entities = value

    # todo: decomposition into simple manytoonefilter (only one entity)

    def __str__(self):
        if not self._entities:
            return ''
        return f' {self.conjunction} '.join([f'{self.name} = {entity}' for entity in self._entities])


class ManyToOneFilter(RelationFilter):
    many_to_one = True # needed?
    conjunction = 'ODER' # todo: i18n

    @property
    def value(self):
        # todo: possible sanitize value to single integer (id of m21 instance)
        return self._value

    @property
    def relation(self):
        return self.model.get_many_to_one_relation(self._relation)

    def to_dict(self):
        return {
            'name': self.name,
            'relation': self.relation.name,
            'value': self.value,
            'description': self.description,
            'negate': self.negate
        }


class ManyToManyFilter(RelationFilter):
    many_to_many = True # needed?
    conjunction = 'UND' # todo: either and or or

    @property
    def value(self):
        # todo: possible sanitize value to list of integers (id of instances)
        return self._value

    @property
    def relation(self):
        return self.model.get_many_to_many_relation(self._relation)

    def to_dict(self):
        return {
            'name': self.name,
            'relation': self.relation.name,
            'value': self.value,
            'description': self.description,
            'negate': self.negate
        }


class OrFieldFilter(FieldFilter):

    def __init__(self,
                 name: str,
                 model,
                 filters: List[FieldFilter],
                 value = None,
                 description: str = None,
                 display_name: str = None,
                 negate: bool = False):
        super().__init__(name, model, value=value, description=description, display_name=display_name, negate=negate)
        self.filters = filters

    def to_dict(self):
        return {
            'name': self.name,
            'filters': [f.to_dict() for f in self.filters],
            'description': self.description,
            'negate': self.negate
        }
