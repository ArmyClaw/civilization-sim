"""
货币系统模块
实现货币的引入和演化，从物物交换向货币经济过渡
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import math
import random
from .economy import Economy, ItemType, Market, TradingPost
from .agent import Agent, ResourceType


class CurrencyType(Enum):
    """货币类型枚举"""
    GOLD_COIN = "gold_coin"     # 金币
    SILVER_COIN = "silver_coin" # 银币
    CROP_NOTE = "crop_note"     # 庄票（农作物票据）
    CRAFT_TOKEN = "craft_token"  # 工匠代币


class Money:
    """货币类"""
    def __init__(self, currency_type: CurrencyType, value: float = 1.0):
        self.currency_type = currency_type
        self.value = value  # 货币面值
        self.stability = 1.0  # 稳定性指数 (0-1)
        self.issuer = None  # 发行者（可选）
        
    def get_effective_value(self, economic_context: Dict) -> float:
        """获取实际价值（考虑经济环境）"""
        # 基础价值
        base_value = self.value
        
        # 考虑稳定性
        stability_factor = self.stability
        
        # 考虑货币类型价值
        type_values = {
            CurrencyType.GOLD_COIN: 1.0,
            CurrencyType.SILVER_COIN: 0.8,
            CurrencyType.CROP_NOTE: 0.6,
            CurrencyType.CRAFT_TOKEN: 0.7
        }
        type_factor = type_values.get(self.currency_type, 1.0)
        
        # 综合计算
        effective_value = base_value * stability_factor * type_factor
        
        return max(0.1, effective_value)


class CurrencyExchange:
    """货币兑换所 - 实现不同货币类型和物品的兑换"""
    def __init__(self, economy: Economy):
        self.economy = economy
        self.exchange_rates: Dict[Tuple[CurrencyType, CurrencyType], float] = {}
        self.reserves: Dict[CurrencyType, float] = {}  # 货币储备
        self.exchange_history: List[Dict] = []
        
        # 初始化货币储备
        for currency_type in CurrencyType:
            self.reserves[currency_type] = 0.0
        
        # 初始化兑换率（金币为基准）
        self._initialize_exchange_rates()
    
    def _initialize_exchange_rates(self):
        """初始化兑换率"""
        # 金币作为基准货币，其他货币相对于金币的价值
        base_rates = {
            (CurrencyType.GOLD_COIN, CurrencyType.SILVER_COIN): 0.8,
            (CurrencyType.GOLD_COIN, CurrencyType.CROP_NOTE): 0.6,
            (CurrencyType.GOLD_COIN, CurrencyType.CRAFT_TOKEN): 0.7,
        }
        
        for (from_curr, to_curr), rate in base_rates.items():
            self.exchange_rates[(from_curr, to_curr)] = rate
            self.exchange_rates[(to_curr, from_curr)] = 1.0 / rate
    
    def get_exchange_rate(self, from_currency: CurrencyType, to_currency: CurrencyType) -> float:
        """获取兑换率"""
        return self.exchange_rates.get((from_currency, to_currency), 1.0)
    
    def exchange_currency(self, agent: Agent, from_currency: CurrencyType, 
                         to_currency: CurrencyType, amount: float) -> bool:
        """货币兑换"""
        if from_currency not in agent.cash or agent.cash[from_currency] < amount:
            return False
        
        # 获取兑换率
        rate = self.get_exchange_rate(from_currency, to_currency)
        exchanged_amount = amount * rate
        
        # 执行兑换
        agent.cash[from_currency] -= amount
        agent.cash[to_currency] = agent.cash.get(to_currency, 0) + exchanged_amount
        
        # 记录兑换历史
        self.exchange_history.append({
            'timestamp': 'now',
            'agent': agent.id,
            'from_currency': from_currency.value,
            'to_currency': to_currency.value,
            'amount': amount,
            'rate': rate,
            'result': exchanged_amount
        })
        
        return True
    
    def create_currency_from_goods(self, agent: Agent, item_type: ItemType, 
                                 quantity: int) -> Optional[CurrencyType]:
        """从货物创建货币（铸币）"""
        # 计算货物价值
        market_price = self.economy.market.get_price(item_type)
        total_value = market_price * quantity
        
        # 根据货物类型决定货币类型
        if item_type in [ItemType.FOOD, ItemType.WATER]:
            # 农作物/水 -> 庄票
            currency_type = CurrencyType.CROP_NOTE
            issued_amount = total_value * 0.8  # 80%的价值转换
        elif item_type == ItemType.WOOD:
            # 木材 -> 工匠代币
            currency_type = CurrencyType.CRAFT_TOKEN
            issued_amount = total_value * 0.9  # 90%的价值转换
        else:
            # 高价值物品 -> 金币
            currency_type = CurrencyType.GOLD_COIN
            issued_amount = total_value * 0.95  # 95%的价值转换
        
        # 发行货币
        agent.cash[currency_type] = agent.cash.get(currency_type, 0) + issued_amount
        
        # 更新储备
        self.reserves[currency_type] += issued_amount
        
        return currency_type
    
    def use_currency_to_buy_goods(self, buyer: Agent, seller: Agent, 
                                 item_type: ItemType, quantity: int,
                                 currency: CurrencyType, amount: float) -> bool:
        """使用货币购买货物"""
        if buyer.cash.get(currency, 0) < amount:
            return False
        
        # 检查卖家是否有足够货物
        required_resource = self._resource_from_item(item_type)
        if seller.inventory.get(required_resource, 0) < quantity:
            return False
        
        # 执行交易
        buyer.cash[currency] -= amount
        seller.cash[currency] = seller.cash.get(currency, 0) + amount * 0.95  # 卖家获得95%
        
        # 转移货物
        seller.inventory[required_resource] -= quantity
        buyer.inventory[required_resource] = buyer.inventory.get(required_resource, 0) + quantity
        
        return True
    
    def _resource_from_item(self, item_type: ItemType) -> ResourceType:
        """物品类型转换为资源类型"""
        mapping = {
            ItemType.FOOD: ResourceType.FOOD,
            ItemType.WATER: ResourceType.WATER,
            ItemType.WOOD: ResourceType.WOOD,
            ItemType.TOOL: ResourceType.MINERAL,  # 简化处理
        }
        return mapping.get(item_type, ResourceType.FOOD)


class Bank:
    """银行类 - 提供货币存储和信贷服务"""
    def __init__(self):
        self.accounts: Dict[int, Dict[CurrencyType, float]] = {}  # Agent账户
        self.loans: Dict[int, Dict] = {}  # 贷款记录
        self.interest_rate = 0.05  # 5%年利率
        self.deposit_interest = 0.02  # 2%存款利率
    
    def create_account(self, agent_id: int):
        """创建银行账户"""
        if agent_id not in self.accounts:
            self.accounts[agent_id] = {}
    
    def deposit(self, agent_id: int, currency_type: CurrencyType, amount: float) -> bool:
        """存款"""
        if agent_id not in self.accounts:
            self.create_account(agent_id)
        
        if self.accounts[agent_id].get(currency_type, 0) >= amount:
            self.accounts[agent_id][currency_type] -= amount
            # 存款增加（简化：自动生息）
            self.accounts[agent_id][currency_type] = self.accounts[agent_id].get(currency_type, 0) + amount * (1 + self.deposit_interest)
            return True
        return False
    
    def withdraw(self, agent_id: int, currency_type: CurrencyType, amount: float) -> bool:
        """取款"""
        if agent_id not in self.accounts:
            self.create_account(agent_id)
        
        if self.accounts[agent_id].get(currency_type, 0) >= amount:
            self.accounts[agent_id][currency_type] -= amount
            return True
        return False
    
    def get_balance(self, agent_id: int, currency_type: CurrencyType) -> float:
        """获取余额"""
        if agent_id not in self.accounts:
            return 0.0
        return self.accounts[agent_id].get(currency_type, 0)
    
    def grant_loan(self, agent_id: int, currency_type: CurrencyType, amount: float) -> bool:
        """发放贷款"""
        # 简化信用评估：基于Agent的健康值
        if agent_id not in self.accounts:
            self.create_account(agent_id)
        
        # 检查还款能力（简化：健康值代表信用）
        max_loan = 50  # 最大贷款金额
        if amount > max_loan:
            return False
        
        # 发放贷款
        self.accounts[agent_id][currency_type] = self.accounts[agent_id].get(currency_type, 0) + amount
        self.loans[agent_id] = {
            'amount': amount,
            'currency_type': currency_type,
            'interest_rate': self.interest_rate,
            'created_time': 'now'
        }
        
        return True
    
    def repay_loan(self, agent_id: int, currency_type: CurrencyType, amount: float) -> bool:
        """还款"""
        if agent_id in self.loans:
            loan = self.loans[agent_id]
            if loan['currency_type'] == currency_type and loan['amount'] <= amount:
                # 计算利息
                total_payment = loan['amount'] * (1 + loan['interest_rate'])
                if self.accounts[agent_id].get(currency_type, 0) >= total_payment:
                    self.accounts[agent_id][currency_type] -= total_payment
                    del self.loans[agent_id]
                    return True
        
        return False


class CurrencyEconomy:
    """货币经济系统 - 整合货币与现有经济"""
    def __init__(self, economy: Economy):
        self.economy = economy
        self.currency_exchange = CurrencyExchange(economy)
        self.bank = Bank()
        self.adoption_rate = 0.0  # 货币采用率 (0-1)
        self.trade_history: List[Dict] = []
        
        # 货币演化参数
        self.efficiency_threshold = 0.3  # 物物交换效率低于30%时开始采用货币
        self.critical_mass = 0.5  # 50%的Agent采用货币后形成临界质量
    
    def evaluate_barter_efficiency(self, agents: List[Agent]) -> float:
        """评估物物交换效率"""
        total_trades = len(self.economy.trading_post.active_trades)
        failed_trades = self.economy.trading_post.failed_trades
        
        if total_trades == 0:
            return 0.0
        
        efficiency = self.economy.trading_post.successful_trades / max(1, total_trades)
        return efficiency
    
    def evolve_currency_system(self, agents: List[Agent]):
        """货币系统自然演化"""
        # 评估物物交换效率
        barter_efficiency = self.evaluate_barter_efficiency(agents)
        
        print(f"物物交换效率: {barter_efficiency:.2f}")
        
        # 当物物交换效率低下时，开始采用货币
        if barter_efficiency < self.efficiency_threshold:
            # 增加货币采用率
            adoption_increment = (self.efficiency_threshold - barter_efficiency) * 0.1
            self.adoption_rate = min(1.0, self.adoption_rate + adoption_increment)
            print(f"货币采用率提升至: {self.adoption_rate:.2f}")
            
            # 随机选择一些Agent开始使用货币
            currency_adopters = random.sample(agents, 
                                            int(len(agents) * adoption_increment))
            
            for agent in currency_adopters:
                # 初始金币（从货物兑换而来）
                initial_resources = [ResourceType.FOOD, ResourceType.WATER, ResourceType.WOOD]
                for resource in initial_resources:
                    if agent.inventory.get(resource, 0) > 5:
                        # 用少量初始资源兑换金币
                        amount = min(2, agent.inventory.get(resource, 0) // 3)
                        item_type = self._item_from_resource(resource)
                        currency_type = self.currency_exchange.create_currency_from_goods(
                            agent, item_type, amount)
                        if currency_type:
                            print(f"Agent {agent.id} 兑换了 {amount} 个 {item_type.value} 为 {currency_type.value}")
                            break
    
    def _item_from_resource(self, resource: ResourceType) -> ItemType:
        """资源类型转换为物品类型"""
        mapping = {
            ResourceType.FOOD: ItemType.FOOD,
            ResourceType.WATER: ItemType.WATER,
            ResourceType.WOOD: ItemType.WOOD,
            ResourceType.MINERAL: ItemType.TOOL
        }
        return mapping.get(resource, ItemType.FOOD)
    
    def make_currency_trade(self, buyer: Agent, seller: Agent, item_type: ItemType,
                           quantity: int, currency: CurrencyType, price: float) -> bool:
        """执行货币交易"""
        # 检查买家是否有足够货币
        if buyer.cash.get(currency, 0) < price:
            return False
        
        # 检查卖家是否有足够货物
        required_resource = self.currency_exchange._resource_from_item(item_type)
        if seller.inventory.get(required_resource, 0) < quantity:
            return False
        
        # 执行交易
        buyer.cash[currency] -= price
        seller.cash[currency] = seller.cash.get(currency, 0) + price * 0.95  # 卖家获得95%
        
        # 转移货物
        seller.inventory[required_resource] -= quantity
        buyer.inventory[required_resource] = buyer.inventory.get(required_resource, 0) + quantity
        
        # 记录交易
        self.trade_history.append({
            'timestamp': 'now',
            'buyer': buyer.id,
            'seller': seller.id,
            'item_type': item_type.value,
            'quantity': quantity,
            'currency': currency.value,
            'price': price
        })
        
        return True
    
    def get_currency_summary(self) -> Dict:
        """获取货币系统摘要"""
        return {
            'adoption_rate': self.adoption_rate,
            'active_currencies': {curr_type.value: sum(agent.cash.get(curr_type, 0) 
                                  for agent in self.economy.agents) 
                               for curr_type in CurrencyType},
            'exchange_rates': {f"{k[0].value}_{k[1].value}": v 
                             for k, v in self.currency_exchange.exchange_rates.items()},
            'bank_accounts': len(self.bank.accounts),
            'active_loans': len(self.bank.loans)
        }