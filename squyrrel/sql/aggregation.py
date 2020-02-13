

class Function:

    def __init__(self, name, args, alias=None):
        self.name = name
        self.args = args
        self.alias = alias

    def __repr__(self):
        args = ', '.join([str(arg) for arg in self.args])
        if self.alias is None:
            return f'{self.name}({args})'
        return f'{self.name}({args}) AS {self.alias}'
