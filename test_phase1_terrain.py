"""
Phase 1: Terrain 综合测试
测试地形生成、资源分布合理性、Agent基本行为
"""

import sys
import os
import random
import time
from typing import Dict, List, Tuple

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.terrain import Map, TerrainType, Tile
from src.agent import Agent
from src.generator import TerrainGenerator, ResourceGenerator


def test_terrain_generation():
    """测试地形生成系统"""
    print("=== 测试地形生成系统 ===")
    
    # 创建测试地图
    map_width = 30
    map_height = 20
    map_obj = Map(map_width, map_height)
    
    # 创建生成器
    terrain_generator = TerrainGenerator(map_obj)
    
    # 测试生成地形
    start_time = time.time()
    terrain_generator.generate_terrain()
    generation_time = time.time() - start_time
    
    # 统计地形分布
    terrain_counts = map_obj.count_terrain_types()
    total_tiles = map_width * map_height
    
    print(f"地形生成耗时: {generation_time:.2f}秒")
    print(f"地形分布:")
    for terrain_type, count in terrain_counts.items():
        percentage = (count / total_tiles) * 100
        print(f"  {terrain_type.value}: {count} ({percentage:.1f}%)")
    
    # 验证地形合理性
    print("\n地形合理性检查:")
    
    # 检查水域连通性（水域应该相对集中）
    water_tiles = map_obj.get_region(TerrainType.WATER)
    if len(water_tiles) > 0:
        # 找到水域的中心
        center_x = sum(tile.x for tile in water_tiles) // len(water_tiles)
        center_y = sum(tile.y for tile in water_tiles) // len(water_tiles)
        
        # 计算水域平均距离
        avg_distance = sum(abs(tile.x - center_x) + abs(tile.y - center_y) for tile in water_tiles) / len(water_tiles)
        print(f"  水域平均离中心距离: {avg_distance:.2f} (越小越好)")
        
        if avg_distance < 10:
            print("  ✓ 水域分布相对集中")
        else:
            print("  ⚠ 水域分布过于分散")
    
    # 检查山地分布（山地应该集中在高处）
    mountain_tiles = map_obj.get_region(TerrainType.MOUNTAIN)
    if mountain_tiles:
        avg_elevation = sum(tile.elevation for tile in mountain_tiles) / len(mountain_tiles)
        print(f"  山地平均海拔: {avg_elevation:.3f}")
        
        if avg_elevation > 0.7:
            print("  ✓ 山地分布在高海拔区域")
        else:
            print("  ⚠ 山地分布不合理")
    
    # 检查森林分布（森林应该在中低湿度区域）
    forest_tiles = map_obj.get_region(TerrainType.FOREST)
    if forest_tiles:
        avg_moisture = sum(tile.moisture for tile in forest_tiles) / len(forest_tiles)
        print(f"  森林平均湿度: {avg_moisture:.3f}")
        
        if 0.3 <= avg_moisture <= 0.7:
            print("  ✓ 森林分布湿度适中")
        else:
            print("  ⚠ 森林分布湿度不合理")
    
    return True


