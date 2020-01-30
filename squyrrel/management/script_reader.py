import collections
import re


Token = collections.namedtuple('Token',
    ['type', 'value', 'line', 'column'])


class Assignment:
    def __init__(self, varname, value):
        pass


class ScriptReader:

    def __init__(self):
        pass

    def read_script(self, text):
        for token in self.tokenize_script(text):
            print(token)

    def tokenize_script(self, text):
        # keywords
        token_specs = [
            ('ASSIGN', r'='),
            ('NUMBER', r'\d+(\.\d*)?'), # integer or decimal number
            ('STRING', r'".+?"'),
            ('FORMATSTRING', r'f".+?"'),
            ('ID', r'[A-Za-z_\-.]+'),
            #('OP', r'[+-*/]'),
            ('NEWLINE', r'\n'),
            ('WHITESPACE', r'[ \t]+'),
            ('MISMATCH', r'.'),
        ]
        token_regex = '|'.join(f'(?P<{token_type}>{token_value})' for token_type,token_value in token_specs)
        line_num = 1
        line_start = 0
        for mo in re.finditer(token_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'ID':
                value = value
            elif kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'WHITESPACE':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpeced on line {line_num}')

            yield Token(kind, value, line_num, column)

    # def handle_format_strings(self, line):
    #     regex = r'f".+?"'
    #     format_strings = re.findall(regex, line)
    #     for format_string in format_strings:

    # def parse_user_input(self, user_input):
    #     try:
    #         command_key, user_input = user_input.split(maxsplit=1)
    #     except ValueError:
    #         command_key = user_input
    #         argv = None
    #         #raise ArgumentParserException(message=f'Could not parse command line=<{user_input}>')
    #     else:

    #         # format strings or strings (both inside "") or words
    #         regex = r'f".+?"|".+?"|[\w-]+'
    #         argv = re.findall(regex, user_input)
    #         print('user_inputs=', argv)

    #     # pattern = re.compile(r'f".+?"')
    #     # for arg in argv:
    #     #     if pattern.fullmatch(arg) is not None:
    #     #         print(f'found:<{arg}>')

    #     #print(f'parse_user_input: command_key={command_key}, argv={str(argv)}')
    #     return command_key, argv

    # def parse_script_line(self, line):

    #     if '=' in line:
    #         # todo: = inside " "
    #         self.read_var_declaration(line)
    #     else:
    #         self.ghost_cmd(cmd_line=line)

    # def read_var_declaration(self, line):
    #     key, value = re.split(r'=', line)
    #     key = key.strip()
    #     value = value.strip()
    #     self.vars[key] = value
    #     print(f'set var: key={key}, value={value}')