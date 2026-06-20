"""
冲突与战争系统模块
实现资源争夺导致的冲突检测、战争机制和结果计算
"""

from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
import random
import math

# 简化的依赖类定义
class ResourceType(Enum):
    FOOD = "food"
    WATER = "water"
    WOOD = "wood"
    MINERAL = "mineral"

class Profession(Enum):
    HUNTER = "hunter"
    FARMER = "farmer"
    CRAFTSMAN = "craftsman"
    GATHERER = "gatherer"

class Agent:
    def __init__(self, agent_id: int, x: int, y: int, tile, profession: Profession = Profession.GATHERER):
        self.id = agent_id
        self.x = x
        self.y = y
        self.profession = profession
        self.inventory = {}

class Tile:
    def __init__(self, x: int, y: int, terrain_type):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type

class Tribe:
    def __init__(self, tribe_id: int, name: str, founder: Agent):
        self.id = tribe_id
        self.name = name
        self.founder = founder
        self.members = {founder}
        self.territory = set()
        self.resources = {}
        self.leader = founder
    
    def add_member(self, agent: Agent):
        self.members.add(agent)
        
    def remove_member(self, agent: Agent):
        self.members.discard(agent)
        
    def update_territory(self):
        self.territory.clear()
        for member in self.members:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x, y = member.x + dx, member.y + dy
                    self.territory.add((x, y))
                    
    def get_population(self) -> int:
        return len(self.members)
        
    def get_resource_summary(self) -> Dict[str, int]:
        summary = {}
        for member in self.members:
            for resource_type, amount in member.inventory.items():
                resource_key = str(resource_type)
                summary[resource_key] = summary.get(resource_key, 0) + amount
        return summary


class ConflictType(Enum):
    """冲突类型枚举"""
    RESOURCE_CONFLICT = "resource_conflict"      # 资源争夺冲突
    TERRITORY_CONFLICT = "territory_conflict"    # 领土争端冲突
    IDEOLOGICAL_CONFLICT = "ideological_conflict" # 意识形态冲突


