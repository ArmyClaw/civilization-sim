#!/usr/bin/env python3
"""
Agent专业化功能演示
展示不同职业Agent的特化和行为差异
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import Agent, Profession, ResourceType
from terrain import TerrainType, Tile, Map
from generator import TerrainGenerator, ResourceGenerator

def create_test_agents():
    """创建测试用的Agent"""
    world_map = Map(15, 15)
    
    # 生成地形和资源
    terrain_generator = TerrainGenerator(world_map)
    terrain_generator.generate_terrain()
    
    resource_generator = ResourceGenerator(world_map)
    resource_generator.generate_all_resources()
    
    # 手动添加一些测试资源
    world_map.get_tile(5, 5).resources['food'] = 20
    world_map.get_tile(10, 5).resources['wood'] = 15
    world_map.get_tile(5, 10).resources['mineral'] = 10
    world_map.get_tile(10, 10).resources['water'] = 25
    
    # 创建不同职业的Agent
    agents = {
        'hunter': Agent(1, 5, 5, world_map.get_tile(5, 5), Profession.HUNTER),
        'farmer': Agent(2, 5, 5, world_map.get_tile(5, 5), Profession.FARMER),
        'craftsman': Agent(3, 5, 5, world_map.get_tile(5, 5), Profession.CRAFTSMAN),
        'gatherer': Agent(4, 5, 5, world_map.get_tile(5, 5), Profession.GATHERER)
    }
    
    return agents, world_map

def run_profession_demo():
    """运行职业演示"""
    print("=== Agent专业化功能演示 ===\n")
    
    agents, world_map = create_test_agents()
    
    print("1. 各职业初始属性对比:")
    for name, agent in agents.items():
        print(f"{name.upper()} ({agent.profession.value}):")
        print(f"  力量:{agent.strength} 敏捷:{agent.agility} 耐力:{agent.endurance}")
        print(f"  饥饿率:{agent.hunger_rate} 能量消耗:{agent.energy_consumption}")
        print(f"  特殊能力: {agent.special_abilities}")
        print()
    
    print("2. 模拟采集行为:")
    
    # 让每个Agent前往不同的资源点采集
    # 猎人 -> 食物
    agents['hunter'].target_tile = world_map.get_tile(5, 5)
    agents['hunter'].state = agents['hunter'].__class__.__dict__['_states'][1]  # MOVING
    
    # 农民 -> 食物（农民擅长种植，对食物需求更稳定）
    agents['farmer'].target_tile = world_map.get_tile(5, 5)
    agents['farmer'].state = agents['farmer'].__class__.__dict__['_states'][1]  # MOVING
    
    # 工匠 -> 木材（制作工具需要木材）
    agents['craftsman'].target_tile = world_map.get_tile(10, 5)
    agents['craftsman'].state = agents['craftsman'].__class__.__dict__['_states'][1]  # MOVING
    
    # 采集者 -> 矿物（采集者擅长收集各种资源）
    agents['gatherer'].target_tile = world_map.get_tile(5, 10)
    agents['gatherer'].state = agents['gatherer'].__class__.__dict__['_states'][1]  # MOVING
    
    # 模拟采集过程
    for step in range(10):
        print(f"\n--- 采集步骤 {step+1} ---")
        all_logs = []
        
        for name, agent in agents.items():
            # 移动到目标位置
            if agent.state.value == "moving" and agent.target_tile:
                agent.x = agent.target_tile.x
                agent.y = agent.target_tile.y
                agent.current_tile = agent.target_tile
                agent.state = agent.__class__.__dict__['_states'][2]  # GATHERING
                print(f"{name} 到达目标位置 ({agent.x}, {agent.y})")
            
            # 采集资源
            if agent.state.value == "gathering":
                # 根据职业计算采集效率
                if agent.target_resource is None:
                    agent.target_resource = ResourceType.FOOD  # 简化处理，都采集食物
                
                base_efficiency = agent.strength / 10.0
                profession_bonus = agent.special_abilities.get('resource_bonus', {})
                resource_bonus = profession_bonus.get(agent.target_resource.value, 1.0)
                efficiency = base_efficiency * resource_bonus
                
                gather_amount = int(efficiency * random.randint(2, 5))
                agent.inventory[agent.target_resource] += gather_amount
                agent.resources_collected += gather_amount
                
                # 职业特殊行为
                if name == 'hunter':
                    agent.profession_exp += gather_amount * 0.5
                    agent.profession_specializations['hunt_success'] += 1
                    print(f"猎人 {agent.id} 采集了 {gather_amount} 食物 (狩猎加成!)")
                elif name == 'farmer':
                    agent.profession_exp += gather_amount * 0.3
                    # 农民有稳定产出
                    if random.random() < 0.3:
                        bonus = 1
                        agent.inventory[agent.target_resource] += bonus
                        print(f"农民 {agent.id} 获得额外产出 {bonus}!")
                elif name == 'craftsman':
                    agent.profession_exp += gather_amount * 0.4
                    if agent.target_resource == ResourceType.WOOD and random.random() < 0.2:
                        agent._craft_tool()
                        print(f"工匠 {agent.id} 制作了一个工具!")
                elif name == 'gatherer':
                    agent.profession_exp += gather_amount * 0.3
                    if random.random() < 0.1:
                        bonus = 1
                        agent.inventory[agent.target_resource] += bonus
                        agent.profession_specializations['gather_rare'] += 1
                        print(f"采集者 {agent.id} 发现了稀有资源!")
                
                # 检查是否需要继续采集
                if sum(agent.inventory.values()) >= agent.max_inventory:
                    agent.state = agent.__class__.__dict__['_states'][0]  # IDLE
                    agent.target_resource = None
                    print(f"{name} 背包已满，停止采集")
    
    print("\n3. 最终成果展示:")
    for name, agent in agents.items():
        status = agent.get_status()
        print(f"\n{name.upper()} 最终状态:")
        print(f"  职业等级: {agent.profession_level}")
        print(f"  职业经验: {agent.profession_exp:.1f}")
        print(f"  背包内容: {status['inventory']}")
        print(f"  总采集资源: {agent.resources_collected}")
        print(f"  特殊化统计: {agent.profession_specializations}")
        
        if agent.crafted_items:
            print(f"  制作物品: {agent.crafted_items}")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    import random
    run_profession_demo()