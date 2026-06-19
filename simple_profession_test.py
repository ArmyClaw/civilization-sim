#!/usr/bin/env python3
"""
简单的Agent专业化功能测试
"""

import sys
import os
import random

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import Agent, Profession, ResourceType
from terrain import TerrainType, Tile, Map

def test_profession_differences():
    """测试职业差异"""
    print("=== Agent职业差异测试 ===\n")
    
    # 创建简单的测试地图
    world_map = Map(5, 5)
    
    # 创建不同职业的Agent
    hunter = Agent(1, 2, 2, world_map.get_tile(2, 2), Profession.HUNTER)
    farmer = Agent(2, 2, 2, world_map.get_tile(2, 2), Profession.FARMER)
    craftsman = Agent(3, 2, 2, world_map.get_tile(2, 2), Profession.CRAFTSMAN)
    gatherer = Agent(4, 2, 2, world_map.get_tile(2, 2), Profession.GATHERER)
    
    agents = [hunter, farmer, craftsman, gatherer]
    
    print("1. 职业属性对比:")
    for agent in agents:
        print(f"{agent.profession.value}:")
        print(f"  力量:{agent.strength} 敏捷:{agent.agility} 耐力:{agent.endurance}")
        print(f"  饥饿率:{agent.hunger_rate} 能量消耗:{agent.energy_consumption}")
    
    print("\n2. 测试采集效率:")
    
    # 手动添加一些资源
    test_tile = world_map.get_tile(2, 2)
    test_tile.resources['food'] = 10
    test_tile.resources['wood'] = 8
    test_tile.resources['mineral'] = 5
    
    # 让每个Agent采集相同类型的资源
    for agent in agents:
        agent.target_resource = ResourceType.FOOD
        agent.state = agent.__class__.__dict__['_states'][2]  # GATHERING
        agent.current_tile = test_tile
    
    # 模拟采集
    for step in range(3):
        print(f"\n--- 采集回合 {step+1} ---")
        for agent in agents:
            # 根据职业计算采集效率
            base_efficiency = agent.strength / 10.0
            profession_bonus = agent.special_abilities.get('resource_bonus', {})
            resource_bonus = profession_bonus.get(agent.target_resource.value, 1.0)
            efficiency = base_efficiency * resource_bonus
            
            gather_amount = int(efficiency * random.randint(2, 4))
            agent.inventory[agent.target_resource] += gather_amount
            agent.resources_collected += gather_amount
            agent.profession_exp += gather_amount * 0.3
            
            print(f"{agent.profession.value} 采集了 {gather_amount} 食物 (效率: {efficiency:.2f})")
    
    print("\n3. 最终成果:")
    for agent in agents:
        status = agent.get_status()
        print(f"\n{agent.profession.value}:")
        print(f"  采集食物: {status['inventory']['food']}")
        print(f"  总采集量: {agent.resources_collected}")
        print(f"  职业经验: {agent.profession_exp:.1f}")
        print(f"  特殊化: {agent.profession_specializations}")
        
        # 测试工匠制作工具
        if agent.profession == Profession.CRAFTSMAN:
            if agent.inventory.get(ResourceType.WOOD, 0) >= 2 and agent.inventory.get(ResourceType.MINERAL, 0) >= 1:
                agent._craft_tool()
                print(f"  工匠制作了工具! 当前背包: {status['inventory']}")
    
    print("\n4. 职业等级提升测试:")
    for agent in agents:
        # 添加足够经验让职业升级
        agent.profession_exp = agent.profession_level * 25  # 超过升级所需
        leveled_up = agent._profession_level_up()
        if leveled_up:
            print(f"{agent.profession.value} 升级到等级 {agent.profession_level}!")
            print(f"  新的力量: {agent.strength}, 新的背包容量: {agent.max_inventory}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_profession_differences()