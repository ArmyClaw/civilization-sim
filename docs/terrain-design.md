# 地形数据模型设计

## 概述

本设计定义了文明模拟器的核心地形系统，包括地形类型、地图网格结构和相关算法。地形系统是整个模拟器的基础，影响资源分布、人口活动、文明发展等各个方面。

## 地形类型定义

### Tile 枚举类型

```python
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random

class TerrainType(Enum):
    """地形类型枚举"""
    WATER = "water"      # 水域 - 不可居住，无资源
    LOWLAND = "lowland"  # 低地 - 适合农业，中等人口密度
    FOREST = "forest"    # 森林 - 提供木材，适合狩猎
    MOUNTAIN = "mountain" # 山地 - 矿物资源，人口稀少
    DESERT = "desert"    # 沙漠 - 极端环境，资源稀缺
```

### 地形属性矩阵

每种地形类型具有以下属性：

| 地形类型 | 可居住性 | 食物资源 | 水资源 | 木材资源 | 矿物资源 | 移动成本 | 人口容量 |
|---------|---------|---------|--------|---------|---------|---------|----------|
| WATER   | 0       | 0       | 0      | 0       | 0       | 3       | 0        |
| LOWLAND | 0.8     | 0.7     | 0.6    | 0.2     | 0.1     | 1       | 100      |
| FOREST  | 0.6     | 0.5     | 0.5    | 0.9     | 0.2     | 2       | 60       |
| MOUNTAIN| 0.3     | 0.2     | 0.3    | 0.3     | 0.9     | 4       | 30       |
| DESERT  | 0.2     | 0.1     | 0.2    | 0.1     | 0.4     | 5       | 20       |

## 地图数据结构

### 2D 网格表示

```python
class Tile:
    """单个地形格子"""
    def __init__(self, x: int, y: int, terrain_type: TerrainType):
        self.x = x                    # X坐标
        self.y = y                    # Y坐标
        self.terrain_type = terrain_type  # 地形类型
        self.elevation = 0.0          # 海拔高度 (0.0-1.0)
        self.moisture = 0.0           # 湿度 (0.0-1.0)
        self.temperature = 0.0        # 温度 (0.0-1.0)
        self.resources = {}           # 资源字典 {resource_type: amount}
        self.population = 0           # 人口数量
        self.improvements = []        # 改进设施列表
        
    def get_habitability(self) -> float:
        """计算可居住性评分"""
        base_values = {
            TerrainType.WATER: 0.0,
            TerrainType.LOWLAND: 0.8,
            TerrainType.FOREST: 0.6,
            TerrainType.MOUNTAIN: 0.3,
            TerrainType.DESERT: 0.2
        }
        return base_values[self.terrain_type]
    
    def get_resource_potential(self, resource_type: str) -> float:
        """获取特定资源的潜力值"""
        resource_matrix = {
            TerrainType.WATER: {"food": 0.0, "water": 0.0, "wood": 0.0, "mineral": 0.0},
            TerrainType.LOWLAND: {"food": 0.7, "water": 0.6, "wood": 0.2, "mineral": 0.1},
            TerrainType.FOREST: {"food": 0.5, "water": 0.5, "wood": 0.9, "mineral": 0.2},
            TerrainType.MOUNTAIN: {"food": 0.2, "water": 0.3, "wood": 0.3, "mineral": 0.9},
            TerrainType.DESERT: {"food": 0.1, "water": 0.2, "wood": 0.1, "mineral": 0.4}
        }
        return resource_matrix[self.terrain_type].get(resource_type, 0.0)

class Map:
    """地图类 - 2D网格地形系统"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: List[List[Tile]] = []
        self.seed = random.randint(0, 2**32)
        
    def generate_terrain(self):
        """生成地形 - 使用柏林噪声和物理规则"""
        # 1. 基于柏林噪声生成基础地形
        # 2. 应用水文规则形成水域
        # 3. 根据海拔和湿度分配地形类型
        pass
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """获取指定位置的格子"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def get_neighbors(self, x: int, y: int) -> List[Tile]:
        """获取相邻格子（8方向）"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbor = self.get_tile(x + dx, y + dy)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors
    
    def get_region(self, terrain_type: TerrainType) -> List[Tile]:
        """获取指定地形类型的所有格子"""
        region = []
        for row in self.grid:
            for tile in row:
                if tile.terrain_type == terrain_type:
                    region.append(tile)
        return region
```

## 程序化生成算法

### 地形生成流程

