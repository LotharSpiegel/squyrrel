import logging
import sys


logging.basicConfig(stream=sys.stdout)
log = logging.getLogger('Squyrrel')
log.setLevel(logging.DEBUG)


def debug(text, tags=None):
    # log.debug(text)
    pass