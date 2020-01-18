
class ArgumentParserException(Exception):
    def __init__(self, command):
        self.command = command


class CommandNotFoundException(Exception):
    pass


class CommandError(Exception):
    pass