#!/usr/bin/env python3
"""
货币演化演示脚本
展示从物物交换向货币系统的自然演化过程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.currency_system import CurrencyType, CurrencyEconomy, Money, CurrencyExchange, Bank
from src.agent_with_currency import AgentWithCurrency
from src.terrain import Tile, TerrainType
from src.agent import Profession, ResourceType
from src.economy import Economy
import random

def create_sample_agents(count: int = 12) -> list:
    """创建支持货币的Agent示例"""
    agents = []
    professions = list(Profession)
    
    for i in range(count):
        x, y = random.randint(0, 15), random.randint(0, 15)
        tile = Tile(x, y, random.choice(list(TerrainType)))
        profession = random.choice(professions)
        
        agent = AgentWithCurrency(i, x, y, tile, profession)
        agent.initialize_currency()  # 初始化货币系统
        
        # 根据职业设置初始资源
        if profession == Profession.HUNTER:
            agent.inventory[ResourceType.FOOD] = random.randint(8, 15)
            agent.inventory[ResourceType.WATER] = random.randint(3, 8)
        elif profession == Profession.FARMER:
            agent.inventory[ResourceType.FOOD] = random.randint(10, 18)
            agent.inventory[ResourceType.WATER] = random.randint(5, 10)
        elif profession == Profession.CRAFTSMAN:
            agent.inventory[ResourceType.WOOD] = random.randint(6, 12)
            agent.inventory[ResourceType.MINERAL] = random.randint(4, 8)
        else:  # GATHERER
            agent.inventory[ResourceType.FOOD] = random.randint(6, 14)
            agent.inventory[ResourceType.WATER] = random.randint(6, 16)
            agent.inventory[ResourceType.WOOD] = random.randint(4, 10)
        
        # 设置初始健康值
        agent.health = random.randint(70, 100)
        agent.max_inventory = 30
        
        agents.append(agent)
    
    return agents


def print_agent_status(agents: list, title: str = ""):
    """打印Agent状态（含货币信息）"""
    if title:
        print(f"\n=== {title} ===")
    
    for agent in agents:
        total_resources = sum(agent.inventory.values())
        total_wealth = agent.get_total_wealth()
        
        print(f"Agent {agent.id} ({agent.profession.value}): "
              f"健康={agent.health:.1f}, "
              f"资源={total_resources}, "
              f"财富={total_wealth:.1f}, "
              f"金币={agent.cash.get(CurrencyType.GOLD_COIN, 0):.1f}")

def print_market_analysis(currency_economy: CurrencyEconomy):
    """打印市场分析"""
    print(f"\n=== 市场分析 ===")
    print(f"物物交换效率: {currency_economy.evaluate_barter_efficiency(currency_economy.economy.agents):.2f}")
    print(f"货币采用率: {currency_economy.adoption_rate:.2f}")
    
    summary = currency_economy.get_currency_summary()
    print(f"\n货币分布:")
    for curr_type, total_amount in summary['active_currencies'].items():
        print(f"  {curr_type}: {total_amount:.1f}")
    
    print(f"\n兑换率:")
    for rate_key, rate in summary['exchange_rates'].items():
        print(f"  {rate_key}: {rate:.2f}")

def simulate_barter_trading(currency_economy: CurrencyEconomy, agents: list, rounds: int = 5):
    """模拟物物交换阶段"""
    print(f"\n=== 物物交换阶段 (前 {rounds} 轮) ===")
    
    for round_num in range(rounds):
        print(f"\n--- 第 {round_num + 1} 轮物物交换 ---")
        
        # 随机选择一些Agent进行物物交换
        active_agents = random.sample(agents, min(6, len(agents)))
        
        for agent in active_agents:
            # 尝试物物交换
            trades_made = 0
            
            # Agent用多余资源交换急需资源
            if agent.inventory.get(ResourceType.FOOD, 0) > 8:
                # 尝试用食物换水
                for other in agents:
                    if other.id != agent.id and other.inventory.get(ResourceType.WATER, 0) > 5:
                        if random.random() < 0.3:  # 30%成功率
                            # 交换3食物换2水
                            food_amount = min(3, agent.inventory[ResourceType.FOOD] - 5)
                            water_amount = min(2, other.inventory[ResourceType.WATER] - 3)
                            
                            agent.inventory[ResourceType.FOOD] -= food_amount
                            agent.inventory[ResourceType.WATER] += water_amount
                            other.inventory[ResourceType.WATER] -= water_amount
                            other.inventory[ResourceType.FOOD] += food_amount
                            
                            agent.barter_trades += 1
                            other.barter_trades += 1
                            trades_made += 1
                            break
            
            if trades_made > 0:
                print(f"  Agent {agent.id} 完成了 {trades_made} 次物物交换")
        
        # 显示当前状态
        if round_num % 2 == 1:  # 每2轮显示一次状态
            print_agent_status(agents, f"第 {round_num + 1} 轮后状态")
    
    print(f"\n物物交换阶段完成，开始货币演化...")

def simulate_currency_evolution(currency_economy: CurrencyEconomy, agents: list, rounds: int = 8):
    """模拟货币演化阶段"""
    print(f"\n=== 货币演化阶段 (接下来 {rounds} 轮) ===")
    
    for round_num in range(rounds):
        print(f"\n--- 第 {round_num + 1} 轮货币演化 ---")
        
        # 货币系统自然演化
        currency_economy.evolve_currency_system(agents)
        
        # 模拟一些使用货币的交易
        active_agents = random.sample(agents, min(8, len(agents)))
        
        for agent in active_agents:
            # 如果Agent还没有货币，从物物交换开始获取
            if CurrencyType.GOLD_COIN not in agent.cash or agent.cash[CurrencyType.GOLD_COIN] == 0:
                # 尝试用少量资源兑换金币
                if agent.inventory.get(agent.ResourceType.FOOD, 0) > 5:
                    amount = 2
                    item_type = agent._item_from_resource(agent.ResourceType.FOOD)
                    currency_type = currency_economy.currency_exchange.create_currency_from_goods(
                        agent, item_type, amount)
                    if currency_type:
                        print(f"  Agent {agent.id} 兑换了 {amount} 个食物为 {currency_type.value}")
            
            # 使用货币进行交易
            elif agent.cash.get(CurrencyType.GOLD_COIN, 0) > 5:
                # 寻找卖家
                for other in agents:
                    if other.id != agent.id:
                        # Agent用金币购买急需物品
                        if agent.hunger > 60 and other.inventory.get(ResourceType.FOOD, 0) > 3:
                            if random.random() < 0.4:  # 40%成功率
                                price = 8.0
                                quantity = 3
                                success = agent.make_purchase(ResourceType.FOOD, quantity, price, CurrencyType.GOLD_COIN)
                                if success and other.make_sale(ResourceType.FOOD, quantity, price, CurrencyType.GOLD_COIN):
                                    print(f"  Agent {agent.id} 用 {price} 金币购买 {quantity} 食物从 Agent {other.id}")
                        break
        
        # 每2轮显示状态
        if round_num % 2 == 1:
            print_agent_status(agents, f"第 {round_num + 1} 轮后状态")
            print_market_analysis(currency_economy)
    
    print(f"\n货币演化阶段完成！")

def demonstrate_advanced_currency_features(currency_economy: CurrencyEconomy, agents: list):
    """演示高级货币功能"""
    print(f"\n=== 高级货币功能演示 ===")
    
    # 1. 货币兑换
    print("\n1. 货币兑换:")
    sample_agent = agents[0]
    if sample_agent.cash.get(CurrencyType.GOLD_COIN, 0) > 5:
        success = sample_agent.exchange_currency(
            CurrencyType.GOLD_COIN, CurrencyType.SILVER_COIN, 5)
        if success:
            print(f"  Agent {sample_agent.id} 成功兑换5金币为银币")
    
    # 2. 银行服务
    print("\n2. 银行服务:")
    sample_agent.deposit_to_bank(CurrencyType.GOLD_COIN, 3)
    print(f"  Agent {sample_agent.id} 存入3金币到银行")
    
    sample_agent.withdraw_from_bank(CurrencyType.GOLD_COIN, 2)
    print(f"  Agent {sample_agent.id} 从银行取出2金币")
    
    # 3. 多种货币使用
    print("\n3. 多种货币使用:")
    for i, agent in enumerate(agents[:3]):
        if agent.cash:
            total_wealth = agent.get_total_wealth()
            status = agent.get_currency_status()
            print(f"  Agent {agent.id}: 总财富={total_wealth:.1f}, "
                  f"现金交易={status['currency_trades']}, "
                  f"物物交易={status['barter_trades']}")

def analyze_currency_impact(currency_economy: CurrencyEconomy, agents: list):
    """分析货币系统的影响"""
    print(f"\n=== 货币系统影响分析 ===")
    
    # 统计数据
    total_barter_trades = sum(agent.barter_trades for agent in agents)
    total_currency_trades = sum(agent.currency_trades for agent in agents)
    
    print(f"物物交换交易次数: {total_barter_trades}")
    print(f"货币交易次数: {total_currency_trades}")
    
    # 计算交易效率
    barter_efficiency = currency_economy.evaluate_barter_efficiency(agents)
    print(f"物物交换效率: {barter_efficiency:.2f}")
    
    # 货币适应性分析
    print(f"\n货币适应性分布:")
    adaptation_levels = [agent.monetary_adaptation_level for agent in agents]
    avg_adaptation = sum(adaptation_levels) / len(adaptation_levels)
    print(f"平均适应性: {avg_adaptation:.2f}")
    
    # Agent财富分布
    print(f"\nAgent财富分布:")
    wealths = [agent.get_total_wealth() for agent in agents]
    print(f"平均财富: {sum(wealths)/len(wealths):.1f}")
    print(f"最富有Agent: {max(wealths):.1f} (Agent {agents[wealths.index(max(wealths))].id})")
    print(f"最贫困Agent: {min(wealths):.1f} (Agent {agents[wealths.index(min(wealths))].id})")
    
    # 货币采用率
    summary = currency_economy.get_currency_summary()
    print(f"\n货币采用率: {currency_economy.adoption_rate:.2f}")
    print(f"活跃银行账户: {summary['bank_accounts']}")
    print(f"活跃贷款: {summary['active_loans']}")

def main():
    """主函数 - 完整的货币演化演示"""
    print("💰 文明模拟器 - 货币演化演示\n")
    print("展示从物物交换向货币系统的自然演化过程\n")
    
    # 创建货币经济系统
    base_economy = Economy()
    currency_economy = CurrencyEconomy(base_economy)
    
    # 创建支持货币的Agent
    agents = create_sample_agents(10)
    
    # 连接Agent到经济系统
    currency_economy.economy.agents = agents
    
    print(f"创建了 {len(agents)} 个支持货币的Agent")
    print_agent_status(agents, "初始状态")
    
    # 第一阶段：物物交换
    simulate_barter_trading(currency_economy, agents, rounds=4)
    
    # 第二阶段：货币演化
    simulate_currency_evolution(currency_economy, agents, rounds=6)
    
    # 第三阶段：高级货币功能
    demonstrate_advanced_currency_features(currency_economy, agents)
    
    # 最终分析
    analyze_currency_impact(currency_economy, agents)
    
    print(f"\n🎉 货币演化演示完成！")
    print("成功展示了从物物交换到货币系统的自然演化过程")
    print("货币系统提高了交易效率，促进了经济发展")

if __name__ == "__main__":
    main()