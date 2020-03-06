"""
PostgreSQL: https://www.postgresql.org/docs/9.5/sql-select.html
"""

from squyrrel.sql.clauses import (UpdateClause, WhereClause, SetClause,
    InsertClause, ValuesClause, DeleteClause)
from squyrrel.sql.expressions import (StringLiteral, NumericalLiteral,
    Equals, Parameter)


class Query:

    def __init__(self,
                select_clause,
                from_clause,
                where_clause=None,
                groupby_clause=None,
                having_clause=None,
                orderby_clause=None,
                pagination=None,
                alias=None,
                is_subquery=False,
                options=None):

        self.select_clause = select_clause
        self.from_clause = from_clause
        self.where_clause = where_clause
        self.groupby_clause = groupby_clause
        self.having_clause = having_clause
        self.orderby_clause = orderby_clause
        self.pagination = pagination
        self.alias = alias
        self.is_subquery = is_subquery

        self.indent = ' ' * 4
        if options is not None:
            if 'indent' in options:
                self.indent = options[indent]

    def get_clauses(self):
        clauses = [self.select_clause, self.from_clause]
        for clause in (self.where_clause,
                       self.groupby_clause,
                       self.having_clause,
                       self.orderby_clause,
                       self.pagination):
            if clause is not None:
                clauses.append(clause)
        return clauses

    def clauses_to_strings(self):
        return [repr(clause) for clause in self.get_clauses()]

    def __repr__(self):
        clauses = self.clauses_to_strings()
        clause_separation = '\n' + self.indent
        output = clauses[0] + clause_separation
        output += clause_separation.join(clauses[1:])
        if self.is_subquery:
            output = f'({output})'
            if self.alias is not None:
                output += f' AS {self.alias}'
        return output


class InsertQuery:
    """
    INSERT INTO table_name (col1, col2, ..)
    VALUES (val1, val2, ...)
    """

    def __init__(self, table, insert_clause=None, values_clause=None):
        self.insert_clause = insert_clause or InsertClause(table=table, columns=[])
        self.values_clause = values_clause or ValuesClause(values=[])

    @property
    def params(self):
        return self.values_clause.params

    def __repr__(self):
        clause_separation = '\n'
        output = repr(self.insert_clause)
        output += clause_separation
        output += repr(self.values_clause)
        return output

    @classmethod
    def build(cls, table, inserts):
        instance = cls(table=table)
        for key, value in inserts.items():
            instance.insert_clause.columns.append(key)
            instance.values_clause.values.append(Parameter(value))
        return instance


class DeleteQuery:
    """
    DELETE FROM table_name
    WHERE cond
    """

    def __init__(self, table, condition=None):
        self.delete_clause = DeleteClause(table=table)
        if condition is None:
            raise Exception('DeleteQuery instantiated with empty condition')
        self.where_clause = WhereClause(condition)

    @property
    def params(self):
        return self.where_clause.params

    def __repr__(self):
        clause_separation = '\n'
        output = repr(self.delete_clause)
        output += clause_separation
        output += repr(self.where_clause)
        return output


class UpdateQuery:
    """
    UPDATE table_name
    SET column1 = value1, column2 = value2, ...
    WHERE condition;
    """

    def __init__(self, update_clause, set_clause, where_clause):
        self.update_clause = update_clause
        self.set_clause = set_clause
        self.where_clause = where_clause

    def __repr__(self):
        clause_separation = '\n'
        output = repr(self.update_clause)
        output += clause_separation
        output += repr(self.set_clause)
        output += clause_separation
        output += repr(self.where_clause)
        return output

    @property
    def params(self):
        return self.set_clause.params + self.where_clause.params
        # params_ = list(self.set_clause.params)
        # if isinstance(self.where_clause.condition, Equals):
        #     if isinstance(self.where_clause.condition.rhs, Parameter):
        #         params_.append(self.where_clause.condition.rhs.value)
        # return params_

    @classmethod
    def build(cls, model, filter_condition, updates):
        return cls(
            update_clause=UpdateClause(model.table_name),
            set_clause=SetClause(**updates),
            where_clause=WhereClause(filter_condition)
        )


# class QueryBuilder:

#     def __init__(self):
#         self.query = None