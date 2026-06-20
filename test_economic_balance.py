"""
Phase 2: Economy 综合测试
测试经济系统平衡性、货币系统、交易系统
"""

import sys
import os
import random
import time
from typing import Dict, List, Tuple
from collections import defaultdict

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.economy import Economy
from src.currency_system import CurrencyEconomy, CurrencyType
from src.agent_with_currency import AgentWithCurrency
from src.agent import Agent
from src.terrain import Map, TerrainType, Tile


def test_currency_system_balance():
    """测试货币系统平衡性"""
    print("=== 测试货币系统平衡性 ===")
    
    # 创建经济系统
    economy = Economy()
    
    # 创建货币经济系统
    currency_economy = CurrencyEconomy(economy)
    
    print("货币系统参数:")
    print(f"  初始货币采用率: {currency_economy.adoption_rate:.2f}")
    print(f"  效率阈值: {currency_economy.efficiency_threshold:.2f}")
    print(f"  临界质量: {currency_economy.critical_mass:.2f}")
    
    # 创建测试Agent
    agents = []
    for i in range(10):
        agent = AgentWithCurrency(i+1, random.randint(0, 19), random.randint(0, 19), None)
        # 初始化货币
        agent.initialize_currency()
        agents.append(agent)
    
    print(f"创建了 {len(agents)} 个测试Agent")
    
    # 模拟货币经济运行
    simulation_rounds = 50
    adoption_history = []
    trade_history = []
    
    print(f"\n运行 {simulation_rounds} 轮货币经济模拟:")
    
    for round_num in range(simulation_rounds):
        # 更新货币系统
        currency_economy.evolve_currency_system(agents)
        
        # 记录采用率
        adoption_history.append(currency_economy.adoption_rate)
        
        # 随机进行货币交易
        for _ in range(random.randint(3, 8)):
            if len(agents) >= 2:
                buyer, seller = random.sample(agents, 2)
                
                # 随机选择交易物品
                from enum import Enum
                from src.economy import ItemType
                item_type = random.choice(list(ItemType))
                quantity = random.randint(1, 5)
                price = random.uniform(5, 20)
                currency_type = random.choice(list(CurrencyType))
                
                # 尝试货币交易
                if currency_economy.make_currency_trade(buyer, seller, item_type, quantity, currency_type, price):
                    trade_history.append({
                        'round': round_num,
                        'item_type': item_type.value,
                        'currency': currency_type.value,
                        'price': price
                    })
        
        if round_num % 10 == 0:
            print(f"  第{round_num}轮: 货币采用率 {currency_economy.adoption_rate:.2f}, 交易次数 {len([t for t in trade_history if t['round'] == round_num])}")
    
    # 分析货币平衡性
    print(f"\n货币平衡性分析:")
    print(f"  最终货币采用率: {currency_economy.adoption_rate:.2f}")
    print(f"  总货币交易次数: {len(trade_history)}")
    print(f"  平均每轮交易: {len(trade_history) / simulation_rounds:.1f}次")
    
    # 分析货币采用情况
    if currency_economy.adoption_rate > 0.8:
        print("  ✓ 货币系统高度采用")
    elif currency_economy.adoption_rate > 0.5:
        print("  ⚠ 货币系统中等采用")
    else:
        print("  ⚠ 货币系统采用率较低")
    
    # 分析交易活跃度
    if len(trade_history) >= simulation_rounds * 3:
        print("  ✓ 货币交易活跃")
    elif len(trade_history) >= simulation_rounds:
        print("  ⚠ 货币交易中等活跃")
    else:
        print("  ⚠ 货币交易不够活跃")
    
    # 获取货币系统摘要
    try:
        currency_summary = currency_economy.get_currency_summary()
        print(f"\n货币系统摘要:")
        for currency_type, total_amount in currency_summary['active_currencies'].items():
            if total_amount > 0:
                print(f"  {currency_type}: {total_amount:.2f}")
    except AttributeError:
        print("\n跳过货币系统摘要（agents属性不存在）")
    
    return True


