"""
地形系统核心模块
定义Tile类型、地图结构和基础数据结构
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import random


class TerrainType(Enum):
    """地形类型枚举"""
    WATER = "water"        # 水域 - 不可居住，无资源
    LOWLAND = "lowland"    # 低地 - 适合农业，中等人口密度
    FOREST = "forest"      # 森林 - 提供木材，适合狩猎
    MOUNTAIN = "mountain"  # 山地 - 矿物资源，人口稀少
    DESERT = "desert"      # 沙漠 - 极端环境，资源稀缺


class Tile:
    """单个地形格子"""
    
    # 地形基础属性矩阵
    TERRAIN_PROPERTIES = {
        TerrainType.WATER.value: {
            "habitability": 0.0,
            "food_potential": 0.0,
            "water_potential": 0.0,
            "wood_potential": 0.0,
            "mineral_potential": 0.0,
            "movement_cost": 3,
            "population_capacity": 0
        },
        TerrainType.LOWLAND.value: {
            "habitability": 0.8,
            "food_potential": 0.7,
            "water_potential": 0.6,
            "wood_potential": 0.2,
            "mineral_potential": 0.1,
            "movement_cost": 1,
            "population_capacity": 100
        },
        TerrainType.FOREST.value: {
            "habitability": 0.6,
            "food_potential": 0.5,
            "water_potential": 0.5,
            "wood_potential": 0.9,
            "mineral_potential": 0.2,
            "movement_cost": 2,
            "population_capacity": 60
        },
        TerrainType.MOUNTAIN.value: {
            "habitability": 0.3,
            "food_potential": 0.2,
            "water_potential": 0.3,
            "wood_potential": 0.3,
            "mineral_potential": 0.9,
            "movement_cost": 4,
            "population_capacity": 30
        },
        TerrainType.DESERT.value: {
            "habitability": 0.2,
            "food_potential": 0.1,
            "water_potential": 0.2,
            "wood_potential": 0.1,
            "mineral_potential": 0.4,
            "movement_cost": 5,
            "population_capacity": 20
        }
    }
    
    def __init__(self, x: int, y: int, terrain_type: TerrainType):
        self.x = x                    # X坐标
        self.y = y                    # Y坐标
        self.terrain_type = terrain_type  # 地形类型
        
        # 环境参数 (0.0-1.0)
        self.elevation = 0.0          # 海拔高度
        self.moisture = 0.0           # 湿度
        self.temperature = 0.0        # 温度
        
        # 资源系统
        self.resources: Dict[str, float] = {}  # 资源字典 {resource_type: amount}
        
        # 人口系统
        self.population = 0           # 当前人口数量
        self.max_population = self.TERRAIN_PROPERTIES[terrain_type.value]["population_capacity"]
        
        # 改进设施
        self.improvements: List[str] = []  # 改进设施列表
        self.owned_by = None           # 所属文明/玩家
    
    def get_habitability(self) -> float:
        """获取地形可居住性评分"""
        return self.TERRAIN_PROPERTIES[self.terrain_type.value]["habitability"]
    
    def get_resource_potential(self, resource_type: str) -> float:
        """获取特定资源的潜力值"""
        properties = self.TERRAIN_PROPERTIES[self.terrain_type.value]
        potential_key = f"{resource_type}_potential"
        return properties.get(potential_key, 0.0)
    
    def get_movement_cost(self) -> int:
        """获取移动成本"""
        return self.TERRAIN_PROPERTIES[self.terrain_type.value]["movement_cost"]
    
    def can_improve(self) -> bool:
        """判断是否可以建设改进设施"""
        return self.population > 0 and self.terrain_type != TerrainType.WATER
    
    def add_improvement(self, improvement: str) -> bool:
        """添加改进设施"""
        if not self.can_improve():
            return False
        
        if improvement not in self.improvements:
            self.improvements.append(improvement)
            return True
        return False
    
    def add_population(self, amount: int) -> bool:
        """添加人口"""
        new_population = self.population + amount
        if new_population <= self.max_population:
            self.population = new_population
            return True
        return False
    
    def get_total_resources(self) -> Dict[str, float]:
        """获取所有资源总量（包括地形潜力）"""
        total_resources = {}
        
        # 基础资源潜力
        for resource_type in ["food", "water", "wood", "mineral"]:
            potential = self.get_resource_potential(resource_type)
            total_resources[resource_type] = potential * self.population
        
        # 添加额外资源
        for resource_type, amount in self.resources.items():
            total_resources[resource_type] = total_resources.get(resource_type, 0) + amount
        
        return total_resources
    
    def __str__(self) -> str:
        return f"Tile({self.x},{self.y},{self.terrain_type.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class Map:
    """地图类 - 2D网格地形系统"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: List[List[Tile]] = []
        self.seed = random.randint(0, 2**32)
    
    def initialize_empty(self):
        """初始化空地图"""
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # 默认为低地
                row.append(Tile(x, y, TerrainType.LOWLAND))
            self.grid.append(row)
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """获取指定位置的格子"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def get_neighbors(self, x: int, y: int, include_diagonal: bool = True) -> List[Tile]:
        """获取相邻格子"""
        neighbors = []
        
        # 定义搜索范围
        if include_diagonal:
            deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        else:
            deltas = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            neighbor = self.get_tile(nx, ny)
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
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """获取地图边界"""
        return (0, 0, self.width - 1, self.height - 1)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """检查坐标是否有效"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def count_terrain_types(self) -> Dict[TerrainType, int]:
        """统计各种地形类型的数量"""
        counts = {terrain_type: 0 for terrain_type in TerrainType}
        
        for row in self.grid:
            for tile in row:
                # 使用枚举对象作为键
                for terrain_type in TerrainType:
                    if tile.terrain_type == terrain_type:
                        counts[terrain_type] += 1
                        break
        
        return counts
    
    def get_total_population(self) -> int:
        """获取总人口"""
        return sum(tile.population for row in self.grid for tile in row)
    
    def get_total_resources(self) -> Dict[str, float]:
        """获取所有格子的资源总量"""
        total_resources = {}
        
        for row in self.grid:
            for tile in row:
                tile_resources = tile.get_total_resources()
                for resource_type, amount in tile_resources.items():
                    total_resources[resource_type] = total_resources.get(resource_type, 0) + amount
        
        return total_resources
    
    def find_best_location(self, criteria: str = "habitat") -> Optional[Tile]:
        """根据标准找到最佳位置"""
        best_tile = None
        best_score = -1
        
        for row in self.grid:
            for tile in row:
                score = 0
                
                if criteria == "habitat":
                    score = tile.get_habitability()
                elif criteria == "population":
                    score = tile.max_population
                elif criteria == "resources":
                    # 综合资源评分
                    total_resources = sum(tile.get_total_resources().values())
                    score = total_resources
                elif criteria == "food":
                    score = tile.get_resource_potential("food")
                
                if score > best_score:
                    best_score = score
                    best_tile = tile
        
        return best_tile
    
    def __str__(self) -> str:
        return f"Map({self.width}x{self.height})"
    
    def __repr__(self) -> str:
        return self.__str__()