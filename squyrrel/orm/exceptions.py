

class DidNotFindForeignIdException(Exception):

    def __init__(self, msg, field):
        super().__init__(msg)
        self.field = field
        self.msg = msg