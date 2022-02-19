from typing import Iterable, Callable, Any

from ..candles_providers import CandlesProvider
from ..market_data_storage import MarketDataStorage
from ..oscillators import Oscillator


class MarketDataAnalyzer:
    """
    Holds oscillators
    initializes, runs update on it's values storage
    and provides access to oscillators results
    """
    def __init__(
            self,
            market_data: CandlesProvider,
            oscillators: Iterable[Callable[[MarketDataStorage], Oscillator]]
    ):
        self._values = MarketDataStorage(market_data)
        # init oscillators
        oscillators = map(lambda x: x(self._values), oscillators)
        # Маппим осцилляторы к их имени для random access
        self._oscillators = {
            oscillator.get_name() : oscillator
                for oscillator in oscillators
        }

    def update(self) -> None:
        """ Runs each time a new candle closes """
        self._values.update()

    def get(self, oscillator_name: str) -> Any:
        """ Calculate oscillator value on demand """
        oscillator = self._oscillators.get(oscillator_name)

        if not oscillator:
            raise ValueError(
                f'No oscillator with provided name {oscillator_name} was found'
            )

        return oscillator()
