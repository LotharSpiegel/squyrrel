from squyrrel.management.base import BaseCommand


class ShellCommand(BaseCommand):
    prefix = 'shell'

    __inject__ = {
        '_cmd_window': 'ShellWindow',
    }


class PrintlnShellCommand(ShellCommand):
    name = 'println'

    def add_arguments(self, parser):
        parser.add_argument('text', type=str, help='Text to be printed in the shell')

    def handle(self, *args, **kwargs):
        tags = None
        text = kwargs['text']
        self._cmd_window.text.append(text, tags=tags)
        self._cmd_window.text.new_line()
        #version = '0.1.0'
        #self.write_in_shell(f'Start Squyrrel CLI (version={version})')