# Perlin Noise地形生成算法规格说明书

## 概述

本文档定义了文明模拟器中Perlin噪声地形生成算法的具体参数和配置方案。该算法用于生成自然、连续的地形高度图，为后续的地形类型分类和资源分布提供基础。

## 算法参数定义

### 核心噪声参数

| 参数名 | 类型 | 默认值 | 范围 | 描述 |
|--------|------|--------|------|------|
| `seed` | int | 随机 | 0-2³² | 随机种子，确保地形可重现 |
| `scale` | float | 0.1 | 0.01-1.0 | 噪声缩放因子，控制地形特征大小 |
| `octaves` | int | 3 | 1-8 | 噪声层数，控制地形细节复杂度 |
| `persistence` | float | 0.5 | 0.1-1.0 | 每层振幅衰减率，控制细节强度 |
| `lacunarity` | float | 2.0 | 1.5-3.0 | 每层频率倍增率，控制细节密度 |

### 地形分类参数

| 参数名 | 类型 | 默认值 | 范围 | 描述 |
|--------|------|--------|------|------|
| `water_threshold` | float | 0.3 | 0.1-0.5 | 水域高度阈值 |
| `mountain_threshold` | float | 0.8 | 0.6-0.9 | 山地高度阈值 |
| `forest_elevation_max` | float | 0.6 | 0.4-0.8 | 森林最大海拔高度 |
| `forest_moisture_min` | float | 0.7 | 0.5-0.9 | 森林最小湿度要求 |
| `desert_elevation_min` | float | 0.6 | 0.4-0.8 | 沙漠最小海拔高度 |
| `desert_moisture_max` | float | 0.3 | 0.1-0.5 | 沙漠最大湿度阈值 |

### 噪声生成配置

```python
# 噪声生成配置类
class PerlinNoiseConfig:
    # 核心参数
    seed: int = 42                    # 固定种子用于测试
    scale: float = 0.1                # 地形特征大小
    octaves: int = 3                  # 细节层数
    persistence: float = 0.5          # 振幅衰减率
    lacunarity: float = 2.0          # 频率倍增率
    
    # 生成参数
    amplitude_multiplier: float = 1.0  # 总振幅倍数
    frequency_multiplier: float = 1.0  # 总频率倍数
    normalize: bool = True            # 是否归一化到[0,1]
    
    # 地形参数
    water_threshold: float = 0.3      # 水域高度阈值
    mountain_threshold: float = 0.8   # 山地高度阈值
    forest_elevation_max: float = 0.6 # 森林最大海拔
    forest_moisture_min: float = 0.7  # 森林最小湿度
    desert_elevation_min: float = 0.6 # 沙漠最小海拔
    desert_moisture_max: float = 0.3  # 沙漠最大湿度
    
    def __init__(self, **kwargs):
        """支持参数覆盖"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
```

### 预设配置方案

#### 1. 标准大陆地形
```python
STANDARD_CONTINENT = PerlinNoiseConfig(
    scale=0.1,
    octaves=3,
    persistence=0.5,
    lacunarity=2.0,
    water_threshold=0.3,
    mountain_threshold=0.8,
    forest_elevation_max=0.6,
    forest_moisture_min=0.7
)
```

#### 2. 群岛地形
```python
ARCHIPELAGO = PerlinNoiseConfig(
    scale=0.05,          # 更小的地形特征
    octaves=4,           # 更多细节
    persistence=0.4,     # 更快衰减
    lacunarity=2.2,      # 更密集的细节
    water_threshold=0.4, # 更高水位
    mountain_threshold=0.9
)
```

#### 3. 大陆地形
```python
CONTINENT = PerlinNoiseConfig(
    scale=0.15,          # 更大的地形特征
    octaves=2,           # 更少细节
    persistence=0.6,     # 更慢衰减
    lacunarity=1.8,      # 更稀疏的细节
    water_threshold=0.25, # 更低水位
    mountain_threshold=0.75
)
```

#### 4. 山地地形
```python
MOUNTAINOUS = PerlinNoiseConfig(
    scale=0.08,          # 中等地形特征
    octaves=5,           # 丰富细节
    persistence=0.7,     # 慢衰减
    lacunarity=2.5,      # 高密度细节
    water_threshold=0.2, # 极低水位
    mountain_threshold=0.7  # 更低的山地阈值
)
```

## 算法实现流程

### 1. 多层噪声合成

```python
def generate_octaved_noise(x: float, y: float, config: PerlinNoiseConfig) -> float:
    """生成多层噪声合成"""
    total_amplitude = 0.0
    total_value = 0.0
    
    for octave in range(config.octaves):
        # 计算当前octave的参数
        frequency = (config.lacunarity ** octave) * config.scale * config.frequency_multiplier
        amplitude = (config.persistence ** octave) * config.amplitude_multiplier
        
        # 生成噪声值
        noise_value = perlin_noise(x * frequency, y * frequency)
        
        # 累加
        total_value += noise_value * amplitude
        total_amplitude += amplitude
    
    # 归一化
    if config.normalize and total_amplitude > 0:
        return total_value / total_amplitude
    return total_value
```

### 2. 地形高度生成

```python
def generate_elevation(map_width: int, map_height: int, config: PerlinNoiseConfig) -> List[List[float]]:
    """生成地形高度图"""
    elevation_map = []
    
    for y in range(map_height):
        row = []
        for x in range(map_width):
            # 生成基础高度
            elevation = generate_octaved_noise(x, y, config)
            
            # 添加边缘衰减（避免海岸线过于锐利）
            edge_distance = min(x, y, map_width - x - 1, map_height - y - 1)
            edge_factor = min(1.0, edge_distance / 10.0)
            elevation *= edge_factor
            
            # 确保在有效范围内
            elevation = max(-1.0, min(1.0, elevation))
            row.append(elevation)
        
        elevation_map.append(row)
    
    return elevation_map
```

