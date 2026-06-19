#!/usr/bin/env python3
"""
经济系统演示脚本
展示物品价值体系、交易机制、供需模型的工作原理
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.economy import Economy, ItemType, Good, Market
from src.agent import Agent, ResourceType, Tile
from src.terrain import TerrainType
import random


def create_sample_agents(count: int = 10) -> list:
    """创建示例Agent"""
    agents = []
    for i in range(count):
        tile = Tile(0, 0, random.choice(list(TerrainType)))  # 简化的tile创建
        agent = Agent(i, random.randint(0, 20), random.randint(0, 20), tile)
        
        # 随机分配初始资源
        agent.inventory[ResourceType.FOOD] = random.randint(5, 15)
        agent.inventory[ResourceType.WATER] = random.randint(5, 15)
        agent.inventory[ResourceType.WOOD] = random.randint(0, 10)
        agent.inventory[ResourceType.MINERAL] = random.randint(0, 5)
        
        agents.append(agent)
    
    return agents


def demonstrate_value_system():
    """演示物品价值体系"""
    print("=== 物品价值体系演示 ===")
    
    # 创建不同质量的物品
    food_low = Good(ItemType.FOOD, quality=0.5)
    food_medium = Good(ItemType.FOOD, quality=1.0)
    food_high = Good(ItemType.FOOD, quality=1.5)
    
    tool_basic = Good(ItemType.TOOL, quality=0.8)
    tool_advanced = Good(ItemType.TOOL, quality=1.5)
    
    medicine_cheap = Good(ItemType.MEDICINE, quality=0.7)
    medicine_premium = Good(ItemType.MEDICINE, quality=1.8)
    
    goods = [food_low, food_medium, food_high, tool_basic, tool_advanced, 
             medicine_cheap, medicine_premium]
    
    print("基础物品价值:")
    for good in goods:
        print(f"- {good.item_type.value}: 质量={good.quality:.1f}, "
              f"基础价值={good.value:.1f}, "
              f"当前价值={good.get_current_value():.1f}")
    
    print()


def demonstrate_supply_demand():
    """演示供需模型"""
    print("=== 供需模型演示 ===")
    
    market = Market()
    
    # 模拟不同的供需场景
    scenarios = [
        ("食物短缺", {ItemType.FOOD: (10, 50)}),
        ("食物过剩", {ItemType.FOOD: (100, 10)}),
        ("供需平衡", {ItemType.FOOD: (50, 45)}),
        ("水过剩", {ItemType.WATER: (80, 20)}),
        ("工具稀缺", {ItemType.TOOL: (5, 30)})
    ]
    
    for scenario_name, supply_demand_data in scenarios:
        print(f"\n{scenario_name}:")
        for item_type, (supply, demand) in supply_demand_data.items():
            market.update_supply_demand(item_type, supply, demand)
            price = market.get_price(item_type)
            factor = market.get_supply_demand_factor(item_type)
            
            print(f"  {item_type.value}: 供应={supply}, 需求={demand}, "
                  f"价格={price:.2f}, 供需因子={factor:.2f}")
    
    print()


def demonstrate_trading():
    """演示交易机制"""
    print("=== 交易机制演示 ===")
    
    economy = Economy()
    agents = create_sample_agents(8)
    
    print("初始Agent状态:")
    for agent in agents:
        total_resources = sum(agent.inventory.values())
        print(f"Agent {agent.id}: 健康={agent.health:.1f}, "
              f"总资源={total_resources}, "
              f"饥饿={agent.hunger:.1f}, 口渴={agent.thirst:.1f}")
    
    print("\n市场初始价格:")
    for item_type in ItemType:
        price = economy.market.get_price(item_type)
        print(f"  {item_type.value}: {price:.2f}")
    
    # 模拟一些交易
    print("\n模拟交易:")
    for i in range(5):
        buyer = random.choice(agents)
        seller = random.choice(agents)
        if buyer != seller:
            item_type = random.choice([ItemType.FOOD, ItemType.WATER])
            quantity = random.randint(1, 3)
            price = economy.market.get_price(item_type) * random.uniform(0.9, 1.1)
            
            success = economy.trading_post.execute_trade(buyer, seller, item_type, quantity, price)
            if success:
                print(f"交易成功: Agent{buyer.id} 购买 {quantity}个{item_type.value} "
                      f"从 Agent{seller.id} (价格: {price:.2f})")
            else:
                print(f"交易失败: Agent{buyer.id} 尝试购买 {quantity}个{item_type.value} "
                      f"从 Agent{seller.id}")
    
    print("\n交易后Agent状态:")
    for agent in agents:
        total_resources = sum(agent.inventory.values())
        print(f"Agent {agent.id}: 健康={agent.health:.1f}, "
              f"总资源={total_resources}")
    
    print()


def demonstrate_technology():
    """演示技术发展"""
    print("=== 技术发展演示 ===")
    
    economy = Economy()
    
    print("初始技术水平:")
    for tech, level in economy.production_technology.items():
        print(f"  {tech}: {level}")
    
    print("\n技术进步:")
    technologies = ['tool_making', 'weapon_crafting', 'shelter_building', 
                   'clothing_making', 'medicine_production']
    
    for tech in technologies:
        if economy.advance_technology(tech):
            new_level = economy.production_technology[tech]
            cost_reduction = 1.0 / (1.0 + new_level * 0.2)
            print(f"  {tech} 升级到 {new_level} (成本降低 {(1-cost_reduction)*100:.1f}%)")
    
    print("\n技术进步后的生产成本:")
    for item_type in [ItemType.TOOL, ItemType.WEAPON, ItemType.SHELTER]:
        cost = economy.calculate_production_cost(item_type)
        print(f"  {item_type.value}: {cost:.2f}")
    
    print()


def main():
    """主函数 - 运行所有演示"""
    print("🏛️ 文明模拟器 - 经济系统演示\n")
    
    demonstrate_value_system()
    demonstrate_supply_demand()
    demonstrate_trading()
    demonstrate_technology()
    
    print("\n=== 经济系统摘要 ===")
    economy = Economy()
    summary = economy.get_economic_summary()
    
    print("市场效率:", f"{summary['market_efficiency']*100:.1f}%")
    print("成功交易:", summary['successful_trades'])
    print("失败交易:", summary['failed_trades'])
    print("\n当前市场价格:")
    for item_type, price in summary['market_prices'].items():
        supply, demand = summary['supply_demand'][item_type]
        print(f"  {item_type.value}: {price:.2f} (供应: {supply}, 需求: {demand})")


if __name__ == "__main__":
    main()