```python
class TerrainGenerator:
    """地形生成器"""
    
    def __init__(self, map: Map):
        self.map = map
        self.noise_scale = 0.1  # 噪声缩放因子
    
    def generate_elevation(self) -> List[List[float]]:
        """生成海拔高度图"""
        # 使用柏林噪声生成连续的地形高度
        elevation_map = []
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                # 简化的噪声函数
                elevation = self.perlin_noise(x * self.noise_scale, y * self.noise_scale)
                row.append(max(0.0, min(1.0, elevation)))
            elevation_map.append(row)
        return elevation_map
    
    def generate_moisture(self, elevation_map: List[List[float]]) -> List[List[float]]:
        """生成湿度分布"""
        # 基于距离水域的距离和海拔计算湿度
        moisture_map = []
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                # 简化的湿度计算
                moisture = self.calculate_moisture(x, y, elevation_map)
                row.append(max(0.0, min(1.0, moisture)))
            moisture_map.append(row)
        return moisture_map
    
    def classify_terrain(self, elevation_map: List[List[float]], 
                        moisture_map: List[List[float]]) -> List[List[TerrainType]]:
        """根据海拔和湿度分类地形"""
        terrain_classification = []
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                elevation = elevation_map[y][x]
                moisture = moisture_map[y][x]
                
                if elevation < 0.3:  # 低海拔
                    if moisture > 0.6:
                        terrain_type = TerrainType.WATER
                    else:
                        terrain_type = TerrainType.LOWLAND
                elif elevation < 0.6:  # 中等海拔
                    if moisture > 0.7:
                        terrain_type = TerrainType.FOREST
                    else:
                        terrain_type = TerrainType.LOWLAND
                else:  # 高海拔
                    if moisture > 0.5:
                        terrain_type = TerrainType.FOREST
                    else:
                        terrain_type = TerrainType.MOUNTAIN if elevation > 0.8 else TerrainType.DESERT
                
                row.append(terrain_type)
            terrain_classification.append(row)
        return terrain_classification
```

## 资源分布系统

### 资源生成算法

```python
class ResourceGenerator:
    """资源生成器"""
    
    def __init__(self, map: Map):
        self.map = map
    
    def distribute_resources(self):
        """在地图上分布资源"""
        for y in range(self.map.height):
            for x in range(self.map.width):
                tile = self.map.grid[y][x]
                
                # 根据地形类型生成资源
                if tile.terrain_type == TerrainType.FOREST:
                    tile.resources["wood"] = random.uniform(0.5, 1.0)
                    tile.resources["food"] = random.uniform(0.3, 0.7)
                
                elif tile.terrain_type == TerrainType.LOWLAND:
                    tile.resources["food"] = random.uniform(0.6, 1.0)
                    tile.resources["water"] = random.uniform(0.5, 0.9)
                
                elif tile.terrain_type == TerrainType.MOUNTAIN:
                    tile.resources["mineral"] = random.uniform(0.6, 1.0)
                    tile.resources["stone"] = random.uniform(0.4, 0.8)
                
                elif tile.terrain_type == TerrainType.DESERT:
                    tile.resources["mineral"] = random.uniform(0.3, 0.7)
                    tile.resources["water"] = random.uniform(0.1, 0.3)
    
    def generate_clusters(self, resource_type: str, cluster_size: int = 5):
        """生成资源集群"""
        # 随机选择中心点
        centers = []
        for _ in range(random.randint(2, 5)):
            x = random.randint(cluster_size, self.map.width - cluster_size)
            y = random.randint(cluster_size, self.map.height - cluster_size)
            centers.append((x, y))
        
        # 在中心点周围生成资源集群
        for center_x, center_y in centers:
            for dx in range(-cluster_size, cluster_size + 1):
                for dy in range(-cluster_size, cluster_size + 1):
                    if dx*dx + dy*dy <= cluster_size*cluster_size:  # 圆形区域
                        tile = self.map.get_tile(center_x + dx, center_y + dy)
                        if tile:
                            distance = (dx*dx + dy*dy)**0.5 / cluster_size
                            concentration = (1.0 - distance) * random.uniform(0.7, 1.0)
                            tile.resources[resource_type] = max(0.0, min(1.0, concentration))
```

## 接口定义

### 核心接口

