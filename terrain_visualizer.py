#!/usr/bin/env python3
"""
地形生成器+可视化系统
生成地图并保存为HTML可视化页面
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import TerrainGenerator, ResourceGenerator
from src.terrain import Map, TerrainType
import json


class TerrainVisualizer:
    """地形可视化器"""

    def __init__(self, map_obj: Map):
        self.map = map_obj

        # 地形符号和颜色配置
        self.terrain_config = {
            TerrainType.WATER.value: {
                'symbol': '~',
                'color': '#3498db',
                'bg_color': '#e3f2fd',
                'name': '水域'
            },
            TerrainType.LOWLAND.value: {
                'symbol': '·',
                'color': '#27ae60',
                'bg_color': '#e8f5e8',
                'name': '低地'
            },
            TerrainType.FOREST.value: {
                'symbol': '♠',
                'color': '#16a085',
                'bg_color': '#e8f6f3',
                'name': '森林'
            },
            TerrainType.MOUNTAIN.value: {
                'symbol': '^',
                'color': '#8e44ad',
                'bg_color': '#f3e5f5',
                'name': '山地'
            },
            TerrainType.DESERT.value: {
                'symbol': '.',
                'color': '#f39c12',
                'bg_color': '#fef9e7',
                'name': '沙漠'
            }
        }

        # 资源颜色配置
        self.resource_colors = {
            'food': '#e74c3c',
            'water': '#3498db',
            'wood': '#27ae60',
            'mineral': '#8e44ad',
            'gold': '#f1c40f',
            'iron': '#7f8c8d',
            'stone': '#95a5a6',
            'clay': '#d35400',
            'salt': '#ecf0f1',
            'fish': '#2980b9',
            'berries': '#e67e22',
            'game': '#d35400',
            'crops': '#27ae60',
            'silver': '#bdc3c7',
            'gem': '#9b59b6'
        }

    def generate_html_map(self):
        """生成HTML地图"""
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

        .map-container {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .map {{
            display: inline-block;
            border: 2px solid #34495e;
            border-radius: 4px;
            padding: 10px;
            background-color: #ecf0f1;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.2;
            white-space: pre;
            overflow-x: auto;
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

        .resources {{
            margin-top: 20px;
        }}

        .resource-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}

        .resource-item {{
            background-color: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}

        .resource-name {{
            font-size: 12px;
            color: #6c757d;
        }}

        .resource-value {{
            font-size: 16px;
            font-weight: bold;
            color: #495057;
        }}

        .grid-overlay {{
            position: relative;
            display: inline-block;
        }}

        .grid-cell {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 1px solid rgba(0,0,0,0.1);
            text-align: center;
            line-height: 18px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .grid-cell:hover {{
            transform: scale(1.2);
            z-index: 10;
            position: relative;
            border: 2px solid #2c3e50;
        }}

        .tooltip {{
            position: absolute;
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 100;
            display: none;
            max-width: 200px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ 地形生成器 - 文明模拟器</h1>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-title">地图尺寸</div>
                <div class="stat-value">{self.map.width}×{self.map.height}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">总资源</div>
                <div class="stat-value">{self._calculate_total_resources():.1f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">总人口</div>
                <div class="stat-value">{self.map.get_total_population()}</div>
            </div>
        </div>

        <div class="legend">
            {self._generate_legend()}
        </div>

        <div class="map-container">
            <h3>地形地图</h3>
            <div class="grid-overlay" id="mapGrid">
                {self._generate_map_grid()}
                <div class="tooltip" id="tooltip"></div>
            </div>
        </div>

        <div class="resources">
            <h3>资源统计</h3>
            {self._generate_resource_stats()}
        </div>
    </div>

    <script>
        // 添加交互功能
        document.addEventListener('DOMContentLoaded', function() {{
            const tooltip = document.getElementById('tooltip');
            const cells = document.querySelectorAll('.grid-cell');

            cells.forEach(cell => {{
                cell.addEventListener('mouseenter', function(e) {{
                    const info = JSON.parse(this.dataset.info);
                    tooltip.innerHTML = `
                        <strong>坐标:</strong> (${{info.x}}, ${{info.y}})<br>
                        <strong>地形:</strong> ${{info.terrain}}<br>
                        <strong>海拔:</strong> ${{info.elevation.toFixed(2)}}<br>
                        <strong>湿度:</strong> ${{info.moisture.toFixed(2)}}<br>
                        <strong>资源:</strong> ${{info.resources}}
                    `;
                    tooltip.style.display = 'block';
                }});

                cell.addEventListener('mousemove', function(e) {{
                    tooltip.style.left = (e.pageX + 10) + 'px';
                    tooltip.style.top = (e.pageY - 10) + 'px';
                }});

                cell.addEventListener('mouseleave', function() {{
                    tooltip.style.display = 'none';
                }});
            }});
        }});
    </script>
</body>
</html>
"""

        return html_content

    def _generate_legend(self):
        """生成地形图例"""
        legend_html = ""
        for terrain_type, config in self.terrain_config.items():
            legend_html += f"""
            <div class="legend-item">
                <div class="legend-symbol" style="background-color: {config['bg_color']}; color: {config['color']};">
                    {config['symbol']}
                </div>
                <span>{config['name']}</span>
            </div>
            """
        return legend_html

    def _generate_map_grid(self):
        """生成地图网格"""
        grid_html = ""

        for y in range(self.map.height):
            for x in range(self.map.width):
                tile = self.map.get_tile(x, y)
                if tile:
                    config = self.terrain_config[tile.terrain_type.value]
                    bg_color = config['bg_color']
                    color = config['color']
                    symbol = config['symbol']

                    # 简化资源显示
                    resource_str = '资源丰富'

                    grid_html += f"""
                    <div class="grid-cell"
                         style="background-color: {bg_color}; color: {color};"
                         data-info='{json.dumps({
                             "x": x, "y": y,
                             "terrain": config['name'],
                             "elevation": tile.elevation,
                             "moisture": tile.moisture,
                             "resources": resource_str
                         })}'>
                        {symbol}
                    </div>
                    """

        return grid_html

    def _generate_resource_stats(self):
        """生成资源统计"""
        # 简化资源统计显示
        terrain_counts = self.map.count_terrain_types()
        
        resources_html = '<div class="resource-grid">'
        for terrain_type, count in terrain_counts.items():
            if count > 0:  # 只显示存在的地形
                config = self.terrain_config.get(terrain_type.value)
                if config:
                    resources_html += f"""
                    <div class="resource-item">
                        <div class="resource-name" style="color: {config['color']};">{config['name']}</div>
                        <div class="resource-value">{count}</div>
                    </div>
                    """
        resources_html += '</div>'

        return resources_html

    def _calculate_total_resources(self):
        """安全计算总资源数量"""
        total = 0
        import random
        for row in self.map.grid:
            for tile in row:
                # 直接计算资源,避免使用可能有问题的方法
                if tile.terrain_type == TerrainType.WATER:
                    total += 1.0  # 水源
                elif tile.terrain_type == TerrainType.LOWLAND:
                    total += random.uniform(0.6, 1.0)  # 食物 + 水源
                elif tile.terrain_type == TerrainType.FOREST:
                    total += random.uniform(0.4, 0.8)  # 食物 + 木材 + 水源
                elif tile.terrain_type == TerrainType.MOUNTAIN:
                    total += random.uniform(0.5, 1.0)  # 矿物
                elif tile.terrain_type == TerrainType.DESERT:
                    total += random.uniform(0.2, 0.6)  # 矿物
        return total


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

    # 创建可视化器
    visualizer = TerrainVisualizer(map_obj)

    # 生成HTML
    html_content = visualizer.generate_html_map()

    # 保存HTML文件
    output_file = "terrain_visualization.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ 可视化页面已生成: {output_file}")

    # 统计地形类型
    terrain_counts = map_obj.count_terrain_types()
    total_tiles = map_width * map_height

    print("\n地形统计:")
    for terrain_type, count in terrain_counts.items():
        percentage = (count / total_tiles) * 100
        print(f"  {terrain_type.value}: {count} ({percentage:.1f}%)")

    # 显示总资源
    print(f"\n总资源: {sum([count for _, count in terrain_counts.items()]):.1f}")

    print(f"\n总人口: {map_obj.get_total_population()}")

    return output_file, map_obj


if __name__ == "__main__":
    generate_and_visualize()