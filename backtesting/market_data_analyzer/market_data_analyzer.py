from typing import Iterable

from ..oscillators import Oscillator
from ..candles_providers import CandlesProvider
from ..market_data_storage import MarketDataStorage


class MarketDataAnalyzer:

    def __init__(
            self,
            market_data: CandlesProvider,
            oscillators: Iterable[Oscillator]
            ):

        if not len(oscillators):
            raise ValueError('Oscillators list must not be empty')

        self._values = MarketDataStorage(market_data)
        # Маппим осцилляторы к их имени для random access
        self._oscillators = {
            oscillator.get_name() : oscillator
                for oscillator in (
                    oscillator.set_market_data(self._values)
                        for oscillator in oscillators
                )
        }

    def update(self) -> None:
        self._values.update()

    def get(self, oscillator_name: str) -> float:
        # calculate oscillator value on demand
        oscillator = self._oscillators.get(oscillator_name)

        if not oscillator:
            raise ValueError(
                f'No oscillator with provided name {oscillator_name} was found'
            )

        return oscillator()
