#!/usr/bin/env python3
"""
部落形成算法演示脚本
展示基于地理距离和社会关系的部落聚类过程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tribe_system import TribeFormation, Tribe
from src.agent import Agent, Profession, ResourceType
from src.terrain import Tile, TerrainType
import random

def create_demo_agents(count: int = 20) -> list:
    """创建演示用的Agent"""
    agents = []
    professions = list(Profession)
    
    # 在地图上分散创建Agent
    positions = []
    for i in range(count):
        # 确保Agent分散在不同位置
        while True:
            x = random.randint(0, 15)
            y = random.randint(0, 15)
            if (x, y) not in positions:
                positions.append((x, y))
                break
        
        tile = Tile(x, y, random.choice(list(TerrainType)))
        profession = random.choice(professions)
        
        agent = Agent(i, x, y, tile, profession)
        
        # 设置初始资源（根据职业）
        if profession == Profession.HUNTER:
            agent.inventory[ResourceType.FOOD] = random.randint(8, 15)
            agent.inventory[ResourceType.WATER] = random.randint(3, 8)
            agent.profession_level = random.randint(2, 5)
        elif profession == Profession.FARMER:
            agent.inventory[ResourceType.FOOD] = random.randint(10, 18)
            agent.inventory[ResourceType.WATER] = random.randint(5, 10)
            agent.profession_level = random.randint(2, 6)
        elif profession == Profession.CRAFTSMAN:
            agent.inventory[ResourceType.WOOD] = random.randint(6, 12)
            agent.inventory[ResourceType.MINERAL] = random.randint(4, 8)
            agent.profession_level = random.randint(1, 4)
        else:  # GATHERER
            agent.inventory[ResourceType.FOOD] = random.randint(6, 14)
            agent.inventory[ResourceType.WATER] = random.randint(6, 16)
            agent.inventory[ResourceType.WOOD] = random.randint(4, 10)
            agent.profession_level = random.randint(2, 5)
        
        agents.append(agent)
    
    return agents

def simulate_social_relationships(agents: list):
    """模拟社会关系网络"""
    # 为每个Agent设置一些交易伙伴
    for agent in agents:
        # 随机选择1-3个交易伙伴
        trade_partners = random.sample([a for a in agents if a != agent], 
                                      min(random.randint(1, 3), len(agents) - 1))
        agent.trade_partners = [a.id for a in trade_partners]

def display_tribe_results(tribes: list, formation_type: str):
    """显示部落形成结果"""
    print(f"\n=== {formation_type}部落形成结果 ===")
    print(f"总部落数: {len(tribes)}")
    print(f"总人口: {sum(tribe.get_population() for tribe in tribes)}")
    
    total_resources = {}
    
    for i, tribe in enumerate(tribes, 1):
        # 更新领土信息
        tribe.update_territory()
        
        print(f"\n部落 {i}: {tribe.name}")
        print(f"  人口: {tribe.get_population()}")
        print(f"  领土: {len(tribe.territory)} 个格子")
        print(f"  创始人: ID{tribe.founder.id} ({tribe.founder.profession.value})")
        print(f"  成员ID: {[member.id for member in tribe.members]}")
        
        # 统计资源
        resources = tribe.get_resource_summary()
        print(f"  资源: {dict(resources)}")
        
        # 更新总资源统计
        for resource, amount in resources.items():
            total_resources[resource] = total_resources.get(resource, 0) + amount

def main():
    """主函数"""
    print("=== 部落形成算法演示 ===")
    
    # 创建演示Agent
    agents = create_demo_agents(20)
    simulate_social_relationships(agents)
    
    print(f"\n创建了 {len(agents)} 个Agent，分布在16x16的地图上")
    
    # 创建部落形成系统
    formation = TribeFormation(agents)
    
    # 1. 基于地理距离的部落形成
    print("\n--- 基于地理距离的部落形成 ---")
    geo_tribes = formation.form_tribes_geographic(max_distance=4.0)
    display_tribe_results(geo_tribes, "地理")
    
    # 2. 基于社会关系的部落形成
    print("\n--- 基于社会关系的部落形成 ---")
    social_tribes = formation.form_tribes_social(similarity_threshold=0.4)
    display_tribe_results(social_tribes, "社会")
    
    # 3. 混合算法的部落形成
    print("\n--- 混合算法的部落形成 ---")
    hybrid_tribes = formation.form_tribes_hybrid(
        geo_distance=4.0, 
        social_threshold=0.4,
        geo_weight=0.6
    )
    display_tribe_results(hybrid_tribes, "混合")
    
    # 4. 优化后的部落划分
    print("\n--- 优化后的部落划分 ---")
    optimized_tribes = formation.optimize_tribes(hybrid_tribes, max_iterations=50)
    display_tribe_results(optimized_tribes, "优化")
    
    # 5. 分析部落分布
    print("\n--- 部落分布分析 ---")
    analysis = formation.analyze_tribe_distribution(optimized_tribes)
    print(f"部落平均人口: {analysis['average_population']:.1f}")
    print(f"部落大小分布: {analysis['tribe_sizes']}")
    
    # 显示资源分布
    print(f"\n总资源分布:")
    for tribe_id, resources in analysis['resource_distribution'].items():
        if resources:
            print(f"  {tribe_id}: {resources}")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main()