from .config import Config
from .db_processor import DB_processor
import sys
import pandas as pd 
from .strategy import TurtleStrategy
from .backtester import Backtester
import backtrader as bt

def main():
    config = Config()
    '''
    df=DB_processor.read_csv(config.china300_file)
      
    for col in ['close', 'open', 'high', 'low']:
           df[col] = df[col].str.replace(',', '').astype(float)
    DB_processor.export_to_csv(df,'/home/litterpigger/myprojects/BTC_backtest/data/china300.csv')
        
    ''' 
    args=Config.arg()
    symbol=args[0]
    if symbol.upper()=='BTC':
        df=DB_processor.read_csv(config.btc_file)
    elif symbol.upper()=='CHINA300':
        df=DB_processor.read_csv(config.china300_file)
    else:
        print('Input does not meet requirements, please read readme file')
        sys.exit(1)

    strategy_param=args[1].split('_')
    if len(strategy_param) !=2:
        print('Not a valid arg format for strategy arg')
        sys.exit(1)
    
    period=int(strategy_param[1])
    print(df.head())
    print(df.index.name)

    data=Backtester(df).get_data_pd()
    cerebro=bt.Cerebro()
    cerebro.adddata(data)
    cerebro.run()
     
    cerebro=bt.Cerebro()
    cerebro.adddata(data)
  
    cerebro.addstrategy(TurtleStrategy,period_high=period)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.broker.setcash(10_000_000)  # 设置初始资金为1000万
    cerebro.broker.setcommission(leverage=20.0)
    cerebro.broker.set_slippage_fixed(1)
    print('初始资金: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    
    # 输出分析结果
    print('最终资金: %.2f' % cerebro.broker.getvalue())
    print('夏普比率:', strat.analyzers.sharpe.get_analysis()['sharperatio'])
    print('最大回撤: %.2f%%' % strat.analyzers.drawdown.get_analysis()['max']['drawdown'])
    print('年化收益: %.2f%%' % (strat.analyzers.returns.get_analysis()['rnorm100']))
    
    # 绘制结果
    cerebro.plot(style='candle', volume=False)
    cerebro.plot(style='bar')
    
main()