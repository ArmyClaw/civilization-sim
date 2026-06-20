#!/usr/bin/env python3
"""
部落形成算法集成测试脚本
将部落系统集成到现有的文明模拟系统中
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tribe_system import TribeFormation, Tribe
from src.agent import Agent, Profession, ResourceType
from src.terrain import Tile, TerrainType
from src.generator import TerrainGenerator, ResourceGenerator
from src.terrain import Map
import random

def create_civilization_map(width: int = 20, height: int = 20, agent_count: int = 30):
    """创建完整的文明模拟环境"""
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
        
        # 根据地形和职业设置初始资源
        if tile.terrain_type == TerrainType.LOWLAND and profession == Profession.FARMER:
            agent.inventory[ResourceType.FOOD] = random.randint(12, 20)
            agent.inventory[ResourceType.WATER] = random.randint(8, 12)
        elif tile.terrain_type == TerrainType.FOREST and profession == Profession.HUNTER:
            agent.inventory[ResourceType.FOOD] = random.randint(10, 18)
            agent.inventory[ResourceType.WOOD] = random.randint(4, 8)
        elif tile.terrain_type == TerrainType.MOUNTAIN and profession == Profession.CRAFTSMAN:
            agent.inventory[ResourceType.MINERAL] = random.randint(6, 12)
            agent.inventory[ResourceType.WOOD] = random.randint(2, 6)
        else:  # GATHERER or general case
            agent.inventory[ResourceType.FOOD] = random.randint(6, 14)
            agent.inventory[ResourceType.WATER] = random.randint(6, 16)
            if tile.terrain_type == TerrainType.FOREST:
                agent.inventory[ResourceType.WOOD] = random.randint(4, 10)
            elif tile.terrain_type == TerrainType.LOWLAND:
                agent.inventory[ResourceType.FOOD] += random.randint(2, 6)
        
        # 设置健康状态
        agent.health = random.randint(70, 100)
        agent.max_inventory = 25
        
        agents.append(agent)
    
    return world_map, agents

def simulate_trading_relationships(agents: list):
    """模拟交易关系网络"""
    # 为每个Agent创建交易伙伴网络
    for agent in agents:
        # 随机选择2-5个交易伙伴
        possible_partners = [a for a in agents if a != agent and 
                           abs(a.x - agent.x) <= 8 and abs(a.y - agent.y) <= 8]
        
        if possible_partners:
            trade_partners = random.sample(possible_partners, 
                                         min(random.randint(2, 5), len(possible_partners)))
            agent.trade_partners = [a.id for a in trade_partners]
            
            # 根据交易伙伴设置一些社会属性
            for partner in trade_partners:
                if agent.profession == partner.profession:
                    agent.profession_level = min(agent.profession_level + 1, 10)

def run_tribe_analysis(agents: list, world_map: Map):
    """运行部落形成分析"""
    print("=== 文明模拟部落形成分析 ===")
    print(f"地图尺寸: {world_map.width}x{world_map.height}")
    print(f"总人口: {len(agents)}")
    
    # 创建部落形成系统
    formation = TribeFormation(agents)
    
    # 1. 基于地理距离的部落形成
    print("\n--- 地理部落形成 ---")
    geo_tribes = formation.form_tribes_geographic(max_distance=6.0)
    analyze_tribe_results(geo_tribes, "地理部落")
    
    # 2. 基于社会关系的部落形成
    print("\n--- 社会部落形成 ---")
    social_tribes = formation.form_tribes_social(similarity_threshold=0.3)
    analyze_tribe_results(social_tribes, "社会部落")
    
    # 3. 混合算法部落形成
    print("\n--- 混合部落形成 ---")
    hybrid_tribes = formation.form_tribes_hybrid(
        geo_distance=6.0, 
        social_threshold=0.3,
        geo_weight=0.5
    )
    analyze_tribe_results(hybrid_tribes, "混合部落")
    
    # 4. 优化后的部落划分
    print("\n--- 优化部落划分 ---")
    optimized_tribes = formation.optimize_tribes(hybrid_tribes, max_iterations=100)
    analyze_tribe_results(optimized_tribes, "优化部落")
    
    # 5. 最终分析
    print("\n--- 最终部落分布分析 ---")
    final_analysis = formation.analyze_tribe_distribution(optimized_tribes)
    print(f"最终部落数量: {final_analysis['total_tribes']}")
    print(f"平均部落人口: {final_analysis['average_population']:.1f}")
    print(f"人口分布: {sorted(final_analysis['tribe_sizes'])}")
    
    # 显示资源分布
    print(f"\n资源分布情况:")
    for tribe_id, resources in final_analysis['resource_distribution'].items():
        if resources:  # 只显示有资源的部落
            total_resources = sum(resources.values())
            if total_resources > 0:
                print(f"  {tribe_id}: {total_resources} 单位资源")
                print(f"    详细: {dict(resources)}")
    
    return optimized_tribes

def analyze_tribe_results(tribes: list, tribe_type: str):
    """分析部落形成结果"""
    print(f"{tribe_type}统计:")
    print(f"  部落数量: {len(tribes)}")
    print(f"  总人口: {sum(tribe.get_population() for tribe in tribes)}")
    
    if tribes:
        sizes = [tribe.get_population() for tribe in tribes]
        print(f"  部落大小: {sizes}")
        print(f"  最大部落: {max(sizes)} 人")
        print(f"  最小部落: {min(sizes)} 人")
        
        # 显示部落成员分布
        for i, tribe in enumerate(tribes[:3]):  # 只显示前3个部落
            tribe.update_territory()
            print(f"  部落{i+1}: {tribe.get_population()}人, 领土{len(tribe.territory)}格子")
            if tribe.get_population() > 0:
                member_profs = [member.profession.value for member in tribe.members]
                print(f"    职业: {member_profs}")
    
    if len(tribes) > 3:
        print(f"  ... 还有 {len(tribes) - 3} 个部落")

def main():
    """主函数"""
    # 创建文明模拟环境
    print("创建文明模拟环境...")
    world_map, agents = create_civilization_map(20, 20, 30)
    
    # 模拟社会关系
    print("建立社会关系网络...")
    simulate_trading_relationships(agents)
    
    # 运行部落分析
    tribes = run_tribe_analysis(agents, world_map)
    
    # 输出最终结果
    print("\n=== 部落形成算法实现完成 ===")
    print("已成功实现基于地理距离和社会关系的部落聚类算法")
    print("算法特性:")
    print("  1. 地理距离聚类：基于空间邻近性")
    print("  2. 社会关系聚类：基于职业相似性和交易历史")
    print("  3. 混合聚类：结合地理和社会因素")
    print("  4. 动态优化：调整部落边界提高同质性")
    print("  5. 领土管理：自动计算部落控制区域")
    print("  6. 资源统计：跟踪部落资源分布")

if __name__ == "__main__":
    main()