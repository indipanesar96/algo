from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

import pandas as pd

import util
from strategies.strategy import Strategy


class Portfolio:
    def __init__(self, assets: List[str],
                 startDate: datetime.date,
                 startingCash: int = 100):

        self.holdings = [{a: 0 for a in assets}]
        self.assets = assets
        self.trades = []
        self.holdings[0]['cash'] = startingCash
        self.currentHoldings = self.holdings[-1].copy()
        self.tradeSize = 40  # trade size in pounds, execute this many pounds worth of the other currency

        self.blotter = None

    def blot(self) -> pd.DataFrame:
        records = []
        for trade in self.trades:
            record = trade.__dict__
            record['holdingsValue'] = record['posAfter'] * record['price'] + record['remainingCash']
            records.append(record)

        return pd.DataFrame.from_dict(records)

    def buy(self, asset: str, closePrice: float,
            d: datetime.date):

        units = util.getTermAmount(closePrice, baseNotional=self.tradeSize)

        # if (self.currentHoldings[asset] <= 0) and \
        if \
                (self.currentHoldings['cash'] - self.tradeSize >= 0):
            newPos = self.currentHoldings[asset] + units
            oldPos = self.currentHoldings[asset]

            self.currentHoldings[asset] = newPos
            self.currentHoldings['cash'] -= self.tradeSize
            self.trades.append(
                util.Trade(
                    asset=asset,
                    action=util.Action.BUY.value,
                    baseSize=self.tradeSize,
                    termSize=units,
                    dt=d,
                    price=closePrice,
                    posAfter=newPos,
                    posBefore=oldPos,
                    remainingCash=self.currentHoldings['cash']
                )
            )

            self.holdings.append(self.currentHoldings.copy())

    def sell(self, asset: str, closePrice: float,
             d: datetime.date):

        unitsToSell = util.getTermAmount(closePrice, baseNotional=self.tradeSize)
        # no short for now
        # if self.currentHoldings[asset] >= 0.0:
        if self.currentHoldings[asset] >= unitsToSell:
            newPos = self.currentHoldings[asset] - unitsToSell
            oldPos = self.currentHoldings[asset]

            self.currentHoldings[asset] = newPos
            self.currentHoldings['cash'] += self.tradeSize
            self.trades.append(
                util.Trade(
                    asset=asset,
                    action=util.Action.SELL.value,
                    baseSize=self.tradeSize,
                    termSize=unitsToSell,
                    dt=d,
                    price=closePrice,
                    posAfter=newPos,
                    posBefore=oldPos,
                    remainingCash=self.currentHoldings['cash']
                )
            )
            self.holdings.append(self.currentHoldings.copy())

    def processAction(self,
                      asset: str,
                      act: util.Action,
                      data: Dict
                      ) -> None:

        if act == util.Action.NOTHING:
            return None

        if len(data) > 1:
            raise ValueError("Blotter got more than 1 timestep of data.")

        closePrice = data[0]['close']
        d = data[0]['close_time'].date()

        if act == util.Action.BUY:
            self.buy(asset, closePrice, d)

        elif act == util.Action.SELL:
            self.sell(asset, closePrice, d)


@dataclass
class ResultSet:
    data: Dict[str, pd.DataFrame]
    assets: List[str]
    portfolios: Dict[Strategy, Portfolio]
    blotters: Dict[Strategy, Portfolio]
