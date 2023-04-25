from typing import Dict

import pandas as pd

from strategies.strategy import Strategy
from strategies.strategyUtil import calcAMA
from util import Action


class AMA(Strategy):
    def __init__(self, lookback: int, name: str):
        if lookback < 0:
            raise ValueError("Can't have a strategy with a negative lookback")

        self.lookback = lookback
        self.amas = dict()
        super().__init__(name)

    def observe(self, d: [str, pd.DataFrame]):
        for asset, data in d.items():
            if asset not in self.amas:
                self.amas[asset] = calcAMA(data.reset_index(), self.lookback)
            else:
                self.amas[asset].extend(
                    calcAMA(data.reset_index(), self.lookback)
                )

    def actuate(self, d: [str, pd.DataFrame]) -> Dict[str, Action]:
        actions = {}
        for asset, data in d.items():
            if data['close'].values[0] > self.amas[asset][-1]:
                actions[asset] = Action.BUY
            else:
                actions[asset] = Action.SELL
        return actions
