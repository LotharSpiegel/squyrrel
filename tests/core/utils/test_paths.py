import os.path
import pytest

from squyrrel.core.utils.paths import *


def test_convert_path_to_import_string():
    assert convert_path_to_import_string('a/b/c') == 'a.b.c'
    assert convert_path_to_import_string('./a/b') == '.a.b'
    assert convert_path_to_import_string('a\\b\\c') == 'a.b.c'
    assert convert_path_to_import_string('a') == 'a'
    assert convert_path_to_import_string('../b') == '..b'
    assert convert_path_to_import_string('../../b') == '...b'
    assert convert_path_to_import_string('./../a') == '..a'

def test_find_first_parent():
    assert find_first_parent(path='a/b/c/d', parent='b') == os.path.join('a', 'b')
    assert find_first_parent(path='c:/a/b/c/d', parent='x') == None