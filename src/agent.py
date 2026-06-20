"""
基础人口Agent模块（简化版）
实现简单Agent：位置、饥饿度、移动、采集资源
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import random
from terrain import Tile, TerrainType
from faith_system import Faith, FaithType, CulturalTrait


class ResourceType(Enum):
    """资源类型枚举"""
    FOOD = "food"          # 食物
    WATER = "water"        # 水
    WOOD = "wood"          # 木材
    MINERAL = "mineral"    # 矿物


class Profession(Enum):
    """职业枚举 - Agent专业化系统"""
    HUNTER = "hunter"          # 猎人 - 擅长狩猎动物，获得更多食物
    FARMER = "farmer"          # 农民 - 擅长种植，稳定食物产出
    CRAFTSMAN = "craftsman"    # 工匠 - 擅长制作工具和武器
    GATHERER = "gatherer"      # 采集者 - 擅长收集各种资源


class AgentState(Enum):
    """Agent状态枚举"""
    IDLE = "idle"          # 空闲
    MOVING = "moving"      # 移动中
    GATHERING = "gathering" # 采集资源
    HUNGRY = "hungry"      # 饥饿
    RESTING = "resting"    # 休息中


class Agent:
    """基础人口Agent类"""
    
    def __init__(self, agent_id: int, x: int, y: int, tile: Tile, profession: Profession = Profession.GATHERER):
        self.id = agent_id                    # Agent唯一标识
        self.x = x                            # X坐标
        self.y = y                            # Y坐标
        self.current_tile = tile              # 当前所在格子
        
        # 职业设置
        self.profession = profession          # Agent的职业
        self.profession_level = 1             # 职业等级 (1-10)
        self.profession_exp = 0.0            # 职业经验值
        
        # 基础属性（根据职业调整）
        self.health = 100.0                   # 健康值 (0-100)
        self.energy = 100.0                   # 能量值 (0-100)
        self.hunger = 0.0                     # 饥饿度 (0-100，越高越饿)
        self.thirst = 0.0                     # 口渴度 (0-100，越高越渴)
        
        # 能力值（根据职业调整）
        self._setup_profession_stats()
        
        # 背包
        self.inventory: Dict[ResourceType, int] = {
            ResourceType.FOOD: 0,
            ResourceType.WATER: 0,
            ResourceType.WOOD: 0,
            ResourceType.MINERAL: 0
        }
        self.max_inventory = 20               # 最大背包容量
        
        # 状态和行为
        self.state = AgentState.IDLE
        self.target_tile = None              # 目标格子
        self.target_resource = None          # 目标资源类型
        
        # 统计数据
        self.resources_collected = 0         # 采集资源总数
        self.steps_taken = 0                # 移动步数
        self.rest_count = 0                  # 休息次数
        self.profession_specializations: Dict[str, int] = {
            'hunt_success': 0,    # 狩猎成功次数
            'farm_harvest': 0,   # 农作物收获次数
            'craft_items': 0,     # 制作物品次数
            'gather_rare': 0      # 稀有资源采集次数
        }
        
        # 交易相关属性
        self.trades_made = 0                 # 完成的交易次数
        self.trades_successful = 0          # 成功交易次数
        self.trade_partners = []            # 交易伙伴列表
        
        # 生存参数（根据职业调整）
        self.hunger_rate = 2.0               # 饥饿增长速率
        self.thirst_rate = 1.5               # 口渴增长速率
        self.energy_consumption = 1.0         # 能量消耗速率
        
        # 职业特殊能力
        self.special_abilities = self._setup_profession_abilities()
        self.crafted_items: List[str] = []    # 工匠制作的物品列表
        
        # 财富（简化用健康值代表）
        self.wealth = 100.0
        
        # 信仰系统
        self.faith: Optional[Faith] = None
        
    def _setup_profession_stats(self):
        """根据职业设置属性"""
        base_stats = {
            Profession.HUNTER: {
                'strength': random.randint(6, 9),    # 猎人力量较高
                'agility': random.randint(7, 9),     # 猎人敏捷很高
                'endurance': random.randint(4, 6),   # 猎人耐力中等
                'hunger_rate': 1.5,                 # 猎人饥饿增长较慢
                'thirst_rate': 1.2                  # 猎人口渴增长较慢
            },
            Profession.FARMER: {
                'strength': random.randint(4, 6),    # 农民力量中等
                'agility': random.randint(5, 7),     # 农民敏捷中等
                'endurance': random.randint(7, 9),   # 农民耐力较高
                'hunger_rate': 1.0,                  # 农民饥饿增长慢
                'thirst_rate': 1.0                   # 农民口渴增长慢
            },
            Profession.CRAFTSMAN: {
                'strength': random.randint(5, 7),    # 工匠力量中等
                'agility': random.randint(4, 6),     # 工匠敏捷中等
                'endurance': random.randint(6, 8),   # 工匠耐力中等
                'hunger_rate': 2.0,                  # 工匠饥饿增长正常
                'thirst_rate': 1.5                   # 工匠口渴增长正常
            },
            Profession.GATHERER: {
                'strength': random.randint(5, 8),    # 采集者力量较高
                'agility': random.randint(6, 8),     # 采集者敏捷较高
                'endurance': random.randint(5, 7),   # 采集者耐力中等
                'hunger_rate': 2.5,                  # 采集者饥饿增长较快
                'thirst_rate': 2.0                   # 采集者口渴增长较快
            }
        }
        
        stats = base_stats[self.profession]
        self.strength = stats['strength']
        self.agility = stats['agility']
        self.endurance = stats['endurance']
        self.hunger_rate = stats['hunger_rate']
        self.thirst_rate = stats['thirst_rate']
    
    def _setup_profession_abilities(self):
        """根据职业设置特殊能力"""
        abilities = {
            Profession.HUNTER: {
                'hunting_bonus': 1.5,
                'resource_bonus': {ResourceType.FOOD: 1.3},
                'move_efficiency': 1.2
            },
            Profession.FARMER: {
                'farming_bonus': 1.4,
                'resource_bonus': {ResourceType.FOOD: 1.2},
                'stamina_bonus': 1.1
            },
            Profession.CRAFTSMAN: {
                'crafting_bonus': 1.5,
                'tool_quality': 1.3,
                'resource_bonus': {ResourceType.MINERAL: 1.2}
            },
            Profession.GATHERER: {
                'gathering_bonus': 1.3,
                'resource_bonus': {ResourceType.WOOD: 1.4, ResourceType.WATER: 1.2},
                'move_efficiency': 1.1
            }
        }
        return abilities.get(self.profession, {})
    
    def update(self, world_map) -> List[str]:
        """更新Agent状态 - 包含信仰影响"""
        logs = []
        
        # 基础生命消耗
        self.hunger += self.hunger_rate
        self.thirst += self.thirst_rate
        
        # 信仰影响基础消耗
        if self.faith:
            if self.faith.faith_type == FaithType.SPIRITUAL:
                # 精神信仰降低基础消耗
                self.hunger += self.hunger_rate * 0.8
                self.thirst += self.thirst_rate * 0.8
            elif self.faith.faith_type == FaithType.NATURE:
                # 自然信仰在特定环境中降低消耗
                if self.current_tile.terrain_type.value == "FOREST":
                    self.hunger += self.hunger_rate * 0.9
                    self.thirst += self.thirst_rate * 0.9
        
        # 根据状态执行行为
        if self.state == AgentState.IDLE:
            logs.extend(self._act_idle(world_map))
        elif self.state == AgentState.MOVING:
            logs.extend(self._act_moving(world_map))
        elif self.state == AgentState.GATHERING:
            logs.extend(self._act_gathering(world_map))
        elif self.state == AgentState.RESTING:
            logs.extend(self._act_resting(world_map))
        
        # 检查生命状态
        if self.hunger > 90:
            self.state = AgentState.HUNGRY
            logs.append(f"Agent {self.id} is very hungry!")
        elif self.thirst > 90:
            self.state = AgentState.HUNGRY
            logs.append(f"Agent {self.id} is very thirsty!")
        elif self.energy < 20:
            self.state = AgentState.RESTING
            logs.append(f"Agent {self.id} is tired and rests.")
        
        # 健康衰减
        if self.hunger > 80 or self.thirst > 80:
            damage = 2
            if self.faith and self.faith.faith_type == FaithType.SPIRITUAL:
                damage = 1  # 精神信仰减少伤害
            self.health = max(0, self.health - damage)
        
        # 信仰强度自然波动
        if self.faith:
            if random.random() < 0.1:  # 10%概率信仰强度变化
                change = random.uniform(-2, 3)  # 轻微波动
                self.faith.strength = max(0, min(100, self.faith.strength + change))
                
                # 信仰强度过低可能导致信仰丧失
                if self.faith.strength < 10:
                    logs.append(f"Agent {self.id}'s faith weakens and is lost.")
                    self.faith = None
        
        return logs
    
    def _act_idle(self, world_map) -> List[str]:
        """空闲状态行为"""
        logs = []
        
        # 检查是否需要进食或饮水
        if self.hunger > 50 or self.thirst > 50:
            # 检查当前格子是否有资源
            if self.current_tile.get_total_resources():
                self.state = AgentState.GATHERING
                self.target_resource = self._find_needed_resource()
                logs.append(f"Agent {self.id} starts gathering resources.")
            else:
                # 寻找有资源的格子
                target = self._find_nearest_resource_tile(world_map)
                if target:
                    self.target_tile = target
                    self.state = AgentState.MOVING
                    logs.append(f"Agent {self.id} moves towards resource at ({target.x}, {target.y}).")
        else:
            # 随机探索
            neighbors = world_map.get_neighbors(self.x, self.y)
            if neighbors and random.random() < 0.3:  # 30%概率移动
                target = random.choice(neighbors)
                self.target_tile = target
                self.state = AgentState.MOVING
                logs.append(f"Agent {self.id} explores to ({target.x}, {target.y}).")
        
        return logs
    
    def _act_moving(self, world_map) -> List[str]:
        """移动状态行为 - 受信仰影响移动模式"""
        logs = []
        
        # 信仰影响移动偏好
        if self.faith and random.random() < 0.2:  # 20%概率按信仰模式移动
            faith_target = self._get_faith_based_movement_target(world_map)
            if faith_target:
                self.target_tile = faith_target
                logs.append(f"Agent {self.id} moves based on faith guidance.")
        
        if self.target_tile:
            # 计算移动方向
            dx = self.target_tile.x - self.x
            dy = self.target_tile.y - self.y
            
            if dx == 0 and dy == 0:
                # 到达目标
                self.state = AgentState.IDLE
                self.target_tile = None
                
                # 信仰相关的到达行为
                if self.faith:
                    if self.faith.faith_type == FaithType.NATURE:
                        self.health = min(100, self.health + 2)  # 自然信仰恢复健康
                    elif self.faith.faith_type == FaithType.SPIRITUAL:
                        self.energy = min(100, self.energy + 3)  # 精神信仰恢复能量
                
                logs.append(f"Agent {self.id} arrived at destination.")
            else:
                # 移动一步
                move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
                move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                # 检查目标格子是否有效
                new_tile = world_map.get_tile(new_x, new_y)
                if new_tile:
                    self.x = new_x
                    self.y = new_y
                    self.current_tile = new_tile
                    self.steps_taken += 1
                    
                    # 移动消耗能量
                    movement_cost = new_tile.get_movement_cost()
                    
                    # 信仰影响移动消耗
                    if self.faith:
                        if self.faith.faith_type == FaithType.COMMUNITY:
                            movement_cost *= 0.8  # 社群信仰减少移动消耗
                        elif self.faith.faith_type == FaithType.NATURE:
                            if new_tile.terrain_type.value == "FOREST":
                                movement_cost *= 0.7  # 自然信仰在森林中移动更有效率
                    
                    self.energy = max(0, self.energy - movement_cost)
                    
                    logs.append(f"Agent {self.id} moved to ({new_x}, {new_y}).")
                    
                    # 检查是否到达资源点
                    if self.target_tile.x == new_x and self.target_tile.y == new_y:
                        if self.current_tile.get_total_resources():
                            self.state = AgentState.GATHERING
                            self.target_resource = self._find_needed_resource()
                            logs.append(f"Agent {self.id} arrived at resource location.")
                        else:
                            self.state = AgentState.IDLE
                            self.target_tile = None
                else:
                    # 无法移动，改变计划
                    self.state = AgentState.IDLE
                    self.target_tile = None
                    logs.append(f"Agent {self.id} cannot move further, searching for new path.")
        else:
            # 没有目标，返回空闲状态
            self.state = AgentState.IDLE
            logs.append(f"Agent {self.id} has no target, returning to idle state.")
        
        return logs
        
    def _get_faith_based_movement_target(self, world_map) -> Optional[Tile]:
        """根据信仰获取移动目标"""
        if not self.faith:
            return None
            
        neighbors = world_map.get_neighbors(self.x, self.y)
        if not neighbors:
            return None
            
        # 根据信仰类型选择移动偏好
        if self.faith.faith_type == FaithType.NATURE:
            # 自然偏好：选择森林或山地
            nature_tiles = [tile for tile in neighbors if tile.terrain_type.value in ["FOREST", "MOUNTAIN"]]
            return random.choice(nature_tiles) if nature_tiles else random.choice(neighbors)
            
        elif self.faith.faith_type == FaithType.COMMUNITY:
            # 社群偏好：选择平坦地形（更容易聚集）
            flat_tiles = [tile for tile in neighbors if tile.terrain_type.value == "LOWLAND"]
            return random.choice(flat_tiles) if flat_tiles else random.choice(neighbors)
            
        elif self.faith.faith_type == FaithType.TECHNOLOGY:
            # 技术偏好：选择有矿物资源的区域
            mineral_tiles = [tile for tile in neighbors if tile.resources.get("mineral", 0) > 0]
            return random.choice(mineral_tiles) if mineral_tiles else random.choice(neighbors)
            
        return random.choice(neighbors)
    
    def _act_gathering(self, world_map) -> List[str]:
        """采集资源行为 - 根据职业专业化和信仰影响"""
        logs = []
        
        if not self.target_resource:
            self.target_resource = self._find_needed_resource()
            
            # 信仰影响资源选择
            if self.faith:
                resource_preference = self._get_faith_based_resource_preference()
                if resource_preference and random.random() < 0.3:  # 30%概率遵循信仰偏好
                    self.target_resource = resource_preference
                    logs.append(f"Agent {self.id} follows faith to gather {resource_preference.value}.")
        
        if self.target_resource:
            # 根据职业计算采集效率和产出
            base_efficiency = self.strength / 10.0
            profession_bonus = self.special_abilities.get('resource_bonus', {})
            resource_bonus = profession_bonus.get(self.target_resource.value, 1.0)
            
            # 信仰影响采集效率
            faith_bonus = 1.0
            if self.faith:
                # 自然崇拜增强资源采集
                if self.faith.faith_type == FaithType.NATURE and self.target_resource == ResourceType.FOOD:
                    faith_bonus = 1.3
                # 技术崇拜增强矿物采集
                elif self.faith.faith_type == FaithType.TECHNOLOGY and self.target_resource == ResourceType.MINERAL:
                    faith_bonus = 1.4
                # 社群崇拜倾向均衡采集
                elif self.faith.faith_type == FaithType.COMMUNITY:
                    faith_bonus = 1.2
                    
            # 计算采集量
            gather_amount = int(base_efficiency * resource_bonus * faith_bonus * random.uniform(1.0, 2.0))
            
            # 检查背包容量
            current_total = sum(self.inventory.values())
            if current_total < self.max_inventory:
                # 添加到背包
                self.inventory[self.target_resource] += gather_amount
                self.resources_collected += gather_amount
                
                # 获得职业经验
                self.profession_exp += gather_amount * 0.5
                
                # 信仰影响经验获得
                if self.faith:
                    if self.faith.faith_type == FaithType.ANCESTOR:
                        self.profession_exp += gather_amount * 0.2  # 祖先崇拜额外经验
                    elif self.faith.faith_type == FaithType.SPIRITUAL:
                        self.health = min(100, self.health + 1)  # 精神信仰恢复健康
                
                logs.append(f"Agent {self.id} gathered {gather_amount} {self.target_resource.value}.")
                
                # 检查职业升级
                if self._profession_level_up():
                    logs.append(f"Agent {self.id} leveled up to {self.profession_level}!")
                
                # 返回空闲状态
                self.state = AgentState.IDLE
                self.target_resource = None
            else:
                # 背包已满
                logs.append(f"Agent {self.id}'s inventory is full!")
                self.state = AgentState.IDLE
                self.target_resource = None
        else:
            self.state = AgentState.IDLE
        
        return logs
        
    def _get_faith_based_resource_preference(self) -> Optional[ResourceType]:
        """根据信仰获取资源偏好"""
        if not self.faith:
            return None
            
        preferences = {
            FaithType.NATURE: ResourceType.FOOD,  # 自然崇拜偏好食物
            FaithType.TECHNOLOGY: ResourceType.MINERAL,  # 技术崇拜偏好矿物
            FaithType.COMMUNITY: ResourceType.WATER,  # 社群崇拜偏好水资源
            FaithType.ANCESTOR: ResourceType.WOOD,  # 祖先崇拜偏好木材（制作祭祀用品）
            FaithType.SPIRITUAL: ResourceType.FOOD,  # 精神崇拜偏好食物（祭祀）
            FaithType.TRADITION: ResourceType.WOOD  # 传统崇拜偏好木材（传统工艺）
        }
        
        return preferences.get(self.faith.faith_type)
    
    def _act_resting(self, world_map) -> List[str]:
        """休息状态行为 - 受信仰影响恢复效果"""
        logs = []
        self.rest_count += 1
        
        # 基础休息恢复
        base_health_recovery = 3
        base_energy_recovery = 5
        
        # 信仰影响恢复效果
        if self.faith:
            if self.faith.faith_type == FaithType.SPIRITUAL:
                # 精神信仰大幅提升恢复效果
                base_health_recovery *= 1.5
                base_energy_recovery *= 1.3
                # 精神信仰也降低饥饿和口渴
                hunger_increase = 0.2
                thirst_increase = 0.1
            elif self.faith.faith_type == FaithType.NATURE:
                # 自然信仰中等提升恢复效果
                base_health_recovery *= 1.3
                base_energy_recovery *= 1.2
                hunger_increase = 0.3
                thirst_increase = 0.2
            elif self.faith.faith_type == FaithType.COMMUNITY:
                # 社群信仰轻微提升恢复效果
                base_health_recovery *= 1.1
                base_energy_recovery *= 1.1
                hunger_increase = 0.4
                thirst_increase = 0.3
            else:
                hunger_increase = 0.5
                thirst_increase = 0.3
        else:
            hunger_increase = 0.5
            thirst_increase = 0.3
        
        # 休息恢复健康和能量
        self.health = min(100, self.health + base_health_recovery)
        self.energy = min(100, self.energy + base_energy_recovery)
        
        # 休息降低饥饿和口渴（但比正常状态慢）
        self.hunger = min(100, self.hunger + hunger_increase)
        self.thirst = min(100, self.thirst + thirst_increase)
        
        # 信仰相关的特殊效果
        if self.faith:
            if self.faith.faith_type == FaithType.ANCESTOR:
                # 祖先信仰：长时间休息增加智慧（经验）
                if self.rest_count >= 3:
                    self.profession_exp += 2.0
                    logs.append(f"Agent {self.id} gains wisdom from ancestors during rest.")
            elif self.faith.faith_type == FaithType.TECHNOLOGY:
                # 技术信仰：休息时思考创新
                if random.random() < 0.3:  # 30%概率产生创新想法
                    self.profession_exp += 1.0
                    logs.append(f"Agent {self.id} has innovative insights during rest.")
        
        if self.health >= 100 and self.energy >= 80:
            self.state = AgentState.IDLE
            logs.append(f"Agent {self.id} finished resting and feels better.")
        else:
            logs.append(f"Agent {self.id} resting... Health: {self.health:.1f}, Energy: {self.energy:.1f}")
        
        return logs
    
    def _find_needed_resource(self) -> Optional[ResourceType]:
        """寻找最需要的资源类型"""
        if self.hunger > self.thirst:
            return ResourceType.FOOD
        else:
            return ResourceType.WATER
    
    def _find_nearest_resource_tile(self, world_map) -> Optional[Tile]:
        """寻找最近的有资源的格子"""
        best_distance = float('inf')
        best_tile = None
        
        for y in range(world_map.height):
            for x in range(world_map.width):
                tile = world_map.get_tile(x, y)
                if tile and tile.get_total_resources():
                    distance = abs(x - self.x) + abs(y - self.y)  # 曼哈顿距离
                    if distance < best_distance:
                        best_distance = distance
                        best_tile = tile
        
        return best_tile
    
    def get_status(self) -> Dict[str, float]:
        """获取Agent状态信息"""
        return {
            "health": self.health,
            "energy": self.energy,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "x": self.x,
            "y": self.y,
            "state": self.state.value,
            "profession": self.profession.value,
            "profession_level": self.profession_level,
            "profession_exp": self.profession_exp,
            "inventory": {res_type.value: amount for res_type, amount in self.inventory.items()},
            "resources_collected": self.resources_collected,
            "steps_taken": self.steps_taken,
            "specializations": self.profession_specializations
        }
    
    def _craft_tool(self) -> bool:
        """工匠制作工具"""
        if self.profession != Profession.CRAFTSMAN:
            return False
        
        # 检查材料
        if self.inventory.get(ResourceType.WOOD, 0) >= 2 and self.inventory.get(ResourceType.MINERAL, 0) >= 1:
            # 消耗材料
            self.inventory[ResourceType.WOOD] -= 2
            self.inventory[ResourceType.MINERAL] -= 1
            
            # 制作工具
            tool_quality = self.special_abilities.get('tool_quality', 1.0)
            tool_name = f"tool_quality_{int(tool_quality * 10)}"
            self.crafted_items.append(tool_name)
            self.profession_specializations['craft_items'] += 1
            self.profession_exp += 5.0  # 工匠制作获得经验
            
            # 工具效果（简化：增加采集效率）
            self.strength += 1
            
            return True
        return False
    
    def _profession_level_up(self) -> bool:
        """职业等级提升"""
        exp_required = self.profession_level * 20  # 等级越高需要越多经验
        if self.profession_exp >= exp_required:
            self.profession_level += 1
            self.profession_exp = 0
            
            # 提升各项属性
            self.strength += 1
            self.agility += 1
            self.endurance += 1
            
            # 增加背包容量
            self.max_inventory += 2
            
            return True
        return False