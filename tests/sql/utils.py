import pytest

from contextlib import contextmanager


@contextmanager
def not_raises():
    try:
        yield
    except Exception as exc:
        pytest.fail('Did raise Exception {}'.format(exc))


def ci_assert_repr(object, expected_value):
    assert repr(object).lower() == expected_value

def extract_separate_strings(value):
    test = value.replace('\n', ' ')
    test = test.replace('\t', ' ')
    return test.split()


def assert_repr_ignore_space(object, expected_value):
    obj_repr_strings = extract_separate_strings(repr(object))
    expected_strings = extract_separate_strings(expected_value)
    assert obj_repr_strings == expected_strings


def assert_query_lines(query, expected_lines):
    query_lines = repr(query).split('\n')
    trimmed_lines = list(line.strip().lower() for line in query_lines)
    try:
        assert trimmed_lines == list(expected_lines)
    except AssertionError:
        output = 'Query lines:\n'
        output += str(trimmed_lines) + '\n'
        output += 'Expected lines:\n'
        output += str(expected_lines)
        raise AssertionError(output)