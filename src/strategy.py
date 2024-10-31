import backtrader as bt
import pandas as pd

class TurtleStrategy(bt.Strategy):
   params = (
       ('period_high', 100),     # 入场周期
       ('period_low', 10),      # 退出周期
       ('atr_period', 20),      # ATR周期
       ('atr_multiple_entry', 0.5),  # 加仓ATR倍数
       ('atr_multiple_exit', 2.0),   # 止损ATR倍数
       ('max_add', 3),          # 最大加仓次数
   )

   def __init__(self):
       # 数据
       self.data_close = self.datas[0].close
       self.data_high = self.datas[0].high
       self.data_low = self.datas[0].low
       
       # 计算指标
       self.atr = bt.indicators.ATR(self.datas[-1], period=self.p.atr_period)
       self.highest_55 = bt.indicators.Highest(self.data_high(-1), period=self.p.period_high)
       self.lowest_55 = bt.indicators.Lowest(self.data_low(-1), period=self.p.period_high)
       self.highest_10 = bt.indicators.Highest(self.data_high(-1), period=self.p.period_low)
       self.lowest_10 = bt.indicators.Lowest(self.data_low(-1), period=self.p.period_low)
       
       # 交易状态
       self.order = None
       self.entry_price = 0     # 入场价格
       self.stop_loss = 0       # 止损价格
       self.add_count = 0       # 加仓次数
       self.position_type = 0   # 1为多头，-1为空头，0为无持仓
       
   def log(self, txt, dt=None):
       dt = dt or self.datas[0].datetime.date(0)
       print(f'{dt.isoformat()} {txt} [Account Value: {self.broker.getvalue():.2f}]')
       
   def notify_order(self, order):
       if order.status in [order.Submitted, order.Accepted]:
           return

       if order.status in [order.Completed]:
           if order.isbuy():
               self.log(f'LONG EXECUTED --- Price: {order.executed.price:.2f}, '
                       f'Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}, '
                       f'Size: {order.executed.size:.0f}, ATR: {self.atr[-1]:.2f}, '
                       f'Margin: {self.broker.getvalue() - self.broker.getcash():.2f}')
               if self.add_count == 0:  # 首次入场
                   self.entry_price = order.executed.price
                   if self.position_type == 1:  # 多头
                       self.stop_loss = self.entry_price - self.p.atr_multiple_exit * self.atr[-1]
                   else:  # 空头
                       self.stop_loss = self.entry_price + self.p.atr_multiple_exit * self.atr[-1]
               else:  # 加仓，更新止损
                   if self.position_type == 1:  # 多头
                       self.stop_loss += 0.5 * self.atr[-1]  # 止损上移
                   else:  # 空头
                       self.stop_loss -= 0.5 * self.atr[-1]  # 止损下移
               
           else:  # 卖出
               self.log(f'SHORT/CLOSE EXECUTED --- Price: {order.executed.price:.2f}, '
                       f'Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}, '
                       f'Size: {order.executed.size:.0f}, '
                       f'Margin: {self.broker.getvalue() - self.broker.getcash():.2f}')
               if not self.position:  # 如果已经没有仓位，重置所有状态
                   self.add_count = 0
                   self.stop_loss = 0
                   self.position_type = 0

       elif order.status in [order.Canceled, order.Margin, order.Rejected]:
           self.log('Order Canceled/Margin/Rejected')

       self.order = None

   def next(self):
       if self.order:
           return
           
       unit = int(400_000 / self.atr[-1])
       
       # 没有持仓
       if not self.position:
           # 多头入场信号
           if self.data_high[0] > self.highest_55[0]:
               self.log(f'LONG ENTRY: Current High: {self.data_high[0]:.2f}, '
                       f'55 Day High: {self.highest_55[0]:.2f}')
               self.order = self.buy(size=unit)
               self.add_count = 0
               self.position_type = 1
               
           # 空头入场信号
           elif self.data_low[0] < self.lowest_55[0]:
               self.log(f'SHORT ENTRY: Current Low: {self.data_low[0]:.2f}, '
                       f'55 Day Low: {self.lowest_55[0]:.2f}')
               self.order = self.sell(size=unit)
               self.add_count = 0
               self.position_type = -1
               
       # 有持仓
       else:
           # 多头持仓
           if self.position_type == 1:
               # 多头加仓
               if self.add_count < self.p.max_add:
                   if self.data_high[0] > self.entry_price + self.p.atr_multiple_entry * self.atr[-1]:
                       self.log(f'ADD LONG --- Current High: {self.data_high[0]:.2f}, '
                               f'Target: {self.entry_price + self.p.atr_multiple_entry * self.atr[-1]:.2f}')
                       self.order = self.buy(size=unit)
                       self.add_count += 1
               
               # 多头止损
               if self.data_low[0] < self.stop_loss:
                   self.log(f'LONG STOP LOSS --- Current Low: {self.data_low[0]:.2f}, '
                           f'Stop: {self.stop_loss:.2f}')
                   self.order = self.close()
                   
               # 多头止盈
               elif self.data_low[0] < self.lowest_10[0]:
                   self.log(f'LONG TAKE PROFIT --- Current Low: {self.data_low[0]:.2f}, '
                           f'10 Day Low: {self.lowest_10[0]:.2f}')
                   self.order = self.close()
           
           # 空头持仓
           else:
               # 空头加仓
               if self.add_count < self.p.max_add:
                   if self.data_low[0] < self.entry_price - self.p.atr_multiple_entry * self.atr[-1]:
                       self.log(f'ADD SHORT --- Current Low: {self.data_low[0]:.2f}, '
                               f'Target: {self.entry_price - self.p.atr_multiple_entry * self.atr[-1]:.2f}')
                       self.order = self.sell(size=unit)
                       self.add_count += 1
               
               # 空头止损
               if self.data_high[0] > self.stop_loss:
                   self.log(f'SHORT STOP LOSS --- Current High: {self.data_high[0]:.2f}, '
                           f'Stop: {self.stop_loss:.2f}')
                   self.order = self.close()
                   
               # 空头止盈
               elif self.data_high[0] > self.highest_10[0]:
                   self.log(f'SHORT TAKE PROFIT --- Current High: {self.data_high[0]:.2f}, '
                           f'10 Day High: {self.highest_10[0]:.2f}')
                   self.order = self.close()