"""
部落系统模块
实现基于地理距离和社会关系的部落聚类算法
"""

from typing import List, Dict, Set, Tuple, Optional
import math
import random
from collections import defaultdict
from agent import Agent, Profession
from terrain import Tile


class Tribe:
    """部落类"""
    
    def __init__(self, tribe_id: int, name: str, founder: Agent):
        self.id = tribe_id
        self.name = name
        self.founder = founder
        self.members: Set[Agent] = {founder}
        self.territory: Set[Tuple[int, int]] = set()
        self.resources: Dict[str, int] = defaultdict(int)
        self.leader = founder
        self.established_at = 0
        
    def add_member(self, agent: Agent):
        """添加成员到部落"""
        self.members.add(agent)
        
    def remove_member(self, agent: Agent):
        """从部落移除成员"""
        self.members.discard(agent)
        
    def update_territory(self):
        """更新部落领土（所有成员周围的区域）"""
        self.territory.clear()
        for member in self.members:
            # 获取成员周围的3x3区域
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x, y = member.x + dx, member.y + dy
                    self.territory.add((x, y))
                    
    def get_population(self) -> int:
        """获取人口数量"""
        return len(self.members)
        
    def get_resource_summary(self) -> Dict[str, int]:
        """获取资源汇总"""
        summary = defaultdict(int)
        for member in self.members:
            for resource_type, amount in member.inventory.items():
                summary[str(resource_type.value)] += amount
        return dict(summary)


