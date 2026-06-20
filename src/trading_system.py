"""
交易系统模块
实现Agent之间的资源交换和市场价格形成
"""

from typing import List, Dict, Optional, Tuple
import random
from .agent import Agent, ResourceType
from .economy import ItemType, Market, TradingPost


class TradingEngine:
    """交易引擎 - 负责协调Agent之间的交易"""
    
    def __init__(self, market: Market):
        self.market = market
        self.successful_trades = 0
        self.failed_trades = 0
        
    def connect_agent_to_market(self, agent: Agent):
        """连接Agent到市场，设定交易偏好"""
        # 根据职业设定交易偏好
        if agent.profession.value == "hunter":
            agent.preferred_items = [ItemType.FOOD, ItemType.WEAPON]
        elif agent.profession.value == "farmer":
            agent.preferred_items = [ItemType.FOOD, ItemType.TOOL]
        elif agent.profession.value == "craftsman":
            agent.preferred_items = [ItemType.TOOL, ItemType.WEAPON, ItemType.CLOTHING]
        elif agent.profession.value == "gatherer":
            agent.preferred_items = [ItemType.FOOD, ItemType.WATER]
        else:
            agent.preferred_items = []
    
    def has_resources_for_trading(self, agent: Agent, item_type: ItemType, quantity: int) -> bool:
        """检查Agent是否有足够资源用于交易"""
        if item_type == ItemType.FOOD:
            return agent.inventory.get(ResourceType.FOOD, 0) >= quantity
        elif item_type == ItemType.WATER:
            return agent.inventory.get(ResourceType.WATER, 0) >= quantity
        elif item_type == ItemType.WOOD:
            return agent.inventory.get(ResourceType.WOOD, 0) >= quantity
        elif item_type == ItemType.TOOL:
            return agent.inventory.get(ResourceType.MINERAL, 0) >= quantity
        return False
    
    def get_trading_capacity(self, agent: Agent) -> int:
        """获取Agent的交易容量（根据背包剩余空间）"""
        current_total = sum(agent.inventory.values())
        return max(0, agent.max_inventory - current_total)
    
    def evaluate_trade_opportunity(self, agent: Agent, item_type: ItemType, quantity: int, price: float) -> Tuple[bool, str]:
        """评估Agent对交易机会的兴趣"""
        # 获取市场价格
        market_price = self.market.get_price(item_type)
        
        # 价格偏差检查
        price_deviation = abs(price - market_price) / market_price
        if price_deviation > 0.3:  # 价格偏离超过30%不太可能接受
            return False, f"价格偏差过大: {price:.2f} vs 市场价 {market_price:.2f}"
        
        # 个人需求评估
        if item_type == ItemType.FOOD and agent.hunger > 70:
            return True, f"急需食物，饥饿度: {agent.hunger:.1f}"
        elif item_type == ItemType.WATER and agent.thirst > 70:
            return True, f"急需饮水，口渴度: {agent.thirst:.1f}"
        elif item_type == ItemType.MEDICINE and agent.health < 50:
            return True, f"急需药物，健康度: {agent.health:.1f}"
        
        # 资源过剩时愿意出售
        if item_type == ItemType.FOOD and agent.inventory.get(ResourceType.FOOD, 0) > 10:
            return True, f"食物过剩，可出售: {agent.inventory[ResourceType.FOOD]}"
        elif item_type == ItemType.WATER and agent.inventory.get(ResourceType.WATER, 0) > 10:
            return True, f"水过剩，可出售: {agent.inventory[ResourceType.WATER]}"
        elif item_type == ItemType.WOOD and agent.inventory.get(ResourceType.WOOD, 0) > 10:
            return True, f"木材过剩，可出售: {agent.inventory[ResourceType.WOOD]}"
        
        return False, "当前不需要此物品"
    
    def execute_trade_between_agents(self, buyer: Agent, seller: Agent, item_type: ItemType, quantity: int, price: float) -> Tuple[bool, str]:
        """在两个Agent之间执行交易"""
        total_cost = price * quantity
        
        # 检查卖家是否有足够资源
        if not self.has_resources_for_trading(seller, item_type, quantity):
            return False, "卖家资源不足"
        
        # 检查买家财富（简化用健康值代表）
        if buyer.health < total_cost * 10:
            return False, "买家财富不足"
        
        # 执行交易逻辑
        success = self._execute_trade_transaction(buyer, seller, item_type, quantity, price)
        
        if success:
            self.successful_trades += 1
            buyer.trades_successful += 1
            seller.trades_successful += 1
        else:
            self.failed_trades += 1
            buyer.trades_made += 1
            seller.trades_made += 1
        
        return success, "交易成功" if success else "交易失败"
    
    def _execute_trade_transaction(self, buyer: Agent, seller: Agent, item_type: ItemType, quantity: int, price: float) -> bool:
        """执行实际的交易事务"""
        total_cost = price * quantity
        
        # 卖家失去资源，获得财富
        if item_type == ItemType.FOOD:
            if seller.inventory.get(ResourceType.FOOD, 0) < quantity:
                return False
            seller.inventory[ResourceType.FOOD] -= quantity
            seller.health += total_cost * 10 * 0.9  # 卖家获得90%的价值
        elif item_type == ItemType.WATER:
            if seller.inventory.get(ResourceType.WATER, 0) < quantity:
                return False
            seller.inventory[ResourceType.WATER] -= quantity
            seller.health += total_cost * 10 * 0.9
        elif item_type == ItemType.WOOD:
            if seller.inventory.get(ResourceType.WOOD, 0) < quantity:
                return False
            seller.inventory[ResourceType.WOOD] -= quantity
            seller.health += total_cost * 10 * 0.9
        
        # 买家获得资源，失去财富
        buyer.health -= total_cost * 10
        
        if item_type == ItemType.FOOD:
            buyer.inventory[ResourceType.FOOD] = buyer.inventory.get(ResourceType.FOOD, 0) + quantity
        elif item_type == ItemType.WATER:
            buyer.inventory[ResourceType.WATER] = buyer.inventory.get(ResourceType.WATER, 0) + quantity
        elif item_type == ItemType.WOOD:
            buyer.inventory[ResourceType.WOOD] = buyer.inventory.get(ResourceType.WOOD, 0) + quantity
        
        # 更新交易统计和伙伴关系
        buyer.trades_made += 1
        seller.trades_made += 1
        
        if seller.id not in buyer.trade_partners:
            buyer.trade_partners.append(seller.id)
        if buyer.id not in seller.trade_partners:
            seller.trade_partners.append(buyer.id)
        
        return True
    
    def find_best_trade_partner(self, agent: Agent, all_agents: List[Agent]) -> Optional[Agent]:
        """为Agent寻找最佳交易伙伴"""
        best_partner = None
        best_score = -1
        
        for other in all_agents:
            if other.id != agent.id and other.id not in agent.trade_partners:
                # 计算交易潜力得分
                score = 0
                
                # 检查互补性
                self_total = sum(agent.inventory.values())
                other_total = sum(other.inventory.values())
                
                if abs(self_total - other_total) < 10:  # 资源量相近
                    score += 1
                
                # 检查不同职业（互补性）
                if agent.profession != other.profession:
                    score += 2
                
                # 检查偏好物品
                if len(agent.preferred_items) > 0:
                    score += 1
                
                if score > best_score:
                    best_score = score
                    best_partner = other
        
        return best_partner
    
    def make_automatic_trades(self, agent: Agent, all_agents: List[Agent], max_trades: int = 3) -> List[str]:
        """让Agent自动进行交易"""
        if not hasattr(agent, 'preferred_items') or len(agent.preferred_items) == 0:
            return ["Agent未设定交易偏好"]
        
        trade_logs = []
        trades_made = 0
        
        for _ in range(max_trades):
            if trades_made >= max_trades:
                break
            
            # 寻找最佳交易伙伴
            partner = self.find_best_trade_partner(agent, all_agents)
            if not partner:
                break
            
            # 选择交易物品
            if random.random() < 0.5 and len(agent.preferred_items) > 0:
                item_type = random.choice(agent.preferred_items)
            else:
                item_type = random.choice(list(ItemType))
            
            # 确定数量和价格
            capacity = self.get_trading_capacity(agent)
            if capacity <= 0:
                # 如果没有容量，考虑出售
                if self.has_resources_for_trading(agent, item_type, 1):
                    quantity = 1
                else:
                    continue
            else:
                quantity = random.randint(1, min(5, capacity))
            
            market_price = self.market.get_price(item_type)
            price = market_price * random.uniform(0.9, 1.1)  # 允许10%的价格浮动
            
            # 评估交易机会
            should_trade, reason = self.evaluate_trade_opportunity(agent, item_type, quantity, price)
            if should_trade:
                # 决定买还是卖
                if agent.hunger > 70 or agent.thirst > 70 or agent.health < 50:
                    # 需求高时优先买入
                    success, message = self.execute_trade_between_agents(agent, partner, item_type, quantity, price)
                else:
                    # 需求低时考虑卖出
                    if self.has_resources_for_trading(agent, item_type, quantity) and random.random() < 0.3:
                        success, message = self.execute_trade_between_agents(partner, agent, item_type, quantity, price)
                    else:
                        continue
                
                if success:
                    trade_logs.append(f"Agent{agent.id} {message} {quantity}个{item_type.value} (价格:{price:.2f})")
                    trades_made += 1
                else:
                    trade_logs.append(f"Agent{agent.id} 交易失败: {reason}")
        
        return trade_logs