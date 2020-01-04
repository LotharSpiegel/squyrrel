"""
https://docs.python.org/3/library/traceback.html
"""

import sys
import traceback


DEFAULT_TRACEBACK_LIMIT = 20


class ExceptionHandler:

    def __init__(self, traceback_limit=DEFAULT_TRACEBACK_LIMIT):
        self.traceback_limit = traceback_limit

    def handle(self, module_meta, exc_type, exc_value, exc_traceback):
        module_name = module_meta.name
        print(f'module <{module_name}> is rotten: {exc_type}: {exc_value}')
        traceback.print_tb(exc_traceback, limit=self.traceback_limit, file=sys.stdout)


class ModuleImportExceptionHandler(ExceptionHandler):

    pass