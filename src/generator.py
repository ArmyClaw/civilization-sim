"""
地形生成器模块
实现程序化地形生成算法
"""

import random
import math
from typing import List, Dict, Tuple
from .terrain import TerrainType, Map, Tile


class PerlinNoise:
    """简化的柏林噪声实现"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 2**32)
        random.seed(self.seed)
        
        # 生成梯度向量
        self.gradients = {}
        for i in range(256):
            angle = random.uniform(0, 2 * math.pi)
            self.gradients[i] = (math.cos(angle), math.sin(angle))
    
    def _fade(self, t: float) -> float:
        """淡出函数"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """线性插值"""
        return a + t * (b - a)
    
    def _grad(self, hash_val: int, x: float, y: float) -> float:
        """计算梯度"""
        h = hash_val & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else 0)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def _perm(self, index: int) -> int:
        """排列函数 - 使用Perlin噪声的排列表"""
        index = index & 255
        if index not in self.gradients:
            # 生成新的梯度向量
            angle = random.uniform(0, 2 * math.pi)
            self.gradients[index] = (math.cos(angle), math.sin(angle))
        return index
    
    def noise(self, x: float, y: float) -> float:
        """生成噪声值"""
        # 找到单位立方体的顶点坐标
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        
        # 相对坐标
        x -= math.floor(x)
        y -= math.floor(y)
        
        # 计算淡出曲线
        u = self._fade(x)
        v = self._fade(y)
        
        # 找到单位立方体的8个顶点的梯度值
        aa = self.gradients[self._perm(X + Y * 256)]
        ab = self.gradients[self._perm(X + (Y + 1) * 256)]
        ba = self.gradients[self._perm((X + 1) + Y * 256)]
        bb = self.gradients[self._perm((X + 1) + (Y + 1) * 256)]
        
        # 计算梯度点积
        da = aa[0] * x + aa[1] * y
        db = ab[0] * x + ab[1] * (y - 1)
        dc = ba[0] * (x - 1) + ba[1] * y
        dd = bb[0] * (x - 1) + bb[1] * (y - 1)
        
        # 插值
        x1 = self._lerp(da, dc, u)
        x2 = self._lerp(db, dd, u)
        
        return self._lerp(x1, x2, v)


class TerrainGenerator:
    """地形生成器"""
    
    def __init__(self, map_obj: Map):
        self.map = map_obj
        self.noise = PerlinNoise(map_obj.seed)
        self.noise_scale = 0.1  # 噪声缩放因子
        
        # 地形生成参数
        self.water_threshold = 0.3
        self.mountain_threshold = 0.8
        self.forest_threshold_moisture = 0.7
        self.forest_threshold_elevation = 0.6
    
    def generate_elevation(self) -> List[List[float]]:
        """生成海拔高度图"""
        elevation_map = []
        
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                # 使用多层噪声生成更自然的地形
                elevation = 0.0
                
                # 主要地形特征
                elevation += self.noise.noise(x * self.noise_scale, y * self.noise_scale) * 0.5
                
                # 添加细节
                elevation += self.noise.noise(x * self.noise_scale * 2, y * self.noise_scale * 2) * 0.25
                
                # 更大尺度的地形特征
                elevation += self.noise.noise(x * self.noise_scale * 0.5, y * self.noise_scale * 0.5) * 0.25
                
                # 归一化到 0.0-1.0
                elevation = (elevation + 1.0) / 2.0
                row.append(max(0.0, min(1.0, elevation)))
            
            elevation_map.append(row)
        
        return elevation_map
    
    def generate_moisture(self, elevation_map: List[List[float]]) -> List[List[float]]:
        """生成湿度分布"""
        moisture_map = []
        
        # 首先基于噪声生成基础湿度
        for y in range(self.map.height):
            row = []
            for x in range(self.map.height):
                # 基础湿度
                base_moisture = self.noise.noise(x * self.noise_scale * 1.5, y * self.noise_scale * 1.5) * 0.5 + 0.5
                
                # 水域附近的湿度增加
                distance_to_water = self._get_distance_to_water(x, y, elevation_map)
                moisture_bonus = max(0, 1.0 - distance_to_water) * 0.5
                
                # 海拔越低湿度越高
                elevation_factor = (1.0 - elevation_map[y][x]) * 0.3
                
                # 综合湿度
                moisture = base_moisture + moisture_bonus + elevation_factor
                moisture = max(0.0, min(1.0, moisture))
                row.append(moisture)
            
            moisture_map.append(row)
        
        # 应用扩散平滑
        moisture_map = self._smooth_map(moisture_map)
        
        return moisture_map
    
    def _get_distance_to_water(self, x: int, y: int, elevation_map: List[List[float]]) -> float:
        """计算到最近水域的距离"""
        min_distance = float('inf')
        
        # 检查周围区域
        search_radius = 20
        for dy in range(-search_radius, search_radius + 1):
            for dx in range(-search_radius, search_radius + 1):
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.map.width and 0 <= ny < self.map.height and
                    elevation_map[ny][nx] < self.water_threshold):
                    distance = math.sqrt(dx*dx + dy*dy)
                    min_distance = min(min_distance, distance)
        
        return min_distance / search_radius
    
    def _smooth_map(self, map_data: List[List[float]], iterations: int = 2) -> List[List[float]]:
        """平滑地图数据"""
        for _ in range(iterations):
            smoothed = []
            for y in range(len(map_data)):
                row = []
                for x in range(len(map_data[0])):
                    # 获取周围格子的平均值
                    values = []
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < len(map_data[0]) and 0 <= ny < len(map_data):
                                values.append(map_data[ny][nx])
                    
                    avg = sum(values) / len(values)
                    row.append(avg)
                smoothed.append(row)
            map_data = smoothed
        
        return map_data
    
    def classify_terrain(self, elevation_map: List[List[float]], 
                        moisture_map: List[List[float]]) -> List[List[TerrainType]]:
        """根据海拔和湿度分类地形"""
        terrain_classification = []
        
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                elevation = elevation_map[y][x]
                moisture = moisture_map[y][x]
                
                if elevation < self.water_threshold:
                    # 低海拔区域
                    if moisture > 0.6:
                        terrain_type = TerrainType.WATER
                    else:
                        terrain_type = TerrainType.LOWLAND
                
                elif elevation < self.forest_threshold_elevation:
                    # 中等海拔区域
                    if moisture > self.forest_threshold_moisture:
                        terrain_type = TerrainType.FOREST
                    else:
                        terrain_type = TerrainType.LOWLAND
                
                else:
                    # 高海拔区域
                    if moisture > self.forest_threshold_moisture * 0.7:
                        terrain_type = TerrainType.FOREST
                    elif elevation > self.mountain_threshold:
                        terrain_type = TerrainType.MOUNTAIN
                    else:
                        terrain_type = TerrainType.DESERT
                
                row.append(terrain_type)
            
            terrain_classification.append(row)
        
        return terrain_classification
    
    def generate_terrain(self):
        """生成完整地形"""
        # 1. 生成海拔高度图
        elevation_map = self.generate_elevation()
        
        # 2. 生成湿度分布
        moisture_map = self.generate_moisture(elevation_map)
        
        # 3. 分类地形
        terrain_map = self.classify_terrain(elevation_map, moisture_map)
        
        # 4. 创建地形网格
        self.map.initialize_empty()
        
        for y in range(self.map.height):
            for x in range(self.map.width):
                terrain_type = terrain_map[y][x]
                tile = self.map.grid[y][x]
                
                # 更新地形类型和参数
                tile.terrain_type = terrain_type
                tile.elevation = elevation_map[y][x]
                tile.moisture = moisture_map[y][x]
                tile.temperature = self._calculate_temperature(elevation_map[y][x], moisture_map[y][x])
    
    def _calculate_temperature(self, elevation: float, moisture: float) -> float:
        """计算温度"""
        # 基础温度（假设赤道为1.0，极地为0.0）
        base_temp = 0.7  # 假设中纬度
        
        # 海拔影响（越高越冷）
        elevation_factor = elevation * 0.4
        
        # 湿度影响（湿度高温度略低）
        moisture_factor = moisture * 0.1
        
        # 综合计算
        temperature = base_temp - elevation_factor - moisture_factor
        return max(0.0, min(1.0, temperature))


class ResourceGenerator:
    """资源生成器"""
    
    def __init__(self, map_obj: Map):
        self.map = map_obj
    
    def distribute_resources(self):
        """在地图上分布基础资源"""
        for y in range(self.map.height):
            for x in range(self.map.width):
                tile = self.map.grid[y][x]
                terrain_type = tile.terrain_type
                
                # 根据地形类型分配资源
                if terrain_type == TerrainType.FOREST:
                    tile.resources["wood"] = random.uniform(0.5, 1.0)
                    tile.resources["food"] = random.uniform(0.3, 0.7)
                    tile.resources["water"] = random.uniform(0.4, 0.8)
                
                elif terrain_type == TerrainType.LOWLAND:
                    tile.resources["food"] = random.uniform(0.6, 1.0)
                    tile.resources["water"] = random.uniform(0.5, 0.9)
                    tile.resources["clay"] = random.uniform(0.2, 0.5)
                
                elif terrain_type == TerrainType.MOUNTAIN:
                    tile.resources["mineral"] = random.uniform(0.6, 1.0)
                    tile.resources["stone"] = random.uniform(0.4, 0.8)
                    tile.resources["iron"] = random.uniform(0.3, 0.7)
                
                elif terrain_type == TerrainType.DESERT:
                    tile.resources["mineral"] = random.uniform(0.3, 0.7)
                    tile.resources["water"] = random.uniform(0.1, 0.3)
                    tile.resources["salt"] = random.uniform(0.4, 0.8)
                
                elif terrain_type == TerrainType.WATER:
                    tile.resources["fish"] = random.uniform(0.3, 0.8)
                    tile.resources["water"] = random.uniform(0.8, 1.0)
    
    def generate_resource_clusters(self, resource_type: str, cluster_count: int = 5):
        """生成资源集群"""
        # 随机选择集群中心
        centers = []
        for _ in range(cluster_count):
            x = random.randint(5, self.map.width - 5)
            y = random.randint(5, self.map.height - 5)
            centers.append((x, y))
        
        # 在中心点周围生成资源集群
        for center_x, center_y in centers:
            cluster_radius = random.randint(3, 8)
            
            for dy in range(-cluster_radius, cluster_radius + 1):
                for dx in range(-cluster_radius, cluster_radius + 1):
                    if dx*dx + dy*dy <= cluster_radius*cluster_radius:  # 圆形区域
                        tile = self.map.get_tile(center_x + dx, center_y + dy)
                        if tile:
                            distance = (dx*dx + dy*dy)**0.5 / cluster_radius
                            concentration = (1.0 - distance) * random.uniform(0.7, 1.0)
                            
                            if resource_type in tile.resources:
                                tile.resources[resource_type] = max(0.0, min(1.0, 
                                    tile.resources[resource_type] + concentration))
                            else:
                                tile.resources[resource_type] = concentration
    
    def place_special_resources(self):
        """放置特殊资源"""
        # 稀有矿物
        rare_minerals = ["gold", "silver", "gem"]
        for mineral in rare_minerals:
            count = random.randint(1, 3)
            for _ in range(count):
                x = random.randint(0, self.map.width - 1)
                y = random.randint(0, self.map.height - 1)
                tile = self.map.get_tile(x, y)
                if tile and tile.terrain_type == TerrainType.MOUNTAIN:
                    tile.resources[mineral] = random.uniform(0.8, 1.0)
    
    def generate_all_resources(self):
        """生成所有资源"""
        # 1. 分散基础资源
        self.distribute_resources()
        
        # 2. 生成资源集群
        resource_types = ["food", "wood", "mineral", "water"]
        for resource_type in resource_types:
            if random.random() < 0.7:  # 70%概率生成集群
                cluster_count = random.randint(2, 5)
                self.generate_resource_clusters(resource_type, cluster_count)
        
        # 3. 放置特殊资源
        self.place_special_resources()