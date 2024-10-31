import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional

class MockAccount:
    def __init__(self, initial_balance: float = 10_000_000, leverage: float = 20, fee_rate: float = 0.0002):
        """
        模拟交易账户
        
        Args:
            initial_balance: 初始资金
            leverage: 杠杆倍数
            fee_rate: 交易费率（包含滑点）
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.leverage = leverage
        self.fee_rate = fee_rate
        
        # 持仓信息
        self.position = 0.0  # 当前持仓数量
        self.entry_price = 0.0  # 开仓均价
        self.unrealized_pnl = 0.0  # 未实现盈亏
        
        # 交易记录
        self.trades: List[Dict] = []
    
    def can_trade(self, price: float, size: float) -> bool:
       
        margin_needed = (price * abs(size)) / self.leverage
        return margin_needed <= self.current_balance * 0.95
    
    def open_position(self, price: float, size: float, direction: int) -> bool:
        """
        开仓
        
        Args:
            price: 开仓价格
            size: 开仓数量
            direction: 方向(1:多头, -1:空头)
        """
        if not self.can_trade(price, size):
            return False
            
        # 计算费用
        fee = price * abs(size) * self.fee_rate
        
        # 更新持仓
        self.position += size * direction
        self.entry_price = price
        self.current_balance -= fee
        
        # 记录交易
        self.trades.append({
            'type': 'open',
            'datetime': None,  # 在Strategy中设置
            'price': price,
            'size': size * direction,
            'fee': fee,
            'balance': self.current_balance
        })
        
        return True
    
    def close_position(self, price: float) -> Optional[float]:
        """
        平仓
        
        Args:
            price: 平仓价格
        Returns:
            float: 交易盈亏
        """
        if self.position == 0:
            return None
            
        # 计算盈亏和费用
        size = abs(self.position)
        fee = price * size * self.fee_rate
        
        if self.position > 0:
            pnl = (price - self.entry_price) * size
        else:
            pnl = (self.entry_price - price) * size
            
        # 更新账户
        self.current_balance += pnl - fee
        self.position = 0
        self.entry_price = 0
        
        # 记录交易
        self.trades.append({
            'type': 'close',
            'datetime': None,  # 在Strategy中设置
            'price': price,
            'size': -self.position,
            'pnl': pnl,
            'fee': fee,
            'balance': self.current_balance
        })
        
        return pnl
class BacktestVisualizer:
    @staticmethod
    def plot_backtest_results(df: pd.DataFrame, results: Dict, system_number: int):
        """
        绘制回测结果
        
        Args:
            df: 原始数据DataFrame
            results: 回测结果字典
            system_number: 系统编号(1或2)
        """
        # 设置图表风格
        plt.style.use('seaborn')
        fig = plt.figure(figsize=(15, 10))
        
        # 创建子图
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        
        # 1. 绘制价格和交易点位
        ax1.plot(df.index, df['priceClose'], label='BTC Price', color='gray', alpha=0.7)
        
        # 标记交易点位
        for trade in results['trade_history']:
            if trade['action'] == 'LONG':
                ax1.scatter(trade['datetime'], trade['price'], 
                          marker='^', color='green', s=100, label='Long')
            elif trade['action'] == 'SHORT':
                ax1.scatter(trade['datetime'], trade['price'], 
                          marker='v', color='red', s=100, label='Short')
            elif trade['action'] == 'STOP':
                ax1.scatter(trade['datetime'], trade['price'], 
                          marker='x', color='black', s=100, label='Stop')
                
        ax1.set_title(f'System {system_number} Trading Signals')
        ax1.set_ylabel('Price')
        handles, labels = ax1.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax1.legend(by_label.values(), by_label.keys())
        
        # 2. 绘制权益曲线
        equity_data = pd.DataFrame(results['equity_curve'])
        ax2.plot(equity_data['datetime'], equity_data['equity'], 
                label='Equity', color='blue')
        ax2.set_title('Equity Curve')
        ax2.set_ylabel('Account Value')
        ax2.legend()
        
        # 3. 绘制回撤
        drawdowns = equity_data['drawdown']
        ax3.fill_between(equity_data['datetime'], drawdowns, 0, 
                        alpha=0.3, color='red', label='Drawdown')
        ax3.set_title('Drawdown')
        ax3.set_ylabel('Drawdown %')
        ax3.legend()
        
        # 添加性能指标文本
        performance_text = (
            f"Return: {results['return_pct']:.2f}%\n"
            f"Sharpe Ratio: {results['sharpe_ratio']:.2f}\n"
            f"Max Drawdown: {results['max_drawdown']:.2f}%\n"
            f"Win Rate: {results['win_rate']*100:.2f}%\n"
            f"Total Trades: {results['total_trades']}"
        )
        plt.figtext(0.02, 0.02, performance_text, fontsize=10, 
                   bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def compare_systems(results1: Dict, results2: Dict):
        """比较两个系统的性能"""
        # 创建比较图表
        plt.figure(figsize=(12, 6))
        
        # 提取要比较的指标
        metrics = {
            'Return (%)': ['return_pct', 100],
            'Win Rate (%)': ['win_rate', 100],
            'Sharpe Ratio': ['sharpe_ratio', 1],
            'Max Drawdown (%)': ['max_drawdown', 1],
            'Total Trades': ['total_trades', 1]
        }
        
        # 准备数据
        system1_data = []
        system2_data = []
        labels = []
        
        for label, (metric, multiplier) in metrics.items():
            system1_data.append(results1[metric] * multiplier)
            system2_data.append(results2[metric] * multiplier)
            labels.append(label)
            
        # 创建条形图
        x = range(len(labels))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], system1_data, width, 
                label='System 1', alpha=0.7)
        plt.bar([i + width/2 for i in x], system2_data, width, 
                label='System 2', alpha=0.7)
        
        plt.ylabel('Value')
        plt.title('System Comparison')
        plt.xticks(x, labels, rotation=45)
        plt.legend()
        
        plt.tight_layout()
        return plt.gcf()

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

if __name__ == "__main__":
    main()