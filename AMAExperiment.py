import datetime

import matplotlib.pyplot as plt
import numpy as np

from dataloader import DataLoader


def calcAlpha(mmin, mmax, df):
    """
    Smaller alpha, the longer our memory is (less sensitive to recent events)
        -   smaller alpha - fewer cares about recent prices

    Consider volume and volatility (std) (must be over some lookback):
    1.  High vol low std    ->   high alpha (trend shift?)
    2.  Low vol low std     ->   middle alpha (not much new info)
    3.  High vol High std   ->   middle alpha (lots of noisy new info)
    4.  Low vol High std    ->   low alpha (lots of noisy new info)
    """
    stdMax = 0.8
    stdMin = 0.2
    std = df['close'].std() / 100.0
    aveVol = df['volume'].mean()
    volScore = np.interp(aveVol,
                         [df['volume'].min(), df['volume'].max()],
                         [0, 1])
    volContrib = volScore  # since when volScore is high, alpha should be high
    stdContrib = np.interp(std, [0, 1], [stdMax, stdMin])
    alpha = np.interp(0.5 * (volContrib + stdContrib), [mmin, mmax], [mmin, mmax])
    return alpha


def calcEMA(df, alpha):
    emas = []
    for idx, row in df.iterrows():
        close = row['close']
        if idx == 0:
            ema = close
        else:
            ema = alpha * close + (1 - alpha) * emas[-1]

        emas.append(ema)
    df[f'ema_{alpha}'] = emas
    return df


def calcAMA(df, lookback: int, alphaInit=0.1):
    """
    like ema but have alpha a fn of volume, time etc..
    """

    alphaMin = 0.1
    alphaMax = 0.9

    amas = []
    alphas = []
    for idx, row in df.reset_index().iterrows():
        if idx < lookback:
            amas.append(row['close'])
            alphas.append(0.5 * (alphaMax + alphaMin))
            continue

        close = row['close']
        alpha = calcAlpha(alphaMin, alphaMax, df.loc[idx - lookback: idx])
        alphas.append(alpha)

        if idx == lookback:
            ema = close
        else:
            ema = alpha * close + (1 - alpha) * amas[-1]

        amas.append(ema)

    df['alpha'] = alphas
    df[f'ama'] = amas
    return df


def main(dataLoader, assetFilter):
    df = dataLoader.load(assetFilter)[assetFilter[0]].reset_index()

    df = calcEMA(df, 0.5)
    df = calcAMA(df, 10)
    df[['close', 'ama'] + [i for i in df.columns if 'ema' in i]].plot()
    plt.show()

    x = 0


if __name__ == '__main__':
    START_DATE = datetime.date(2020, 1, 1)
    END_DATE = datetime.date(2023, 4, 6)
    # END_DATE = datetime.date.today()

    # assetFilter = ['ETHUSDT', 'BTCUSDT']
    assetFilter = ['ETHUSDT']
    dataLoader = DataLoader(START_DATE, END_DATE)
    main(dataLoader, assetFilter)
