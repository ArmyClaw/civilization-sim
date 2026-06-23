#!/usr/bin/env python3
"""
文明模拟器 - 经济平衡性测试
测试资源生成和人口增长的合理性
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import TerrainGenerator, ResourceGenerator
from src.terrain import Map, TerrainType
import json


def test_resource_balance():
    """测试资源平衡性"""
    print("=== 经济平衡性测试 ===\n")
    
    test_maps = []
    
    # 生成多个地图进行测试
    for i in range(5):
        print(f"测试地图 #{i+1}")
        
        # 创建地图
        map_obj = Map(20, 15)
        map_obj.map_id = i
        
        # 生成地形
        terrain_generator = TerrainGenerator(map_obj)
        terrain_generator.generate_terrain()
        
        # 生成资源
        resource_generator = ResourceGenerator(map_obj)
        resource_generator.generate_all_resources()
        
        # 统计资源
        terrain_counts = map_obj.count_terrain_types()
        total_population = map_obj.get_total_population()
        total_resources = 0
        
        for y in range(map_obj.height):
            for x in range(map_obj.width):
                tile = map_obj.get_tile(x, y)
                if tile and hasattr(tile, 'resources') and isinstance(tile.resources, (int, float)):
                    total_resources += tile.resources
                elif tile and hasattr(tile, 'resources') and isinstance(tile.resources, dict):
                    # 如果是字典，累加所有类型的资源
                    for resource_value in tile.resources.values():
                        if isinstance(resource_value, (int, float)):
                            total_resources += resource_value
        
        # 计算资源密度
        resource_density = total_resources / (map_obj.width * map_obj.height)
        population_density = total_population / (map_obj.width * map_obj.height)
        
        map_data = {
            'id': i,
            'terrain_distribution': {terrain_type.value: count for terrain_type, count in terrain_counts.items()},
            'total_population': total_population,
            'total_resources': total_resources,
            'resource_density': resource_density,
            'population_density': population_density
        }
        
        test_maps.append(map_data)
        print(f"  人口: {total_population}, 资源: {total_resources:.1f}, 密度: {resource_density:.2f}")
    
    # 分析结果
    print("\n=== 经济平衡性分析 ===")
    
    avg_population = sum(m['total_population'] for m in test_maps) / len(test_maps)
    avg_resources = sum(m['total_resources'] for m in test_maps) / len(test_maps)
    avg_resource_density = sum(m['resource_density'] for m in test_maps) / len(test_maps)
    avg_population_density = sum(m['population_density'] for m in test_maps) / len(test_maps)
    
    print(f"平均人口: {avg_population:.1f}")
    print(f"平均资源总量: {avg_resources:.1f}")
    print(f"平均资源密度: {avg_resource_density:.2f} (每格)")
    print(f"平均人口密度: {avg_population_density:.2f} (每格)")
    if avg_population > 0:
        print(f"人均资源: {avg_resources/avg_population:.2f}")
    else:
        print("人均资源: N/A (人口为0)")
    
    # 资源平衡性评估
    if avg_population == 0:
        print("⚠️ 当前人口为0，无法计算人均资源")
        balance_score = "NeedPopulation"
    elif avg_resources / avg_population < 2.0:
        print("⚠️ 资源不足，人口增长受限")
        balance_score = "Poor"
    elif avg_resources / avg_population > 5.0:
        print("🎯 资源充足，适合快速发展")
        balance_score = "Good"
    else:
        print("✅ 资源平衡，适合稳步发展")
        balance_score = "Balanced"
    
    # 生成测试报告
    report = {
        'test_type': 'economy_balance',
        'maps_tested': len(test_maps),
        'average_population': avg_population,
        'average_resources': avg_resources,
        'resource_per_person': avg_resources / avg_population if avg_population > 0 else 0,
        'balance_score': balance_score,
        'recommendations': []
    }
    
    # 生成建议
    if avg_population == 0:
        report['recommendations'].append("需要实现人口生成逻辑")
    elif avg_resources / avg_population < 2.0:
        report['recommendations'].append("增加资源生成倍率")
    elif avg_resources / avg_population > 5.0:
        report['recommendations'].append("降低资源生成倍率")
    else:
        report['recommendations'].append("当前平衡性良好")
    
    # 保存报告
    with open('economy_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 测试报告已保存: economy_test_report.json")
    return report


def test_population_growth():
    """测试人口增长逻辑"""
    print("\n=== 人口增长测试 ===")
    
    map_obj = Map(20, 15)
    
    # 生成地形和资源
    terrain_generator = TerrainGenerator(map_obj)
    terrain_generator.generate_terrain()
    
    resource_generator = ResourceGenerator(map_obj)
    resource_generator.generate_all_resources()
    
    # 测试不同地形的人口增长潜力
    terrain_potential = {}
    
    for terrain_type in TerrainType:
        total_potential = 0
        tiles_count = 0
        
        for y in range(map_obj.height):
            for x in range(map_obj.width):
                tile = map_obj.get_tile(x, y)
                if tile and tile.terrain_type == terrain_type:
                    potential = tile.max_population
                    if hasattr(tile, 'resources'):
                        if isinstance(tile.resources, (int, float)):
                            potential *= (1 + tile.resources * 0.1)  # 资源加成
                        elif isinstance(tile.resources, dict):
                            # 如果是字典，计算总资源加成
                            total_resource = sum(v for v in tile.resources.values() if isinstance(v, (int, float)))
                            potential *= (1 + total_resource * 0.1)
                    
                    total_potential += potential
                    tiles_count += 1
        
        if tiles_count > 0:
            terrain_potential[terrain_type.value] = {
                'tiles': tiles_count,
                'total_potential': total_potential,
                'avg_potential': total_potential / tiles_count
            }
    
    print("地形人口潜力分析:")
    for terrain, data in terrain_potential.items():
        print(f"  {terrain}: {data['tiles']} 格, 总潜力 {data['total_potential']:.0f}, 平均 {data['avg_potential']:.1f}/格")
    
    return terrain_potential


if __name__ == "__main__":
    test_resource_balance()
    test_population_growth()