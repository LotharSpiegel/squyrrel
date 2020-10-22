import pytest
from squyrrel.orm.field import IntegerField

from squyrrel.orm.model import Model

from squyrrel.sql.query_builder import QueryBuilder

# todo: refactor: use fixture DummyModel for test_wizzard and test_query_builder
from squyrrel.sql.test_utils import assert_query_lines


class DummyModel(Model):
    table_name = 'dummy_table'

    dummy_id = IntegerField(primary_key=True)


@pytest.fixture(scope='module')
def qb():
    return QueryBuilder(model=DummyModel)


@pytest.mark.usefixtures("qb")
class TestQueryBuilder:

    def test_build_raises_ValueError_when_mandatory_select_clause_is_missing(self, qb):
        with pytest.raises(ValueError):
            qb.build()

    def test_build_basic_query(self, qb: QueryBuilder):
        query = qb.select(['dummy_id', 'name']).build()
        assert_query_lines(query, ('select dummy_id, name',
                                   'from dummy_table'))

    def test_build_basic_query_also_tolerate_list_as_first_arg(self, qb: QueryBuilder):
        query = qb.select(['dummy_id', 'name']).build()
        assert_query_lines(query, ('select dummy_id, name',
                                   'from dummy_table'))

    def test_build_query_by_id(self, qb: QueryBuilder):
        query = qb.select(['*']).by_id(17).build()
        assert_query_lines(query, ('select *',
                                   'from dummy_table',
                                   'where dummy_table.dummy_id = ?'))
        assert query.params[0] == 17

    # todo: test necessary joins
