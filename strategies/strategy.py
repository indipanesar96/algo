from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd
from util import Action


class Strategy(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def observe(self, d: [str, pd.DataFrame]):
        pass

    @abstractmethod
    def actuate(self, d: [str, pd.DataFrame]):
        pass


class MACD(Strategy):
    def __init__(self, slow: int, fast: int, name: str):
        assert fast < slow
        self.slow = slow
        self.fast = fast
        self.assetData = {}
        super().__init__(name)

    def observe(self, d: [str, pd.DataFrame]):
        self.assetData = d

    def actuate(self, d: [str, pd.DataFrame]) -> Dict[str, Action]:
        actions = {}
        for asset, data in d.items():
            full = pd.concat([self.assetData[asset], data])
            fast = full['close'].rolling(self.fast).mean()
            slow = full['close'].rolling(self.slow).mean()

            if (fast.iloc[-2] < slow.iloc[-2]) and (fast.iloc[-1] > slow.iloc[-1]):
                actions[asset] = Action.BUY
            elif (fast.iloc[-2] > slow.iloc[-2]) and (fast.iloc[-1] < slow.iloc[-1]):
                actions[asset] = Action.SELL
            else:
                actions[asset] = Action.NOTHING

        return actions




class Momentum(Strategy):
    def __init__(self, period: int, name: str):
        if period < 0:
            raise ValueError("Can't have a strategy with a negative epriod")

        self.period = period
        super().__init__(name)

    def rsi(self, se: pd.Series) -> float:
        avgGain = abs(se[se > 0].mean())
        avgLoss = abs(se[se <= 0].mean())
        rs = avgGain / avgLoss
        rsi = 100 * (1 - 1 / rs)
        return rsi

    def observe(self, d: [str, pd.DataFrame]):
        for asset, data in d.items():
            returns = data['close'].pct_change().dropna()
            rsi = returns.rolling(self.period).agg(self.rsi)
            # nUp = (returns > 0).astype(int).rolling(self.period).sum().dropna()
            # nDown = self.period - nUp
            l = 0

    def actuate(self, d: [str, pd.DataFrame]) -> Dict[str, Action]:
        actions = {}
        for asset, data in d.items():
            full = pd.concat([self.assetData[asset], data])
            fast = full['close'].rolling(self.fast).mean()
            slow = full['close'].rolling(self.slow).mean()

            if (fast.iloc[-2] < slow.iloc[-2]) and (fast.iloc[-1] > slow.iloc[-1]):
                actions[asset] = Action.BUY
            elif (fast.iloc[-2] > slow.iloc[-2]) and (fast.iloc[-1] < slow.iloc[-1]):
                actions[asset] = Action.SELL
            else:
                actions[asset] = Action.NOTHING

        return actions
