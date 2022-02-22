from collections import deque
from .float_generator import FloatGenerator


class PropertyBuffer:
    """ Resizeable circular buffer for float values """
    def __init__(self, size: int):
        self._buf = deque(maxlen=size)

    def append(self, value: float) -> None:
        self._buf.append(value)

    def pop(self) -> float:
        return self._buf.pop()

    def values(self) -> FloatGenerator:
        return (x for x in self._buf)

    def capacity(self) -> int:
        return self._buf.maxlen

    def __len__(self) -> int:
        return len(self._buf)

    def resize(self, new_size: int) -> None:
        self._buf = deque(self._buf, maxlen=new_size)
