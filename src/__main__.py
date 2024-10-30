from .config import Config
from .db_processor import DB_processor
import sys
import pandas as pd 
from .mockAccount import MockAccount
from .strategy import TurtleStrategy
from .backtester import Backtester
import backtrader as bt

def main():
    config = Config()
    df = DB_processor.read_csv(config.btc_file)
    print(df.head())
    data=Backtester(df).get_data_pd()
    
    cerebro=bt.Cerebro()
    cerebro.adddata(data)
    datas = cerebro.datas
    print(f"Number of data feeds: {len(datas)}") 
     
main()