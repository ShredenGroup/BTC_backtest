from .strategy import TurtleStrategy
from .mockAccount import MockAccount
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
class Backtest:

    def __init__(self, df: pd.DataFrame, strategy: TurtleStrategy):
        """
        回测系统
        
        Args:
            df: 数据DataFrame
            strategy: 策略实例(System 1或System 2)
        """
        self.df = df.copy()  # 复制数据避免修改原始DataFrame
        self.strategy = strategy
        self.system_number = strategy.system
        self.trade_history: List[Dict] = []
        self.equity_curve = []  # 记录权益曲线
        self.drawdowns = []     # 记录回撤
        
    def run(self):
        """执行回测"""
        # 记录初始权益
        self.equity_curve.append({
            'datetime': self.df.index[0],
            'equity': self.strategy.account.current_balance,
            'drawdown': 0.0
        })
        
        max_equity = self.strategy.account.current_balance
        
        for index, row in self.df.iterrows():
            # 跳过ATR为空的数据
            if pd.isna(row['ATR']):
                continue
                
            # 执行策略
            action = self.strategy.on_bar(row)
            
            # 记录交易
            if action != "HOLD":
                self.trade_history.append({
                    'datetime': index,
                    'action': action,
                    'price': row['priceClose'],
                    'balance': self.strategy.account.current_balance,
                    'position': self.strategy.account.position,
                    'units': self.strategy.units,
                    'stop_loss': self.strategy.stop_loss
                })
            
            # 更新权益曲线和回撤
            current_equity = self.strategy.account.current_balance
            if self.strategy.account.position != 0:
                # 如果有持仓，计算未实现盈亏
                unrealized_pnl = self.strategy.account.position * (
                    row['priceClose'] - self.strategy.account.entry_price
                )
                current_equity += unrealized_pnl
            
            max_equity = max(max_equity, current_equity)
            drawdown = (max_equity - current_equity) / max_equity * 100
            
            self.equity_curve.append({
                'datetime': index,
                'equity': current_equity,
                'drawdown': drawdown
            })
            self.drawdowns.append(drawdown)
    
    def get_results(self) -> Dict:
        """获取回测结果统计"""
        account = self.strategy.account
        trades = account.trades
        
        # 计算交易统计
        profitable_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        # 计算平均利润和亏损
        avg_profit = np.mean([t['pnl'] for t in profitable_trades]) if profitable_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        # 计算最大回撤
        max_drawdown = max(self.drawdowns) if self.drawdowns else 0
        
        # 计算夏普比率 (假设无风险利率为0)
        if len(self.equity_curve) > 1:
            returns = pd.Series([e['equity'] for e in self.equity_curve]).pct_change().dropna()
            sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std()) if len(returns) > 0 else 0
        else:
            sharpe_ratio = 0
            
        return {
            'system': f"System {self.system_number}",
            'initial_balance': account.initial_balance,
            'final_balance': account.current_balance,
            'return_pct': (account.current_balance / account.initial_balance - 1) * 100,
            'total_trades': len(trades),
            'profitable_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(profitable_trades) / len(trades) if trades else 0,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_profit / avg_loss) if avg_loss != 0 else float('inf'),
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'trade_history': self.trade_history,
            'equity_curve': self.equity_curve
        }
        
    @staticmethod
    def compare_systems(results1: Dict, results2: Dict) -> pd.DataFrame:
        """比较两个系统的表现"""
        metrics = [
            'return_pct', 'total_trades', 'win_rate', 
            'profit_factor', 'max_drawdown', 'sharpe_ratio'
        ]
        
        comparison = pd.DataFrame({
            'System 1': [results1[m] for m in metrics],
            'System 2': [results2[m] for m in metrics]
        }, index=metrics)
        
        return comparison
        
    def plot_results(self):
        """绘制回测结果图表"""
        
        # 创建子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[2, 1])
        
        # 绘制权益曲线
        dates = [e['datetime'] for e in self.equity_curve]
        equity = [e['equity'] for e in self.equity_curve]
        ax1.plot(dates, equity, label=f'System {self.system_number} Equity')
        ax1.set_title('Equity Curve')
        ax1.legend()
        
        # 绘制回撤
        drawdowns = [e['drawdown'] for e in self.equity_curve]
        ax2.fill_between(dates, drawdowns, 0, alpha=0.3, color='red')
        ax2.set_title('Drawdown (%)')
        
        plt.tight_layout()
        plt.show()

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
        # 创建图表
        fig = plt.figure(figsize=(15, 10))
        
        # 创建子图
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        
        # 1. 绘制价格和交易点位
        ax1.plot(df.index, df['priceClose'], label='BTC Price', color='gray', alpha=0.7)
        
        # 标记交易点位
        long_points = []
        short_points = []
        stop_points = []
        
        for trade in results['trade_history']:
            if trade['action'] == 'LONG':
                long_points.append((trade['datetime'], trade['price']))
            elif trade['action'] == 'SHORT':
                short_points.append((trade['datetime'], trade['price']))
            elif trade['action'] == 'STOP':
                stop_points.append((trade['datetime'], trade['price']))
        
        # 绘制交易点位
        if long_points:
            lp = np.array(long_points)
            ax1.scatter(lp[:, 0], lp[:, 1], marker='^', color='green', s=100, label='Long')
        if short_points:
            sp = np.array(short_points)
            ax1.scatter(sp[:, 0], sp[:, 1], marker='v', color='red', s=100, label='Short')
        if stop_points:
            stp = np.array(stop_points)
            ax1.scatter(stp[:, 0], stp[:, 1], marker='x', color='black', s=100, label='Stop')
        
        ax1.set_title(f'System {system_number} Trading Signals')
        ax1.set_ylabel('Price')
        ax1.grid(True)
        ax1.legend()
        
        # 2. 绘制权益曲线
        equity_data = pd.DataFrame(results['equity_curve'])
        ax2.plot(equity_data['datetime'], equity_data['equity'], 
                label='Equity', color='blue')
        ax2.set_title('Equity Curve')
        ax2.set_ylabel('Account Value')
        ax2.grid(True)
        ax2.legend()
        
        # 3. 绘制回撤
        drawdowns = equity_data['drawdown']
        ax3.fill_between(equity_data['datetime'], drawdowns, 0, 
                        alpha=0.3, color='red', label='Drawdown')
        ax3.set_title('Drawdown')
        ax3.set_ylabel('Drawdown %')
        ax3.grid(True)
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
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        return plt.gcf()