#!/usr/bin/env python3
"""
最终交易系统演示脚本
展示Agent之间如何通过经济系统进行资源交换，形成市场价格
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.economy import Economy, ItemType, Market
from src.agent_simple import Agent, ResourceType, Tile, Profession, TerrainType
from src.trading_system import TradingEngine
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
            agent.inventory[ResourceType.FOOD] = random.randint(5, 10)
            agent.inventory[ResourceType.WOOD] = random.randint(0, 3)
        elif profession == Profession.FARMER:
            agent.inventory[ResourceType.FOOD] = random.randint(8, 15)
            agent.inventory[ResourceType.WATER] = random.randint(3, 8)
        elif profession == Profession.CRAFTSMAN:
            agent.inventory[ResourceType.WOOD] = random.randint(3, 8)
            agent.inventory[ResourceType.MINERAL] = random.randint(2, 5)
        else:  # GATHERER
            agent.inventory[ResourceType.FOOD] = random.randint(5, 12)
            agent.inventory[ResourceType.WATER] = random.randint(5, 15)
            agent.inventory[ResourceType.WOOD] = random.randint(2, 8)
        
        # 设置初始健康值（代表财富）
        agent.health = random.randint(60, 100)
        # 设置更大的背包容量以便交易
        agent.max_inventory = 30
        
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
              f"健康={agent.health:.1f}, 资源={total_resources}, "
              f"交易成功率={trade_success_rate:.1f}%, 交易次数={agent.trades_made}")


def print_market_prices(market: Market):
    """打印市场价格信息"""
    print(f"\n=== 市场价格 ===")
    for item_type in ItemType:
        price = market.get_price(item_type)
        supply, demand = market.supply_demand[item_type]
        print(f"{item_type.value}: 价格={price:.2f}, 供应={supply}, 需求={demand}")


def simulate_trading_rounds(trading_engine: TradingEngine, agents: list, rounds: int = 10):
    """模拟多轮交易"""
    print(f"\n=== 开始 {rounds} 轮交易模拟 ===")
    
    for round_num in range(rounds):
        print(f"\n--- 第 {round_num + 1} 轮 ---")
        
        # 随机选择一些Agent进行交易
        active_agents = random.sample(agents, min(6, len(agents)))
        trade_count = 0
        
        for agent in active_agents:
            if trade_count >= 15:  # 限制每轮交易次数
                break
            
            # Agent进行自动交易
            trade_logs = trading_engine.make_automatic_trades(agent, agents, max_trades=2)
            if trade_logs:
                for log in trade_logs[:1]:  # 只显示前1条交易记录
                    print(f"  {log}")
                trade_count += len(trade_logs)
        
        # 每3轮显示一次市场状态
        if round_num % 3 == 2:
            print_market_prices(trading_engine.market)
    
    print(f"\n=== {rounds} 轮交易完成 ===")


def demonstrate_market_dynamics(economy: Economy, agents: list):
    """演示市场动态变化"""
    print(f"\n=== 市场动态演示 ===")
    
    # 统计初始市场状态
    print("初始市场状态:")
    print_market_prices(economy.market)
    
    # 模拟资源短缺
    print("\n模拟食物短缺:")
    for agent in agents:
        agent.inventory[ResourceType.FOOD] = max(0, agent.inventory.get(ResourceType.FOOD, 0) - 5)
    
    economy.update_market(agents)
    print_market_prices(economy.market)
    
    # 模拟资源过剩
    print("\n模拟木材过剩:")
    for agent in agents:
        agent.inventory[ResourceType.WOOD] = agent.inventory.get(ResourceType.WOOD, 0) + 8
    
    economy.update_market(agents)
    print_market_prices(economy.market)
    
    # 模拟需求激增
    print("\n模拟医疗需求激增:")
    for agent in agents:
        agent.health = max(10, agent.health - random.randint(15, 30))
    
    economy.update_market(agents)
    print_market_prices(economy.market)


def analyze_trading_patterns(agents: list):
    """分析交易模式"""
    print(f"\n=== 交易模式分析 ===")
    
    # 统计交易数据
    profession_trades = {prof.value: 0 for prof in Profession}
    total_trades = 0
    
    for agent in agents:
        if agent.trades_made > 0:
            profession_trades[agent.profession.value] += agent.trades_made
            total_trades += agent.trades_made
    
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
    print("🔄 文明模拟器 - 最终交易系统演示\n")
    print("展示Agent之间如何通过经济系统进行资源交换，形成市场价格\n")
    
    # 创建经济系统
    economy = Economy()
    
    # 创建交易引擎
    trading_engine = TradingEngine(economy.market)
    
    # 创建Agent
    agents = create_sample_agents(8)
    
    # 连接Agent到市场
    for agent in agents:
        trading_engine.connect_agent_to_market(agent)
    
    print(f"创建了 {len(agents)} 个Agent，已集成交易系统")
    
    # 显示初始状态
    print_agent_status(agents, "初始状态")
    print_market_prices(economy.market)
    
    # 模拟交易过程
    simulate_trading_rounds(trading_engine, agents, rounds=8)
    
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
    
    print(f"\n🎉 最终交易系统演示完成！")
    print("Agent已成功实现资源交换和价格形成机制")


if __name__ == "__main__":
    main()