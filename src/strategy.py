from .mockAccount import MockAccount
import pandas as pd
import numpy as np
class TurtleStrategy:
    def __init__(self, account: MockAccount, system: int = 1):
        """
        海龟交易策略
        
        Args:
            account: MockAccount实例
            system: 使用的系统(1或2)
                   System 1: 20日突破
                   System 2: 55日突破
        """
        self.account = account
        self.system = system
        self.current_atr = 0.0
        self.stop_loss = 0.0
        self.units = 0
        self.unit_prices: List[float] = []
        self.last_add_price = 0.0
        
    def calculate_unit_size(self, price: float, atr: float) -> float:
        """计算单位大小"""
        risk_amount = self.account.current_balance * 0.01  # 1%风险
        dollar_volatility = atr * 2  # 2N止损
        position_size = risk_amount / dollar_volatility
        contract_size = position_size / price * self.account.leverage
        return np.floor(contract_size * 100) / 100  # 向下取整到0.01
        
    def on_bar(self, row: pd.Series) -> str:
        """
        处理每根K线
        
        Args:
            row: 当前K线数据
        Returns:
            str: 交易动作
        """
        action = "HOLD"
        self.current_atr = row['ATR']
        
        # 1. 检查止损
        if self.account.position != 0:
            if self.should_stop_loss(row['priceClose']):
                self.account.close_position(row['priceClose'])
                self.reset_position_info()
                return "STOP"
                
        # 2. 检查加仓
        if self.account.position != 0:
            if self.should_add_unit(row['priceClose']):
                size = self.calculate_unit_size(row['priceClose'], row['ATR'])
                if self.account.open_position(row['priceClose'], size, 
                                           np.sign(self.account.position)):
                    self.units += 1
                    self.unit_prices.append(row['priceClose'])
                    self.last_add_price = row['priceClose']
                    return "ADD"
        
        # 3. 检查入场信号
        # System 1: 20日突破
        if self.system == 1:
            if row['long_signal_20']:
                size = self.calculate_unit_size(row['priceClose'], row['ATR'])
                if self.account.open_position(row['priceClose'], size, 1):
                    self.units = 1
                    self.unit_prices = [row['priceClose']]
                    self.last_add_price = row['priceClose']
                    self.stop_loss = row['priceClose'] - 2 * row['ATR']
                    return "LONG"
                    
            elif row['short_signal_20']:
                size = self.calculate_unit_size(row['priceClose'], row['ATR'])
                if self.account.open_position(row['priceClose'], size, -1):
                    self.units = 1
                    self.unit_prices = [row['priceClose']]
                    self.last_add_price = row['priceClose']
                    self.stop_loss = row['priceClose'] + 2 * row['ATR']
                    return "SHORT"
                    
        # System 2: 55日突破
        elif self.system == 2:
            if row['long_signal_55']:
                size = self.calculate_unit_size(row['priceClose'], row['ATR'])
                if self.account.open_position(row['priceClose'], size, 1):
                    self.units = 1
                    self.unit_prices = [row['priceClose']]
                    self.last_add_price = row['priceClose']
                    self.stop_loss = row['priceClose'] - 2 * row['ATR']
                    return "LONG"
                    
            elif row['short_signal_55']:
                size = self.calculate_unit_size(row['priceClose'], row['ATR'])
                if self.account.open_position(row['priceClose'], size, -1):
                    self.units = 1
                    self.unit_prices = [row['priceClose']]
                    self.last_add_price = row['priceClose']
                    self.stop_loss = row['priceClose'] + 2 * row['ATR']
                    return "SHORT"
                    
        return action

    def should_stop_loss(self, price: float) -> bool:
        """检查是否触发止损"""
        if self.account.position > 0:
            return price < self.stop_loss
        elif self.account.position < 0:
            return price > self.stop_loss
        return False
    
    def should_add_unit(self, price: float) -> bool:
        """检查是否可以加仓"""
        if self.units >= 4:  # 最多4个单位
            return False
            
        if self.account.position > 0:
            return price >= self.last_add_price + 0.5 * self.current_atr
        elif self.account.position < 0:
            return price <= self.last_add_price - 0.5 * self.current_atr
        return False
    
    def reset_position_info(self):
        """重置持仓相关信息"""
        self.units = 0
        self.unit_prices = []
        self.last_add_price = 0
        self.stop_loss = 0