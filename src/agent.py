"""
基础人口Agent模块
实现简单Agent：位置、饥饿度、移动、采集资源
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import random
from terrain import Tile, TerrainType


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
        
        # 生存参数（根据职业调整）
        self.hunger_rate = 2.0               # 饥饿增长速率
        self.thirst_rate = 1.5               # 口渴增长速率
        self.energy_consumption = 1.0         # 能量消耗速率
        
        # 职业特殊能力
        self.special_abilities = self._setup_profession_abilities()
        self.crafted_items: List[str] = []    # 工匠制作的物品列表
        
    def _setup_profession_stats(self):
        """根据职业设置属性"""
        base_stats = {
            Profession.HUNTER: {
                'strength': random.randint(6, 9),    # 猎人力量较高
                'agility': random.randint(7, 9),     # 猎人敏捷很高
                'endurance': random.randint(4, 6),   # 猎人耐力中等
                'hunger_rate': 2.5,                 # 猎人消耗更多体力
                'energy_consumption': 1.2            # 猎人能量消耗较高
            },
            Profession.FARMER: {
                'strength': random.randint(3, 5),    # 农民力量较低
                'agility': random.randint(3, 5),     # 农民敏捷较低
                'endurance': random.randint(6, 8),   # 农民耐力较好
                'hunger_rate': 1.8,                 # 农民饥饿增长较慢
                'energy_consumption': 0.9            # 农民能量消耗较低
            },
            Profession.CRAFTSMAN: {
                'strength': random.randint(4, 6),    # 工匠力量中等
                'agility': random.randint(4, 6),     # 工匠敏捷中等
                'endurance': random.randint(5, 7),   # 工匠耐力中等
                'hunger_rate': 2.0,                 # 农民饥饿增长中等
                'energy_consumption': 1.0            # 农民能量消耗中等
            },
            Profession.GATHERER: {
                'strength': random.randint(5, 7),    # 采集者力量中等偏上
                'agility': random.randint(5, 7),     # 采集者敏捷中等偏上
                'endurance': random.randint(5, 7),   # 采集者耐力中等
                'hunger_rate': 2.2,                 # 采集者饥饿增长中等
                'energy_consumption': 1.1            # 采集者能量消耗中等偏上
            }
        }
        
        stats = base_stats.get(self.profession, base_stats[Profession.GATHERER])
        self.strength = stats['strength']
        self.agility = stats['agility']
        self.endurance = stats['endurance']
        self.hunger_rate = stats['hunger_rate']
        self.energy_consumption = stats['energy_consumption']
    
    def _setup_profession_abilities(self) -> Dict[str, float]:
        """设置职业特殊能力"""
        return {
            Profession.HUNTER: {
                'hunting_efficiency': 1.5,    # 狩猎效率50%提升
                'movement_speed': 1.2,        # 移动速度20%提升
                'resource_bonus': {'FOOD': 1.3}  # 食物产出30%提升
            },
            Profession.FARMER: {
                'farming_efficiency': 1.4,    # 种植效率40%提升
                'food_production': 1.2,        # 食物生产20%提升
                'resource_bonus': {'FOOD': 1.2, 'WOOD': 0.8}  # 食物+20%，木材-20%
            },
            Profession.CRAFTSMAN: {
                'crafting_efficiency': 1.6,   # 制作效率60%提升
                'tool_quality': 1.3,          # 工具质量30%提升
                'resource_bonus': {'WOOD': 1.2, 'MINERAL': 1.1}  # 木材+20%，矿物+10%
            },
            Profession.GATHERER: {
                'gathering_range': 1.5,       # 采集范围50%提升
                'rare_chance': 1.3,          # 稀有资源几率30%提升
                'resource_bonus': {'WOOD': 1.1, 'MINERAL': 1.1, 'FOOD': 1.0}  # 各类资源均衡提升
            }
        }[self.profession]
    
    def update(self, world_map) -> List[str]:
        """更新Agent状态，返回行为日志"""
        logs = []
        
        # 更新生存需求
        self.hunger = min(100, self.hunger + self.hunger_rate)
        self.thirst = min(100, self.thirst + self.thirst_rate)
        
        # 饥饿和口渴影响健康
        if self.hunger > 80:
            self.health -= 2
            logs.append(f"Agent {self.id} is very hungry! Health: {self.health:.1f}")
        
        if self.thirst > 80:
            self.health -= 2
            logs.append(f"Agent {self.id} is very thirsty! Health: {self.health:.1f}")
        
        # 检查死亡状态
        if self.health <= 0:
            self.state = AgentState.RESTING
            logs.append(f"Agent {self.id} has died!")
            return logs
        
        # 根据状态执行行为
        if self.state == AgentState.IDLE:
            logs.extend(self._act_idle(world_map))
        elif self.state == AgentState.MOVING:
            logs.extend(self._act_moving(world_map))
        elif self.state == AgentState.GATHERING:
            logs.extend(self._act_gathering(world_map))
        elif self.state == AgentState.HUNGRY:
            logs.extend(self._act_hungry(world_map))
        elif self.state == AgentState.RESTING:
            logs.extend(self._act_resting())
        
        # 更新能量
        if self.state != AgentState.RESTING:
            self.energy = max(0, self.energy - self.energy_consumption)
        else:
            self.energy = min(100, self.energy + 5)
        
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
        """移动状态行为"""
        logs = []
        
        if self.target_tile:
            # 计算移动方向
            dx = self.target_tile.x - self.x
            dy = self.target_tile.y - self.y
            
            if dx == 0 and dy == 0:
                # 到达目标
                self.state = AgentState.IDLE
                self.target_tile = None
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
                    self.energy = max(0, self.energy - new_tile.get_movement_cost())
                    
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
    
    def _act_gathering(self, world_map) -> List[str]:
        """采集资源行为 - 根据职业专业化"""
        logs = []
        
        if not self.target_resource:
            self.target_resource = self._find_needed_resource()
        
        if self.target_resource:
            # 根据职业计算采集效率和产出
            base_efficiency = self.strength / 10.0
            profession_bonus = self.special_abilities.get('resource_bonus', {})
            resource_bonus = profession_bonus.get(self.target_resource.value, 1.0)
            
            efficiency = base_efficiency * resource_bonus
            
            # 职业特定的采集行为
            if self.profession == Profession.HUNTER:
                gather_amount = int(efficiency * random.randint(3, 6))
                self.profession_exp += gather_amount * 0.5
                logs.append(f"Hunter {self.id} hunting efficiency!")
            elif self.profession == Profession.FARMER:
                gather_amount = int(efficiency * random.randint(2, 4))
                self.profession_exp += gather_amount * 0.3
                # 农民有稳定产出
                if random.random() < 0.3:  # 30%概率额外产出
                    gather_amount += 1
                    logs.append(f"Farmer {self.id} got bonus harvest!")
            elif self.profession == Profession.CRAFTSMAN:
                # 工匠主要收集制作工具的材料
                if self.target_resource == ResourceType.WOOD or self.target_resource == ResourceType.MINERAL:
                    gather_amount = int(efficiency * random.randint(2, 5))
                    self.profession_exp += gather_amount * 0.4
                    # 工匠会制作工具
                    if random.random() < 0.2:  # 20%概率制作工具
                        self._craft_tool()
                        logs.append(f"Craftsman {self.id} crafted a tool!")
                else:
                    gather_amount = int(efficiency * random.randint(1, 3))
            else:  # GATHERER
                gather_amount = int(efficiency * random.randint(2, 5))
                self.profession_exp += gather_amount * 0.3
                # 采集者有几率找到稀有资源
                if random.random() < 0.1:  # 10%几率
                    gather_amount += 1
                    self.profession_specializations['gather_rare'] += 1
                    logs.append(f"Gatherer {self.id} found rare resource!")
            
            # 检查背包容量
            current_total = sum(self.inventory.values())
            if current_total < self.max_inventory:
                # 执行采集
                self.inventory[self.target_resource] += gather_amount
                self.resources_collected += gather_amount
                
                # 消耗资源来满足需求
                if self.target_resource == ResourceType.FOOD and self.hunger > 0:
                    consume = min(gather_amount, int(self.hunger / 10))
                    self.inventory[self.target_resource] -= consume
                    self.hunger = max(0, self.hunger - consume * 5)
                    self.health = min(100, self.health + consume)
                    logs.append(f"Agent {self.id} ate {consume} food, hunger: {self.hunger:.1f}")
                
                elif self.target_resource == ResourceType.WATER and self.thirst > 0:
                    consume = min(gather_amount, int(self.thirst / 10))
                    self.inventory[self.target_resource] -= consume
                    self.thirst = max(0, self.thirst - consume * 5)
                    self.health = min(100, self.health + consume * 2)
                    logs.append(f"Agent {self.id} drank {consume} water, thirst: {self.thirst:.1f}")
                
                logs.append(f"Agent {self.id} gathered {gather_amount} {self.target_resource.value}.")
                
                # 检查是否还需要继续采集
                if (self.hunger < 30 and self.thirst < 30 and 
                    sum(self.inventory.values()) >= self.max_inventory):
                    self.state = AgentState.IDLE
                    self.target_resource = None
                    logs.append(f"Agent {self.id} finished gathering, returning to idle.")
            else:
                # 背包已满，需要消耗或移动
                if self.hunger > 20 or self.thirst > 20:
                    # 使用背包中的资源
                    if self.inventory.get(ResourceType.FOOD, 0) > 0:
                        self.inventory[ResourceType.FOOD] -= 1
                        self.hunger = max(0, self.hunger - 10)
                        self.health = min(100, self.health + 2)
                        logs.append(f"Agent {self.id} consumed food from inventory.")
                    elif self.inventory.get(ResourceType.WATER, 0) > 0:
                        self.inventory[ResourceType.WATER] -= 1
                        self.thirst = max(0, self.thirst - 10)
                        self.health = min(100, self.health + 1)
                        logs.append(f"Agent {self.id} consumed water from inventory.")
                else:
                    # 背包满且不需要消耗，寻找新地点
                    self.state = AgentState.IDLE
                    self.target_resource = None
                    logs.append(f"Agent {self.id} inventory full, exploring new area.")
        else:
            # 没有可采集的资源，移动寻找
            self.state = AgentState.IDLE
            logs.append(f"Agent {self.id} no resources available, searching for new location.")
        
        return logs
    
    def _act_hungry(self, world_map) -> List[str]:
        """饥饿状态行为"""
        logs = []
        self.state = AgentState.IDLE  # 简化处理，转为空闲状态
        logs.append(f"Agent {self.id} is hungry, searching for food.")
        return logs
    
    def _act_resting(self) -> List[str]:
        """休息状态行为"""
        logs = []
        self.rest_count += 1
        
        # 休息恢复健康和能量
        self.health = min(100, self.health + 3)
        self.energy = min(100, self.energy + 5)
        
        # 休息降低饥饿和口渴（但比正常状态慢）
        self.hunger = min(100, self.hunger + 0.5)
        self.thirst = min(100, self.thirst + 0.3)
        
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
    
    def __str__(self) -> str:
        return f"Agent({self.id}, {self.x},{self.y}, {self.state.value})"
    
    def __repr__(self) -> str:
        return self.__str__()