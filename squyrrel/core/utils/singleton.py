

class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    _instance = None

    # def __init__(cls, name, bases, attrs, **kwargs):
    #     super().__init__(name, bases, attrs)
    #     cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        else:
            pass
        return cls._instance

    def exists(cls):
        if not hasattr(cls, '_instance'):
            return False
        if cls._instance is None:
            return False
        return True

    def kill(cls):
        cls._instance = None