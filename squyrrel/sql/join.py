from enum import Enum

# from squyrrel.sql.clauses import FromClause
from squyrrel.sql.references import TableReference


class JoinType(Enum):
    INNER_JOIN = 1
    LEFT_OUTER_JOIN = 2
    RIGHT_OUTER_JOIN = 3
    FULL_OUTER_JOIN = 4
    NATURAL_JOIN = 5
    CROSS_JOIN = 6

join_type = [
    'invalid',
    'INNER JOIN',
    'LEFT OUTER JOIN',
    'RIGHT OUTER JOIN',
    'FULL OUTER JOIN',
    'NATURAL JOIN',
    'CROSS JOIN',
]

# todo remove table1 from JoinConstruct!

class JoinConstruct(TableReference):
    def __init__(self, table1, join_type, table2, join_condition=None):
        """table1 is of type TableReference and table2 is either a simple TableReference
        or a further JoinConstruct"""
        # if isinstance(table1, str):
        #     # todo or if isinstance(TableReference)
        #     self.table1 = FromClause(table1)
        # else:
        self.table1 = table1
        self.join_type = join_type
        self.table2 = table2
        self.join_condition = join_condition

    def join(self, join_type, table2, join_condition):
        return JoinConstruct(
            table1=self,
            join_type=JoinType.LEFT_OUTER_JOIN,
            table2=table2,
            join_condition=join_condition
        )

    def as_lines(self):
        lines = []
        if self.table1 is None:
            pass
        elif isinstance(self.table1, JoinConstruct):
            lines.extend(self.table1.as_lines())
        else:
            lines.append(repr(self.table1))
        join_type_descr = join_type[self.join_type.value]
        lines.append(f'{join_type_descr} {str(self.table2)}')
        lines.append(repr(self.join_condition))
        return lines

    def __repr__(self):
        lines = self.as_lines()
        return '\n'.join(lines)

class JoinCondition:
    pass

class OnJoinCondition(JoinCondition):
    def __init__(self, boolean_expr):
        self.boolean_expr = boolean_expr

    def __repr__(self):
        return 'ON {}'.format(repr(self.boolean_expr))

class UsingJoinCondition(JoinCondition):
    def __init__(self, columns_list):
        self.columns_list = columns_list

    def __repr__(self):
        return 'USING {}'.format(str(self.columns_list))

class JoinChain:
    """A more complex sort table reference"""
    def __init__(self, first_table, joins):
        self.joins = joins
        self.joins[0].table1 = first_table
        for i, join in enumerate(joins[1:]):
            join.table1 = None#joins[i-1]

    def __str__(self):
        return 'JoinChain'