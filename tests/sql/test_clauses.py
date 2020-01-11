import pytest

from squyrrel.sql.expressions import *
from squyrrel.sql.clauses import *
from utils import ci_assert_repr


def test_from_clause_single_table_name():
    table = TableReference('table_name')
    from_clause = FromClause(table)
    ci_assert_repr(from_clause, "from table_name")

    from_clause = FromClause('table_name')
    ci_assert_repr(from_clause, "from table_name")


def test_where_clause():
    column = ColumnReference('column', table=TableReference('table'))
    condition = GreaterThanOrEquals(column, 5)
    where_clause = WhereClause(condition)

    ci_assert_repr(where_clause, "where table.column >= 5")


def test_select_clause():
    column = ColumnReference('column', table=TableReference('table'))
    select_clause = SelectClause(column, 'another_column', 5, StringLiteral('string'))
    ci_assert_repr(select_clause, "select table.column, another_column, 5, 'string'")