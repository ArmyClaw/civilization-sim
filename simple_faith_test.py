#!/usr/bin/env python3
"""
简单信仰系统测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import Agent, Profession, ResourceType, AgentState
from src.terrain import TerrainType, Tile
from src.faith_system import FaithManager, FaithType
import random

def test_basic_faith():
    """测试基础信仰功能"""
    print("=== 基础信仰系统测试 ===")
    
    # 创建一个简单的地形
    tile = Tile(0, 0, TerrainType.FOREST)
    
    # 创建一个agent
    agent = Agent(1, 0, 0, tile, Profession.HUNTER)
    
    # 创建信仰管理器
    faith_manager = FaithManager()
    
    # 生成信仰
    faith_manager.generate_initial_faith(agent)
    
    print(f"Agent 1:")
    print(f"  职业: {agent.profession.value}")
    print(f"  位置: {agent.current_tile.terrain_type.value}")
    if agent.faith:
        print(f"  信仰类型: {agent.faith.faith_type.value}")
        print(f"  信仰强度: {agent.faith.strength:.1f}")
        print(f"  传统: {agent.faith.traditions}")
        print(f"  价值观: {[t.value for t in agent.faith.values]}")
    else:
        print("  无信仰")
    
    # 测试信仰影响行为
    print(f"\\n=== 测试信仰影响行为 ===")
    
    # 设置初始状态
    agent.hunger = 60
    agent.energy = 80
    agent.state = AgentState.IDLE
    
    print(f"初始状态:")
    print(f"  饥饿度: {agent.hunger:.1f}")
    print(f"  能量: {agent.energy:.1f}")
    print(f"  状态: {agent.state.value}")
    
    # 模拟几次更新
    for i in range(3):
        logs = agent.update(None)  # 简化测试，传None作为world_map
        if logs:
            print(f"\\n步骤{i+1}: {logs[-1]}")
        print(f"  饥饿度: {agent.hunger:.1f}")
        print(f"  能量: {agent.energy:.1f}")
        print(f"  状态: {agent.state.value}")
        
    # 测试信仰传播
    print(f"\\n=== 测试信仰传播 ===")
    
    # 创建第二个agent
    tile2 = Tile(2, 2, TerrainType.LOWLAND)
    agent2 = Agent(2, 2, 2, tile2, Profession.FARMER)
    
    # 给第二个agent也生成信仰
    faith_manager.generate_initial_faith(agent2)
    
    print(f"Agent 2:")
    print(f"  职业: {agent2.profession.value}")
    print(f"  信仰类型: {agent2.faith.faith_type.value}")
    print(f"  信仰强度: {agent2.faith.strength:.1f}")
    
    # 计算距离
    distance = ((agent.x - agent2.x)**2 + (agent.y - agent2.y)**2)**0.5
    print(f"\\n距离: {distance:.1f}")
    
    # 尝试传播信仰
    result = faith_manager.cultural_spread.spread_faith_between_agents(agent, agent2, distance)
    print(f"信仰传播结果: {result}")
    
    if agent2.faith:
        print(f"Agent 2 信仰强度: {agent2.faith.strength:.1f}")
    
    print(f"\\n✅ 基础信仰系统测试完成!")

if __name__ == "__main__":
    test_basic_faith()