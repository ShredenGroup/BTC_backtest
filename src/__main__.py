from .config import Config
from .db_processor import DB_processor
import sys
import pandas as pd 
from .mockAccount import MockAccount
from .strategy import TurtleStrategy
from .backtest import Backtest,BacktestVisualizer
import matplotlib.pyplot as plt

def main():
    config = Config()
    df = DB_processor.read_csv(config.btc_file)
    
    # System 1: 20日突破系统
    account1 = MockAccount(initial_balance=10_000_000, leverage=20, fee_rate=0.0002)
    strategy1 = TurtleStrategy(account1, system=1)
    backtest1 = Backtest(df, strategy1)
    
    # System 2: 55日突破系统
    account2 = MockAccount(initial_balance=10_000_000, leverage=20, fee_rate=0.0002)
    strategy2 = TurtleStrategy(account2, system=2)
    backtest2 = Backtest(df, strategy2)
    
    # 运行回测
    backtest1.run()
    backtest2.run()
    
    # 获取结果
    results1 = backtest1.get_results()
    results2 = backtest2.get_results()
    
    # 创建可视化实例
    visualizer = BacktestVisualizer()
    
    # 绘制每个系统的详细结果
    fig1 = visualizer.plot_backtest_results(df, results1, 1)
    fig2 = visualizer.plot_backtest_results(df, results2, 2)
    
    # 绘制系统比较
    fig3 = visualizer.compare_systems(results1, results2)
    
    # 显示图表
    plt.show()
    
    # 打印详细结果
    print("\nSystem 1 Results:")
    print(results1)
    print("\nSystem 2 Results:")
    print(results2)
main()