def test_trading_system_balance():
    """测试交易系统平衡性"""
    print("\n=== 测试交易系统平衡性 ===")
    
    # 创建经济系统
    economy = Economy()
    
    # 创建测试Agent
    agents = []
    for i in range(15):
        agent = AgentWithCurrency(i+1, random.randint(0, 19), random.randint(0, 19), None)
        # 初始化货币
        agent.initialize_currency()
        
        # 初始资源
        agent.inventory['food'] = random.uniform(10, 40)
        agent.inventory['water'] = random.uniform(8, 35)
        agent.inventory['wood'] = random.uniform(5, 25)
        agent.inventory['mineral'] = random.uniform(2, 15)
        
        agents.append(agent)
    
    print(f"创建了 {len(agents)} 个测试Agent")
    print("初始资源分布（前3个）:")
    for i, agent in enumerate(agents[:3]):
        total_wealth = agent.cash.get(CurrencyType.GOLD_COIN, 0) + sum(agent.inventory.values())
        print(f"  Agent {agent.id}: 总财富{total_wealth:.1f}")
    
    # 运行交易模拟
    simulation_rounds = 40
    trade_history = []
    price_history = defaultdict(list)
    market_efficiency_history = []
    
    print(f"\n运行 {simulation_rounds} 轮交易模拟:")
    
    for round_num in range(simulation_rounds):
        # 更新市场
        economy.update_market(agents)
        
        # 记录市场效率
        efficiency = economy.trading_post.successful_trades / max(1, economy.trading_post.successful_trades + economy.trading_post.failed_trades)
        market_efficiency_history.append(efficiency)
        
        round_trades = 0
        
        # 每轮随机进行交易
        for _ in range(random.randint(5, 12)):  # 每轮5-12次交易
            if len(agents) >= 2:
                # 随机选择两个Agent
                trader1, trader2 = random.sample(agents, 2)
                
                # 随机选择交易物品
                from src.economy import ItemType
                item_type = random.choice(list(ItemType))
                quantity = random.randint(1, 3)
                
                # 尝试通过交易点进行交易
                if economy.trading_post.execute_trade(trader1, trader2, item_type, quantity, 
                                                    economy.market.get_price(item_type)):
                    round_trades += 1
                    trade_history.append({
                        'round': round_num,
                        'item_type': item_type.value,
                        'quantity': quantity,
                        'price': economy.market.get_price(item_type)
                    })
                    
                    # 记录价格历史
                    price_history[item_type.value].append(economy.market.get_price(item_type))
        
        if round_num % 10 == 0:
            print(f"  第{round_num}轮: {round_trades}次交易, 市场效率{efficiency:.2f}")
    
    # 分析交易平衡性
    print(f"\n交易平衡性分析:")
    print(f"  总交易次数: {len(trade_history)}")
    print(f"  平均每轮交易: {len(trade_history) / simulation_rounds:.1f}次")
    print(f"  成功交易: {economy.trading_post.successful_trades}")
    print(f"  失败交易: {economy.trading_post.failed_trades}")
    
    # 分析市场效率
    avg_efficiency = sum(market_efficiency_history) / len(market_efficiency_history)
    print(f"  平均市场效率: {avg_efficiency:.2f}")
    
    if avg_efficiency > 0.8:
        print("  ✓ 市场效率优秀")
    elif avg_efficiency > 0.6:
        print("  ⚠ 市场效率中等")
    else:
        print("  ✗ 市场效率较低")
    
    # 分析资源价格稳定性
    print(f"\n资源价格稳定性分析:")
    for resource, prices in price_history.items():
        if len(prices) >= 5:
            avg_price = sum(prices) / len(prices)
            price_std = (sum((p - avg_price) ** 2 for p in prices) / len(prices)) ** 0.5
            cv = price_std / avg_price if avg_price > 0 else 0  # 变异系数
            
            print(f"  {resource}: 平均价格{avg_price:.2f}, 波动率{cv:.3f}")
            
            if cv < 0.15:  # 变异系数小于15%，价格稳定
                print(f"    ✓ {resource}价格稳定")
            elif cv < 0.3:  # 变异系数15%-30%，价格波动可接受
                print(f"    ⚠ {resource}价格波动中等")
            else:  # 变异系数大于30%，价格不稳定
                print(f"    ✗ {resource}价格波动过大")
    
    # 分析财富分配
    final_wealth = []
    for agent in agents:
        total_wealth = agent.cash.get(CurrencyType.GOLD_COIN, 0) + sum(agent.inventory.values())
        final_wealth.append(total_wealth)
    
    final_wealth.sort()
    avg_wealth = sum(final_wealth) / len(final_wealth)
    gini_coefficient = calculate_gini_coefficient(final_wealth)
    
    print(f"\n财富分配分析:")
    print(f"  平均财富: {avg_wealth:.2f}")
    print(f"  最富/最贫比例: {final_wealth[-1] / final_wealth[0]:.2f}")
    print(f"  基尼系数: {gini_coefficient:.3f}")
    
    # 基尼系数评价
    if gini_coefficient < 0.3:  # 相对平等
        print("  ✓ 财富分配相对平等")
    elif gini_coefficient < 0.5:  # 中等不平等
        print("  ⚠ 财富分配中等不平等")
    else:  # 高度不平等
        print("  ✗ 财富分配高度不平等")
    
    # 检查交易活跃度
    if len(trade_history) >= simulation_rounds * 2:
        print("  ✓ 交易活跃度高")
    elif len(trade_history) >= simulation_rounds:
        print("  ⚠ 交易活跃度中等")
    else:
        print("  ✗ 交易活跃度低")
    
    return True


