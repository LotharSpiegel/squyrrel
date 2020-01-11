import pytest

from utils import ci_assert_repr, assert_query_lines

from squyrrel.sql.expressions import *
from squyrrel.sql.clauses import *
from squyrrel.sql.query import Query


def test_query_repr():
    select_clause = SelectClause(ColumnReference('a_column', 'table1'),
                                 ColumnReference('b_column', 'table2'))
    from_clause = FromClause('table1, table2')
    where_clause = WhereClause(Equals(ColumnReference('a_column', 'table1'), 17))
    query = Query(select_clause, from_clause, where_clause=where_clause)

    print(query)
    assert_query_lines(query,
        ('select table1.a_column, table2.b_column',
         'from table1, table2',
         'where table1.a_column = 17'))
    #ci_assert_repr(query, """select table1.a_column, table2.b_column
    #from )


if __name__ == '__main__':
    test_query_repr()