```python
class TerrainSystem:
    """地形系统接口"""
    
    def __init__(self, width: int, height: int):
        self.map = Map(width, height)
        self.generator = TerrainGenerator(self.map)
        self.resource_generator = ResourceGenerator(self.map)
    
    def generate_world(self):
        """生成完整的世界"""
        # 1. 生成基础地形
        elevation_map = self.generator.generate_elevation()
        moisture_map = self.generator.generate_moisture(elevation_map)
        terrain_map = self.generator.classify_terrain(elevation_map, moisture_map)
        
        # 2. 创建地形网格
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                terrain_type = terrain_map[y][x]
                tile = Tile(x, y, terrain_type)
                tile.elevation = elevation_map[y][x]
                tile.moisture = moisture_map[y][x]
                row.append(tile)
            self.map.grid.append(row)
        
        # 3. 分布资源
        self.resource_generator.distribute_resources()
    
    def get_statistics(self) -> Dict:
        """获取地形统计信息"""
        stats = {
            "total_tiles": self.map.width * self.map.height,
            "terrain_distribution": {},
            "resource_summary": {}
        }
        
        # 统计地形分布
        for terrain_type in TerrainType:
            count = len(self.map.get_region(terrain_type))
            percentage = (count / stats["total_tiles"]) * 100
            stats["terrain_distribution"][terrain_type.value] = {
                "count": count,
                "percentage": round(percentage, 2)
            }
        
        return stats
    
    def serialize(self) -> Dict:
        """序列化地图数据"""
        return {
            "width": self.map.width,
            "height": self.map.height,
            "tiles": [
                [
                    {
                        "x": tile.x,
                        "y": tile.y,
                        "terrain_type": tile.terrain_type.value,
                        "elevation": tile.elevation,
                        "moisture": tile.moisture,
                        "resources": tile.resources,
                        "population": tile.population
                    }
                    for tile in row
                ]
                for row in self.map.grid
            ]
        }
    
    def load_from_serialized(self, data: Dict):
        """从序列化数据加载地图"""
        self.map.width = data["width"]
        self.map.height = data["height"]
        
        for y, row_data in enumerate(data["tiles"]):
            row = []
            for tile_data in row_data:
                tile = Tile(
                    tile_data["x"],
                    tile_data["y"],
                    TerrainType(tile_data["terrain_type"])
                )
                tile.elevation = tile_data["elevation"]
                tile.moisture = tile_data["moisture"]
                tile.resources = tile_data["resources"]
                tile.population = tile_data["population"]
                row.append(tile)
            self.map.grid.append(row)
```

## 使用示例

### 基础使用

```python
# 创建100x100的世界
terrain_system = TerrainSystem(100, 100)

# 生成世界
terrain_system.generate_world()

# 获取统计信息
stats = terrain_system.get_statistics()
print(f"水域占比: {stats['terrain_distribution']['water']['percentage']}%")

# 访问特定格子
tile = terrain_system.map.get_tile(50, 50)
if tile:
    print(f"(50,50)的地形: {tile.terrain_type.value}")
    print(f"资源: {tile.resources}")
```

### 高级使用

```python
# 获取所有森林区域
forest_tiles = terrain_system.map.get_region(TerrainType.FOREST)

# 计算总木材资源
total_wood = sum(tile.resources.get("wood", 0) for tile in forest_tiles)

# 查找资源密集区域
resource_dense_tiles = [tile for tile in forest_tiles 
                      if tile.resources.get("wood", 0) > 0.8]

# 在森林格子中添加人口
for tile in forest_tiles[:10]:  # 前10个森林格子
    tile.population = 50
    tile.improvements.append("camp")
```

## 性能考虑

### 优化策略

1. **空间分区**: 将地图划分为多个区域，减少查询范围
2. **延迟计算**: 只在需要时计算复杂的地形属性
3. **缓存机制**: 缓存频繁访问的地形数据
4. **并行处理**: 使用多线程处理大规模地图生成

### 内存优化

1. **使用numpy数组**: 替代Python列表提高性能
2. **数据压缩**: 对大面积相同地形使用压缩存储
3. **分块加载**: 按需加载地图的不同区域

## 扩展性设计

### 未来扩展点

1. **多层地形**: 支地下多层结构
2. **动态地形**: 支地形随时间变化（如火山爆发、河流改道）
3. **季节变化**: 地形属性随季节变化
4. **地形改造**: 支玩家对地形的改造（如建水坝、挖矿）

### 配置化参数

```python
class TerrainConfig:
    """地形生成配置"""
    def __init__(self):
        self.map_width = 100
        self.map_height = 100
        self.noise_scale = 0.1
        self.water_threshold = 0.3
        self.mountain_threshold = 0.8
        self.resource_density = 0.7
        self.cluster_probability = 0.3
```

这个设计提供了完整的地形系统架构，从基础数据结构到高级算法，考虑了性能、扩展性和易用性。可以根据具体需求进一步细化和实现各个组件。