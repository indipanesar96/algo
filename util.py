import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict

import pandas as pd

TMP_DIR = Path(r'/Users/inderpalpanesar/dev/Python/algo/resources')

binAPIDFtmer = lambda d: d.strftime('%d %b, %Y')
diskDateFmter = lambda d: d.strftime('%Y%m%d')


class Action(Enum):
    BUY = 'buy'
    SELL = 'sell'
    NOTHING = 'do_nothing'


@dataclass
class Trade:
    dt: datetime.date
    action: Action
    asset: str
    baseSize: float
    termSize: float
    price: float
    posBefore: float
    posAfter: float
    remainingCash: float


def getTermAmount(assetPrice: float, baseNotional: float) -> float:
    return baseNotional / assetPrice


def getBaseAmount(assetPrice: float, termAmount: float) -> float:
    return assetPrice * termAmount


def walkResourceDir() -> Dict[str, Path]:
    res = {}
    for root, dirs, files in os.walk(TMP_DIR, topdown=False):
        print(root, dirs, files)
        for f in files:
            res[f] = os.path.join(TMP_DIR, f)
    return res


def saveToDisk(name: str, payload: pd.DataFrame, overwrite=False, dir=TMP_DIR):
    if not (isinstance(payload, pd.DataFrame) or isinstance(payload, pd.Series)):
        return ValueError("Don't know how to save this type.")

    if not name.endswith('.pickle'):
        name += '.pickle'

    full = dir.joinpath(name)
    if checkExists(full) and not overwrite:
        print("Don't need to save.")
        return None

    payload.to_pickle(full)


def generateName(asset, sdt, edt) -> str:
    return f"{asset}_{diskDateFmter(sdt)}_{diskDateFmter(edt)}.pickle"


def checkExists(fn):
    return os.path.exists(fn)


def loadPickle(fn: str, dir=TMP_DIR):
    full = dir.joinpath(fn)
    return pd.read_pickle(full)


if __name__ == '__main__':
    walkResourceDir()
