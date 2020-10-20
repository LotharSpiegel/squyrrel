import pytest

from squyrrel.core.registry.meta import ClassMeta, ModuleMeta
from squyrrel.db.mock.connection import DummyConnection
from squyrrel.orm.field import IntegerField
from squyrrel.orm.model import Model
from squyrrel.orm.wizzard import QueryWizzard, ModelNotFoundException, Equals
from squyrrel.sql.query import Query


class DummyModel(Model):
    table_name = 'dummy_table'

    dummy_id = IntegerField(primary_key=True)


@pytest.fixture(scope='module')
def wizzard():
    qw = QueryWizzard(db=DummyConnection())
    model_cls_meta = ClassMeta(module=ModuleMeta(package='testPackage',
                                                 module_name='test_module'),
                               class_name='TestModel',
                               class_reference=DummyModel)
    qw.register_model(model_cls_meta, table_name="test_table")
    return qw


@pytest.mark.usefixtures("wizzard")
class TestWizzard:

    def test_model(self, wizzard):
        with pytest.raises(ModelNotFoundException):
            wizzard.get_model('ModelWhichDoesNotExists')

    def test_build_get_all_query(self, wizzard):
        query: Query = wizzard.build_get_all_query('TestModel',
                                                   select_fields=['field1'],
                                                   filter_condition=Equals('dummy_id', 1))
        assert 'field1' in query.select_clause.items
        assert str(query.from_clause.table_reference) == 'dummy_table'
