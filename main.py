import datetime
from typing import List

import pandas as pd

from dataloader import DataLoader
from plotting import Plotter
from portfolio import Portfolio, ResultSet
from strategies.AMA import AMA
from strategies.strategy import Strategy


# 1.    They have the agents (strategies) return their desired position in the asset(s), and then create trades off the back of this
# 3.    A typical breakdown of an update function
#           -   before: sanitisation (initialising lists etc, nothing much)
#           -   main: generating thr desired positions in the asset(s)
#                     -   preprocessor - create agent specific pre indicators
#                     -   strategy logic - FSM matrix
#                     -   post processor - create agent specific post indicators
#           -   after: generating the trades/orders that get us to our desired positions
#                       -   these are then passed to an exchange api adapter
#                       -   compute trade stats
# 4.    Agent specific post processor.process() is called
# 5.    Worth moving to event based system (like cbr), each price is an event as a json/class

class Backtest:
    def __init__(self,
                 sdt: datetime.date,
                 edt: datetime.date,
                 windowSize: int,
                 assets: List[str],
                 dataloader: DataLoader,
                 strategies: List[Strategy]):
        """
        https://twitter.com/quant_arb/status/1645395834605903872?s=46&t=w28yXIl4PDy1Gkm7L91FpA
        """

        self.sdt = sdt
        self.edt = edt
        self.assets = assets
        self.windowSize = windowSize  # days
        self.dates = pd.bdate_range(self.sdt, self.edt)
        self.dl = dataloader
        self.data = self.dl.load(assets)
        self.strategies = strategies
        self.pfls = {s: Portfolio(assets, self.sdt)
                     for s in self.strategies}

    def windowGenerator(self):
        for i in range(len(self.dates) - self.windowSize - 1):
            winStart = pd.to_datetime(self.dates[i]).date()
            winEnd = pd.to_datetime(self.dates[i + self.windowSize]).date()
            evalD = pd.to_datetime(self.dates[i + self.windowSize + 1]).date()
            yield i, winStart, winEnd, evalD

    def run(self) -> ResultSet:
        for idx, winS, winE, evalD in self.windowGenerator():

            print(f"{idx}\tTraining from: {winS}~{winE}, evaluating: {evalD}")
            thisWindow = pd.IndexSlice[winS: winE]
            windowData = {k: v.loc[thisWindow] for k, v in self.data.items()}
            evalData = {k: v.loc[evalD:evalD] for k, v in self.data.items()}
            evalDataDict = {k: v.to_dict('records') for k, v in evalData.items()}

            for s in self.strategies:
                s.observe(windowData)
                assetLevelAction = s.actuate(evalData)
                for asset, action in assetLevelAction.items():
                    self.pfls[s].processAction(asset,
                                               action,
                                               evalDataDict[asset])

        blotters = {s: self.pfls[s].blot() for s in self.strategies}

        return ResultSet(
            self.data,
            self.assets,
            self.pfls,
            blotters
        )


if __name__ == '__main__':
    START_DATE = datetime.date(2020, 1, 1)
    END_DATE = datetime.date(2023, 4, 6)
    # END_DATE = datetime.date.today()

    # assetFilter = ['ETHUSDT', 'BTCUSDT']
    assetFilter = ['ETHUSDT']

    dataLoader = DataLoader(START_DATE, END_DATE)

    strats = [
        # Momentum(30, 'Mom30'),
        # MACD(slow=20, fast=5, name='MACD-20-5'),
        AMA(10, 'ama10'),
        AMA(5, 'ama5'),
        AMA(20, 'ama20'),
        AMA(30, 'ama30')
        # MACD(slow=10, fast=2, name='MACD-10-2')
    ]
    bt = Backtest(START_DATE, END_DATE, 60, assetFilter, dataLoader, strats)
    res = bt.run()

    plotter = Plotter(res)
    plotter.plotPortfolios()
    plotter.plotBlotterTables()
