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




class ValueExpression:

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class Literal(ValueExpression):
    pass


ScalarExpression=ValueExpression


class StringLiteral(Literal):
    pass


class DateLiteral(StringLiteral):
    pass


class NumericalLiteral(Literal):

    def __init__(self, value):
        if isinstance(value, str):
            if NumericalLiteral.is_int(value):
                self.value = int(value)
            elif NumericalLiteral.is_float(value):
                self.value = float(value)
            else:
                self.value = value
        else:
            self.value = value

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
    pass


class BooleanLiteral(Literal, Predicate):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        if self.value is None:
            return 'UNKNOWN'
        if self.value:
            return 'TRUE'
        return 'FALSE'


class BooleanExpression(Predicate):
    """A boolean expr is built out of true, false, boolean operators and boolean functions (and other boolean expressions)"""
    pass


class ComparisionOperator(Predicate):
    """The lhs and rhs of comparision operators are value expressions"""

    # todo: class attribute: operator_token = Token('=')

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs


class Equals(ComparisionOperator):

    def __repr__(self):
        return f'{repr(self.lhs)} = {repr(self.rhs)}'


class GreaterThanOrEquals(ComparisionOperator):

    def __repr__(self):
        return f'{repr(self.lhs)} >= {repr(self.rhs)}'


class BooleanOperator(Predicate):
    pass


class And(BooleanOperator):
    def __init__(self, lhs, rhs):
        if not isinstance(lhs, Predicate) or not isinstance(rhs, Predicate):
            raise Exception('Both sides of the AND operator must be of type Predicate')
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f'{repr(self.lhs)} AND {repr(self.rhs)}'


class Or(BooleanOperator):
    def __init__(self, lhs, rhs):
        if not isinstance(lhs, Predicate) or not isinstance(rhs, Predicate):
            raise Exception('Both sides of the OR operator must be of type Predicate')
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f'{repr(self.lhs)} OR {repr(self.rhs)}'


class Not(BooleanOperator):
    def __init__(self, predicate):
        if not isinstance(predicate, Predicate):
            raise Exception('NOT can only be applied to a Predicate')
        self.predicate = predicate

    def __repr__(self):
        return f'NOT {repr(self.predicate)}'

