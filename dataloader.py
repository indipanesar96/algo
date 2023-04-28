import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

import pandas as pd

from util import TMP_DIR
import util


class DataLoader:
    def __init__(self,
                 sdt: datetime.date,
                 edt: datetime.date):
        self.sdt = sdt
        self.edt = edt
        self.pairToLocation = util.walkResourceDir()

    def load(self, assetFilter: Optional[List[str]]) -> Dict[str, pd.DataFrame]:
        assetFilterFullyFormedNames = {util.generateName(a, self.sdt, self.edt) for a in assetFilter}

        ret = {}
        for asset, fileName in self.pairToLocation.items():
            if asset in assetFilterFullyFormedNames:
                df = util.loadPickle(fileName)
                df.index = df.index.date
                ret[asset.split('_')[0]] = df

        return ret
