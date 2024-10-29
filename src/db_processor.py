import pandas as pd 
from pathlib import Path
import sys
import os
class DB_processor():
    @staticmethod
    def read_csv(path:Path)->pd.DataFrame:
        P=Path(path)
        path_check=P.exists()
        if not path_check:
            print('path is not valid')
            sys.exit(1)
        df=pd.read_csv(path)
        print('Successfully read csv file and return df')
        return df
    
    @staticmethod
    def add_date_column(df:pd.DataFrame)->pd.DataFrame:
        df['open_time_GMT']=pd.to_datetime(df['timeOpen'],unit='ms')
        df['close_time_GMT']=pd.to_datetime(df['timeClose'],unit='ms')
        return df
    
    @staticmethod
    def atr_caculator(df:pd.DataFrame)->pd.DataFrame:
       df=df.copy()
       high_low=df['priceHigh']-df['priceLow']
       high_close=abs(df['priceHigh']-df['priceClose'].shift(1))
       low_close=abs(df['priceLow']-df['priceClose'].shift(1))
       df['TR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
       df['ATR'] = df['TR'].rolling(window=20).mean()
       return df
    
    @staticmethod
    def turtle_indicators(df:pd.DataFrame)->pd.DataFrame:
        df=df.copy()
        df['highest_20']=df['priceHigh'].rolling(window=20).max()
        df['lowest_20']=df['priceLow'].rolling(window=20).min()
        df['highest_55']=df['priceHigh'].rolling(window=55).max()
        df['lowest_55']=df['priceLow'].rolling(window=55).min()
        df['long_signal_20'] = df['priceHigh'] > df['highest_20'].shift(1)
        df['short_signal_20'] = df['priceHigh'] < df['lowest_20'].shift(1)
        df['long_signal_55'] = df['priceLow'] > df['highest_55'].shift(1)
        df['short_signal_55'] = df['priceLow'] < df['lowest_55'].shift(1)
        return df

    @staticmethod
    def export_to_csv(df:pd.DataFrame,path:Path):
        df.to_csv(path,index=False)
        print('Export successfully')

    
