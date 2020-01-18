from squyrrel import Squyrrel
from squyrrel.management.exceptions import ArgumentParserException


def execute_cmd_from_shell(squyrrel, cmd_line):
    app = squyrrel.app
    cmd_mgr = app.cmd_mgr
    cmd_window = app.cmd_window
    try:
        _dict = {
            '_squyrrel': squyrrel,
            '_cmd_mgr': cmd_mgr,
            '_app': app
        }
        output = cmd_mgr.execute_from_input(
            prog_name="Squyrrel", user_input=cmd_line, **_dict)
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

def on_return(**kwargs):
    execute_cmd_from_shell(
        squyrrel=Squyrrel(),
        cmd_line=kwargs['user_input'])