from collections import deque


NO_NAME = 'NO_NAME'

class Signal:

    def __init__(self, name=None, caching=True):
        self._slots = []
        self.name = name or NO_NAME
        self.cache = SignalCache()
        self.caching = caching

    def connect(self, slot):
        """Connect slot to signal"""

        # raise exc if slot not callable
        if not self.is_connected(slot):
            self._slots.append(slot)

    def disconnect(self, slot):
        """Removes slot from signal (in case it is connected)"""

        try:
            index = self._slots.index(slot)
        except ValueError:
            pass
        else:
            self._slots.pop(index)

    def emit(self, *args, **kwargs):
        """Calls all slots (connected to this signal)"""

        for slot in self._slots:
            slot(*args, **kwargs)

        if self.caching:
            self.cache.append(args, kwargs)

    def is_connected(self, slot):
        return slot in self._slots

    def clear_cache(self):
        _cache = list(self.cache.cache)
        self.cache.cache.clear()
        return _cache


class SignalFreeze:

    # replace by namedtuple

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


class SignalCache:

    def __init__(self):
        self.cache = deque()

    def append(self, args, kwargs):
        self.cache.append(SignalFreeze(args, kwargs))

    def popfirst(self):
        try:
            return self.cache.popleft()
        except IndexError:
            return None