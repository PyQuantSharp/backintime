

class TickCounter:

    def __init__(self):
        self._ticks = 0

    def get_ticks(self) -> int:
        return self._ticks

    def increment(self) -> None:
        self._ticks += 1
