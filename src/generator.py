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
        self.noise_scale = 0.01  # 噪声缩放因子，产生更大范围的地形变化
        self.detail_scale = 0.08  # 细节噪声缩放
        
        # 地形生成参数 - 调整以获得更多样化的地形
        self.water_threshold = 0.1   # 水域阈值
        self.mountain_threshold = 0.8  # 山地阈值
        self.forest_threshold_moisture = 0.4  # 森林湿度要求
        self.forest_threshold_elevation = 0.5
        self.desert_threshold_moisture = 0.2  # 沙漠湿度要求
    
    def generate_elevation(self) -> List[List[float]]:
        """生成海拔高度图 - 改进版本"""
        elevation_map = []
        
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                # 使用多层噪声生成更自然的地形
                elevation = 0.0
                
                # 大尺度地形特征（决定主要地形区域）
                elevation += self.noise.noise(x * self.noise_scale, y * self.noise_scale) * 1.0
                
                # 中尺度地形变化（增加地形多样性）
                elevation += self.noise.noise(x * self.noise_scale * 1.2, y * self.noise_scale * 1.2) * 0.6
                
                # 细节噪声（增加表面细节）
                elevation += self.noise.noise(x * self.detail_scale, y * self.detail_scale) * 0.4
                
                # 归一化到 0.0-1.0
                elevation = (elevation + 1.0) / 2.0
                row.append(max(0.0, min(1.0, elevation)))
            
            elevation_map.append(row)
        
        return elevation_map
    
    def generate_moisture(self, elevation_map: List[List[float]]) -> List[List[float]]:
        """生成湿度分布 - 改进版本"""
        moisture_map = []
        
        # 首先基于噪声生成基础湿度
        for y in range(self.map.height):
            row = []
            for x in range(self.map.width):
                # 基础湿度（使用不同的噪声模式）
                base_moisture = self.noise.noise(x * self.noise_scale * 3.0, y * self.noise_scale * 3.0) * 0.6 + 0.4
                
                # 海拔越低湿度越高
                elevation_factor = (1.0 - elevation_map[y][x]) * 0.5
                
                # 添加一些随机性
                random_factor = self.noise.noise(x * 0.1, y * 0.1) * 0.1
                
                # 综合湿度
                moisture = base_moisture + elevation_factor + random_factor
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
                    # 低海拔区域 - 水域
                    terrain_type = TerrainType.WATER
                
                elif elevation < 0.35:  # 低海拔区域
                    # 低海拔根据湿度决定地形类型
                    if moisture > 0.7:  # 湿润地区 - 森林
                        terrain_type = TerrainType.FOREST
                    elif moisture > 0.4:  # 中等湿度 - 低地（适合农业）
                        terrain_type = TerrainType.LOWLAND
                    else:  # 干燥地区 - 沙漠
                        terrain_type = TerrainType.DESERT
                
                elif elevation < 0.6:  # 中等海拔区域
                    # 中海拔根据湿度决定
                    if moisture > 0.6:  # 湿润地区 - 森林
                        terrain_type = TerrainType.FOREST
                    elif moisture > 0.3:  # 中等湿度 - 低地
                        terrain_type = TerrainType.LOWLAND
                    else:  # 干燥地区 - 沙漠
                        terrain_type = TerrainType.DESERT
                
                elif elevation < self.mountain_threshold:  # 高海拔区域
                    # 高海拔但不够成为山地，可能是森林或沙漠
                    if moisture > 0.5:  # 较湿润地区 - 森林
                        terrain_type = TerrainType.FOREST
                    else:  # 干燥地区 - 沙漠
                        terrain_type = TerrainType.DESERT
                
                else:
                    # 最高海拔 - 山地
                    terrain_type = TerrainType.MOUNTAIN
                
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
        """在地图上分布基础资源 - 增强版本"""
        for y in range(self.map.height):
            for x in range(self.map.width):
                tile = self.map.grid[y][x]
                terrain_type = tile.terrain_type
                elevation = tile.elevation
                moisture = tile.moisture
                
                # 根据地形类型和环境参数分配资源
                if terrain_type == TerrainType.WATER:
                    # 水域资源：鱼类和水源
                    tile.resources["water"] = 1.0  # 水源丰富
                    tile.resources["fish"] = random.uniform(0.4, 1.0)
                    tile.resources["clay"] = random.uniform(0.1, 0.4)
                    
                elif terrain_type == TerrainType.LOWLAND:
                    # 低地：适合农业，丰富食物和水源
                    tile.resources["food"] = random.uniform(0.6, 1.0) * (1.0 + moisture * 0.3)
                    tile.resources["water"] = random.uniform(0.5, 0.9) * (1.0 + moisture * 0.2)
                    tile.resources["clay"] = random.uniform(0.2, 0.6)
                    tile.resources["crops"] = random.uniform(0.3, 0.8)
                    
                elif terrain_type == TerrainType.FOREST:
                    # 森林：木材、食物、水源
                    tile.resources["wood"] = random.uniform(0.6, 1.0) * (1.0 + (1.0 - elevation) * 0.3)
                    tile.resources["food"] = random.uniform(0.4, 0.8) * (1.0 + moisture * 0.2)
                    tile.resources["water"] = random.uniform(0.4, 0.8) * (1.0 + moisture * 0.3)
                    tile.resources["berries"] = random.uniform(0.3, 0.7)
                    tile.resources["game"] = random.uniform(0.3, 0.6)
                    
                elif terrain_type == TerrainType.MOUNTAIN:
                    # 山地：矿物资源
                    tile.resources["mineral"] = random.uniform(0.5, 1.0) * (elevation * 1.5)
                    tile.resources["stone"] = random.uniform(0.4, 0.9) * (elevation * 1.2)
                    tile.resources["iron"] = random.uniform(0.2, 0.7) if elevation > 0.7 else random.uniform(0.1, 0.4)
                    tile.resources["coal"] = random.uniform(0.2, 0.6)
                    tile.resources["gold"] = random.uniform(0.05, 0.3) if elevation > 0.8 else 0
                    tile.resources["silver"] = random.uniform(0.1, 0.4) if elevation > 0.75 else random.uniform(0.05, 0.2)
                    
                elif terrain_type == TerrainType.DESERT:
                    # 沙漠：稀缺资源，但可能有矿物和盐
                    tile.resources["mineral"] = random.uniform(0.2, 0.6) * (1.0 - moisture * 0.5)
                    tile.resources["water"] = random.uniform(0.05, 0.3) * (1.0 - moisture * 0.3)
                    tile.resources["salt"] = random.uniform(0.5, 1.0) * (1.0 - moisture * 0.2)
                    tile.resources["copper"] = random.uniform(0.1, 0.4)
                    tile.resources["gem"] = random.uniform(0.05, 0.2)  # 沙漠可能有宝石
    
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