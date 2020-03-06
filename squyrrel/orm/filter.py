


class ManyToOneFilter:

    many_to_one = True

    def __init__(self, name, model, relation, id_value):
        self.name = name
        self.model = model
        self.relation = relation
        self.id_value = id_value