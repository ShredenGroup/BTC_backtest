import backtrader as bt
import pandas as pd
from .db_processor import DB_processor

class Backtester:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def get_data_pd(self):
        df_processed = self.df.copy()
        print(df_processed.head()) 
        class CryptoPanda(bt.feeds.PandasData):
            params = (
                ('datetime', None),
                ('open', -1),
                ('close', -1),
                ('high', -1),
                ('low', -1),
                ('volume', -1),
                ('openinterest',None)
            )
            
        data_feed = CryptoPanda(dataname=df_processed)
        return data_feed