class TribeFormation:
    """部落形成算法"""
    
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.tribes: List[Tribe] = []
        self.next_tribe_id = 1
        
    def calculate_geographic_distance(self, agent1: Agent, agent2: Agent) -> float:
        """计算两个Agent之间的地理距离"""
        dx = agent1.x - agent2.x
        dy = agent1.y - agent2.y
        return math.sqrt(dx * dx + dy * dy)
        
    def calculate_social_similarity(self, agent1: Agent, agent2: Agent) -> float:
        """计算两个Agent之间的社会相似度（0-1之间）"""
        similarity_score = 0.0
        factors = 0
        
        # 职业相似度
        if agent1.profession == agent2.profession:
            similarity_score += 0.3
        factors += 1
        
        # 资源拥有相似度
        total_resources1 = sum(agent1.inventory.values())
        total_resources2 = sum(agent2.inventory.values())
        
        if total_resources1 > 0 and total_resources2 > 0:
            resource_similarity = 0
            for resource_type in agent1.inventory:
                if resource_type in agent2.inventory:
                    resource_similarity += min(agent1.inventory[resource_type], 
                                             agent2.inventory[resource_type])
            resource_similarity = resource_similarity / (total_resources1 + total_resources2)
            similarity_score += resource_similarity * 0.3
            factors += 0.3
            
        # 交易历史相似度（如果有交易记录）
        if hasattr(agent1, 'trade_partners') and hasattr(agent2, 'trade_partners'):
            common_partners = len(set(agent1.trade_partners) & set(agent2.trade_partners))
            total_partners = len(set(agent1.trade_partners + agent2.trade_partners))
            if total_partners > 0:
                trade_similarity = common_partners / total_partners
                similarity_score += trade_similarity * 0.4
                factors += 0.4
                
        return similarity_score / factors if factors > 0 else 0.0
        
    def form_tribes_geographic(self, max_distance: float = 5.0) -> List[Tribe]:
        """基于地理距离的部落形成"""
        tribes = []
        unassigned_agents = set(self.agents)
        tribe_id = 1
        
        while unassigned_agents:
            # 随机选择一个未分配的Agent作为部落创始人
            founder = random.choice(list(unassigned_agents))
            tribe = Tribe(tribe_id, f"部落{tribe_id}", founder)
            tribes.append(tribe)
            tribe_id += 1
            
            unassigned_agents.remove(founder)
            
            # 查找附近的Agent
            changed = True
            while changed and unassigned_agents:
                changed = False
                new_members = []
                
                for agent in unassigned_agents:
                    # 计算与部落现有成员的平均距离
                    min_distance = float('inf')
                    for member in tribe.members:
                        distance = self.calculate_geographic_distance(agent, member)
                        min_distance = min(min_distance, distance)
                    
                    # 如果距离足够近，加入部落
                    if min_distance <= max_distance:
                        new_members.append(agent)
                        changed = True
                
                # 添加新成员
                for agent in new_members:
                    tribe.add_member(agent)
                    unassigned_agents.remove(agent)
                    
        return tribes
        
    def form_tribes_social(self, similarity_threshold: float = 0.5) -> List[Tribe]:
        """基于社会关系的部落形成"""
        tribes = []
        unassigned_agents = set(self.agents)
        tribe_id = 1
        
        while unassigned_agents:
            # 选择社会相似度最高的Agent作为创始人
            founder = max(unassigned_agents, 
                         key=lambda a: sum(self.calculate_social_similarity(a, other) 
                                         for other in unassigned_agents if other != a))
            
            tribe = Tribe(tribe_id, f"社会部落{tribe_id}", founder)
            tribes.append(tribe)
            tribe_id += 1
            
            unassigned_agents.remove(founder)
            
            # 查找社会相似的Agent
            changed = True
            while changed and unassigned_agents:
                changed = False
                new_members = []
                
                for agent in unassigned_agents:
                    # 计算与部落现有成员的平均社会相似度
                    avg_similarity = sum(self.calculate_social_similarity(agent, member) 
                                       for member in tribe.members) / len(tribe.members)
                    
                    # 如果社会相似度足够高，加入部落
                    if avg_similarity >= similarity_threshold:
                        new_members.append(agent)
                        changed = True
                
                # 添加新成员
                for agent in new_members:
                    tribe.add_member(agent)
                    unassigned_agents.remove(agent)
                    
        return tribes
        
    def form_tribes_hybrid(self, geo_distance: float = 5.0, 
                         social_threshold: float = 0.4,
                         geo_weight: float = 0.6) -> List[Tribe]:
        """混合地理距离和社会关系的部落形成算法"""
        tribes = []
        unassigned_agents = set(self.agents)
        tribe_id = 1
        
        while unassigned_agents:
            # 找到最适合的创始人（考虑地理和社会因素）
            best_founder = None
            best_score = -1
            
            for agent in unassigned_agents:
                # 计算该Agent作为创始人的潜力得分
                geo_score = sum(1 for other in unassigned_agents 
                              if other != agent and 
                              self.calculate_geographic_distance(agent, other) <= geo_distance)
                
                social_score = sum(self.calculate_social_similarity(agent, other) 
                                 for other in unassigned_agents if other != agent)
                
                total_score = geo_score * geo_weight + social_score * (1 - geo_weight)
                
                if total_score > best_score:
                    best_score = total_score
                    best_founder = agent
            
            if best_founder is None:
                break
                
            tribe = Tribe(tribe_id, f"混合部落{tribe_id}", best_founder)
            tribes.append(tribe)
            tribe_id += 1
            
            unassigned_agents.remove(best_founder)
            
            # 动态添加成员
            changed = True
            while changed and unassigned_agents:
                changed = False
                new_members = []
                
                for agent in unassigned_agents:
                    # 计算与部落的综合得分
                    geo_score = sum(1 for member in tribe.members 
                                  if self.calculate_geographic_distance(agent, member) <= geo_distance)
                    
                    social_score = sum(self.calculate_social_similarity(agent, member) 
                                     for member in tribe.members)
                    
                    total_score = geo_score * geo_weight + social_score * (1 - geo_weight)
                    
                    # 如果综合得分足够高，加入部落
                    if total_score >= geo_weight + (1 - geo_weight) * social_threshold:
                        new_members.append(agent)
                        changed = True
                
                # 添加新成员
                for agent in new_members:
                    tribe.add_member(agent)
                    unassigned_agents.remove(agent)
                    
        return tribes
        
    def optimize_tribes(self, tribes: List[Tribe], max_iterations: int = 100) -> List[Tribe]:
        """优化部落划分，提高同质性和紧密性"""
        for iteration in range(max_iterations):
            improved = False
            
            for tribe in tribes:
                # 尝试移动边缘成员
                members_to_check = list(tribe.members)
                
                for member in members_to_check:
                    # 计算该成员在当前部落的归属感
                    current_tribe_score = self._calculate_tribe_belonging_score(member, tribe)
                    
                    # 计算在其他部落的归属感
                    best_other_score = 0
                    best_other_tribe = None
                    
                    for other_tribe in tribes:
                        if other_tribe != tribe and member in other_tribe.members:
                            continue
                            
                        other_score = self._calculate_tribe_belonging_score(member, other_tribe)
                        if other_score > best_other_score:
                            best_other_score = other_score
                            best_other_tribe = other_tribe
                    
                    # 如果有更好的归属选择，则移动
                    if best_other_score > current_tribe_score:
                        tribe.remove_member(member)
                        best_other_tribe.add_member(member)
                        improved = True
                        
            if not improved:
                break
                
        return tribes
        
    def _calculate_tribe_belonging_score(self, agent: Agent, tribe: Tribe) -> float:
        """计算Agent对部落的归属感得分"""
        if not tribe.members:
            return 0
            
        # 地理距离得分
        geo_distances = [self.calculate_geographic_distance(agent, member) 
                        for member in tribe.members if member != agent]
        avg_geo_distance = sum(geo_distances) / len(geo_distances) if geo_distances else 0
        geo_score = max(0, 1 - avg_geo_distance / 10)  # 距离越近得分越高
        
        # 社会相似度得分
        social_scores = [self.calculate_social_similarity(agent, member) 
                        for member in tribe.members if member != agent]
        avg_social_score = sum(social_scores) / len(social_scores) if social_scores else 0
        
        # 综合得分
        return (geo_score * 0.5 + avg_social_score * 0.5)
        
    def analyze_tribe_distribution(self, tribes: List[Tribe]) -> Dict:
        """分析部落分布情况"""
        analysis = {
            'total_tribes': len(tribes),
            'total_population': len(self.agents),
            'average_population': len(self.agents) / len(tribes) if tribes else 0,
            'tribe_sizes': [tribe.get_population() for tribe in tribes],
            'resource_distribution': {}
        }
        
        # 计算资源分布
        for tribe in tribes:
            tribe.update_territory()
            resources = tribe.get_resource_summary()
            tribe_id = tribe.id
            analysis['resource_distribution'][f'tribe_{tribe_id}'] = resources
            
        return analysis