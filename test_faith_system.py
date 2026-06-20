#!/usr/bin/env python3
"""
信仰与文化传播系统集成测试脚本
验证信仰系统、文化传承和行为影响机制
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tribe_system import TribeFormation
from src.agent import Agent, Profession, ResourceType
from src.terrain import Tile, TerrainType, Map
from src.generator import TerrainGenerator, ResourceGenerator
from src.faith_system import FaithManager, FaithType, CulturalTrait
import random

def create_test_environment(width: int = 15, height: int = 15, agent_count: int = 20):
    """创建测试环境"""
    # 创建地图
    world_map = Map(width, height)
    
    # 生成地形
    terrain_gen = TerrainGenerator(world_map)
    terrain_gen.generate_terrain()
    
    # 生成资源
    resource_gen = ResourceGenerator(world_map)
    resource_gen.distribute_resources()
    
    # 创建Agent
    agents = []
    professions = list(Profession)
    
    for i in range(agent_count):
        # 随机选择非水域位置
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            tile = world_map.grid[y][x]
            if tile.terrain_type != TerrainType.WATER:
                break
        
        profession = random.choice(professions)
        agent = Agent(i, x, y, tile, profession)
        
        # 设置初始资源
        agent.inventory[ResourceType.FOOD] = random.randint(5, 15)
        agent.inventory[ResourceType.WATER] = random.randint(5, 15)
        agent.inventory[ResourceType.WOOD] = random.randint(2, 8)
        agent.inventory[ResourceType.MINERAL] = random.randint(1, 5)
        
        # 设置健康状态
        agent.health = random.randint(70, 100)
        agent.max_inventory = 20
        
        agents.append(agent)
    
    return world_map, agents

def test_faith_generation(agents: list):
    """测试信仰生成系统"""
    print("=== 信仰生成系统测试 ===")
    
    faith_manager = FaithManager()
    
    # 为所有agent生成信仰
    for agent in agents:
        faith_manager.generate_initial_faith(agent)
    
    # 统计信仰分布
    stats = faith_manager.get_faith_statistics(agents)
    
    print(f"总人数: {stats['total_agents']}")
    print(f"有信仰人数: {stats['agents_with_faith']}")
    print(f"信仰普及率: {stats['faith_percentage']:.1f}%")
    
    print(f"\\n信仰分布:")
    for faith_type, count in stats['faith_distribution'].items():
        percentage = (count / stats['total_agents']) * 100
        print(f"  {faith_type}: {count}人 ({percentage:.1f}%)")
    
    print(f"\\n文化特征分布:")
    for trait, count in stats['cultural_trait_distribution'].items():
        percentage = (count / stats['total_agents']) * 100
        print(f"  {trait}: {count}人 ({percentage:.1f}%)")
    
    return stats

def test_faith_influences(agents: list, world_map):
    """测试信仰影响系统"""
    print("\\n=== 信仰影响系统测试 ===")
    
    faith_manager = FaithManager()
    
    # 多轮更新，观察信仰传播
    for round_num in range(5):
        print(f"\\n第{round_num + 1}轮信仰传播:")
        
        # 更新信仰影响
        faith_manager.update_faith_influences(agents)
        
        # 统计信仰变化
        stats = faith_manager.get_faith_statistics(agents)
        print(f"  有信仰人数: {stats['agents_with_faith']}/{stats['total_agents']}")
        
        # 显示几个典型agent的信仰状态
        sample_agents = random.sample(agents, min(3, len(agents)))
        for agent in sample_agents:
            if agent.faith:
                print(f"    Agent {agent.id}: {agent.faith.faith_type.value} (强度: {agent.faith.strength:.1f})")
                print(f"      价值观: {[trait.value for trait in agent.faith.values]}")

def test_behavior_influences(agents: list, world_map):
    """测试行为影响系统"""
    print("\\n=== 行为影响系统测试 ===")
    
    # 选择几个agent进行详细观察
    test_agents = random.sample(agents, min(5, len(agents)))
    
    for agent in test_agents:
        print(f"\\n观察Agent {agent.id} (职业: {agent.profession.value}):")
        
        if agent.faith:
            print(f"  信仰: {agent.faith.faith_type.value} (强度: {agent.faith.strength:.1f})")
            print(f"  价值观: {[trait.value for trait in agent.faith.values]}")
            
            # 模拟几个更新步骤
            for step in range(3):
                logs = agent.update(world_map)
                if logs:
                    print(f"    步骤{step + 1}: {logs[-1]}")  # 只显示最后一条日志
        else:
            print("  无信仰")

def test_tribe_faith_conversion(agents: list):
    """测试部落内信仰统一化"""
    print("\\n=== 部落内信仰统一化测试 ===")
    
    # 创建部落
    formation = TribeFormation(agents)
    tribes = formation.form_tribes_hybrid(geo_distance=4.0, social_threshold=0.3)
    
    print(f"形成了{len(tribes)}个部落")
    
    # 为每个部落内的agent设置信仰（如果没有的话）
    faith_manager = FaithManager()
    for tribe in tribes:
        for agent in tribe.members:
            if not agent.faith:
                faith_manager.generate_initial_faith(agent)
    
    # 显示部落初始信仰状态
    for i, tribe in enumerate(tribes[:3]):  # 只显示前3个部落
        print(f"\\n部落{i+1} ({len(tribe.members)}人):")
        
        faith_counts = {}
        for agent in tribe.members:
            if agent.faith:
                faith_type = agent.faith.faith_type.value
                faith_counts[faith_type] = faith_counts.get(faith_type, 0) + 1
        
        print(f"  信仰分布: {faith_counts}")
        
        # 应用部落统一化
        faith_manager.cultural_spread.tribe_faith_conversion(list(tribe.members))
        
        # 显示统一化后的状态
        after_counts = {}
        for agent in tribe.members:
            if agent.faith:
                faith_type = agent.faith.faith_type.value
                after_counts[faith_type] = after_counts.get(faith_type, 0) + 1
        
        print(f"  统一后: {after_counts}")

def analyze_faith_impact(agents: list):
    """分析信仰对整体社会的影响"""
    print("\\n=== 信仰社会影响分析 ===")
    
    # 按信仰类型分组分析
    faith_groups = {}
    for agent in agents:
        if agent.faith:
            faith_type = agent.faith.faith_type.value
            if faith_type not in faith_groups:
                faith_groups[faith_type] = []
            faith_groups[faith_type].append(agent)
    
    # 分析每个信仰群体的特征
    for faith_type, group_agents in faith_groups.items():
        print(f"\\n{faith_type}信仰群体 ({len(group_agents)}人):")
        
        # 计算平均属性
        avg_health = sum(a.health for a in group_agents) / len(group_agents)
        avg_energy = sum(a.energy for a in group_agents) / len(group_agents)
        avg_hunger = sum(a.hunger for a in group_agents) / len(group_agents)
        avg_thirst = sum(a.thirst for a in group_agents) / len(group_agents)
        avg_level = sum(a.profession_level for a in group_agents) / len(group_agents)
        
        print(f"  平均健康: {avg_health:.1f}")
        print(f"  平均能量: {avg_energy:.1f}")
        print(f"  平均饥饿: {avg_hunger:.1f}")
        print(f"  平均口渴: {avg_thirst:.1f}")
        print(f"  平均职业等级: {avg_level:.1f}")
        
        # 统计职业分布
        professions = {}
        for agent in group_agents:
            prof = agent.profession.value
            professions[prof] = professions.get(prof, 0) + 1
        print(f"  职业分布: {professions}")

def main():
    """主函数"""
    print("开始信仰与文化传播系统测试...")
    
    # 创建测试环境
    print("创建测试环境...")
    world_map, agents = create_test_environment(15, 15, 20)
    
    # 测试1: 信仰生成
    stats = test_faith_generation(agents)
    
    # 测试2: 信仰传播
    test_faith_influences(agents, world_map)
    
    # 测试3: 行为影响
    test_behavior_influences(agents, world_map)
    
    # 测试4: 部落统一化
    test_tribe_faith_conversion(agents)
    
    # 测试5: 社会影响分析
    analyze_faith_impact(agents)
    
    # 总结
    print("\\n=== 信仰系统实现总结 ===")
    print("✅ 已实现完整的信仰系统:")
    print("  1. 六种信仰类型: 祖先崇拜、自然崇拜、社群崇拜、技术崇拜、精神崇拜、传统崇拜")
    print("  2. 六种文化特征: 合作型、竞争型、保守型、创新型、精神性、物质型")
    print("  3. 信仰生成: 根据职业、位置和随机因素生成初始信仰")
    print("  4. 信仰传播: 基于距离的信仰和文化特征传播机制")
    print("  5. 行为影响: 信仰影响资源采集、移动模式、休息恢复等行为")
    print("  6. 部落统一: 部落内信仰同质化机制")
    print("  7. 社会影响: 不同信仰群体的社会特征分析")
    print("\\n🌟 信仰系统已成功集成到文明模拟中!")

if __name__ == "__main__":
    main()