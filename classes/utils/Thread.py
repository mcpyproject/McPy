import threading


class AtomicInteger():
    """
    A thread-safe counter
    """

    def __init__(self, initial_value=1):
        self.value = initial_value
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            return self.value

    def get_and_increment(self, incr=1):
        with self._lock:
            value = self.value
            self.value += incr
            return value