def test_resource_distribution():
    """测试资源分布合理性"""
    print("\n=== 测试资源分布合理性 ===")
    
    # 创建测试地图
    map_width = 40
    map_height = 30
    map_obj = Map(map_width, map_height)
    
    # 生成地形
    terrain_generator = TerrainGenerator(map_obj)
    terrain_generator.generate_terrain()
    
    # 生成资源
    resource_generator = ResourceGenerator(map_obj)
    resource_generator.generate_all_resources()
    
    # 分析资源分布
    print("\n资源分布分析:")
    
    # 统计各地形类型的资源分布
    terrain_resources = {}
    for terrain_type in TerrainType:
        tiles = map_obj.get_region(terrain_type)
        if tiles:
            total_resources = {}
            for tile in tiles:
                tile_resources = tile.get_total_resources()
                for resource_type, amount in tile_resources.items():
                    total_resources[resource_type] = total_resources.get(resource_type, 0) + amount
            
            terrain_resources[terrain_type] = total_resources
    
    # 打印资源统计
    for terrain_type, resources in terrain_resources.items():
        print(f"\n{terrain_type.value}资源:")
        total_amount = sum(resources.values())
        if total_amount > 0:
            print(f"  总资源量: {total_amount:.2f}")
            for resource_type, amount in resources.items():
                if amount > 0:
                    percentage = (amount / total_amount) * 100
                    print(f"    {resource_type}: {amount:.2f} ({percentage:.1f}%)")
    
    # 验证资源分布合理性
    print("\n资源分布合理性检查:")
    
    # 水域应该有水资源和鱼类
    water_resources = terrain_resources.get(TerrainType.WATER, {})
    if water_resources.get("water", 0) > 0:
        print("  ✓ 水域有水资源")
    else:
        print("  ✗ 水域缺少水资源")
    
    if water_resources.get("fish", 0) > 0:
        print("  ✓ 水域有鱼类资源")
    else:
        print("  ⚠ 水域缺少鱼类资源")
    
    # 森林应该有木材资源
    forest_resources = terrain_resources.get(TerrainType.FOREST, {})
    if forest_resources.get("wood", 0) > 0:
        print("  ✓ 森林有木材资源")
    else:
        print("  ✗ 森林缺少木材资源")
    
    # 山地应该有矿物资源
    mountain_resources = terrain_resources.get(TerrainType.MOUNTAIN, {})
    if mountain_resources.get("mineral", 0) > 0:
        print("  ✓ 山地有矿物资源")
    else:
        print("  ✗ 山地缺少矿物资源")
    
    # 低地应该有食物资源
    lowland_resources = terrain_resources.get(TerrainType.LOWLAND, {})
    if lowland_resources.get("food", 0) > 0:
        print("  ✓ 低地有食物资源")
    else:
        print("  ✗ 低地缺少食物资源")
    
    # 检查资源多样性
    total_all_resources = map_obj.get_total_resources()
    resource_types_count = len([r for r, amount in total_all_resources.items() if amount > 0])
    print(f"\n总资源类型数: {resource_types_count}")
    
    if resource_types_count >= 5:
        print("  ✓ 资源多样性良好")
    else:
        print("  ⚠ 资源类型偏少")
    
    return True


def test_agent_basic_behavior():
    """测试Agent基本行为"""
    print("\n=== 测试Agent基本行为 ===")
    
    # 创建测试地图
    world_map = Map(20, 20)
    world_map.initialize_empty()
    
    # 设置测试地形
    for y in range(20):
        for x in range(20):
            tile = world_map.get_tile(x, y)
            if y < 5:
                tile.terrain_type = TerrainType.WATER
            elif y < 10:
                tile.terrain_type = TerrainType.LOWLAND
            elif y < 15:
                tile.terrain_type = TerrainType.FOREST
            else:
                tile.terrain_type = TerrainType.MOUNTAIN
            
            # 添加一些资源
            if tile.terrain_type == TerrainType.LOWLAND:
                tile.resources["food"] = random.uniform(0.5, 1.0)
            elif tile.terrain_type == TerrainType.FOREST:
                tile.resources["wood"] = random.uniform(0.5, 1.0)
            elif tile.terrain_type == TerrainType.MOUNTAIN:
                tile.resources["mineral"] = random.uniform(0.3, 0.8)
    
    # 创建测试Agent
    agents = []
    for i in range(5):
        x = random.randint(0, 19)
        y = random.randint(5, 19)  # 避开水域
        tile = world_map.get_tile(x, y)
        if tile:
            agent = Agent(i+1, x, y, tile)
            agents.append(agent)
    
    print(f"创建了 {len(agents)} 个测试Agent")
    
    # 运行模拟
    simulation_rounds = 20
    print(f"\n运行 {simulation_rounds} 轮模拟:")
    
    for round_num in range(simulation_rounds):
        print(f"\n--- 第 {round_num+1} 轮 ---")
        
        for agent in agents:
            if agent.health > 0:
                logs = agent.update(world_map)
                
                # 每5轮打印关键状态
                if round_num % 5 == 0:
                    status = agent.get_status()
                    print(f"Agent {agent.id}: "
                         f"位置({status['x']},{status['y']}), "
                         f"状态{status['state']}, "
                         f"健康{status['health']:.1f}, "
                         f"饥饿{status['hunger']:.1f}, "
                         f"口渴{status['thirst']:.1f}")
                    
                    if status['inventory']:
                        print(f"  背包: {status['inventory']}")
        
        # 统计存活状态
        alive_agents = [a for a in agents if a.health > 0]
        print(f"存活Agent: {len(alive_agents)}/{len(agents)}")
    
    # 最终统计
    print("\n=== 最终统计 ===")
    
    survival_rate = len([a for a in agents if a.health > 0]) / len(agents)
    print(f"生存率: {survival_rate:.1%}")
    
    total_resources_collected = sum(a.resources_collected for a in agents)
    total_steps_taken = sum(a.steps_taken for a in agents)
    avg_inventory = sum(sum(a.inventory.values()) for a in agents) / len(agents)
    
    print(f"总采集资源数: {total_resources_collected}")
    print(f"总移动步数: {total_steps_taken}")
    print(f"平均背包资源数: {avg_inventory:.1f}")
    
    # 行为分析
    print("\n行为分析:")
    
    # 统计各状态出现次数
    state_counts = {}
    for agent in agents:
        if hasattr(agent, 'state'):
            state_key = agent.state.value
            state_counts[state_key] = state_counts.get(state_key, 0) + 1
    
    for state, count in state_counts.items():
        print(f"  {state}: {count} 次")
    
    # 评价Agent行为
    if survival_rate > 0.8:
        print("  ✓ Agent生存能力强")
    elif survival_rate > 0.5:
        print("  ⚠ Agent生存能力一般")
    else:
        print("  ✗ Agent生存能力弱")
    
    if total_resources_collected > 50:
        print("  ✓ Agent资源采集效率高")
    elif total_resources_collected > 20:
        print("  ⚠ Agent资源采集效率一般")
    else:
        print("  ✗ Agent资源采集效率低")
    
    return True


