
class ArgumentParserException(Exception):
    def __init__(self, command=None, message=None):
        self.command = command
        self.message = message


class CommandNotFoundException(Exception):
    pass


class CommandError(Exception):
    pass