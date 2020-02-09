from squyrrel.sql.query import Query
from squyrrel.sql.clauses import *
from squyrrel.sql.expressions import Equals, NumericalLiteral
from squyrrel.sql.references import (OnJoinCondition, JoinConstruct, ColumnReference,
    JoinType, TableReference)
from squyrrel.orm.signals import model_loaded_signal
from squyrrel.orm.field import ManyToOne


class QueryWizzard:

    def __init__(self, db, builder):
        self.db = db
        self.builder = builder
        self.last_sql_query = None
        self.models = {}
        model_loaded_signal.connect(self.on_model_loaded)

    def execute_query(self, sql, params=None):
        self.last_sql_query = sql
        self.db.execute(sql=sql, params=params)

    def on_model_loaded(self, *args, **kwargs):
        new_model_class_meta = kwargs.get('class_meta') or args[0]
        new_model_class = new_model_class_meta.class_reference
        self.register_model(
            model_cls_meta=new_model_class_meta,
            table_name=new_model_class.table_name)

    def register_model(self, model_cls_meta, table_name):
        if table_name is None:
            print(f'Warning: Model {model_cls_meta.class_name} has table_name=None. Will not be registered.')
            return
        key = model_cls_meta.class_name
        if key in self.models.keys():
            print(f'There is already a model on key <{key}>')
            return
        self.models[key] = model_cls_meta.class_reference
        print('register_model:', key)

    def get_model(self, model):
        if isinstance(model, str):
            try:
                return self.models[model]
            except KeyError:
                raise Exception(f'Orm: did not find model {model}')
        return model

    def sql_exc(self, sql, exc):
        return Exception(f'Error during execution of query: \n{sql}\nSql Exc.: {str(exc)}')

    def build_select_fields(self, model, select_fields=None):
        if select_fields is None:
            select_fields = []
            for field_name, field in model.fields():
                select_fields.append(ColumnReference(field_name, table=model.table_name))
        return select_fields

    def build_where_clause(self, model, filter_condition, **kwargs):
        if filter_condition is None:
            filter_conditions = []
            for key, value in kwargs.items():
                filter_conditions.append(Equals(
                    ColumnReference(key, table=model.table_name), NumericalLiteral(value)))
            if filter_conditions:
                return WhereClause(filter_conditions[0])
            else:
                return None
        else:
            return WhereClause(filter_condition)

    def get(self, model, select_fields=None, filter_condition=None, **kwargs):

        model = self.get_model(model)
        select_fields = self.build_select_fields(model, select_fields)

        where_clause = self.build_where_clause(model, filter_condition=filter_condition, **kwargs)

        from_clause = FromClause(model.table_name)

        many_to_one_entities = self.handle_many_to_one_entities(model=model,
            select_fields=select_fields, from_clause=from_clause)

        query = Query(
            select_clause=SelectClause(*select_fields),
            from_clause=from_clause,
            where_clause=where_clause,
            pagination=None
        )

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception as exc:
            raise self.sql_exc(sql, exc) from exc

        data = self.db.fetchone()

        if data is None:
            return None

        return self.build_entity(model, data, select_fields, many_to_one_entities)

    def handle_many_to_one(self, model, select_fields, relation_name, relation, from_clause):
        if relation.lazy_load:
            return False
        foreign_model = self.get_model(relation.foreign_model)
        foreign_select_fields = self.build_select_fields(foreign_model)
        join_condition = OnJoinCondition(
            Equals(ColumnReference(relation.foreign_key_field, table=model.table_name),
                   ColumnReference(relation.foreign_model_key_field, table=foreign_model.table_name))
        )
        from_clause.table_reference = JoinConstruct(
            table1=model.table_name,
            join_type=JoinType.INNER_JOIN,
            table2=foreign_model.table_name,
            join_condition=join_condition
        )
        select_fields.extend(foreign_select_fields)
        return True

    def handle_many_to_one_entities(self, model, select_fields, from_clause):
        many_to_one_entities = []
        for relation_name, relation in model.relations():
            relation.foreign_model = self.get_model(relation.foreign_model)
            if isinstance(relation, ManyToOne):
                if self.handle_many_to_one(model=model,
                                            select_fields=select_fields,
                                            relation_name=relation_name,
                                            relation=relation,
                                            from_clause=from_clause):
                    many_to_one_entities.append((relation_name, relation))
        return many_to_one_entities

    def get_all(self, model, select_fields=None, filter_condition=None, page_size=None, page_number=None, **kwargs):
        model = self.get_model(model)
        select_fields = self.build_select_fields(model, select_fields)

        if page_number is None:
            pagination = None
        else:
            pagination = Pagination(page_number=page_number, page_size=page_size)

        where_clause = self.build_where_clause(model, filter_condition=filter_condition, **kwargs)

        from_clause = FromClause(model.table_name)

        many_to_one_entities = self.handle_many_to_one_entities(model=model,
            select_fields=select_fields, from_clause=from_clause)

        query = Query(
            select_clause=SelectClause(*select_fields),
            from_clause=from_clause,
            where_clause=where_clause,
            pagination=pagination
        )

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception as exc:
            raise self.sql_exc(sql, exc) from exc

        res = self.db.fetchall()
        if not res:
            return []
        entities = []
        for data in res:
            entities.append(self.build_entity(model, data, select_fields, many_to_one_entities))
        return entities

    def build_entity(self, model, data, select_fields, many_to_one_relations):
        kwargs = {}
        for i, column_reference in enumerate(select_fields):
            if column_reference.table == model.table_name:
                kwargs[column_reference.name] = data[i]
        for relation_name, relation in many_to_one_relations:
            foreign_kwargs = {}
            for i, column_reference in enumerate(select_fields):
                if column_reference.table == relation.foreign_model.table_name:
                    foreign_kwargs[column_reference.name] = data[i]
            kwargs[relation_name] = relation.foreign_model(**foreign_kwargs)
        return model(**kwargs)