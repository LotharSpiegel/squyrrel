
class ArgumentParserException(Exception):
    def __init__(self, command):
        self.command = command