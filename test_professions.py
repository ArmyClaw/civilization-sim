#!/usr/bin/env python3
"""
测试Agent专业化功能
创建不同职业的Agent并测试其行为
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import Agent, Profession, ResourceType
from terrain import TerrainType, Tile, Map
from generator import TerrainGenerator, ResourceGenerator

def test_professions():
    """测试不同职业的Agent"""
    print("=== 测试Agent专业化功能 ===\n")
    
    # 创建一个简单的世界地图
    world_map = Map(10, 10)
    
    # 生成地形
    terrain_generator = TerrainGenerator(world_map)
    terrain_generator.generate_terrain()
    
    # 生成资源
    resource_generator = ResourceGenerator(world_map)
    resource_generator.generate_all_resources()
    
    # 创建不同职业的Agent
    agents = [
        Agent(1, 5, 5, world_map.get_tile(5, 5), Profession.HUNTER),
        Agent(2, 5, 5, world_map.get_tile(5, 5), Profession.FARMER),
        Agent(3, 5, 5, world_map.get_tile(5, 5), Profession.CRAFTSMAN),
        Agent(4, 5, 5, world_map.get_tile(5, 5), Profession.GATHERER)
    ]
    
    # 添加一些资源
    world_map.get_tile(3, 3).resources['food'] = 10
    world_map.get_tile(7, 7).resources['wood'] = 8
    world_map.get_tile(2, 8).resources['mineral'] = 5
    world_map.get_tile(8, 2).resources['water'] = 12
    
    print("1. 测试Agent初始状态:")
    for agent in agents:
        status = agent.get_status()
        print(f"Agent {agent.id} ({agent.profession.value}):")
        print(f"  力量: {agent.strength}, 敏捷: {agent.agility}, 耐力: {agent.endurance}")
        print(f"  饥饿率: {agent.hunger_rate}, 能量消耗: {agent.energy_consumption}")
        print(f"  特殊能力: {agent.special_abilities}")
        print()
    
    print("2. 测试采集行为:")
    for i in range(5):  # 模拟5个时间步
        print(f"--- 时间步 {i+1} ---")
        for agent in agents:
            logs = agent.update(world_map)
            if logs:
                for log in logs:
                    print(f"Agent {agent.id} ({agent.profession.value}): {log}")
            
            # 每隔几步检查职业经验
            if i % 2 == 0:
                agent._profession_level_up()
    
    print("\n3. 最终状态:")
    for agent in agents:
        status = agent.get_status()
        print(f"Agent {agent.id} ({agent.profession.value}):")
        print(f"  等级: {agent.profession_level}, 经验: {agent.profession_exp:.1f}")
        print(f"  背包: {status['inventory']}")
        print(f"  采集资源: {agent.resources_collected}")
        print(f"  特殊化: {agent.profession_specializations}")
        if agent.crafted_items:
            print(f"  制作物品: {agent.crafted_items}")
        print()
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_professions()