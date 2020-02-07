from squyrrel.sql.query import Query
from squyrrel.sql.clauses import *
from squyrrel.orm.signals import model_loaded_signal


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

    def build_select_fields(self, model, select_fields):
        if select_fields is None:
            select_fields = []
            for field_name, field in model.fields():
                select_fields.append(field_name)
        return select_fields

    def get(self, model, select_fields=None, filter_condition=None):

        model = self.get_model(model)
        select_fields = self.build_select_fields(model, select_fields)

        print('model:', model)
        print('select_fields:', select_fields)
        print('filter_condition:', filter_condition)

        query = Query(
            select_clause=SelectClause(*select_fields),
            from_clause=FromClause(model.table_name),
            where_clause=WhereClause(filter_condition),
            pagination=None
        )

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception:
            raise Exception(f'Error during execution of query: \n{sql}')

        data = self.db.fetchone()

        if data is None:
            return None

        return self.build_entity(model, data, select_fields)

    def get_all(self, model, select_fields=None, page_size=None, page_number=None):

        model = self.get_model(model)
        select_fields = self.build_select_fields(model, select_fields)

        if page_number is None:
            pagination = None
        else:
            pagination = Pagination(page_number, page_size)

        query = Query(
            select_clause=SelectClause(*select_fields),
            from_clause=FromClause(model.table_name),
            pagination=pagination
        )

        sql = self.builder.build(query)
        print(sql)

        try:
            self.execute_query(sql)
        except Exception:
            raise Exception(f'Error during execution of query: \n{sql}')

        res = self.db.fetchall()
        if not res:
            return []
        entities = []
        for data in res:
            entities.append(self.build_entity(model, data, select_fields))
        return entities

    def build_entity(self, model, data, select_fields):
        kwargs = {}
        for i, field_name in enumerate(select_fields):
            # print(field_name, data[i])
            kwargs[field_name] = data[i]
        return model(**kwargs)