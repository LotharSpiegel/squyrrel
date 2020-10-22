"""
Value expressions, also scalar expressions are the simplest type of expressions:
they have a scalar value (of different types).

Sql allows arithmetic operations on scalar expressions.

Value expressions:
a constant or a literal value (string, integer, floating point number)

a column reference



A Predicate is an expression which evaluates to TRUE or FALSE (or UNKNOWN in case of SQL logic)
Examples:
A OR B (which is a Boolean expression)
A BETWEEN 5 AND 10 (not a Boolean expression, but a predicate); build by the comparision operator BETWEEN
column_name

Boolean Operators: AND, OR, NOT

Comparision Operators: <, >, <=, >=, =, <> or != (for all data types);
return values of type boolean
Further comparisino predicates:
a BETWEEN x AND y (which is equivalent to a >= x AND a >= y)
a NOT BETWEEN x AND y (equ to a < x OR a > y)

expression IS NULL ('is null operator')
expression IS NOT NULL
boolean_expr IS TRUE

https://www.postgresql.org/docs/9.6/functions-comparison.html



Mathematical operators:
+, -, *, /, % (modulo), ^ (exp), |/ square root, ||/ cube root
! factorial, !! factoriall
@ absolute value, & bitwise AND, | bitwise OR, # bitwise XOR
~ bitwise NOT, << bitwise left shift, >> bitwise right shift

"""

from squyrrel.sql.references import ColumnReference
from squyrrel.sql.utils import sanitize_column_reference


class ValueExpression:

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class Parameter(ValueExpression):

    @property
    def params(self):
        return [self.value]

    @property
    def columns(self):
        return []

    def __repr__(self):
        return '?'

    def __str__(self):
        return self.__repr__


class Literal(ValueExpression):

    @property
    def params(self):
        return []

    @property
    def columns(self):
        return []


ScalarExpression = ValueExpression


class StringLiteral(Literal):

    @classmethod
    def empty(cls):
        return StringLiteral('')


class DateLiteral(StringLiteral):
    pass


class NumericalLiteral(Literal):

    def __init__(self, value):
        if isinstance(value, str):
            if NumericalLiteral.is_int(value):
                v = int(value)
            elif NumericalLiteral.is_float(value):
                v = float(value)
            else:
                v = value
        else:
            v = value
        super().__init__(v)

    @staticmethod
    def is_float(value):
        try:
            float(value)
        except ValueError:
            return False
        return True

    @staticmethod
    def is_int(value):
        try:
            int(value)
        except ValueError:
            return False
        return True


class Predicate:

    @property
    def params(self):
        return []

    @property
    def columns(self):
        return []


class BooleanLiteral(Literal, Predicate):

    def __init__(self, value):
        super().__init__(value)

    def __repr__(self):
        if self.value is None:
            return 'UNKNOWN'
        if self.value:
            return 'TRUE'
        return 'FALSE'


class BooleanExpression(Predicate):
    """A boolean expr is built out of true, false, boolean operators and boolean functions (and other boolean
    expressions) """
    pass


class ComparisionOperator(Predicate):
    """The lhs and rhs of comparision operators are value expressions"""

    # todo: class attribute: operator_token = Token('=')

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    @property
    def params(self):
        return self.lhs.params + self.rhs.params

    @property
    def columns(self):
        # todo: refactor this into utility method which takes as parameters an arbitrary number of objects
        if hasattr(self.lhs, 'columns') and hasattr(self.rhs, 'columns'):
            return self.lhs.columns + self.rhs.columns
        if hasattr(self.lhs, 'columns'):
            return self.lhs.columns
        if hasattr(self.rhs, 'columns'):
            return self.rhs.columns
        return []


class Equals(ComparisionOperator):

    @classmethod
    def id_as_parameter(cls, model, id):
        return cls(lhs=ColumnReference(model.id_field_name(), table=model.table_name),
                   rhs=Parameter(id))

    @classmethod
    def column_as_parameter(cls, column_reference, value):
        column_reference = sanitize_column_reference(column_reference)
        return cls(lhs=column_reference,
                   rhs=Parameter(value))

    def __repr__(self):
        return f'{repr(self.lhs)} = {repr(self.rhs)}'


class Like(ComparisionOperator):

    @classmethod
    def column_as_parameter(cls, column_reference, search_value):
        column_reference = sanitize_column_reference(column_reference)
        return cls(lhs=column_reference,
                   rhs=Parameter(f'%{search_value}%'))

    def __repr__(self):
        return f'{repr(self.lhs)} LIKE {repr(self.rhs)}'


class GreaterThanOrEquals(ComparisionOperator):

    def __repr__(self):
        return f'{repr(self.lhs)} >= {repr(self.rhs)}'


class BooleanOperator(Predicate):
    pass


class BooleanBinaryOperator(BooleanOperator):
    operator_name = None

    def __init__(self, lhs, rhs):
        if not isinstance(lhs, Predicate) or not isinstance(rhs, Predicate):
            raise Exception(f'Both sides of the {self.__class__.operator_name} operator must be of type Predicate')
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f'({repr(self.lhs)} {self.operator_name} {repr(self.rhs)})'

    @property
    def params(self):
        # todo: lhs is of type Predicate, but params not resolved attribute of this class?
        return self.lhs.params + self.rhs.params

    @property
    def columns(self):
        # todo: lhs is of type Predicate, but params not resolved attribute of this class?
        return self.lhs.columns + self.rhs.columns

    @classmethod
    def concat(cls, conditions):
        """ Builder method to build conditions[0] OR conditions[1] OR ...
        analogously for AND, ..."""
        concated_condition = conditions[0]
        for condition in conditions[1:]:
            concated_condition = cls(concated_condition, condition)
        return concated_condition


class And(BooleanBinaryOperator):
    operator_name = 'AND'


class Or(BooleanBinaryOperator):
    operator_name = 'OR'


class Not(BooleanOperator):

    def __init__(self, predicate):
        if not isinstance(predicate, Predicate):
            raise Exception('NOT can only be applied to a Predicate')
        self.predicate = predicate

    def __repr__(self):
        return f'NOT {repr(self.predicate)}'

    @property
    def params(self):
        return self.predicate.params

    @property
    def columns(self):
        return self.predicate.columns
