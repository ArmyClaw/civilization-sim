#!/usr/bin/env python3
"""
交易系统演示脚本
展示Agent之间如何通过经济系统进行资源交换，形成市场价格
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.economy import Economy, ItemType, Good, Market
from src.agent import Agent, ResourceType, Tile, Profession, TerrainType
from src.terrain import Terrain
import random


def create_sample_agents(count: int = 10) -> list:
    """创建示例Agent，模拟不同职业和初始资源分布"""
    agents = []
    professions = list(Profession)
    
    for i in range(count):
        x, y = random.randint(0, 20), random.randint(0, 20)
        tile = Tile(x, y, random.choice(list(TerrainType)))
        profession = random.choice(professions)
        agent = Agent(i, x, y, tile, profession)
        
        # 根据职业设置初始资源
        if profession == Profession.HUNTER:
            agent.inventory[ResourceType.FOOD] = random.randint(8, 15)
            agent.inventory[ResourceType.WOOD] = random.randint(0, 3)
        elif profession == Profession.FARMER:
            agent.inventory[ResourceType.FOOD] = random.randint(10, 18)
            agent.inventory[ResourceType.WATER] = random.randint(3, 8)
        elif profession == Profession.CRAFTSMAN:
            agent.inventory[ResourceType.WOOD] = random.randint(5, 12)
            agent.inventory[ResourceType.MINERAL] = random.randint(3, 8)
        else:  # GATHERER
            agent.inventory[ResourceType.FOOD] = random.randint(5, 12)
            agent.inventory[ResourceType.WATER] = random.randint(5, 15)
            agent.inventory[ResourceType.WOOD] = random.randint(2, 8)
        
        # 设置初始健康值（代表财富）
        agent.health = random.randint(60, 100)
        
        agents.append(agent)
    
    return agents


def print_agent_status(agents: list, title: str = ""):
    """打印所有Agent状态"""
    if title:
        print(f"\n=== {title} ===")
    for agent in agents:
        total_resources = sum(agent.inventory.values())
        trade_success_rate = (agent.trades_successful / max(1, agent.trades_made)) * 100
        print(f"Agent {agent.id} ({agent.profession.value}): "
              f"健康={agent.health:.1f}, "
              f"资源={total_resources}, "
              f"交易成功率={trade_success_rate:.1f}%, "
              f"交易次数={agent.trades_made}")


def print_market_prices(economy: Economy):
    """打印市场价格信息"""
    print(f"\n=== 市场价格 ===")
    for item_type in ItemType:
        price = economy.market.get_price(item_type)
        supply, demand = economy.market.supply_demand[item_type]
        print(f"{item_type.value}: 价格={price:.2f}, 供应={supply}, 需求={demand}")


def simulate_economic_cycles(economy: Economy, agents: list, cycles: int = 5):
    """模拟多个经济周期"""
    print(f"\n=== 开始 {cycles} 个经济周期模拟 ===")
    
    for cycle in range(cycles):
        print(f"\n--- 第 {cycle + 1} 周期 ---")
        
        # 更新市场供需（基于Agent的当前状态）
        economy.update_market(agents)
        
        # 每个Agent尝试进行交易
        trade_count = 0
        for agent in agents:
            if trade_count >= 20:  # 限制每周期交易次数
                break
            
            # 随机选择一些Agent进行交易
            if random.random() < 0.6:  # 60%概率尝试交易
                trade_logs = agent.make_automatic_trades(agents, max_trades=2)
                if trade_logs:
                    for log in trade_logs[:2]:  # 只显示前2条交易记录
                        print(f"  Agent{agent.id}: {log}")
                    trade_count += len(trade_logs)
        
        # 每3个周期显示一次市场状态
        if cycle % 3 == 2:
            print_market_prices(economy)
    
    print(f"\n=== {cycles} 周期完成 ===")


def demonstrate_market_dynamics(economy: Economy, agents: list):
    """演示市场动态变化"""
    print(f"\n=== 市场动态演示 ===")
    
    # 统计初始市场状态
    print("初始市场状态:")
    print_market_prices(economy)
    
    # 模拟资源短缺
    print("\n模拟食物短缺:")
    for agent in agents:
        agent.inventory[ResourceType.FOOD] = max(0, agent.inventory.get(ResourceType.FOOD, 0) - 8)
    
    economy.update_market(agents)
    print_market_prices(economy)
    
    # 模拟资源过剩
    print("\n模拟木材过剩:")
    for agent in agents:
        agent.inventory[ResourceType.WOOD] = agent.inventory.get(ResourceType.WOOD, 0) + 10
    
    economy.update_market(agents)
    print_market_prices(economy)
    
    # 模拟需求激增
    print("\n模拟医疗需求激增:")
    for agent in agents:
        agent.health = max(10, agent.health - random.randint(20, 40))
    
    economy.update_market(agents)
    print_market_prices(economy)


def analyze_trading_patterns(agents: list):
    """分析交易模式"""
    print(f"\n=== 交易模式分析 ===")
    
    # 统计交易数据
    profession_trades = {prof.value: 0 for prof in Profession}
    total_trades = 0
    
    for agent in agents:
        if agent.trades_made > 0:
            profession_trades[agent.profession.value] += agent.trades_made
            total_trades += agent.trades_makes
    
    print("各职业交易次数:")
    for profession, count in profession_trades.items():
        print(f"  {profession}: {count}")
    
    # 分析贸易网络
    print(f"\n贸易网络连接数:")
    for agent in agents:
        print(f"  Agent{agent.id}: {len(agent.trade_partners)} 个贸易伙伴")
    
    # 计算市场效率
    successful_trades = sum(agent.trades_successful for agent in agents)
    total_attempts = sum(agent.trades_made for agent in agents)
    market_efficiency = (successful_trades / max(1, total_attempts)) * 100
    
    print(f"\n市场效率: {market_efficiency:.1f}%")
    print(f"成功交易: {successful_trades}")
    print(f"失败交易: {total_attempts - successful_trades}")


def main():
    """主函数 - 完整交易系统演示"""
    print("🔄 文明模拟器 - 交易系统演示\n")
    print("展示Agent之间如何通过经济系统进行资源交换，形成市场价格\n")
    
    # 创建经济系统
    economy = Economy()
    
    # 创建Agent并集成到经济系统
    agents = create_sample_agents(12)
    
    for agent in agents:
        agent.integrate_with_economy(economy)
    
    print(f"创建了 {len(agents)} 个Agent，已集成经济系统")
    
    # 显示初始状态
    print_agent_status(agents, "初始状态")
    print_market_prices(economy)
    
    # 模拟经济周期
    simulate_economic_cycles(economy, agents, cycles=5)
    
    # 显示最终状态
    print_agent_status(agents, "最终状态")
    
    # 演示市场动态
    demonstrate_market_dynamics(economy, agents)
    
    # 分析交易模式
    analyze_trading_patterns(agents)
    
    # 显示经济摘要
    print(f"\n=== 经济系统最终摘要 ===")
    summary = economy.get_economic_summary()
    
    print(f"市场效率: {summary['market_efficiency']*100:.1f}%")
    print(f"成功交易: {summary['successful_trades']}")
    print(f"失败交易: {summary['failed_trades']}")
    print(f"技术水平:")
    for tech, level in summary['technology_levels'].items():
        print(f"  {tech}: {level}")
    
    print(f"\n🎉 交易系统演示完成！")
    print("Agent已成功实现资源交换和价格形成机制")


if __name__ == "__main__":
    main()