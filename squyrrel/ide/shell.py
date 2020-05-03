from squyrrel import Squyrrel
from squyrrel.management.exceptions import ArgumentParserException


def inject_dependencies_into_cdm(squyrrel, cmd_cls):
    cmd_dict = {}
    for obj_name, obj_cls_name in cmd_cls.__inject__.items():
        cmd_dict[obj_name] = squyrrel.get_object(class_name_or_meta=obj_cls_name)
    return cmd_dict

def execute_cmd_from_shell(squyrrel, cmd_line):
    app = squyrrel.get_object('App')
    cmd_mgr = app.cmd_mgr
    cmd_window = app.cmd_window
    try:
        command_key, argv = cmd_mgr.parse_user_input(user_input=cmd_line)
        print('execute_cmd_from_shell, command_key=', command_key)
        cmd_cls = cmd_mgr.get_command_class(command_key)
        cmd = cmd_cls(**inject_dependencies_into_cdm(squyrrel, cmd_cls))
        output = cmd_mgr.execute_command(cmd, argv, command_key=command_key, prog_name="Squyrrel")
    except ArgumentParserException as exc:
        if hasattr(exc, 'command') and exc.command is not None:
            output = f'Error calling command <{exc.command.name}> ({exc.command.help}). Did you forget arguments?'
        else:
            output = exc.message
        cmd_window.text.new_line()
        cmd_window.text.append(output, tags='error')
    except Exception as exc:
        output = str(exc)
        cmd_window.text.new_line()
        cmd_window.text.append(output, tags='error')
        raise exc
    else:
        if isinstance(output, str):
            cmd_window.text.append(output)

def on_return(**kwargs):
    execute_cmd_from_shell(
        squyrrel=Squyrrel(),
        cmd_line=kwargs['user_input'])