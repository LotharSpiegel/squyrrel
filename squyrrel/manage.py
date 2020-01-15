import os


def main():
    try:
        from squyrrel.management.command_manager import CommandManager
    except ImportError as exc:
        raise ImportError(
            "Could not import squyrrel. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? "
            "Did you maybe forget to activate a virtual environment?"
        ) from exc
    cmd_mgr = CommandManager(base_path=os.path.dirname(os.path.abspath(__file__)))
    cmd_mgr.execute_from_command_line()

if __name__ == '__main__':
    main()