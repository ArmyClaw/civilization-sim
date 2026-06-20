"""
支持货币系统的Agent模块
继承自基础Agent，添加现金、银行账户等货币相关功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from .agent import Agent, Profession
from .currency_system import CurrencyType
from .agent import ResourceType


class AgentWithCurrency(Agent):
    """支持货币系统的Agent类"""
    
    def __init__(self, agent_id: int, x: int, y, tile, profession: Profession = Profession.GATHERER):
        super().__init__(agent_id, x, y, tile, profession)
        
        # 货币相关属性
        self.cash: dict = {}  # 现金余额 {CurrencyType: amount}
        self.bank_account: dict = {}  # 银行账户余额 {CurrencyType: amount}
        self.preferred_currency: CurrencyType = CurrencyType.GOLD_COIN  # 偏好货币类型
        self.currency_trust: dict = {curr_type: 0.5 for curr_type in CurrencyType}  # 对各种货币的信任度
        
        # 贸易相关扩展
        self.trade_history = []  # 交易历史
        self.currency_trades = 0  # 货币交易次数
        self.barter_trades = 0  # 物物交换次数
        
        # 货币适应性
        self.monetary_adaptation_level = 0.0  # 货币适应性 (0-1)
        self.learning_rate = 0.1  # 学习速率
    
    def initialize_currency(self):
        """初始化货币（首次使用货币系统时调用）"""
        # 给每个Agent一些初始金币（模拟早期货币）
        initial_gold = 10.0  # 初始10金币
        self.cash[CurrencyType.GOLD_COIN] = self.cash.get(CurrencyType.GOLD_COIN, 0) + initial_gold
        
        # 设置初始偏好金币
        self.preferred_currency = CurrencyType.GOLD_COIN
        self.currency_trust[CurrencyType.GOLD_COIN] = 1.0
        
        print(f"Agent {self.id} 初始化货币系统，获得 {initial_gold} 金币")
    
    def exchange_currency(self, from_curr_type: CurrencyType, to_curr_type: CurrencyType, 
                          amount: float, exchange_rate: float = None) -> bool:
        """货币兑换"""
        if from_curr_type not in self.cash or self.cash[from_curr_type] < amount:
            return False
        
        # 如果没有提供兑换率，使用标准兑换率
        if exchange_rate is None:
            exchange_rate = self._get_standard_exchange_rate(from_curr_type, to_curr_type)
        
        # 计算兑换金额
        exchanged_amount = amount * exchange_rate
        
        # 执行兑换
        self.cash[from_curr_type] -= amount
        self.cash[to_curr_type] = self.cash.get(to_curr_type, 0) + exchanged_amount
        
        # 更新信任度（成功的兑换增加信任）
        success_rate = 0.95 if exchanged_amount > 0 else 0.5
        self.currency_trust[to_curr_type] = min(1.0, 
                                               self.currency_trust[to_curr_type] + 
                                               self.learning_rate * success_rate)
        
        # 记录交易
        self.trade_history.append({
            'type': 'currency_exchange',
            'from_currency': from_curr_type.value,
            'to_currency': to_curr_type.value,
            'amount': amount,
            'exchanged_amount': exchanged_amount,
            'rate': exchange_rate
        })
        
        return True
    
    def _get_standard_exchange_rate(self, from_curr_type: CurrencyType, 
                                  to_curr_type: CurrencyType) -> float:
        """获取标准兑换率"""
        # 简化的兑换率
        rates = {
            (CurrencyType.GOLD_COIN, CurrencyType.SILVER_COIN): 0.8,
            (CurrencyType.GOLD_COIN, CurrencyType.CROP_NOTE): 0.6,
            (CurrencyType.GOLD_COIN, CurrencyType.CRAFT_TOKEN): 0.7,
            (CurrencyType.SILVER_COIN, CurrencyType.GOLD_COIN): 1.25,
            (CurrencyType.CROP_NOTE, CurrencyType.GOLD_COIN): 1.67,
            (CurrencyType.CRAFT_TOKEN, CurrencyType.GOLD_COIN): 1.43
        }
        return rates.get((from_curr_type, to_curr_type), 1.0)
    
    def make_purchase(self, item_type, quantity: int, price: float, 
                     currency_type: CurrencyType) -> bool:
        """使用货币购买物品"""
        if currency_type not in self.cash or self.cash[currency_type] < price:
            return False
        
        # 扣除货币
        self.cash[currency_type] -= price
        
        # 添加物品到背包
        if item_type in [ResourceType.FOOD, ResourceType.WATER, ResourceType.WOOD, ResourceType.MINERAL]:
            self.inventory[item_type] = self.inventory.get(item_type, 0) + quantity
            self.currency_trades += 1
            
            # 记录交易
            self.trade_history.append({
                'type': 'purchase',
                'item_type': item_type.value,
                'quantity': quantity,
                'currency': currency_type.value,
                'price': price
            })
            
            return True
        return False
    
    def make_sale(self, item_type, quantity: int, price: float, 
                  currency_type: CurrencyType) -> bool:
        """出售物品获得货币"""
        # 检查是否有足够物品
        if item_type not in self.inventory or self.inventory[item_type] < quantity:
            return False
        
        # 扣除物品
        self.inventory[item_type] -= quantity
        
        # 获得货币
        self.cash[currency_type] = self.cash.get(currency_type, 0) + price
        self.currency_trades += 1
        
        # 记录交易
        self.trade_history.append({
            'type': 'sale',
            'item_type': item_type.value,
            'quantity': quantity,
            'currency': currency_type.value,
            'price': price
        })
        
        return True
    
    def deposit_to_bank(self, currency_type: CurrencyType, amount: float) -> bool:
        """存入银行"""
        if currency_type not in self.cash or self.cash[currency_type] < amount:
            return False
        
        # 从现金扣除
        self.cash[currency_type] -= amount
        
        # 存入银行账户
        self.bank_account[currency_type] = self.bank_account.get(currency_type, 0) + amount
        
        # 记录
        self.trade_history.append({
            'type': 'deposit',
            'currency': currency_type.value,
            'amount': amount
        })
        
        return True
    
    def withdraw_from_bank(self, currency_type: CurrencyType, amount: float) -> bool:
        """从银行取款"""
        if currency_type not in self.bank_account or self.bank_account[currency_type] < amount:
            return False
        
        # 从银行扣除
        self.bank_account[currency_type] -= amount
        
        # 获得现金
        self.cash[currency_type] = self.cash.get(currency_type, 0) + amount
        
        # 记录
        self.trade_history.append({
            'type': 'withdraw',
            'currency': currency_type.value,
            'amount': amount
        })
        
        return True
    
    def get_total_wealth(self, currency_type: CurrencyType = CurrencyType.GOLD_COIN) -> float:
        """计算总财富"""
        # 现金价值
        cash_value = self.cash.get(currency_type, 0)
        
        # 银行存款价值
        bank_value = self.bank_account.get(currency_type, 0)
        
        # 物品价值（简化计算）
        item_value = 0
        item_prices = {
            ResourceType.FOOD: 1.0,
            ResourceType.WATER: 1.2,
            ResourceType.WOOD: 0.8,
            ResourceType.MINERAL: 2.0
        }
        for item_type, quantity in self.inventory.items():
            item_value += item_prices.get(item_type, 0) * quantity
        
        # 转换为目标货币
        if currency_type != CurrencyType.GOLD_COIN:
            exchange_rate = self._get_standard_exchange_rate(currency_type, CurrencyType.GOLD_COIN)
            cash_value *= exchange_rate
            bank_value *= exchange_rate
            item_value *= exchange_rate
        
        return cash_value + bank_value + item_value
    
    def update_monetary_adaptation(self, success: bool):
        """更新货币适应性"""
        if success:
            # 成功交易提高适应性
            self.monetary_adaptation_level = min(1.0, self.monetary_adaptation_level + self.learning_rate * 0.1)
        else:
            # 失败交易降低适应性
            self.monetary_adaptation_level = max(0.0, self.monetary_adaptation_level - self.learning_rate * 0.05)
    
    def decide_currency_use(self, transaction_value: float) -> bool:
        """决定是否使用货币进行交易"""
        # 高价值交易更倾向于使用货币
        if transaction_value > 20:
            return True
        
        # 货币适应性高的Agent更倾向于使用货币
        if self.monetary_adaptation_level > 0.7:
            return True
        
        # 根据职业倾向
        if self.profession == Profession.CRAFTSMAN or self.profession == Profession.FARMER:
            return True
        
        return False
    
    def get_currency_status(self) -> dict:
        """获取货币状态"""
        return {
            'cash': {curr_type.value: amount for curr_type, amount in self.cash.items()},
            'bank_account': {curr_type.value: amount for curr_type, amount in self.bank_account.items()},
            'total_wealth': self.get_total_wealth(),
            'preferred_currency': self.preferred_currency.value,
            'monetary_adaptation': self.monetary_adaptation_level,
            'currency_trades': self.currency_trades,
            'barter_trades': self.barter_trades,
            'trade_history': len(self.trade_history)
        }