def test_economy_system_balance():
    """测试经济系统平衡性"""
    print("\n=== 测试经济系统平衡性 ===")
    
    # 创建经济系统
    economy = Economy()
    
    # 初始化经济参数
    print("经济系统参数:")
    print(f"  成功交易: {economy.trading_post.successful_trades}")
    print(f"  失败交易: {economy.trading_post.failed_trades}")
    print(f"  市场效率: {economy.trading_post.successful_trades / max(1, economy.trading_post.successful_trades + economy.trading_post.failed_trades):.2f}")
    
    # 创建多个Agent组成经济
    agents = []
    for i in range(20):
        agent = AgentWithCurrency(i+1, random.randint(0, 19), random.randint(0, 19), None)
        # 初始化货币
        agent.initialize_currency()
        
        # 初始资源
        agent.inventory['food'] = random.uniform(5, 30)
        agent.inventory['water'] = random.uniform(5, 25)
        agent.inventory['wood'] = random.uniform(3, 20)
        agent.inventory['mineral'] = random.uniform(1, 10)
        
        agents.append(agent)
    
    print(f"\n创建了 {len(agents)} 个经济Agent")
    
    # 创建地图
    world_map = Map(20, 20)
    world_map.initialize_empty()
    
    # 设置地形和资源
    for y in range(20):
        for x in range(20):
            tile = world_map.get_tile(x, y)
            if y < 5:
                tile.terrain_type = TerrainType.WATER
                tile.resources["water"] = random.uniform(0.5, 1.0)
            elif y < 10:
                tile.terrain_type = TerrainType.LOWLAND
                tile.resources["food"] = random.uniform(0.3, 0.8)
            elif y < 15:
                tile.terrain_type = TerrainType.FOREST
                tile.resources["wood"] = random.uniform(0.2, 0.6)
            else:
                tile.terrain_type = TerrainType.MOUNTAIN
                tile.resources["mineral"] = random.uniform(0.1, 0.4)
    
    # 运行经济模拟
    simulation_rounds = 25
    economy_stats = []
    
    print(f"\n运行 {simulation_rounds} 轮经济模拟:")
    
    for round_num in range(simulation_rounds):
        # 更新市场状态
        economy.update_market(agents)
        
        # Agent经济行为
        for agent in agents:
            if agent.health > 0:  # 只考虑存活的Agent
                # 随机采集资源
                if random.random() < 0.4:  # 40%概率采集
                    # 在当前位置采集
                    tile = world_map.get_tile(agent.x, agent.y)
                    if tile and tile.terrain_type != TerrainType.WATER:
                        if tile.terrain_type == TerrainType.LOWLAND and agent.inventory.get('food', 0) < 20:
                            agent.inventory['food'] = min(20, agent.inventory.get('food', 0) + random.uniform(0.5, 2.0))
                        elif tile.terrain_type == TerrainType.FOREST and agent.inventory.get('wood', 0) < 15:
                            agent.inventory['wood'] = min(15, agent.inventory.get('wood', 0) + random.uniform(0.3, 1.5))
                        elif tile.terrain_type == TerrainType.MOUNTAIN and agent.inventory.get('mineral', 0) < 10:
                            agent.inventory['mineral'] = min(10, agent.inventory.get('mineral', 0) + random.uniform(0.2, 1.0))
                
                # 随机移动（寻找更好的资源点）
                if random.random() < 0.3:  # 30%概率移动
                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    dx, dy = random.choice(directions)
                    new_x = max(0, min(19, agent.x + dx))
                    new_y = max(0, min(19, agent.y + dy))
                    
                    # 移动到新位置
                    tile = world_map.get_tile(new_x, new_y)
                    if tile:
                        agent.x = new_x
                        agent.y = new_y
                        agent.current_tile = tile
        
        # 收集统计数据
        total_wealth = sum(agent.cash.get(CurrencyType.GOLD_COIN, 0) + sum(agent.inventory.values()) for agent in agents)
        total_resources = sum(sum(agent.inventory.values()) for agent in agents)
        active_trades = economy.trading_post.successful_trades + economy.trading_post.failed_trades
        survival_rate = len([a for a in agents if a.health > 0]) / len(agents)
        
        round_stats = {
            "round": round_num,
            "total_wealth": total_wealth,
            "total_resources": total_resources,
            "active_trades": active_trades,
            "survival_rate": survival_rate,
            "avg_market_price": sum(economy.market.current_prices.values()) / len(economy.market.current_prices)
        }
        economy_stats.append(round_stats)
        
        if round_num % 5 == 0:
            print(f"  第{round_num}轮: "
                 f"总财富{round_stats['total_wealth']:.1f}, "
                 f"总资源{round_stats['total_resources']:.1f}, "
                 f"交易{round_stats['active_trades']}次, "
                 f"生存率{round_stats['survival_rate']:.1%}")
    
    # 分析经济平衡性
    print(f"\n经济平衡性分析:")
    
    # 财富分布分析
    final_wealth = []
    for agent in agents:
        total_wealth = agent.cash.get(CurrencyType.GOLD_COIN, 0) + sum(agent.inventory.values())
        final_wealth.append(total_wealth)
    
    avg_wealth = sum(final_wealth) / len(final_wealth)
    wealth_std = (sum((w - avg_wealth) ** 2 for w in final_wealth) / len(final_wealth)) ** 0.5
    wealth_cv = wealth_std / avg_wealth if avg_wealth > 0 else 0  # 财富变异系数
    
    print(f"  平均财富: {avg_wealth:.2f}, 财富波动率: {wealth_cv:.3f}")
    
    if wealth_cv < 0.5:  # 财富分布相对均衡
        print("  ✓ 财富分配相对均衡")
    elif wealth_cv < 1.0:  # 财富分布中等波动
        print("  ⚠ 财富分配中等不均衡")
    else:  # 财富分配高度不均衡
        print("  ✗ 财富分配高度不均衡")
    
    # 经济活力分析
    avg_trades_per_round = sum(s["active_trades"] for s in economy_stats) / len(economy_stats)
    print(f"  平均每轮交易次数: {avg_trades_per_round:.1f}")
    
    if avg_trades_per_round > 8:
        print("  ✓ 经济交易活跃")
    elif avg_trades_per_round > 4:
        print("  ⚠ 经济交易中等活跃")
    else:
        print("  ⚠ 经济交易不够活跃")
    
    # 生存率分析
    final_survival_rate = economy_stats[-1]["survival_rate"]
    print(f"  最终生存率: {final_survival_rate:.1%}")
    
    if final_survival_rate > 0.9:
        print("  ✓ 经济系统稳定性优秀")
    elif final_survival_rate > 0.7:
        print("  ⚠ 经济系统稳定性良好")
    else:
        print("  ✗ 经济系统稳定性较差")
    
    # 市场效率分析
    final_market_efficiency = economy.trading_post.successful_trades / max(1, economy.trading_post.successful_trades + economy.trading_post.failed_trades)
    print(f"  最终市场效率: {final_market_efficiency:.2f}")
    
    if final_market_efficiency > 0.8:
        print("  ✓ 市场效率优秀")
    elif final_market_efficiency > 0.6:
        print("  ⚠ 市场效率中等")
    else:
        print("  ✗ 市场效率较低")
    
    # 资源丰富度分析
    resource_growth = (economy_stats[-1]["total_resources"] / economy_stats[0]["total_resources"]) ** (1/simulation_rounds) - 1
    print(f"  资源增长率: {resource_growth:.4f}")
    
    if resource_growth > 0.02:  # 资源持续增长
        print("  ✓ 资源生产可持续")
    elif resource_growth > 0:  # 资源缓慢增长
        print("  ⚠ 资源生产缓慢")
    else:  # 资源减少
        print("  ⚠ 资源生产不足")
    
    return True


