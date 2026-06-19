"""
经济系统模块
实现物品价值体系、交易机制、供需模型
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import math
import random
from .agent import Agent, ResourceType


class ItemType(Enum):
    """物品类型枚举"""
    FOOD = "food"          # 食物
    WATER = "water"        # 水
    WOOD = "wood"          # 木材
    TOOL = "tool"          # 工具
    WEAPON = "weapon"      # 武器
    SHELTER = "shelter"    # 庇护所
    CLOTHING = "clothing"  # 衣物
    MEDICINE = "medicine"  # 药物


class Good:
    """物品类"""
    def __init__(self, item_type: ItemType, quality: float = 1.0, durability: float = 1.0):
        self.item_type = item_type
        self.quality = quality  # 质量 (0.1-2.0)
        self.durability = durability  # 耐久度 (0.1-1.0)
        self.value = self._calculate_base_value()
    
    def _calculate_base_value(self) -> float:
        """计算基础价值"""
        base_values = {
            ItemType.FOOD: 1.0,
            ItemType.WATER: 1.2,
            ItemType.WOOD: 0.8,
            ItemType.TOOL: 3.0,
            ItemType.WEAPON: 5.0,
            ItemType.SHELTER: 8.0,
            ItemType.CLOTHING: 2.5,
            ItemType.MEDICINE: 6.0
        }
        return base_values.get(self.item_type, 1.0) * self.quality
    
    def get_current_value(self, supply_demand_factor: float = 1.0) -> float:
        """获取当前价值（考虑供需）"""
        return self.value * self.quality * self.durability * supply_demand_factor


class Market:
    """市场类 - 实现供需模型"""
    def __init__(self):
        self.price_history: Dict[ItemType, List[Tuple[float, int]]] = {}  # (价格, 交易量) 历史记录
        self.current_prices: Dict[ItemType, float] = {}  # 当前价格
        self.supply_demand: Dict[ItemType, Tuple[int, int]] = {}  # (供应量, 需求量)
        
        # 初始化历史记录
        for item_type in ItemType:
            self.price_history[item_type] = []
            self.current_prices[item_type] = self._get_base_price(item_type)
            self.supply_demand[item_type] = (0, 0)
    
    def _get_base_price(self, item_type: ItemType) -> float:
        """获取基础价格"""
        base_prices = {
            ItemType.FOOD: 1.0,
            ItemType.WATER: 1.2,
            ItemType.WOOD: 0.8,
            ItemType.TOOL: 3.0,
            ItemType.WEAPON: 5.0,
            ItemType.SHELTER: 8.0,
            ItemType.CLOTHING: 2.5,
            ItemType.MEDICINE: 6.0
        }
        return base_prices.get(item_type, 1.0)
    
    def update_supply_demand(self, item_type: ItemType, supply: int, demand: int):
        """更新供需数据"""
        self.supply_demand[item_type] = (supply, demand)
        
        # 计算供需平衡因子
        if supply == 0:
            supply_demand_factor = 2.0  # 稀缺商品价格翻倍
        elif demand == 0:
            supply_demand_factor = 0.5  # 供过于求价格减半
        else:
            ratio = demand / supply if supply > 0 else float('inf')
            supply_demand_factor = min(2.0, max(0.5, ratio * 0.8))
        
        # 更新价格，加入历史价格的影响（平滑价格波动）
        old_price = self.current_prices[item_type]
        new_price = old_price * 0.7 + self._get_base_price(item_type) * 0.3 * supply_demand_factor
        
        # 限制价格波动范围
        max_change = old_price * 0.2  # 最大20%的单次波动
        if abs(new_price - old_price) > max_change:
            new_price = old_price + max_change if new_price > old_price else old_price - max_change
        
        self.current_prices[item_type] = max(0.1, new_price)
        
        # 记录价格历史
        self.price_history[item_type].append((new_price, supply + demand))
        if len(self.price_history[item_type]) > 100:  # 只保留最近100条记录
            self.price_history[item_type].pop(0)
    
    def get_price(self, item_type: ItemType) -> float:
        """获取当前价格"""
        return self.current_prices[item_type]
    
    def get_supply_demand_factor(self, item_type: ItemType) -> float:
        """获取供需平衡因子"""
        supply, demand = self.supply_demand[item_type]
        if supply == 0:
            return 2.0
        elif demand == 0:
            return 0.5
        else:
            ratio = demand / supply
            return min(2.0, max(0.5, ratio * 0.8))


class TradingPost:
    """交易点类 - 实现交易机制"""
    def __init__(self, market: Market):
        self.market = market
        self.active_trades: List[Dict] = []
        self.successful_trades = 0
        self.failed_trades = 0
    
    def create_trade_offer(self, agent: Agent, item_type: ItemType, quantity: int, 
                          price_per_unit: float, is_selling: bool = True) -> bool:
        """创建交易要约"""
        # 检查Agent是否有足够的物品
        if is_selling:
            # 转换资源到物品（简化处理）
            if item_type == ItemType.FOOD and agent.inventory.get(ResourceType.FOOD, 0) >= quantity:
                return True
            elif item_type == ItemType.WATER and agent.inventory.get(ResourceType.WATER, 0) >= quantity:
                return True
            elif item_type == ItemType.WOOD and agent.inventory.get(ResourceType.WOOD, 0) >= quantity:
                return True
            else:
                return False
        else:
            # 检查Agent是否有足够的资金（简化处理，用健康值代表财富）
            if agent.health >= price_per_unit * quantity * 10:  # 简化换算
                return True
            else:
                return False
    
    def execute_trade(self, buyer: Agent, seller: Agent, item_type: ItemType, 
                    quantity: int, price_per_unit: float) -> bool:
        """执行交易"""
        # 确定价格（市场价为基础，允许一定浮动）
        market_price = self.market.get_price(item_type)
        max_price = market_price * 1.2  # 最高可接受价格
        min_price = market_price * 0.8   # 最低可接受价格
        
        if price_per_unit > max_price or price_per_unit < min_price:
            return False  # 价格超出可接受范围
        
        # 检查双方是否有足够资源
        if (seller.inventory.get(self._resource_from_item(item_type), 0) >= quantity and 
            buyer.health >= price_per_unit * quantity * 10):
            
            # 执行交易
            self._resource_from_item(item_type)
            seller.inventory[self._resource_from_item(item_type)] -= quantity
            
            # 转换为支付（简化处理）
            buyer.health -= price_per_unit * quantity * 10
            seller.health += price_per_unit * quantity * 10 * 0.9  # 卖家获得90%的价值
            
            # 记录交易
            self.active_trades.append({
                'buyer': buyer.id,
                'seller': seller.id,
                'item_type': item_type,
                'quantity': quantity,
                'price': price_per_unit,
                'timestamp': 'now'
            })
            self.successful_trades += 1
            
            # 更新市场供需
            current_supply, current_demand = self.market.supply_demand[item_type]
            self.market.update_supply_demand(item_type, 
                                           current_supply - quantity,
                                           current_demand - quantity)
            
            return True
        
        return False
    
    def _resource_from_item(self, item_type: ItemType) -> ResourceType:
        """物品类型转换为资源类型（简化处理）"""
        mapping = {
            ItemType.FOOD: ResourceType.FOOD,
            ItemType.WATER: ResourceType.WATER,
            ItemType.WOOD: ResourceType.WOOD
        }
        return mapping.get(item_type, ResourceType.FOOD)


class Economy:
    """经济系统主类"""
    def __init__(self):
        self.market = Market()
        self.trading_post = TradingPost(self.market)
        self.production_technology: Dict[str, int] = {}  # 生产技术等级
        self.specialization_scores: Dict[str, int] = {}  # 专业分工得分
        
        # 初始化一些基础技术
        self.production_technology = {
            'basic_gathering': 1,
            'tool_making': 0,
            'weapon_crafting': 0,
            'shelter_building': 0,
            'clothing_making': 0,
            'medicine_production': 0
        }
    
    def update_market(self, agents: List[Agent]):
        """根据Agent的行为更新市场"""
        # 统计供需
        supply_counts: Dict[ItemType, int] = {item_type: 0 for item_type in ItemType}
        demand_counts: Dict[ItemType, int] = {item_type: 0 for item_type in ItemType}
        
        for agent in agents:
            # 统计供应（简化处理：根据库存统计）
            if agent.inventory.get(ResourceType.FOOD, 0) > 5:
                supply_counts[ItemType.FOOD] += agent.inventory.get(ResourceType.FOOD, 0) - 5
            if agent.inventory.get(ResourceType.WATER, 0) > 5:
                supply_counts[ItemType.WATER] += agent.inventory.get(ResourceType.WATER, 0) - 5
            if agent.inventory.get(ResourceType.WOOD, 0) > 3:
                supply_counts[ItemType.WOOD] += agent.inventory.get(ResourceType.WOOD, 0) - 3
            
            # 统计需求（简化处理：根据饥饿口渴程度统计）
            if agent.hunger > 70:
                demand_counts[ItemType.FOOD] += int(agent.hunger / 10)
            if agent.thirst > 70:
                demand_counts[ItemType.WATER] += int(agent.thirst / 10)
            if agent.health < 50:
                demand_counts[ItemType.MEDICINE] += max(1, int((50 - agent.health) / 20))
        
        # 更新市场
        for item_type in ItemType:
            self.market.update_supply_demand(item_type, 
                                           supply_counts[item_type], 
                                           demand_counts[item_type])
    
    def calculate_production_cost(self, item_type: ItemType, quality: float = 1.0) -> float:
        """计算生产成本"""
        base_costs = {
            ItemType.FOOD: 1.0,
            ItemType.WATER: 0.5,
            ItemType.WOOD: 2.0,
            ItemType.TOOL: 10.0,
            ItemType.WEAPON: 15.0,
            ItemType.SHELTER: 50.0,
            ItemType.CLOTHING: 8.0,
            ItemType.MEDICINE: 20.0
        }
        
        base_cost = base_costs.get(item_type, 1.0)
        tech_level = self.production_technology.get(self._tech_for_item(item_type), 1)
        
        # 技术进步降低成本
        cost_reduction = 1.0 / (1.0 + tech_level * 0.2)
        quality_premium = quality  # 高质量产品成本更高
        
        return base_cost * cost_reduction * quality_premium
    
    def _tech_for_item(self, item_type: ItemType) -> str:
        """获取对应的技术"""
        tech_mapping = {
            ItemType.TOOL: 'tool_making',
            ItemType.WEAPON: 'weapon_crafting',
            ItemType.SHELTER: 'shelter_building',
            ItemType.CLOTHING: 'clothing_making',
            ItemType.MEDICINE: 'medicine_production'
        }
        return tech_mapping.get(item_type, 'basic_gathering')
    
    def advance_technology(self, technology: str):
        """推进技术发展"""
        if technology in self.production_technology:
            self.production_technology[technology] += 1
            return True
        return False
    
    def get_economic_summary(self) -> Dict:
        """获取经济摘要"""
        return {
            'market_prices': self.market.current_prices,
            'supply_demand': self.market.supply_demand,
            'successful_trades': self.trading_post.successful_trades,
            'failed_trades': self.trading_post.failed_trades,
            'technology_levels': self.production_technology,
            'market_efficiency': self.trading_post.successful_trades / 
                               max(1, self.trading_post.successful_trades + self.trading_post.failed_trades)
        }