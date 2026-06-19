#!/usr/bin/env python3
"""
快速测试Agent专业化功能
"""

import sys
import os
import random

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import Agent, Profession, ResourceType
from terrain import TerrainType, Tile

def create_simple_tile():
    """创建简单的Tile用于测试"""
    return Tile(0, 0, TerrainType.LOWLAND)

def test_profession_system():
    """测试职业系统"""
    print("=== Agent职业系统快速测试 ===\n")
    
    # 创建不同职业的Agent
    hunter = Agent(1, 0, 0, create_simple_tile(), Profession.HUNTER)
    farmer = Agent(2, 0, 0, create_simple_tile(), Profession.FARMER)
    craftsman = Agent(3, 0, 0, create_simple_tile(), Profession.CRAFTSMAN)
    gatherer = Agent(4, 0, 0, create_simple_tile(), Profession.GATHERER)
    
    agents = [hunter, farmer, craftsman, gatherer]
    
    print("1. 职业属性对比:")
    for agent in agents:
        print(f"{agent.profession.value}:")
        print(f"  力量:{agent.strength} 敏捷:{agent.agility} 耐力:{agent.endurance}")
        print(f"  饥饿率:{agent.hunger_rate} 能量消耗:{agent.energy_consumption}")
        print(f"  特殊能力: {list(agent.special_abilities.keys())}")
    
    print("\n2. 资源采集测试:")
    
    # 模拟资源采集
    for agent in agents:
        target_resource = ResourceType.FOOD
        
        # 根据职业计算采集效率
        base_efficiency = agent.strength / 10.0
        profession_bonus = agent.special_abilities.get('resource_bonus', {})
        resource_bonus = profession_bonus.get(target_resource.value, 1.0)
        efficiency = base_efficiency * resource_bonus
        
        gather_amount = int(efficiency * random.randint(3, 6))
        agent.inventory[target_resource] += gather_amount
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
            # 给工匠一些材料
            agent.inventory[ResourceType.WOOD] = 3
            agent.inventory[ResourceType.MINERAL] = 2
            
            if agent._craft_tool():
                print(f"  工匠成功制作了工具!")
                print(f"  当前背包: 食物:{status['inventory']['food']}, 木材:{agent.inventory[ResourceType.WOOD]}, 矿物:{agent.inventory[ResourceType.MINERAL]}")
                print(f"  制作物品数量: {len(agent.crafted_items)}")
    
    print("\n4. 职业等级提升测试:")
    for agent in agents:
        # 添加足够经验让职业升级
        agent.profession_exp = agent.profession_level * 25  # 超过升级所需
        leveled_up = agent._profession_level_up()
        if leveled_up:
            print(f"{agent.profession.value} 升级到等级 {agent.profession_level}!")
            print(f"  新的力量: {agent.strength}, 新的背包容量: {agent.max_inventory}")
        else:
            print(f"{agent.profession.value} 还不能升级 (经验: {agent.profession_exp:.1f})")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_profession_system()