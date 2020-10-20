import pytest

from squyrrel.sql.clauses import *


# from utils import ci_assert_repr
from squyrrel.sql.test_utils import ci_assert_repr


class TestSelectClause:

    def test_build_raises_exception_when_empty_select_clause(self):
        with pytest.raises(ValueError):
            SelectClause()

    def test_build(self):
        fields = ['field1', 'field2']
        ci_assert_repr(SelectClause(*fields), "select field1, field2")

    def test_build_ignores_empty_fields(self):
        fields = ['field1', None, 'field2', '']
        select_clause = SelectClause(*fields)
        assert len(select_clause.items) == 2


class TestFromClause:

    def test_build(self):
        from_clause = FromClause('dummy_table')
        ci_assert_repr(from_clause, "from dummy_table")

#
# def test_where_clause():
#     column = ColumnReference('column', table=TableReference('table'))
#     condition = GreaterThanOrEquals(column, 5)
#     where_clause = WhereClause(condition)
#
#     ci_assert_repr(where_clause, "where table.column >= 5")
#
#
# def test_select_clause():
#     column = ColumnReference('column', table=TableReference('table'))
#     select_clause = SelectClause(column, 'another_column', 5, StringLiteral('string'))
#     ci_assert_repr(select_clause, "select table.column, another_column, 5, 'string'")