class WarResult:
    """战争结果类"""
    
    def __init__(self, attacker: Tribe, defender: Tribe, attacker_victory: bool):
        self.attacker = attacker
        self.defender = defender
        self.attacker_victory = attacker_victory
        
        # 战争伤亡
        self.attacker_casualties = 0
        self.defender_casualties = 0
        
        # 资源掠夺
        self.resources_taken = {}
        self.resources_lost = {}
        
        # 领土变化
        self.territory_gained = set()
        self.territory_lost = set()
        
        # 战争强度
        self.war_intensity = 0.0
        
    def calculate_casualties(self):
        """计算双方伤亡"""
        if self.attacker_victory:
            # 攻击方胜利，伤亡较少
            self.attacker_casualties = max(1, int(len(self.attacker.members) * 0.1 * self.war_intensity))
            self.defender_casualties = max(1, int(len(self.defender.members) * 0.3 * self.war_intensity))
        else:
            # 防守方胜利，攻击方伤亡惨重
            self.attacker_casualties = max(1, int(len(self.attacker.members) * 0.4 * self.war_intensity))
            self.defender_casualties = max(1, int(len(self.defender.members) * 0.15 * self.war_intensity))
    
    def calculate_resource_transfer(self):
        """计算资源转移"""
        # 攻击方掠夺的资源
        defender_resources = self.defender.get_resource_summary()
        total_defender_resources = sum(defender_resources.values())
        
        if self.attacker_victory and total_defender_resources > 0:
            # 攻击方胜利，掠夺30%-60%的资源
            plunder_ratio = 0.3 + random.random() * 0.3
            plunder_amount = int(total_defender_resources * plunder_ratio)
            
            # 随机选择资源类型进行掠夺
            resource_types = list(defender_resources.keys())
            for resource_type in resource_types:
                if defender_resources[resource_type] > 0:
                    take_amount = min(int(defender_resources[resource_type] * plunder_ratio), 
                                    defender_resources[resource_type])
                    self.resources_taken[resource_type] = take_amount
                    self.resources_lost[resource_type] = take_amount
    
    def calculate_territory_change(self):
        """计算领土变化"""
        if self.attacker_victory:
            # 攻击方获得部分领土
            defender_territory = list(self.defender.territory)
            if defender_territory:
                take_count = max(1, len(defender_territory) // 3)
                self.territory_gained = set(random.sample(defender_territory, take_count))
                self.territory_lost = self.territory_gained.intersection(self.attacker.territory)


class ConflictSystem:
    """冲突与战争系统"""
    
    def __init__(self, tribes: List[Tribe]):
        self.tribes = tribes
        self.conflict_threshold = 0.3  # 进一步降低冲突阈值，更容易触发冲突
        self.war_cooldown = {}  # 战争冷却时间（部落ID -> 回合数）
        
    def detect_conflicts(self) -> List[Tuple[Tribe, Tribe, ConflictType]]:
        """检测可能发生冲突的部落对"""
        conflicts = []
        
        # 检查所有部落对
        for i, tribe1 in enumerate(self.tribes):
            for tribe2 in self.tribes[i+1:]:
                conflict_type = self._analyze_conflict_type(tribe1, tribe2)
                if conflict_type:
                    conflicts.append((tribe1, tribe2, conflict_type))
        
        return conflicts
    
    def _analyze_conflict_type(self, tribe1: Tribe, tribe2: Tribe) -> Optional[ConflictType]:
        """分析两个部落之间的冲突类型"""
        
        # 检查战争冷却
        current_cooldown = self.war_cooldown.get(tribe1.id, 0)
        if current_cooldown > 0:
            return None
        
        # 计算地理距离
        distance = self._calculate_tribe_distance(tribe1, tribe2)
        if distance > 10:  # 距离太远，不考虑冲突
            return None
        
        # 检查资源冲突
        resource_conflict = self._check_resource_conflict(tribe1, tribe2)
        if resource_conflict > self.conflict_threshold:
            return ConflictType.RESOURCE_CONFLICT
        
        # 检查领土冲突
        territory_conflict = self._check_territory_conflict(tribe1, tribe2)
        if territory_conflict > self.conflict_threshold:
            return ConflictType.TERRITORY_CONFLICT
        
        # 检查意识形态冲突
        ideology_conflict = self._check_ideological_conflict(tribe1, tribe2)
        if ideology_conflict > self.conflict_threshold:
            return ConflictType.IDEOLOGICAL_CONFLICT
        
        return None
    
    def _calculate_tribe_distance(self, tribe1: Tribe, tribe2: Tribe) -> float:
        """计算两个部落之间的平均距离"""
        if not tribe1.members or not tribe2.members:
            return float('inf')
        
        total_distance = 0
        count = 0
        
        for member1 in tribe1.members:
            for member2 in tribe2.members:
                dx = member1.x - member2.x
                dy = member1.y - member2.y
                distance = math.sqrt(dx * dx + dy * dy)
                total_distance += distance
                count += 1
        
        return total_distance / count if count > 0 else float('inf')
    
    def _check_resource_conflict(self, tribe1: Tribe, tribe2: Tribe) -> float:
        """检查资源冲突程度（0-1）"""
        resources1 = tribe1.get_resource_summary()
        resources2 = tribe2.get_resource_summary()
        
        print(f"   资源冲突检查: {tribe1.name} vs {tribe2.name}")
        print(f"   {tribe1.name} 资源: {resources1}")
        print(f"   {tribe2.name} 资源: {resources2}")
        
        # 计算资源压力
        pressure1 = self._calculate_resource_pressure(resources1)
        pressure2 = self._calculate_resource_pressure(resources2)
        
        print(f"   压力指数: {tribe1.name}={pressure1:.2f}, {tribe2.name}={pressure2:.2f}")
        
        # 如果两个部落资源都很紧张，冲突概率高
        if pressure1 > 0.6 and pressure2 > 0.6:
            conflict_score = 0.8 + (pressure1 + pressure2) * 0.1
            print(f"   双方都紧张 -> 冲突评分: {conflict_score:.2f}")
            return min(conflict_score, 1.0)
        
        # 如果一个部落资源丰富，另一个部落资源紧张，冲突概率中等
        if (pressure1 < 0.3 and pressure2 > 0.6) or (pressure2 < 0.3 and pressure1 > 0.6):
            conflict_score = 0.5 + max(pressure1, pressure2) * 0.3
            print(f"   一方紧张 -> 冲突评分: {conflict_score:.2f}")
            return conflict_score
        
        # 领土重叠增加冲突概率
        territory_overlap = len(tribe1.territory.intersection(tribe2.territory))
        total_territory = len(tribe1.territory.union(tribe2.territory))
        if total_territory > 0:
            overlap_ratio = territory_overlap / total_territory
            if overlap_ratio > 0.3:
                base_conflict = 0.3 + overlap_ratio * 0.4
                print(f"   领土重叠 {overlap_ratio:.2f} -> 冲突评分: {base_conflict:.2f}")
                return base_conflict
        
        print(f"   基础冲突评分: 0.2")
        return 0.2
    
    def _calculate_resource_pressure(self, resources: Dict[str, int]) -> float:
        """计算资源压力指数（0-1，越高越紧张）"""
        if not resources:
            print(f"   资源为空 -> 压力: 1.0")
            return 1.0
        
        # 计算人均资源量
        total_resources = sum(resources.values())
        resource_count = len(resources)
        
        # 如果资源种类少，压力大
        if resource_count < 2:
            print(f"   资源种类少({resource_count}) -> 压力: 0.8")
            return 0.8
        
        # 如果人均资源少，压力大
        avg_resources = total_resources / resource_count if resource_count > 0 else 0
        print(f"   人均资源: {avg_resources:.1f} (总计:{total_resources}, 种类:{resource_count})")
        
        if avg_resources < 5:
            pressure = 0.9
        elif avg_resources < 10:
            pressure = 0.6
        elif avg_resources < 20:
            pressure = 0.4
        else:
            pressure = 0.2
            
        print(f"   压力计算结果: {pressure}")
        return pressure
    
    def _check_territory_conflict(self, tribe1: Tribe, tribe2: Tribe) -> float:
        """检查领土冲突程度"""
        # 计算领土重叠
        overlap = len(tribe1.territory.intersection(tribe2.territory))
        total_territory = len(tribe1.territory.union(tribe2.territory))
        
        if total_territory == 0:
            return 0.0
        
        overlap_ratio = overlap / total_territory
        return min(overlap_ratio * 2, 1.0)  # 重叠比例越高，冲突越激烈
    
    def _check_ideological_conflict(self, tribe1: Tribe, tribe2: Tribe) -> float:
        """检查意识形态冲突程度"""
        # 这里简化处理，随机生成一些意识形态差异
        # 实际实现中可以根据部落的信仰、文化等来计算
        return random.random() * 0.5  # 0-0.5的随机冲突度
    
    def initiate_war(self, attacker: Tribe, defender: Tribe) -> WarResult:
        """发起战争并返回结果"""
        print(f"⚔️ 部落 {attacker.name} 对 {defender.name} 发起战争！")
        
        # 计算战争强度
        war_intensity = self._calculate_war_intensity(attacker, defender)
        
        # 计算战争结果
        attacker_power = self._calculate_tribe_power(attacker) * war_intensity
        defender_power = self._calculate_tribe_power(defender) * war_intensity
        
        attacker_victory = attacker_power > defender_power
        
        # 创建战争结果
        result = WarResult(attacker, defender, attacker_victory)
        result.war_intensity = war_intensity
        result.calculate_casualties()
        result.calculate_resource_transfer()
        result.calculate_territory_change()
        
        # 应用战争结果
        self._apply_war_result(result)
        
        # 设置战争冷却
        self.war_cooldown[attacker.id] = 5  # 5回合内不能再战
        self.war_cooldown[defender.id] = 3  # 3回合内不能再战
        
        return result
    
    def _calculate_war_intensity(self, tribe1: Tribe, tribe2: Tribe) -> float:
        """计算战争强度"""
        # 基于双方人口比例和资源压力
        pop_ratio = min(len(tribe1.members), len(tribe2.members)) / max(len(tribe1.members), len(tribe2.members))
        resource_pressure = (self._calculate_resource_pressure(tribe1.get_resource_summary()) + 
                           self._calculate_resource_pressure(tribe2.get_resource_summary())) / 2
        
        return 0.5 + pop_ratio * 0.3 + resource_pressure * 0.2
    
    def _calculate_tribe_power(self, tribe: Tribe) -> float:
        """计算部落综合实力"""
        # 基础实力 = 人口 * 0.4 + 资源丰富度 * 0.3 + 职业多样性 * 0.3
        population_factor = len(tribe.members) * 0.4
        
        resources = tribe.get_resource_summary()
        total_resources = sum(resources.values())
        resource_factor = min(total_resources / 100, 1.0) * 0.3
        
        # 职业多样性
        professions = set(member.profession for member in tribe.members)
        profession_factor = len(professions) / 5 * 0.3  # 假设最多5种职业
        
        return population_factor + resource_factor + profession_factor
    
    def _apply_war_result(self, result: WarResult):
        """应用战争结果"""
        # 应用伤亡
        self._apply_casualties(result.attacker, result.attacker_casualties)
        self._apply_casualties(result.defender, result.defender_casualties)
        
        # 应用资源转移
        for resource_type, amount in result.resources_taken.items():
            # 从防守方成员的库存中移除资源
            defenders_with_resource = [m for m in result.defender.members if m.inventory.get(resource_type, 0) > 0]
            if defenders_with_resource:
                # 平均分配掠夺
                per_defender = amount // len(defenders_with_resource)
                for member in defenders_with_resource:
                    take = min(per_defender, member.inventory.get(resource_type, 0))
                    member.inventory[resource_type] = max(0, member.inventory.get(resource_type, 0) - take)
                    
                # 给攻击方成员添加资源
                attackers_per_member = amount // len(result.attacker.members)
                for member in result.attacker.members:
                    member.inventory[resource_type] = member.inventory.get(resource_type, 0) + attackers_per_member
            
            print(f"   资源转移: {resource_type} {amount} (防守方 -> 攻击方)")
        
        # 应用领土变化
        result.defender.territory -= result.territory_gained
        result.attacker.territory.update(result.territory_gained)
        
        print(f"🏆 战争结束！{'攻击方' if result.attacker_victory else '防守方'}胜利！")
        print(f"💀 伤亡：攻击方 {result.attacker_casualties} 人，防守方 {result.defender_casualties} 人")
        if result.resources_taken:
            print(f"💰 资源掠夺：{result.resources_taken}")
        if result.territory_gained:
            print(f"🗺️ 领土变化：获得 {len(result.territory_gained)} 个格子")
    
    def _apply_casualties(self, tribe: Tribe, casualties: int):
        """应用伤亡"""
        if casualties >= len(tribe.members):
            # 部落灭绝
            print(f"💀 部落 {tribe.name} 被消灭！")
            self.tribes.remove(tribe)
        else:
            # 随机移除成员
            casualties_list = random.sample(list(tribe.members), min(casualties, len(tribe.members)))
            for agent in casualties_list:
                tribe.remove_member(agent)
                print(f"💀 部落 {tribe.name} 成员 {agent.id} 在战争中死亡")