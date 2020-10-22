
class FieldFilter:

    def __init__(self, name: str, model, description: str = None, negate: bool = False):
        self.name = name
        self.model = model
        self.description = description
        self.negate = negate

    @property
    def model_name(self):
        if isinstance(self.model, str):
            return self.model
        else:
            return self.model.name()


class StringFieldFilter(FieldFilter):

    def __init__(self, name, model, field_name, value=None, description: str = None, negate: bool = False):
        super().__init__(name=name, model=model, description=description, negate=negate)
        self.field_name = field_name
        self._value = value

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

    def __init__(self, name, model, relation, id_values=None, entities=None, load_all=False, description: str = None, negate: bool = False):
        super().__init__(name=name, model=model, description=description, negate=negate)
        self._relation = relation
        self.id_values = id_values
        self._entities = None
        self.load_all = load_all
        self.select_options = None

    def clone(self, id_values, entities=None, relation=None):
        field_clone = self.__class__(
            name=self.name,
            model=self.model,
            relation=relation or self._relation,
            load_all=self.load_all)
        # for attr in self.clone_attributes:
        #    setattr(field_clone, attr, getattr(self, attr))
        field_clone.id_values = id_values
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
    def value(self):
        if self.id_values and len(self.id_values) == 1:
            return self.id_values[0]
        return self.id_values

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
    def relation(self):
        return self.model.get_many_to_one_relation(self._relation)


class ManyToManyFilter(RelationFilter):
    many_to_many = True # needed?
    conjunction = 'UND' # todo: either and or or

    @property
    def relation(self):
        return self.model.get_many_to_many_relation(self._relation)