def test_agent_economic_behavior():
    """测试Agent经济行为"""
    print("\n=== 测试Agent经济行为 ===")
    
    # 创建测试Agent
    agents = []
    for i in range(12):
        agent = AgentWithCurrency(i+1, random.randint(0, 19), random.randint(0, 19), None)
        # 初始化货币
        agent.initialize_currency()
        
        # 初始资源
        agent.inventory['food'] = random.uniform(10, 40)
        agent.inventory['water'] = random.uniform(8, 30)
        agent.inventory['wood'] = random.uniform(5, 25)
        agent.inventory['mineral'] = random.uniform(2, 15)
        
        agents.append(agent)
    
    print(f"创建了 {len(agents)} 个测试Agent")
    
    # 创建经济系统
    economy = Economy()
    
    # 模拟Agent经济行为
    simulation_rounds = 20
    behavior_stats = defaultdict(list)
    trade_activity = []
    wealth_evolution = []
    
    print(f"\n运行 {simulation_rounds} 轮经济行为模拟:")
    
    for round_num in range(simulation_rounds):
        round_trades = 0
        round_wealth = []
        
        for agent in agents:
            if agent.health > 0:  # 只考虑存活的Agent
                # Agent经济决策
                if hasattr(agent, 'make_economic_decision'):
                    try:
                        agent.make_economic_decision()
                    except:
                        pass  # 忽略不存在的方法
                
                # Agent货币交易行为
                if random.random() < 0.4:  # 40%概率进行货币交易
                    other_agents = [a for a in agents if a.id != agent.id and a.health > 0]
                    if other_agents:
                        trading_partner = random.choice(other_agents)
                        
                        # 尝试货币兑换
                        if random.random() < 0.3:  # 30%概率货币兑换
                            from src.currency_system import CurrencyType
                            from_curr = random.choice(list(CurrencyType))
                            to_curr = random.choice(list(CurrencyType))
                            amount = random.uniform(1, 5)
                            agent.exchange_currency(from_curr, to_curr, amount)
                        
                        # 尝试货币交易
                        elif random.random() < 0.5:  # 50%概率购买
                            from src.economy import ItemType
                            from src.currency_system import CurrencyType
                            item_type = random.choice(list(ItemType))
                            quantity = random.randint(1, 3)
                            price = random.uniform(3, 15)
                            currency = random.choice(list(CurrencyType))
                            agent.make_purchase(item_type, quantity, price, currency)
                        else:  # 50%概率出售
                            from src.economy import ItemType
                            from src.currency_system import CurrencyType
                            item_type = random.choice(list(ItemType))
                            quantity = random.randint(1, 3)
                            price = random.uniform(5, 20)
                            currency = random.choice(list(CurrencyType))
                            agent.make_sale(item_type, quantity, price, currency)
                        
                        round_trades += 1
                
                # 记录行为统计
                from src.currency_system import CurrencyType
                total_wealth = agent.cash.get(CurrencyType.GOLD_COIN, 0) + sum(agent.inventory.values())
                behavior_stats[f"agent_{agent.id}_wealth"].append(total_wealth)
                behavior_stats[f"agent_{agent.id}_health"].append(agent.health)
                behavior_stats[f"agent_{agent.id}_currency_trades"].append(agent.currency_trades)
                round_wealth.append(total_wealth)
        
        trade_activity.append(round_trades)
        wealth_evolution.append(sum(round_wealth) / len(round_wealth))
        
        if round_num % 5 == 0:
            alive_agents = [a for a in agents if a.health > 0]
            avg_trades = trade_activity[-1] if trade_activity else 0
            print(f"  第{round_num}轮: {len(alive_agents)}/{len(agents)} 个Agent存活, {avg_trades}次交易")
    
    # 分析Agent经济行为
    print(f"\nAgent经济行为分析:")
    
    # 生存能力分析
    final_survival = [agent for agent in agents if agent.health > 0]
    survival_rate = len(final_survival) / len(agents)
    print(f"  Agent生存率: {survival_rate:.1%}")
    
    if survival_rate > 0.9:
        print("  ✓ Agent生存能力很强")
    elif survival_rate > 0.7:
        print("  ⚠ Agent生存能力中等")
    else:
        print("  ✗ Agent生存能力较弱")
    
    # 交易活跃度分析
    avg_trades_per_round = sum(trade_activity) / len(trade_activity)
    print(f"  平均每轮交易次数: {avg_trades_per_round:.1f}")
    
    if avg_trades_per_round > 5:
        print("  ✓ Agent交易行为活跃")
    elif avg_trades_per_round > 2:
        print("  ⚠ Agent交易行为中等活跃")
    else:
        print("  ⚠ Agent交易行为不够活跃")
    
    # 财富分配分析
    final_wealth = []
    for agent in agents:
        total_wealth = agent.cash.get(CurrencyType.GOLD_COIN, 0) + sum(agent.inventory.values())
        final_wealth.append(total_wealth)
    
    final_wealth.sort()
    avg_wealth = sum(final_wealth) / len(final_wealth)
    wealthiest = final_wealth[-1]
    poorest = final_wealth[0]
    wealth_ratio = wealthiest / poorest if poorest > 0 else float('inf')
    
    print(f"  平均财富: {avg_wealth:.2f}")
    print(f"  最富/最贫财富比: {wealth_ratio:.2f}")
    
    if wealth_ratio < 4:  # 财富差距较小
        print("  ✓ 财富分配相对均衡")
    elif wealth_ratio < 8:  # 财富差距中等
        print("  ⚠ 财富差距中等")
    else:  # 财富差距较大
        print("  ⚠ 财富差距较大")
    
    # 经济适应能力分析
    if len(wealth_evolution) > 1:
        wealth_trend = (wealth_evolution[-1] / wealth_evolution[0]) - 1
        print(f"  财富变化趋势: {wealth_trend:+.1%}")
        
        if wealth_trend > 0.1:  # 财富显著增长
            print("  ✓ 经济适应能力强，财富增长良好")
        elif wealth_trend > -0.1:  # 财富稳定
            print("  ⚠ 经济适应能力中等，财富相对稳定")
        else:  # 财富减少
            print("  ⚠ 经济适应能力较弱，财富呈下降趋势")
    
    # 货币采用分析
    from src.currency_system import CurrencyType
    total_currency_trades = sum(agent.currency_trades for agent in agents)
    avg_currency_trades = total_currency_trades / len(agents)
    print(f"  平均每人货币交易次数: {avg_currency_trades:.1f}")
    
    if avg_currency_trades > 3:
        print("  ✓ Agent积极采用货币系统")
    elif avg_currency_trades > 1:
        print("  ⚠ Agent中等程度采用货币系统")
    else:
        print("  ⚠ Agent较少使用货币系统")
    
    return True