### 3. 湿度生成

```python
def generate_moisture(elevation_map: List[List[float]], config: PerlinNoiseConfig) -> List[List[float]]:
    """生成湿度分布"""
    moisture_map = []
    height, width = len(elevation_map), len(elevation_map[0])
    
    for y in range(height):
        row = []
        for x in range(width):
            # 基础湿度（基于噪声）
            base_moisture = generate_octaved_noise(x, y, config) * 0.5 + 0.5
            
            # 水域影响
            elevation = elevation_map[y][x]
            water_influence = max(0, 1.0 - abs(elevation - config.water_threshold) / 0.3)
            
            # 综合湿度
            moisture = base_moisture * 0.7 + water_influence * 0.3
            moisture = max(0.0, min(1.0, moisture))
            
            row.append(moisture)
        moisture_map.append(row)
    
    return moisture_map
```

### 4. 地形分类

```python
def classify_terrain(elevation_map: List[List[float]], 
                     moisture_map: List[List[float]], 
                     config: PerlinNoiseConfig) -> List[List[str]]:
    """地形分类"""
    height, width = len(elevation_map), len(elevation_map[0])
    terrain_map = []
    
    for y in range(height):
        row = []
        for x in range(width):
            elevation = elevation_map[y][x]
            moisture = moisture_map[y][x]
            
            # 标准化高度到[0,1]
            normalized_elevation = (elevation + 1.0) / 2.0
            
            # 地形分类逻辑
            if normalized_elevation < config.water_threshold:
                terrain_type = "water"
            elif normalized_elevation > config.mountain_threshold:
                terrain_type = "mountain"
            elif normalized_elevation > config.desert_elevation_min and moisture < config.desert_moisture_max:
                terrain_type = "desert"
            elif normalized_elevation < config.forest_elevation_max and moisture > config.forest_moisture_min:
                terrain_type = "forest"
            else:
                terrain_type = "lowland"
            
            row.append(terrain_type)
        terrain_map.append(row)
    
    return terrain_map
```

## 参数调优指南

### 地形特征控制

| 目标地形特征 | scale | octaves | persistence | 效果 |
|-------------|-------|---------|-------------|------|
| 大陆级地形 | 0.1-0.2 | 2-3 | 0.5-0.7 | 宽广的陆地和海洋 |
| 群岛地形 | 0.03-0.06 | 3-4 | 0.4-0.5 | 分散的小岛屿 |
| 山地地形 | 0.05-0.1 | 4-6 | 0.6-0.8 | 密集的山脉和峡谷 |
| 平原地形 | 0.15-0.25 | 1-2 | 0.3-0.5 | 平坦开阔的区域 |

### 细节控制

| 细节级别 | octaves | persistence | lacunarity | 效果 |
|----------|---------|-------------|------------|------|
| 简单地形 | 1-2 | 0.3-0.5 | 1.5-2.0 | 基础地形轮廓 |
| 中等地形 | 2-4 | 0.5-0.7 | 2.0-2.5 | 自然的地形变化 |
| 复杂地形 | 4-8 | 0.7-0.9 | 2.5-3.0 | 丰富的地形细节 |

### 性能考虑

1. **地图大小**: 100x100以下使用默认参数，100x100以上减少octaves数量
2. **生成速度**: octaves数量是主要性能瓶颈，每增加一层约增加50%计算时间
3. **内存使用**: 地图尺寸的平方级内存消耗，大型地图考虑分块生成

## 使用示例

### 基础使用

```python
# 创建标准大陆地形
config = PerlinNoiseConfig(
    seed=12345,                    # 固定种子
    scale=0.1,                     # 地形特征大小
    octaves=3,                     # 3层细节
    persistence=0.5,               # 中等细节强度
    water_threshold=0.3            # 30%面积是水域
)

# 生成地形
elevation_map = generate_elevation(100, 100, config)
moisture_map = generate_moisture(elevation_map, config)
terrain_map = classify_terrain(elevation_map, moisture_map, config)
```

### 高级使用

```python
# 动态配置
def generate_world_template(world_type: str, seed: int = None) -> PerlinNoiseConfig:
    """根据世界类型生成配置"""
    templates = {
        "archipelago": ARCHIPELAGO,
        "continent": CONTINENT,
        "mountainous": MOUNTAINOUS,
        "standard": STANDARD_CONTINENT
    }
    
    config = templates.get(world_type, STANDARD_CONTINENT)
    if seed is not None:
        config.seed = seed
    
    return config

# 使用示例
config = generate_world_template("archipelago", seed=42)
```

## 测试用例

```python
def test_perlin_parameters():
    """测试不同参数组合"""
    # 测试标准配置
    config = STANDARD_CONTINENT
    assert 0.1 <= config.scale <= 0.2
    assert 2 <= config.octaves <= 4
    assert 0.4 <= config.persistence <= 0.6
    
    # 测试群岛配置
    config = ARCHIPELAGO
    assert config.scale < 0.1  # 群岛需要更小的地形特征
    assert config.water_threshold > 0.3  # 更多水域
    
    # 测试山地配置
    config = MOUNTAINOUS
    assert config.octaves >= 4  # 山地需要更多细节
    assert config.mountain_threshold < 0.8  # 更低的山地阈值
```

这个规格说明书提供了完整的Perlin噪声地形生成参数定义，包括核心算法参数、地形分类参数、预设配置方案、实现流程和调优指南。