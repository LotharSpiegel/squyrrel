"""
PostgreSQL: https://www.postgresql.org/docs/9.5/sql-select.html
"""


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


# class QueryBuilder:

#     def __init__(self):
#         self.query = None