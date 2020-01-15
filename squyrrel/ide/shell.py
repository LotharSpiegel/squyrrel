from squyrrel import Squyrrel
from squyrrel.management.exceptions import ArgumentParserException


def on_return(**kwargs):
    print('shell.on_return')
    user_input = kwargs['user_input']
    squyrrel = Squyrrel()
    app = squyrrel.app
    cmd_mgr = app.cmd_mgr
    cmd_window = app.cmd_window
    try:
        output = cmd_mgr.execute_from_input(
            prog_name="Squyrrel", user_input=user_input, squyrrel=squyrrel)
    except ArgumentParserException as exc:
        output = f'Error calling command <{exc.command.name}> ({exc.command.help}). Did you forget arguments?'
        cmd_window.text.new_line()
        cmd_window.text.append(output, tags='error')
    except Exception as exc:
        output = str(exc)
        cmd_window.text.new_line()
        cmd_window.text.append(output, tags='error')
    else:
        if isinstance(output, str):
            cmd_window.text.append(output)