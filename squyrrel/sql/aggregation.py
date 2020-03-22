

class Function:
    name = None

    def __init__(self, args, name=None, alias=None):
        if name is not None:
            self.name = name
        self.args = args
        self.alias = alias

    def __repr__(self):
        args = ', '.join([repr(arg) for arg in self.args])
        if self.alias is None:
            return f'{self.name}({args})'
        return f'{self.name}({args}) AS {self.alias}'


class Count(Function):
    name = 'COUNT'


class GroupConcat(Function):
    name = 'GROUP_CONCAT'


class Coalesce(Function):
    name = 'COALESCE'


class NullIf(Function):
    name = 'NULLIF'