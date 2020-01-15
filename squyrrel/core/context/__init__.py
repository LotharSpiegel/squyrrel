

class ContextDict(dict):
    pass


class Context:

    def __init__(self):
        self.ctx = ContextDict()

    def add(self, key, value):
        self.ctx[key] = value

    def build(self, *args, **kwargs):
        raise NotImplementedError()