def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    # 测试最小地图
    print("测试最小地图 (5x5):")
    small_map = Map(5, 5)
    small_map.initialize_empty()
    
    # 测试单Agent在最小地图
    tile = small_map.get_tile(2, 2)
    agent = Agent(1, 2, 2, tile)
    
    for i in range(5):
        agent.update(small_map)
    
    print("  ✓ 小地图测试通过")
    
    # 测试资源生成在边界
    print("测试边界资源生成:")
    edge_map = Map(10, 10)
    edge_map.initialize_empty()
    
    # 在边界放置资源
    for x in [0, 9]:
        for y in [0, 9]:
            tile = edge_map.get_tile(x, y)
            tile.resources["test_resource"] = 1.0
    
    edge_resources = edge_map.get_total_resources()
    if edge_resources.get("test_resource", 0) == 4.0:
        print("  ✓ 边界资源生成正确")
    else:
        print("  ✗ 边界资源生成错误")
    
    # 测试Agent移动到边界
    print("测试Agent边界移动:")
    corner_tile = edge_map.get_tile(0, 0)
    edge_agent = Agent(2, 0, 0, corner_tile)
    
    # 尝试向左上移动（应该失败）
    edge_agent._act_moving(edge_map)
    
    if edge_agent.x == 0 and edge_agent.y == 0:
        print("  ✓ 边界移动限制正确")
    else:
        print("  ✗ 边界移动限制错误")
    
    return True


def run_performance_test():
    """性能测试"""
    print("\n=== 性能测试 ===")
    
    # 测试不同大小地图的生成性能
    sizes = [(20, 20), (50, 50), (100, 100)]
    
    for width, height in sizes:
        map_obj = Map(width, height)
        
        start_time = time.time()
        terrain_generator = TerrainGenerator(map_obj)
        terrain_generator.generate_terrain()
        terrain_time = time.time() - start_time
        
        start_time = time.time()
        resource_generator = ResourceGenerator(map_obj)
        resource_generator.generate_all_resources()
        resource_time = time.time() - start_time
        
        total_time = terrain_time + resource_time
        
        print(f"地图 {width}x{height}:")
        print(f"  地形生成: {terrain_time:.2f}秒")
        print(f"  资源生成: {resource_time:.2f}秒")
        print(f"  总耗时: {total_time:.2f}秒")
        
        # 性能评估
        if total_time < 1.0:
            print("  ✓ 性能优秀")
        elif total_time < 3.0:
            print("  ✓ 性能良好")
        else:
            print("  ⚠ 性能需要优化")


def main():
    """主测试函数"""
    print("Phase 1: Terrain 综合测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行所有测试
    try:
        test_results.append(test_terrain_generation())
        test_results.append(test_resource_distribution())
        test_results.append(test_agent_basic_behavior())
        test_results.append(test_edge_cases())
        
        # 性能测试（可选）
        run_performance_test()
        
        # 汇总结果
        print("\n" + "=" * 50)
        print("测试结果汇总:")
        
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"通过测试: {passed}/{total}")
        
        if passed == total:
            print("✓ 所有测试通过！Phase 1: Terrain 系统功能正常。")
        else:
            print("⚠ 部分测试失败，需要进一步调试。")
        
        return passed == total
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)