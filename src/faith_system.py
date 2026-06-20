"""
信仰与文化传播系统模块
实现信仰系统、文化传承和影响行为偏好的机制
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Tuple, TYPE_CHECKING
import random
import math
from dataclasses import dataclass

if TYPE_CHECKING:
    from agent import Agent


class FaithType(Enum):
    """信仰类型枚举"""
    ANCESTOR = "ancestor"          # 祖先崇拜
    NATURE = "nature"             # 自然崇拜
    COMMUNITY = "community"        # 社群崇拜
    TECHNOLOGY = "technology"      # 技术崇拜
    SPIRITUAL = "spiritual"        # 精神崇拜
    TRADITION = "tradition"        # 传统崇拜


class CulturalTrait(Enum):
    """文化特征枚举"""
    COOPERATIVE = "cooperative"     # 合作型
    COMPETITIVE = "competitive"     # 竞争型
    CONSERVATIVE = "conservative"   # 保守型
    INNOVATIVE = "innovative"      # 创新型
    SPIRITUAL = "spiritual"        # 精神性
    MATERIALISTIC = "materialistic" # 物质型


@dataclass
class Faith:
    """信仰类"""
    faith_type: FaithType
    strength: float  # 信仰强度 (0-100)
    traditions: List[str]  # 传统习俗
    values: List[CulturalTrait]  # 文化价值观
    influence_radius: float = 3.0  # 影响半径
    
    def get_influence_strength(self, distance: float) -> float:
        """计算在给定距离上的影响强度"""
        if distance <= self.influence_radius:
            return self.strength * (1 - distance / self.influence_radius)
        return 0.0


class CulturalSpread:
    """文化传播系统"""
    
    def __init__(self):
        self.faith_spread_rate = 0.1  # 信仰传播速率
        self.cultural_conversion_rate = 0.05  # 文化转化速率
        self.min_influence_strength = 10.0  # 最小影响强度
        
    def spread_faith_between_agents(self, agent1: 'Agent', agent2: 'Agent', distance: float) -> bool:
        """两个agent之间的信仰传播"""
        if not agent1.faith or not agent2.faith:
            return False
            
        # 计算相互影响
        agent1_to_agent2 = agent1.faith.get_influence_strength(distance)
        agent2_to_agent1 = agent2.faith.get_influence_strength(distance)
        
        # 确定传播方向（从强到弱）
        if agent1_to_agent2 > agent2_to_agent1:
            stronger, weaker = agent1, agent2
            influence_strength = agent1_to_agent2
        else:
            stronger, weaker = agent2, agent1
            influence_strength = agent2_to_agent1
            
        # 检查是否达到传播阈值
        if influence_strength < self.min_influence_strength:
            return False
            
        # 传播信仰的强度衰减
        spread_amount = influence_strength * self.faith_spread_rate
        
        # 如果较弱者还没有信仰，则有概率接受
        if weaker.faith is None:
            if random.random() < spread_amount / 100:
                weaker.faith = Faith(
                    faith_type=stronger.faith.faith_type,
                    strength=spread_amount * 0.5,  # 新接受者强度较低
                    traditions=[],  # 继承部分传统
                    values=stronger.faith.values.copy()
                )
                return True
                
        # 如果较弱者已有信仰，则有概率改变信仰类型
        else:
            if random.random() < spread_amount / 200:  # 改变信仰的门槛更高
                weaker.faith.faith_type = stronger.faith.faith_type
                weaker.faith.strength = min(100, weaker.faith.strength + spread_amount * 0.3)
                return True
                
        return False
    
    def spread_cultural_traits(self, agent1: 'Agent', agent2: 'Agent', distance: float) -> bool:
        """传播文化特征"""
        if not agent1.faith or not agent2.faith:
            return False
            
        influence_strength = agent1.faith.get_influence_strength(distance)
        
        if influence_strength < self.min_influence_strength:
            return False
            
        # 文化特征传播
        spread_chance = influence_strength * self.cultural_conversion_rate / 100
        
        if random.random() < spread_chance:
            # 随机传播一个价值观
            if agent1.faith.values and random.random() < 0.5:
                trait_to_spread = random.choice(agent1.faith.values)
                if trait_to_spread not in agent2.faith.values:
                    agent2.faith.values.append(trait_to_spread)
                    return True
                    
        return False
    
    def tribe_faith_conversion(self, tribe_agents: List['Agent']) -> None:
        """部落内信仰统一化"""
        if len(tribe_agents) < 2:
            return
            
        # 找出部落中最强的信仰类型
        faith_counts = {}
        for agent in tribe_agents:
            if agent.faith:
                faith_type = agent.faith.faith_type.value
                faith_counts[faith_type] = faith_counts.get(faith_type, 0) + 1
                
        if not faith_counts:
            return
            
        # 找出主流信仰
        dominant_faith = max(faith_counts, key=faith_counts.get)
        
        # 部落内弱化其他信仰，强化主流信仰
        for agent in tribe_agents:
            if agent.faith:
                if agent.faith.faith_type.value == dominant_faith:
                    # 同信仰者增强信仰强度
                    agent.faith.strength = min(100, agent.faith.strength + 2)
                else:
                    # 异信仰者减弱信仰强度
                    agent.faith.strength = max(0, agent.faith.strength - 1)
                    
                    # 有概率改变信仰
                    if agent.faith.strength < 20 and random.random() < 0.1:
                        agent.faith.faith_type = FaithType(dominant_faith)
                        agent.faith.strength = 30


class FaithManager:
    """信仰管理器"""
    
    def __init__(self):
        self.faith_types = list(FaithType)
        self.cultural_traits = list(CulturalTrait)
        self.cultural_spread = CulturalSpread()
        
    def generate_initial_faith(self, agent: 'Agent') -> None:
        """为agent生成初始信仰"""
        # 根据职业和位置选择信仰类型
        faith_weights = {
            FaithType.ANCESTOR: 1.0,
            FaithType.NATURE: 1.0,
            FaithType.COMMUNITY: 1.0,
            FaithType.TECHNOLOGY: 1.0,
            FaithType.SPIRITUAL: 1.0,
            FaithType.TRADITION: 1.0
        }
        
        # 根据职业调整信仰偏好
        if agent.profession.value == "hunter":
            faith_weights[FaithType.NATURE] *= 2.0
            faith_weights[FaithType.ANCESTOR] *= 1.5
        elif agent.profession.value == "farmer":
            faith_weights[FaithType.NATURE] *= 1.8
            faith_weights[FaithType.COMMUNITY] *= 1.5
            faith_weights[FaithType.TRADITION] *= 1.3
        elif agent.profession.value == "craftsman":
            faith_weights[FaithType.TECHNOLOGY] *= 2.0
            faith_weights[FaithType.COMMUNITY] *= 1.2
        elif agent.profession.value == "gatherer":
            faith_weights[FaithType.NATURE] *= 1.5
            faith_weights[FaithType.SPIRITUAL] *= 1.3
            
        # 根据位置调整信仰偏好
        if agent.current_tile:
            terrain_type = str(agent.current_tile.terrain_type.value).lower()
            if "forest" in terrain_type or "mountain" in terrain_type:
                faith_weights[FaithType.NATURE] *= 1.5
            elif "lowland" in terrain_type or "plain" in terrain_type:
                faith_weights[FaithType.COMMUNITY] *= 1.3
                faith_weights[FaithType.TRADITION] *= 1.2
                
        # 加权随机选择信仰类型
        total_weight = sum(faith_weights.values())
        rand_val = random.uniform(0, total_weight)
        cumulative = 0
        
        for faith_type, weight in faith_weights.items():
            cumulative += weight
            if rand_val <= cumulative:
                selected_faith = faith_type
                break
                
        # 生成信仰
        agent.faith = Faith(
            faith_type=selected_faith,
            strength=random.uniform(30, 70),  # 初始强度
            traditions=self._generate_traditions(selected_faith),
            values=self._generate_cultural_values(selected_faith)
        )
        
    def _generate_traditions(self, faith_type: FaithType) -> List[str]:
        """生成与信仰相关的传统"""
        traditions_map = {
            FaithType.ANCESTOR: ["祖先祭祀", "族谱记录", "口述历史"],
            FaithType.NATURE: ["自然崇拜", "季节庆典", "动物图腾"],
            FaithType.COMMUNITY: ["集体决策", "资源共享", "互助传统"],
            FaithType.TECHNOLOGY: ["工艺传承", "技术创新", "工具崇拜"],
            FaithType.SPIRITUAL: ["冥想修行", "占卜预测", "灵魂沟通"],
            FaithType.TRADITION: ["礼仪规范", "代际传承", "习俗遵守"]
        }
        
        return random.sample(traditions_map.get(faith_type, []), 
                           min(2, len(traditions_map.get(faith_type, []))))
        
    def _generate_cultural_values(self, faith_type: FaithType) -> List[CulturalTrait]:
        """生成与文化价值观"""
        values_map = {
            FaithType.ANCESTOR: [CulturalTrait.CONSERVATIVE, CulturalTrait.SPIRITUAL],
            FaithType.NATURE: [CulturalTrait.COOPERATIVE, CulturalTrait.SPIRITUAL],
            FaithType.COMMUNITY: [CulturalTrait.COOPERATIVE, CulturalTrait.CONSERVATIVE],
            FaithType.TECHNOLOGY: [CulturalTrait.INNOVATIVE, CulturalTrait.MATERIALISTIC],
            FaithType.SPIRITUAL: [CulturalTrait.SPIRITUAL, CulturalTrait.CONSERVATIVE],
            FaithType.TRADITION: [CulturalTrait.CONSERVATIVE, CulturalTrait.COOPERATIVE]
        }
        
        return values_map.get(faith_type, [CulturalTrait.COOPERATIVE])
        
    def update_faith_influences(self, agents: List['Agent']) -> None:
        """更新所有agent之间的信仰影响"""
        # 传播信仰
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents[i+1:], i+1):
                distance = math.sqrt((agent1.x - agent2.x)**2 + (agent1.y - agent2.y)**2)
                
                # 信仰传播
                self.cultural_spread.spread_faith_between_agents(agent1, agent2, distance)
                self.cultural_spread.spread_cultural_traits(agent1, agent2, distance)
                
        # 部落内信仰统一
        # 这里需要传入部落信息，暂时留空
        
    def get_faith_statistics(self, agents: List['Agent']) -> Dict:
        """获取信仰统计信息"""
        stats = {
            'total_agents': len(agents),
            'agents_with_faith': 0,
            'faith_distribution': {},
            'cultural_trait_distribution': {}
        }
        
        # 统计信仰分布
        for agent in agents:
            if agent.faith:
                stats['agents_with_faith'] += 1
                
                faith_type = agent.faith.faith_type.value
                stats['faith_distribution'][faith_type] = stats['faith_distribution'].get(faith_type, 0) + 1
                
                # 统计文化特征分布
                for trait in agent.faith.values:
                    trait_name = trait.value
                    stats['cultural_trait_distribution'][trait_name] = stats['cultural_trait_distribution'].get(trait_name, 0) + 1
                    
        # 计算百分比
        if stats['total_agents'] > 0:
            stats['faith_percentage'] = (stats['agents_with_faith'] / stats['total_agents']) * 100
        else:
            stats['faith_percentage'] = 0
            
        return stats