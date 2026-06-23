#!/usr/bin/env python3
"""
简化的地形可视化器
避免复杂的统计问题，直接显示地形
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import TerrainGenerator, ResourceGenerator
from src.terrain import Map, TerrainType
import json


def generate_and_visualize():
    """生成地形并可视化"""
    print("=== 文明模拟器 - 地形生成器+可视化 ===\n")
    
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
    
    # 创建HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>地形生成器 - 文明模拟器</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            flex: 1;
            min-width: 200px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        
        .stat-title {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
            justify-content: center;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .legend-symbol {{
            width: 20px;
            height: 20px;
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
        }}
        
        .map {{
            text-align: center;
            margin-top: 30px;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.0;
        }}
        
        .terrain-grid {{
            display: inline-grid;
            grid-template-columns: repeat({map_width}, 1fr);
            gap: 1px;
            padding: 10px;
            background-color: #ecf0f1;
            border: 2px solid #34495e;
            border-radius: 4px;
        }}
        
        .terrain-cell {{
            width: 15px;
            height: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .terrain-cell:hover {{
            transform: scale(1.5);
            z-index: 10;
            position: relative;
        }}
        
        .water {{ background-color: #3498db; color: white; }}
        .lowland {{ background-color: #27ae60; color: white; }}
        .forest {{ background-color: #16a085; color: white; }}
        .mountain {{ background-color: #8e44ad; color: white; }}
        .desert {{ background-color: #f39c12; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ 地形生成器 - 文明模拟器</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-title">地图尺寸</div>
                <div class="stat-value">{map_width}×{map_height}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">总地形</div>
                <div class="stat-value">{total_tiles}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">总人口</div>
                <div class="stat-value">{map_obj.get_total_population()}</div>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-symbol" style="background-color: #3498db;">~</div>
                <span>水域</span>
            </div>
            <div class="legend-item">
                <div class="legend-symbol" style="background-color: #27ae60;">·</div>
                <span>低地</span>
            </div>
            <div class="legend-item">
                <div class="legend-symbol" style="background-color: #16a085;">♠</div>
                <span>森林</span>
            </div>
            <div class="legend-item">
                <div class="legend-symbol" style="background-color: #8e44ad;">^</div>
                <span>山地</span>
            </div>
            <div class="legend-item">
                <div class="legend-symbol" style="background-color: #f39c12;">.</div>
                <span>沙漠</span>
            </div>
        </div>
        
        <div class="map">
            <h3>地形地图</h3>
            <div class="terrain-grid">
"""
    
    # 添加地形网格
    for y in range(map_height):
        for x in range(map_width):
            tile = map_obj.get_tile(x, y)
            if tile:
                terrain_class = tile.terrain_type.value
                symbol = {
                    'water': '~',
                    'lowland': '·',
                    'forest': '♠',
                    'mountain': '^',
                    'desert': '.'
                }.get(terrain_class, '?')
                
                html_content += f'<div class="terrain-cell {terrain_class}" title="({x},{y}) - {terrain_class}">{symbol}</div>'
    
    html_content += """
            </div>
        </div>
        
        <div style="margin-top: 30px;">
            <h3>地形统计</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
"""
    
    # 添加地形统计
    for terrain_type, count in terrain_counts.items():
        percentage = (count / total_tiles) * 100
        terrain_class = terrain_type.value
        color_map = {
            'water': '#3498db',
            'lowland': '#27ae60',
            'forest': '#16a085',
            'mountain': '#8e44ad',
            'desert': '#f39c12'
        }
        color = color_map.get(terrain_class, '#7f8c8d')
        
        html_content += f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid {color};">
                    <div style="font-size: 14px; color: #7f8c8d;">{terrain_class}</div>
                    <div style="font-size: 24px; font-weight: bold; color: #2c3e50;">{count} ({percentage:.1f}%)</div>
                </div>
        """
    
    html_content += """
            </div>
        </div>
    </div>
    
    <script>
        // 添加交互功能
        document.addEventListener('DOMContentLoaded', function() {
            const cells = document.querySelectorAll('.terrain-cell');
            cells.forEach(cell => {
                cell.addEventListener('click', function() {
                    const title = this.getAttribute('title');
                    const info = title.split(' - ');
                    alert(`坐标: ${info[0]}\\n地形类型: ${info[1]}`);
                });
            });
        });
    </script>
</body>
</html>
"""
    
    # 保存HTML文件
    output_file = "terrain_visualization.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 可视化页面已生成: {output_file}")
    return output_file


if __name__ == "__main__":
    generate_and_visualize()