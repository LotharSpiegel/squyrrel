import os
import sys


def main():
    try:
        from squyrrel.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Could not import squyrrel. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? "
            "Did you maybe forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv, base_path=os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    main()