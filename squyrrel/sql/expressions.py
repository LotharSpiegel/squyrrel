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
    pass



class ColumnReference:
    """
    Typically, a column reference looks like:
        table_name.column_name or even just
        column_name

    Note, that instead of the table_name, we can use an alias (defined in a from clause)
        t.column_name

    Further, the table_name can be qualified by a schema_name


    """

    def __init__(self, name, table=None):
        """
        table can be simply a table name (table reference including schema name) or a Table object
        """

        self.table = table
        self.name = name

    def __repr__(self):
        """Here, we use str(self.table) rather than repr(self.table)
        to make it possible to pass table and column as str object instead
        of TableReference or ColumnReference objects"""
        if self.table is not None:
            return f'{str(self.table)}.{str(self.name)}'
        return self.name


class TableReference:

    def __init__(self, name, schema_name=None):
        self.name = name
        self.schema_name = schema_name

    def __repr__(self):
        if self.schema_name is not None:
            return f'{str(self.schema_name)}.{str(self.name)}'
        return self.name


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

