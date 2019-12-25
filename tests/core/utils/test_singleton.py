import pytest

from squyrrel.core.utils.singleton import Singleton


def test_singleton():
    class TestSingletonClass(metaclass=Singleton):
        pass

    assert not TestSingletonClass.exists()

    first_instance = TestSingletonClass()
    assert TestSingletonClass.exists()
    second_instance = TestSingletonClass()

    assert id(first_instance) == id(second_instance)
