

# todo: could also put these exception types on the class Model to encapsulate


class DidNotFindObjectWithIdException(Exception):

    def __init__(self, msg, model_name, id):
        super().__init__(msg)
        self.msg = msg
        self.model_name = model_name
        self.id = id


class DidNotFindForeignIdException(Exception):

    def __init__(self, msg, field):
        super().__init__(msg)
        self.field = field
        self.msg = msg


class RelationNotFoundException(Exception):

    def __init__(self, fk_id_column=None, foreign_model=None, model=None):
        if fk_id_column is not None:
            msg = f'Did not find relation corresponding to foreign key column {fk_id_column}'
        elif foreign_model is not None:
            msg = f'Did not find relation on model {model} corresponding to foreign model {foreign_model}'
        else:
            msg = 'Did not find relation'
        super().__init__(msg)
        self.fk_id_column = fk_id_column
        self.foreign_model = foreign_model