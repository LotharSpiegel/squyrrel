"""
PostgreSQL: https://www.postgresql.org/docs/9.5/sql-select.html
"""
from squyrrel.orm.field import ForeignKey
from squyrrel.orm.model import Model
from squyrrel.orm.utils import field_to_sql_data_type
from squyrrel.sql.clauses import (UpdateClause, WhereClause, SetClause,
                                  InsertClause, ValuesClause, DeleteClause, SelectClause)
from squyrrel.sql.expressions import Parameter
from squyrrel.sql.table import TableName


class Query:

    def __init__(self,
                 select_clause: SelectClause,
                 from_clause,
                 where_clause=None,
                 groupby_clause=None,
                 having_clause=None,
                 orderby_clause=None,
                 pagination=None,
                 alias=None,
                 is_subquery=False,
                 options=None):

        self.select_clause: SelectClause = select_clause
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
                self.indent = options['indent']

        self.model = None

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

    @property
    def params(self):
        # todo: add params of all clauses together
        return self.where_clause.params if self.where_clause else []

    def __repr__(self):
        clauses = self.clauses_to_strings()
        clause_separation = '\n' + self.indent
        output = clauses[0] + clause_separation
        output += clause_separation.join(clauses[1:])
        if self.is_subquery:
            output = f'({output})'
            if self.alias is not None:
                output += f' AS {self.alias}'
        if not self.is_subquery:
            output += ';'
        return output


class ColumnDefinition:

    def __init__(self,
                 name,
                 data_type,
                 primary_key=False,
                 foreign_key: ForeignKey = None,
                 not_null=False,
                 default=None,
                 unique=False,
                 collate=None):
        self.name = name
        self.data_type = data_type
        self.primary_key = primary_key
        self.foreign_key = foreign_key
        self.not_null = not_null
        self.default = default
        self.unique = unique
        self.collate = collate

    def __repr__(self):
        output = f'{self.name} {self.data_type}'
        if self.primary_key:
            output += ' PRIMARY KEY'
        if self.not_null:
            output += ' NOT NULL'
        if self.default:
            output += f' DEFAULT {repr(self.default)}'
        if self.unique:
            output += ' UNIQUE'
        if self.collate is not None:
            output += f' COLLATE {self.collate}'
        if self.foreign_key is not None:
            output += f' {repr(self.foreign_key)}'
        return output


class CreateTableClause:

    def __init__(self, table_name, if_not_exists=False):
        self.table = TableName(name=table_name)
        self.if_not_exists = if_not_exists

    def __repr__(self):
        if_not_exists_str = ' IF NOT EXISTS' if self.if_not_exists else ''
        return f'CREATE TABLE{if_not_exists_str} {repr(self.table)}'


class CreateTableQuery:
    """
    CREATE TABLE [IF NOT EXISTS] table_name (
        col1 data_type PRIMARY KEY,
        col2 data_type NOT NULL,
        ...
        UNIQUE (col1, col2)
        PRIMARY KEY (col5, col6)
    );
    """

    def __init__(self, create_clause, column_definitions, uniqueness_constraints=None, pk_constraints=None):
        self.create_clause = create_clause
        self.column_definitions = column_definitions
        self.uniqueness_constraints = uniqueness_constraints
        self.pk_constraints = pk_constraints

    def __repr__(self):
        clause_separation = '\n'
        output = repr(self.create_clause) + ' ('
        output += clause_separation
        col_outputs = []
        for col in self.column_definitions:
            col_outputs.append(repr(col))
        output += (',' + clause_separation).join(col_outputs)

        # table constraints:
        constraint_outputs = []
        if self.uniqueness_constraints is not None:
            # todo: refactor: create class UniquenessConstraint (for table and for column)
            for uniqueness_constraint in self.uniqueness_constraints:
                constraint_columns = ', '.join(uniqueness_constraint)
                constraint = f'UNIQUE ({constraint_columns})'
                constraint_outputs.append(constraint)
        if self.pk_constraints is not None:
            # todo: refactor: create class UniquenessConstraint (for table and for column)
            for pk_constraint in self.pk_constraints:
                constraint_columns = ', '.join(pk_constraint)
                constraint = f'PRIMARY KEY ({constraint_columns})'
                constraint_outputs.append(constraint)
        if constraint_outputs:
            output += (',' + clause_separation)
            output += (',' + clause_separation).join(constraint_outputs)

        output += ');'
        return output

    @property
    def params(self):
        return None

    @classmethod
    def build(cls, table, columns, if_not_exists=False, uniqueness_constraints=None):
        create_clause = CreateTableClause(table, if_not_exists=if_not_exists)
        column_definitions = []
        for column_name, column_kwargs in columns.items():
            column_definitions.append(ColumnDefinition(
                name=column_name,
                data_type=column_kwargs['data_type'],
                primary_key=column_kwargs.get('primary_key', False),
                foreign_key=column_kwargs.get('foreign_key', None),
                not_null=column_kwargs.get('not_null', False),
                default=column_kwargs.get('default', None),
                unique=column_kwargs.get('unique', False),
                collate=column_kwargs.get('collate', None)
            ))
        return cls(create_clause, column_definitions=column_definitions, uniqueness_constraints=uniqueness_constraints)


class CreateManyToManyJunctionTableQuery(CreateTableQuery):

    def __init__(self, model1: Model, model2: Model, junction_table_name, if_not_exists=False):
        field_name1 = model1.id_field_name()
        field_name2 = model2.id_field_name()
        fk1 = ForeignKey(model=model1,
                         foreign_field=field_name1,
                         on_delete=ForeignKey.ReferentialAction.CASCADE)
        fk2 = ForeignKey(model=model2,
                         foreign_field=field_name2,
                         on_delete=ForeignKey.ReferentialAction.CASCADE)
        column_definitions = [
            ColumnDefinition(name=field_name1,
                             data_type=field_to_sql_data_type(model1.id_field()),
                             primary_key=False,
                             foreign_key=fk1,
                             not_null=True),
            ColumnDefinition(name=field_name2,
                             data_type=field_to_sql_data_type(model2.id_field()),
                             primary_key=False,
                             foreign_key=fk2,
                             not_null=True),
        ]
        primary_key_constraint = (field_name1, field_name2)
        super().__init__(create_clause=CreateTableClause(junction_table_name, if_not_exists=if_not_exists),
                         column_definitions=column_definitions,
                         pk_constraints=[primary_key_constraint])


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
        output += ';'
        return output

    @classmethod
    def build(cls, table, inserts):
        instance = cls(table=table)
        for key, value in inserts.items():
            instance.insert_clause.columns.append(key)
            instance.values_clause.values.append(Parameter(value))
        return instance


class BatchInsertQuery(InsertQuery):
    """
    INSERT INTO table_name (col1, col2, ...)
    VALUES
    (val1, val2, ...)
    (val1, val2, ...)
    """

    def __init__(self, table, insert_clause=None, rows=None):
        super().__init__(table, insert_clause=insert_clause)
        self.rows = rows

    def __repr__(self):
        clause_separation = '\n'
        output = repr(self.insert_clause)
        output += clause_separation
        output += 'VALUES' + clause_separation

        for row in self.rows[:-1]:
            output += '({}),\n'.format(', '.join(repr(value) for value in row))
        output += '({})\n'.format(', '.join(repr(value) for value in self.rows[-1]))
        output += ';'
        return output


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
        output += ';'
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
        output += ';'
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