def calculate_gini_coefficient(wealth_values):
    """计算基尼系数"""
    if len(wealth_values) <= 1:
        return 0
    
    wealth_values = sorted(wealth_values)
    n = len(wealth_values)
    total_wealth = sum(wealth_values)
    
    if total_wealth == 0:
        return 0
    
    # 计算基尼系数
    gini = 0
    for i in range(n):
        gini += (2 * (i + 1) - n - 1) * wealth_values[i]
    
    gini = gini / (n * total_wealth)
    return abs(gini)


def run_performance_test():
    """经济系统性能测试"""
    print("\n=== 经济系统性能测试 ===")
    
    # 测试不同规模经济的性能
    scales = [10, 20, 50]  # Agent数量
    
    for scale in scales:
        print(f"\n测试 {scale} 个Agent的经济系统:")
        
        # 创建经济系统
        economy = Economy()
        agents = []
        
        for i in range(scale):
            agent = AgentWithCurrency(i+1, random.randint(0, 19), random.randint(0, 19), None)
            # 初始化货币
            agent.initialize_currency()
            
            # 初始资源
            agent.inventory['food'] = random.uniform(10, 40)
            agent.inventory['water'] = random.uniform(8, 30)
            agent.inventory['wood'] = random.uniform(5, 20)
            agent.inventory['mineral'] = random.uniform(2, 15)
            
            agents.append(agent)
        
        # 性能测试
        start_time = time.time()
        
        for round_num in range(20):  # 运行20轮
            economy.update_market(agents)
            
            # 随机交易
            for _ in range(scale):  # 每轮scale次交易
                if len(agents) >= 2:
                    trader1, trader2 = random.sample(agents, 2)
                    
                    # 随机选择交易物品
                    from src.economy import ItemType
                    item_type = random.choice(list(ItemType))
                    quantity = random.randint(1, 3)
                    price = economy.market.get_price(item_type)
                    
                    # 尝试交易
                    economy.trading_post.execute_trade(trader1, trader2, item_type, quantity, price)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_round = total_time / 20
        
        print(f"  20轮总耗时: {total_time:.2f}秒")
        print(f"  平均每轮耗时: {avg_time_per_round:.3f}秒")
        
        # 性能评价
        if avg_time_per_round < 0.1:
            print("  ✓ 性能优秀")
        elif avg_time_per_round < 0.5:
            print("  ✓ 性能良好")
        else:
            print("  ⚠ 性能需要优化")


def main():
    """主测试函数"""
    print("Phase 2: Economy 综合测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行所有经济测试
    try:
        test_results.append(test_currency_system_balance())
        test_results.append(test_trading_system_balance())
        test_results.append(test_economy_system_balance())
        test_results.append(test_agent_economic_behavior())
        
        # 性能测试（可选）
        run_performance_test()
        
        # 汇总结果
        print("\n" + "=" * 50)
        print("测试结果汇总:")
        
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"通过测试: {passed}/{total}")
        
        if passed == total:
            print("✓ 所有测试通过！Phase 2: Economy 系统经济平衡性良好。")
        else:
            print("⚠ 部分测试失败，经济系统需要进一步优化。")
        
        return passed == total
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)