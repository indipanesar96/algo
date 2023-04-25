import datetime
import pandas as pd
from binance.client import Client
import client
import util

START_DATE = datetime.date(2020, 1, 1)
END_DATE = datetime.date.today()

interval = Client.KLINE_INTERVAL_1DAY



class Scraper:
    def __init__(self, sdt: datetime.date,
                 edt: datetime.date):
        self.sdt = sdt
        self.edt = edt
        self.cl = client.getClient()

    def getSymbols(self):
        return [i['symbol'] for i in self.cl.get_exchange_info()['symbols']]

    def scrape(self, asset, startDate=START_DATE, endDate=END_DATE,
               interval=Client.KLINE_INTERVAL_1DAY, overwrite=False):

        print(f"Running for {asset=}, {startDate=}, {endDate=}, {interval=}")

        fn = self.generateName(asset, startDate, endDate)

        if util.checkExists(fn) and not overwrite:
            return util.loadPickle(fn)

        sdtStr = util.binAPIDFtmer(startDate)
        edtStr = util.binAPIDFtmer(endDate)

        df = self.cl.get_historical_klines(asset, interval, sdtStr, edtStr)

        # klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

        data = pd.DataFrame(df)
        if data.empty:
            print(f"{asset=}, {startDate=}, {endDate=}, {interval=} was empty.")
            return

        data.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                        'taker_base_vol', 'taker_quote_vol', 'ignore']

        data.index = data['close_time'].map(lambda s: datetime.datetime.fromtimestamp(s / 1e3))

        data['close_time'] = data['close_time'].map(lambda s: datetime.datetime.fromtimestamp(s / 1e3))
        data['open_time'] = data['open_time'].map(lambda s: datetime.datetime.fromtimestamp(s / 1e3))

        colsToKeep = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'ignore']
        data = data[colsToKeep]

        for c in ['open', 'high', 'low', 'close', 'volume']:
            data[c] = data[c].astype(float)

        util.saveToDisk(fn, data, overwrite=False)
        return fn



if __name__ == '__main__':
    scraper = Scraper(START_DATE, END_DATE)
    assets = scraper.getSymbols()
    names = [scraper.scrape(i) for i in assets]

    x = 0
