"""
测试基础人口Agent功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.terrain import Map, TerrainType
from src.agent import Agent


def test_agent_basic():
    """测试基础Agent功能"""
    print("=== 测试基础Agent功能 ===")
    
    # 创建测试地图
    world_map = Map(10, 10)
    world_map.initialize_empty()
    
    # 创建一个低地格子
    tile = world_map.get_tile(5, 5)
    tile.terrain_type = TerrainType.FOREST
    tile.add_improvement("camp")
    
    # 创建Agent
    agent = Agent(1, 5, 5, tile)
    
    print(f"创建Agent: {agent}")
    print(f"初始状态: {agent.get_status()}")
    
    # 运行几轮测试
    print("\n=== 运行10轮模拟 ===")
    for i in range(10):
        print(f"\n--- 第{i+1}轮 ---")
        logs = agent.update(world_map)
        
        if logs:
            for log in logs:
                print(f"  {log}")
        
        status = agent.get_status()
        print(f"  位置: ({status['x']}, {status['y']})")
        print(f"  状态: {status['state']}")
        print(f"  健康: {status['health']:.1f}")
        print(f"  饥饿: {status['hunger']:.1f}")
        print(f"  口渴: {status['thirst']:.1f}")
        print(f"  背包: {status['inventory']}")
    
    print(f"\n=== 最终统计 ===")
    print(f"采集资源总数: {agent.resources_collected}")
    print(f"移动步数: {agent.steps_taken}")
    print(f"休息次数: {agent.rest_count}")


def test_agent_survival():
    """测试Agent生存能力"""
    print("\n=== 测试Agent生存能力 ===")
    
    # 创建测试地图
    world_map = Map(15, 15)
    world_map.initialize_empty()
    
    # 在几个格子放置一些资源
    for _ in range(20):
        x = random.randint(0, 14)
        y = random.randint(0, 14)
        tile = world_map.get_tile(x, y)
        if tile and tile.terrain_type != TerrainType.WATER:
            # 随机添加资源
            from src.agent import ResourceType
            resource_type = random.choice(list(ResourceType))
            tile.resources[resource_type.value] = random.randint(5, 15)
    
    # 创建多个Agent进行测试
    agents = []
    for i in range(3):
        x = random.randint(0, 14)
        y = random.randint(0, 14)
        tile = world_map.get_tile(x, y)
        if tile:
            agent = Agent(i+1, x, y, tile)
            agents.append(agent)
    
    # 运行30轮生存测试
    print("\n=== 运行30轮生存测试 ===")
    alive_agents = len(agents)
    
    for round_num in range(30):
        print(f"\n--- 第{round_num+1}轮 ---")
        alive_count = 0
        
        for agent in agents:
            if agent.health > 0:
                logs = agent.update(world_map)
                if logs:
                    for log in logs:
                        if "died" in log:
                            print(f"  {log}")
                
                if agent.health > 0:
                    alive_count += 1
                    if round_num % 5 == 0:  # 每5轮打印一次状态
                        status = agent.get_status()
                        print(f"  Agent {agent.id}: 生命值{status['health']:.1f}, "
                             f"位置({status['x']},{status['y']}), "
                             f"背包:{status['inventory']}")
        
        alive_agents = alive_count
        if alive_agents == 0:
            print("所有Agent都已死亡！")
            break
        
        print(f"存活Agent数: {alive_agents}")
    
    print(f"\n=== 生存测试结束 ===")
    print(f"最终存活Agent数: {alive_agents}")


if __name__ == "__main__":
    test_agent_basic()
    import random
    test_agent_survival()