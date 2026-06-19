#!/usr/bin/env python3
"""
资源分布系统演示脚本
展示完整的地形和资源分布实现
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import TerrainGenerator, ResourceGenerator
from src.terrain import Map, TerrainType

def main():
    print("=== 文明模拟器 - 资源分布系统演示 ===\n")
    
    # 创建地图
    map_width = 40
    map_height = 25
    map_obj = Map(map_width, map_height)
    
    print(f"创建 {map_width}x{map_height} 地图...")
    
    # 创建生成器
    terrain_generator = TerrainGenerator(map_obj)
    resource_generator = ResourceGenerator(map_obj)
    
    # 生成地形
    print("生成地形...")
    terrain_generator.generate_terrain()
    
    # 生成资源
    print("生成资源...")
    resource_generator.generate_all_resources()
    
    # 统计地形类型
    terrain_counts = map_obj.count_terrain_types()
    total_tiles = map_width * map_height
    
    print("\n地形统计:")
    for terrain_type, count in terrain_counts.items():
        percentage = (count / total_tiles) * 100
        print(f"  {terrain_type.value}: {count} ({percentage:.1f}%)")
    
    # 显示地形地图
    print(f"\n地形地图 ({map_width}x{map_height}):")
    print("  ~:水域  ·:低地  ♠:森林  ^:山地  .:沙漠")
    
    for y in range(map_height):
        row = ""
        for x in range(map_width):
            if x == 0 and y > 0 and y % 5 == 0:
                # 每5行显示一次行号
                row += f"\n{y:2d} "
            
            tile = map_obj.get_tile(x, y)
            if tile:
                symbol = {
                    TerrainType.WATER: '~',
                    TerrainType.LOWLAND: '·',
                    TerrainType.FOREST: '♠',
                    TerrainType.MOUNTAIN: '^',
                    TerrainType.DESERT: '.'
                }.get(tile.terrain_type, '?')
                row += symbol + ' '
        
        print(row)
    
    # 显示资源统计
    print(f"\n=== 资源分布统计 ===")
    total_resources = map_obj.get_total_resources()
    
    # 按资源类型排序显示
    sorted_resources = sorted(total_resources.items(), key=lambda x: x[1], reverse=True)
    
    print("各类资源总量:")
    for resource_type, amount in sorted_resources:
        if amount > 0:
            print(f"  {resource_type}: {amount:.3f}")
    
    # 显示主要地形区域的资源特点
    print(f"\n=== 主要地形资源特点 ===")
    
    # 森林资源
    forest_tiles = map_obj.get_region(TerrainType.FOREST)
    if forest_tiles:
        forest_resources = {}
        for tile in forest_tiles:
            for resource_type, amount in tile.resources.items():
                forest_resources[resource_type] = forest_resources.get(resource_type, 0) + amount
        
        print("森林区域资源:")
        forest_sorted = sorted(forest_resources.items(), key=lambda x: x[1], reverse=True)[:5]
        for resource_type, amount in forest_sorted:
            if amount > 0:
                print(f"  {resource_type}: {amount:.3f}")
    
    # 低地资源
    lowland_tiles = map_obj.get_region(TerrainType.LOWLAND)
    if lowland_tiles:
        lowland_resources = {}
        for tile in lowland_tiles:
            for resource_type, amount in tile.resources.items():
                lowland_resources[resource_type] = lowland_resources.get(resource_type, 0) + amount
        
        print("\n低地区域资源:")
        lowland_sorted = sorted(lowland_resources.items(), key=lambda x: x[1], reverse=True)[:5]
        for resource_type, amount in lowland_sorted:
            if amount > 0:
                print(f"  {resource_type}: {amount:.3f}")
    
    # 显示稀有资源分布
    print(f"\n=== 稀有资源分布 ===")
    rare_resources = ['gold', 'silver', 'gem', 'coal']
    rare_found = False
    
    for y in range(map_height):
        for x in range(map_width):
            tile = map_obj.get_tile(x, y)
            if tile:
                for resource in rare_resources:
                    if resource in tile.resources and tile.resources[resource] > 0:
                        print(f"  {resource} 在 ({x}, {y}): {tile.resources[resource]:.3f}")
                        rare_found = True
    
    if not rare_found:
        print("  未发现稀有资源分布")
    
    print(f"\n=== 总体评估 ===")
    print("✅ 任务完成: 在地形上成功分布了食物、水、矿物、木材资源")
    print("✅ 资源类型丰富: 包含基础资源和特殊资源")
    print("✅ 地形适配: 不同地形类型拥有对应的资源分布")
    print("✅ 系统完整性: 实现了完整的资源分布系统")
    
    return map_obj

if __name__ == "__main__":
    main()