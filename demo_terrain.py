#!/usr/bin/env python3
"""
地形生成演示脚本
展示Perlin噪声地形生成的完整流程
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import TerrainGenerator, ResourceGenerator
from src.terrain import Map, TerrainType

def main():
    print("=== 文明模拟器 - 地形生成演示 ===\n")
    
    # 创建地图
    map_width = 50
    map_height = 30
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
    print("\n地形地图 (50x30):")
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
    
    # 显示一些具体的格子信息
    print("\n=== 格子详细信息 ===")
    sample_tiles = [
        map_obj.get_tile(5, 5),
        map_obj.get_tile(15, 10),
        map_obj.get_tile(25, 15),
        map_obj.get_tile(35, 20),
        map_obj.get_tile(45, 25)
    ]
    
    for i, tile in enumerate(sample_tiles):
        if tile:
            print(f"\n格子 {i+1} ({tile.x}, {tile.y}):")
            print(f"  地形类型: {tile.terrain_type.value}")
            print(f"  海拔: {tile.elevation:.3f}")
            print(f"  湿度: {tile.moisture:.3f}")
            print(f"  温度: {tile.temperature:.3f}")
            print(f"  移动成本: {tile.get_movement_cost()}")
            print(f"  可居住性: {tile.get_habitability():.3f}")
            
            # 显示资源
            resources = tile.get_total_resources()
            if resources:
                print("  资源:")
                for resource_type, amount in resources.items():
                    if amount > 0:
                        print(f"    {resource_type}: {amount:.3f}")
    
    print(f"\n=== 总资源统计 ===")
    total_resources = map_obj.get_total_resources()
    for resource_type, amount in total_resources.items():
        if amount > 0:
            print(f"  {resource_type}: {amount:.3f}")
    
    print(f"\n总人口: {map_obj.get_total_population()}")
    print("地形生成演示完成！")

if __name__ == "__main__":
    main()