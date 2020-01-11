import pytest

from squyrrel.sql.expressions import *
from utils import not_raises, ci_assert_repr


def test_Literals_repr_and_str():
    v = NumericalLiteral(value=2)
    assert repr(v) == '2'
    assert str(v) == '2'

    v = NumericalLiteral(value=3.14)
    assert repr(v) == '3.14'
    assert str(v) == '3.14'

    v = StringLiteral(value='monthy')
    assert repr(v) == "'monthy'"
    assert str(v) == 'monthy'

def test_ColumnReference_repr():
    c = ColumnReference('column_name')
    assert repr(c) == 'column_name'

    c = ColumnReference('column_name', 'table_name')
    assert repr(c) == 'table_name.column_name'

    c = ColumnReference('column_name', TableReference('table_name'))
    assert repr(c) == 'table_name.column_name'

def test_boolean_literal_repr():
    assert repr(BooleanLiteral(True)).upper() == 'TRUE'
    assert repr(BooleanLiteral(False)).upper() == 'FALSE'
    assert repr(BooleanLiteral(None)).upper() == 'UNKNOWN'
    assert repr(BooleanLiteral(1)).upper() == 'TRUE'
    assert repr(BooleanLiteral(0)).upper() == 'FALSE'

def test_comparision_operators_repr():
    pass

def test_logical_operators_when_init_values_not_predicates_raise_exception():
    with pytest.raises(Exception):
        And('test', 3)
    with pytest.raises(Exception):
        Not(6)
    with not_raises():
        And(BooleanLiteral(True), BooleanLiteral(False))

def test_comparision_operators_repr():
    c = ColumnReference('column')
    ci_assert_repr(Equals(c, NumericalLiteral(5)), 'column = 5')
    ci_assert_repr(Equals(StringLiteral('monthy'), c), "'monthy' = column")
    ci_assert_repr(GreaterThanOrEquals(ColumnReference('date_column'), DateLiteral('2013-11-08')),
                   "date_column >= '2013-11-08'")

# def test_logical_operator_factory():

# yyyy-mm-dd format e.g., 2000-12-31

def test_logical_operators_repr():
    c = ColumnReference('column')
    predicate1 = Equals(c, NumericalLiteral(5))
    predicate2 = GreaterThanOrEquals(ColumnReference('date_column'), DateLiteral('2013-11-08'))
    column = ColumnReference('column', table=TableReference('table'))
    pred = GreaterThanOrEquals(column, 5)

    ci_assert_repr(Not(predicate1), "not column = 5")
    ci_assert_repr(And(predicate1, predicate2), "column = 5 and date_column >= '2013-11-08'")
    ci_assert_repr(pred, "table.column >= 5")