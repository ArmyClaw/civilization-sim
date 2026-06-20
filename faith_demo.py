#!/usr/bin/env python3
"""
信仰与文化传播系统完整演示
展示所有信仰功能：生成、传播、行为影响、部落统一等
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import Agent, Profession, ResourceType, AgentState
from src.terrain import TerrainType, Tile
from src.faith_system import FaithManager, FaithType, CulturalTrait
import random

def create_agents(count: int = 15):
    """创建测试agents"""
    agents = []
    
    for i in range(count):
        # 随机地形和位置
        terrain_types = [TerrainType.FOREST, TerrainType.LOWLAND, TerrainType.MOUNTAIN]
        terrain = random.choice(terrain_types)
        tile = Tile(i % 5, i // 5, terrain)  # 5x3网格
        
        # 随机职业
        profession = random.choice(list(Profession))
        
        # 创建agent
        agent = Agent(i, i % 5, i // 5, tile, profession)
        
        # 设置初始资源
        agent.inventory[ResourceType.FOOD] = random.randint(5, 20)
        agent.inventory[ResourceType.WATER] = random.randint(5, 20)
        agent.health = random.randint(60, 100)
        agent.energy = random.randint(40, 100)
        
        agents.append(agent)
    
    return agents

def demonstrate_faith_generation(agents):
    """演示信仰生成"""
    print("=== 1. 信仰生成演示 ===")
    
    faith_manager = FaithManager()
    
    # 为所有agents生成信仰
    for agent in agents:
        faith_manager.generate_initial_faith(agent)
    
    # 统计和展示信仰分布
    stats = faith_manager.get_faith_statistics(agents)
    
    print(f"创建了{len(agents)}个agents")
    print(f"信仰普及率: {stats['faith_percentage']:.1f}%")
    
    print("\\n信仰类型分布:")
    for faith_type, count in stats['faith_distribution'].items():
        percentage = (count / len(agents)) * 100
        print(f"  {faith_type}: {count}人 ({percentage:.1f}%)")
    
    print("\\n文化特征分布:")
    for trait, count in stats['cultural_trait_distribution'].items():
        percentage = (count / len(agents)) * 100
        print(f"  {trait}: {count}人 ({percentage:.1f}%)")
    
    return faith_manager

def demonstrate_faith_influences(agents, faith_manager):
    """演示信仰影响和传播"""
    print("\\n=== 2. 信仰传播演示 ===")
    
    # 展示初始状态
    print("\\n初始状态:")
    for i, agent in enumerate(agents[:5]):  # 只显示前5个
        if agent.faith:
            print(f"  Agent {agent.id} ({agent.profession.value}): {agent.faith.faith_type.value} (强度: {agent.faith.strength:.1f})")
    
    # 进行多轮传播
    for round_num in range(3):
        print(f"\\n第{round_num + 1}轮传播:")
        
        # 更新信仰影响
        faith_manager.update_faith_influences(agents)
        
        # 显示变化
        changed_count = 0
        for i, agent in enumerate(agents[:5]):
            if agent.faith:
                print(f"  Agent {agent.id}: {agent.faith.faith_type.value} (强度: {agent.faith.strength:.1f})")
                
        stats = faith_manager.get_faith_statistics(agents)
        print(f"  总信仰普及率: {stats['faith_percentage']:.1f}%")

def demonstrate_behavior_influences(agents, faith_manager):
    """演示行为影响"""
    print("\\n=== 3. 行为影响演示 ===")
    
    # 选择几个agents详细观察
    test_agents = agents[:3]
    
    for agent in test_agents:
        print(f"\\n观察Agent {agent.id} ({agent.profession.value}):")
        if agent.faith:
            print(f"  信仰: {agent.faith.faith_type.value} (强度: {agent.faith.strength:.1f})")
            print(f"  价值观: {[t.value for t in agent.faith.values]}")
        else:
            print("  无信仰")
        
        # 模拟行为
        print("  行为模拟:")
        for step in range(2):
            # 简化的行为模拟（不依赖world_map）
            old_hunger = agent.hunger
            old_energy = agent.energy
            
            # 基础消耗
            agent.hunger += agent.hunger_rate
            agent.thirst += agent.thirst_rate
            
            # 信仰影响消耗
            if agent.faith:
                if agent.faith.faith_type == FaithType.SPIRITUAL:
                    agent.hunger += agent.hunger_rate * 0.8
                    agent.thirst += agent.thirst_rate * 0.8
                elif agent.faith.faith_type == FaithType.NATURE:
                    if agent.current_tile.terrain_type == TerrainType.FOREST:
                        agent.hunger += agent.hunger_rate * 0.9
            
            # 恢复行为（模拟休息）
            if agent.energy < 50:
                agent.energy = min(100, agent.energy + 10)
                if agent.faith and agent.faith.faith_type == FaithType.SPIRITUAL:
                    agent.health = min(100, agent.health + 2)
                print(f"    步骤{step+1}: 休息恢复 - 能量: {old_energy:.1f}→{agent.energy:.1f}, 健康: {agent.health:.1f}")
            else:
                print(f"    步骤{step+1}: 正常状态 - 饥饿: {old_hunger:.1f}→{agent.hunger:.1f}, 能量: {old_energy:.1f}→{agent.energy:.1f}")

def demonstrate_tribe_effects(agents):
    """演示部落统一化效果"""
    print("\\n=== 4. 部落统一化演示 ===")
    
    # 创建模拟部落（按ID分组）
    tribes = {}
    for i, tribe_id in enumerate([0, 0, 1, 1, 2, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]):
        if tribe_id not in tribes:
            tribes[tribe_id] = []
        tribes[tribe_id].append(agents[i])
    
    print(f"形成了{len(tribes)}个部落")
    
    # 为每个部落应用统一化
    for tribe_id, tribe_agents in tribes.items():
        print(f"\\n部落{tribe_id} ({len(tribe_agents)}人):")
        
        # 显示统一前状态
        before_counts = {}
        for agent in tribe_agents:
            if agent.faith:
                faith_type = agent.faith.faith_type.value
                before_counts[faith_type] = before_counts.get(faith_type, 0) + 1
        
        print(f"  统一前: {before_counts}")
        
        # 应用部落统一化
        faith_manager = FaithManager()
        faith_manager.cultural_spread.tribe_faith_conversion(tribe_agents)
        
        # 显示统一后状态
        after_counts = {}
        for agent in tribe_agents:
            if agent.faith:
                faith_type = agent.faith.faith_type.value
                after_counts[faith_type] = after_counts.get(faith_type, 0) + 1
        
        print(f"  统一后: {after_counts}")

def analyze_faith_impact(agents):
    """分析信仰对社会的影响"""
    print("\\n=== 5. 信仰社会影响分析 ===")
    
    # 按信仰类型分组分析
    faith_groups = {}
    for agent in agents:
        if agent.faith:
            faith_type = agent.faith.faith_type.value
            if faith_type not in faith_groups:
                faith_groups[faith_type] = []
            faith_groups[faith_type].append(agent)
    
    # 分析每个信仰群体
    for faith_type, group_agents in faith_groups.items():
        print(f"\\n{faith_type}信仰群体分析:")
        
        # 基本属性
        avg_health = sum(a.health for a in group_agents) / len(group_agents)
        avg_energy = sum(a.energy for a in group_agents) / len(group_agents)
        avg_hunger = sum(a.hunger for a in group_agents) / len(group_agents)
        
        print(f"  平均健康: {avg_health:.1f}")
        print(f"  平均能量: {avg_energy:.1f}")
        print(f"  平均饥饿: {avg_hunger:.1f}")
        
        # 职业分布
        professions = {}
        for agent in group_agents:
            prof = agent.profession.value
            professions[prof] = professions.get(prof, 0) + 1
        print(f"  职业分布: {professions}")
        
        # 价值观分布
        traits = {}
        for agent in group_agents:
            for trait in agent.faith.values:
                trait_name = trait.value
                traits[trait_name] = traits.get(trait_name, 0) + 1
        print(f"  价值观: {traits}")

def main():
    """主演示函数"""
    print("🌟 信仰与文化传播系统完整演示 🌟")
    print("=" * 50)
    
    # 创建agents
    agents = create_agents(15)
    
    # 1. 信仰生成
    faith_manager = demonstrate_faith_generation(agents)
    
    # 2. 信仰传播
    demonstrate_faith_influences(agents, faith_manager)
    
    # 3. 行为影响
    demonstrate_behavior_influences(agents, faith_manager)
    
    # 4. 部落统一化
    demonstrate_tribe_effects(agents)
    
    # 5. 社会影响分析
    analyze_faith_impact(agents)
    
    # 总结
    print("\\n" + "=" * 50)
    print("🎉 信仰系统演示完成!")
    print("\\n已实现的功能:")
    print("✅ 六种信仰类型: 祖先、自然、社群、技术、精神、传统")
    print("✅ 六种文化特征: 合作、竞争、保守、创新、精神、物质")
    print("✅ 智能信仰生成: 基于职业、位置、随机因素")
    print("✅ 信仰传播机制: 基于距离的传播和同化")
    print("✅ 行为影响系统: 信仰影响资源采集、移动、恢复等")
    print("✅ 部落统一化: 部落内信仰同质化")
    print("✅ 社会影响分析: 不同信仰群体的特征分析")
    print("\\n🌟 信仰系统已成功集成到文明模拟中!")

if __name__ == "__main__":
    main()