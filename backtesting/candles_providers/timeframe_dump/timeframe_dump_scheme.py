

class TimeframeDumpScheme:
    """
    Specifies indexes for OHLC info, timestamp and volume (optional)
    in input file for `TimeframeDump`
    """
    def __init__(self, open_time=0, close_time=1, open=2, high=3, low=4, close=5, volume=None):
        self.open_time_idx = open_time
        self.close_time_idx = close_time
        self.open_idx = open
        self.high_idx = high
        self.low_idx = low
        self.close_idx = close
        self.volume_idx = volume
