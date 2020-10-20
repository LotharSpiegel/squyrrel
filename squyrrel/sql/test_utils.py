import pytest

from contextlib import contextmanager


@contextmanager
def not_raises():
    try:
        yield
    except Exception as exc:
        pytest.fail('Did raise Exception {}'.format(exc))


def ci_assert_repr(obj, expected_value):
    result = repr(obj).lower()
    expected_value = expected_value.lower()
    try:
        assert result == expected_value
    except AssertionError:
        output = '\nResult: '
        output += result + '\n'
        output += 'Expected: '
        output += expected_value
        raise AssertionError(output)


def extract_separate_strings(value):
    test = value.replace('\n', ' ')
    test = test.replace('\t', ' ')
    return test.split()


def assert_repr_ignore_space(object, expected_value):
    obj_repr_strings = extract_separate_strings(repr(object))
    expected_strings = extract_separate_strings(expected_value)
    assert obj_repr_strings == expected_strings


def format_lines(lines):
    output = ''
    for line in lines[:-1]:
        output += line + '\n'
    output += lines[-1]
    return output


def assert_query_lines(query, expected_lines):
    query_lines = repr(query).split('\n')
    trimmed_lines = list(line.strip().lower() for line in query_lines)
    try:
        assert trimmed_lines == list(expected_lines)
    except AssertionError:
        output = 'Resulting Query:\n'
        output += format_lines(trimmed_lines) + '\n\n'
        output += 'Expected query:\n'
        output += format_lines(expected_lines)
        raise AssertionError(output)
