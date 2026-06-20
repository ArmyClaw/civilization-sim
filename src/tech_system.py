"""
科技系统模块 - 实现基于人口/资源/时间的科技发现机制
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
import random
import json
from dataclasses import dataclass


class Era(Enum):
    """文明时代枚举"""
    PALEOLITHIC = "paleolithic"        # 石器时代
    NEOLITHIC = "neolithic"           # 新石器时代
    METALWORKING = "metalworking"      # 冶金时代
    INDUSTRIAL = "industrial"         # 工业时代
    INFORMATION = "information"       # 信息时代


class ResourceType(Enum):
    """资源类型枚举"""
    FOOD = "food"
    WATER = "water"
    WOOD = "wood"
    MINERAL = "mineral"


@dataclass
class TechEffect:
    """科技效果数据类"""
    economic_bonus: float = 0.0
    military_bonus: float = 0.0
    social_bonus: float = 0.0
    cultural_bonus: float = 0.0
    population_capacity: int = 0
    production_efficiency: float = 0.0
    trade_efficiency: float = 0.0


@dataclass
class TechNode:
    """科技节点类"""
    id: str
    name: str
    description: str
    era: Era
    cost: int
    prerequisites: List[str]
    effects: TechEffect
    is_completed: bool = False
    is_researching: bool = False
    progress: float = 0.0
    
    def can_research(self, completed_techs: Set[str]) -> bool:
        """检查是否可以研究此科技"""
        if self.is_completed:
            return False
        # 检查前置科技
        for prereq in self.prerequisites:
            if prereq not in completed_techs:
                return False
        return True
    
    def start_research(self):
        """开始研究"""
        self.is_researching = True
        self.progress = 0.0
    
    def add_progress(self, amount: float):
        """添加研究进度"""
        self.progress = min(100.0, self.progress + amount)
        if self.progress >= 100.0:
            self.complete()
    
    def complete(self):
        """完成研究"""
        self.is_completed = True
        self.is_researching = False
        self.progress = 100.0


class TechTree:
    """科技树系统类"""
    
    def __init__(self):
        self.technologies: Dict[str, TechNode] = {}
        self.completed_techs: Set[str] = set()
        self.current_era = Era.PALEOLITHIC
        self.tech_points = 0
        self.research_rate = 1.0
        self.population = 0
        self.resources: Dict[ResourceType, int] = {}
        self.cultural_value = 0
        self.trade_value = 0
        
        self._initialize_tech_tree()
    
    def _initialize_tech_tree(self):
        """初始化科技树结构"""
        # 石器时代科技
        self.technologies["fire_control"] = TechNode(
            id="fire_control",
            name="🔥 火的控制",
            description="掌握火的使用，提供烹饪和防御能力",
            era=Era.PALEOLITHIC,
            cost=15,
            prerequisites=[],
            effects=TechEffect(
                economic_bonus=0.2,
                military_bonus=0.1,
                social_bonus=0.1,
                population_capacity=5
            )
        )
        
        self.technologies["stone_tools"] = TechNode(
            id="stone_tools",
            name="🛠️ 石器制作",
            description="制作和使用石器工具，提高采集效率",
            era=Era.PALEOLITHIC,
            cost=10,
            prerequisites=[],
            effects=TechEffect(
                production_efficiency=0.3,
                economic_bonus=0.25
            )
        )
        
        self.technologies["basic_construction"] = TechNode(
            id="basic_construction",
            name="🏠 基础建造",
            description="建造基础住所，提高营地防御和容量",
            era=Era.PALEOLITHIC,
            cost=20,
            prerequisites=["fire_control"],
            effects=TechEffect(
                military_bonus=0.4,
                population_capacity=5
            )
        )
        
        self.technologies["language"] = TechNode(
            id="language",
            name="🌐 语言与沟通",
            description="发展语言系统，提高协作效率",
            era=Era.PALEOLITHIC,
            cost=15,
            prerequisites=["fire_control"],
            effects=TechEffect(
                social_bonus=0.35,
                trade_efficiency=0.5
            )
        )
        
        # 新石器时代科技
        self.technologies["agriculture"] = TechNode(
            id="agriculture",
            name="🌾 农业革命",
            description="发展农业，实现食物稳定生产",
            era=Era.NEOLITHIC,
            cost=50,
            prerequisites=["stone_tools"],
            effects=TechEffect(
                economic_bonus=2.0,
                population_capacity=50,
                production_efficiency=0.8
            )
        )
        
        self.technologies["pottery"] = TechNode(
            id="pottery",
            name="🏺 陶器制作",
            description="制作陶器，提高食物储存能力",
            era=Era.NEOLITHIC,
            cost=25,
            prerequisites=["fire_control"],
            effects=TechEffect(
                economic_bonus=0.6,
                cultural_bonus=0.25
            )
        )
        
        self.technologies["specialization"] = TechNode(
            id="specialization",
            name="👨‍🌾 专业分工",
            description="社会专业分工，提高生产效率",
            era=Era.NEOLITHIC,
            cost=30,
            prerequisites=["agriculture", "language"],
            effects=TechEffect(
                production_efficiency=0.45,
                social_bonus=0.3
            )
        )
        
        self.technologies["tribal_organization"] = TechNode(
            id="tribal_organization",
            name="🏛️ 部落组织",
            description="形成部落组织结构，提高管理效率",
            era=Era.NEOLITHIC,
            cost=40,
            prerequisites=["specialization", "basic_construction"],
            effects=TechEffect(
                social_bonus=0.4,
                military_bonus=-0.3  # 减少冲突
            )
        )
        
        # 冶金时代科技
        self.technologies["bronze_working"] = TechNode(
            id="bronze_working",
            name="⚒️ 青铜冶炼",
            description="掌握青铜冶炼技术，制造更好的工具和武器",
            era=Era.METALWORKING,
            cost=60,
            prerequisites=["agriculture", "pottery"],
            effects=TechEffect(
                military_bonus=0.6,
                economic_bonus=0.8,
                production_efficiency=0.8
            )
        )
        
        self.technologies["urbanization"] = TechNode(
            id="urbanization",
            name="🏙️ 城市建设",
            description="发展城市，增加人口容量和经济中心",
            era=Era.METALWORKING,
            cost=80,
            prerequisites=["tribal_organization", "specialization"],
            effects=TechEffect(
                population_capacity=200,
                economic_bonus=1.5
            )
        )
        
        self.technologies["writing"] = TechNode(
            id="writing",
            name="📜 文字系统",
            description="发明文字，增强知识积累和文化传承",
            era=Era.METALWORKING,
            cost=50,
            prerequisites=["language", "pottery"],
            effects=TechEffect(
                cultural_bonus=1.0,
                economic_bonus=0.5,
                trade_efficiency=0.8
            )
        )
        
        self.technologies["trade_networks"] = TechNode(
            id="trade_networks",
            name="🛒 贸易网络",
            description="建立贸易网络，促进资源交换",
            era=Era.METALWORKING,
            cost=70,
            prerequisites=["writing", "urbanization"],
            effects=TechEffect(
                trade_efficiency=2.0,
                economic_bonus=0.7
            )
        )
        
        # 工业时代科技
        self.technologies["steam_power"] = TechNode(
            id="steam_power",
            name="🔧 蒸汽动力",
            description="蒸汽机发明，引发工业革命",
            era=Era.INDUSTRIAL,
            cost=100,
            prerequisites=["bronze_working", "writing"],
            effects=TechEffect(
                production_efficiency=5.0,
                economic_bonus=3.0
            )
        )
        
        self.technologies["factory_system"] = TechNode(
            id="factory_system",
            name="🏭 工厂体系",
            description="建立工厂，实现大规模生产",
            era=Era.INDUSTRIAL,
            cost=120,
            prerequisites=["steam_power", "urbanization"],
            effects=TechEffect(
                production_efficiency=8.0,
                economic_bonus=2.0
            )
        )
        
        self.technologies["railway"] = TechNode(
            id="railway",
            name="🚂 铁路运输",
            description="建设铁路系统，提高运输效率",
            era=Era.INDUSTRIAL,
            cost=90,
            prerequisites=["steam_power", "trade_networks"],
            effects=TechEffect(
                trade_efficiency=4.0,
                economic_bonus=0.7
            )
        )
        
        self.technologies["electricity"] = TechNode(
            id="electricity",
            name="⚡ 电力系统",
            description="建立电力系统，开启现代工业",
            era=Era.INDUSTRIAL,
            cost=110,
            prerequisites=["factory_system", "railway"],
            effects=TechEffect(
                production_efficiency=3.0,
                economic_bonus=1.5
            )
        )
        
        # 信息时代科技
        self.technologies["computing"] = TechNode(
            id="computing",
            name="💻 计算机技术",
            description="发明计算机，开启信息时代",
            era=Era.INFORMATION,
            cost=150,
            prerequisites=["electricity", "writing"],
            effects=TechEffect(
                economic_bonus=5.0,
                production_efficiency=10.0,
                cultural_bonus=1.5
            )
        )
        
        self.technologies["internet"] = TechNode(
            id="internet",
            name="🌐 互联网",
            description="建立全球互联网，实现信息共享",
            era=Era.INFORMATION,
            cost=200,
            prerequisites=["computing", "railway"],
            effects=TechEffect(
                trade_efficiency=10.0,
                cultural_bonus=2.0,
                economic_bonus=3.0
            )
        )
        
        self.technologies["ai"] = TechNode(
            id="ai",
            name="🤖 人工智能",
            description="发展人工智能技术，提高决策效率",
            era=Era.INFORMATION,
            cost=250,
            prerequisites=["computing", "internet"],
            effects=TechEffect(
                economic_bonus=8.0,
                production_efficiency=6.0
            )
        )
        
        self.technologies["biotechnology"] = TechNode(
            id="biotechnology",
            name="🧬 生物技术",
            description="掌握生物技术，改善医疗和农业",
            era=Era.INFORMATION,
            cost=180,
            prerequisites=["computing", "electricity"],
            effects=TechEffect(
                economic_bonus=2.0,
                population_capacity=100
            )
        )
    
    def update_stats(self, population: int, resources: Dict[ResourceType, int], 
                    cultural_value: int, trade_value: int):
        """更新文明统计信息"""
        self.population = population
        self.resources = resources.copy()
        self.cultural_value = cultural_value
        self.trade_value = trade_value
        
        # 根据时代和研究进度调整研究速率
        era_multiplier = {
            Era.PALEOLITHIC: 0.5,
            Era.NEOLITHIC: 1.0,
            Era.METALWORKING: 1.5,
            Era.INDUSTRIAL: 2.0,
            Era.INFORMATION: 3.0
        }
        
        self.research_rate = era_multiplier[self.current_era]
        
        # 资源加成
        resource_multiplier = 1.0
        if resources.get(ResourceType.MINERAL, 0) > 100:
            resource_multiplier += 0.3
        if resources.get(ResourceType.WOOD, 0) > 200:
            resource_multiplier += 0.2
            
        self.research_rate *= resource_multiplier
    
    def calculate_tech_points(self) -> int:
        """计算获得的科技点数"""
        base_points = 0
        
        # 人口贡献: 每增加1人口 = 1科技点
        base_points += self.population
        
        # 经济贡献: GDP每增长10% = 2科技点 (简化计算)
        trade_value_points = int(self.trade_value / 10) * 2
        base_points += trade_value_points
        
        # 文化贡献: 文化值每增长100 = 1科技点
        cultural_points = int(self.cultural_value / 100)
        base_points += cultural_points
        
        # 资源贡献
        resource_points = sum(self.resources.values()) // 50
        base_points += resource_points
        
        # 时代加成
        era_bonus = {
            Era.PALEOLITHIC: 1.0,
            Era.NEOLITHIC: 1.2,
            Era.METALWORKING: 1.5,
            Era.INDUSTRIAL: 2.0,
            Era.INFORMATION: 3.0
        }
        
        return int(base_points * era_bonus[self.current_era])
    
    def generate_discovery_probability(self) -> Dict[str, float]:
        """生成各科技发现概率"""
        probabilities = {}
        
        for tech_id, tech in self.technologies.items():
            if not tech.can_research(self.completed_techs):
                continue
                
            # 基础概率
            base_prob = 0.1
            
            # 人口加成
            pop_bonus = min(self.population * 0.01, 0.3)
            
            # 资源加成
            resource_bonus = sum(self.resources.values()) * 0.001
            resource_bonus = min(resource_bonus, 0.2)
            
            # 文化加成
            culture_bonus = min(self.cultural_value * 0.0005, 0.15)
            
            # 时代进度加成
            progress_bonus = len(self.completed_techs) * 0.02
            progress_bonus = min(progress_bonus, 0.25)
            
            # 综合概率
            total_prob = base_prob + pop_bonus + resource_bonus + culture_bonus + progress_bonus
            total_prob = min(total_prob, 0.8)  # 最高80%概率
            
            probabilities[tech_id] = total_prob
        
        return probabilities
    
    def discover_technology(self, tech_id: str) -> bool:
        """尝试发现指定科技"""
        if tech_id not in self.technologies:
            return False
            
        tech = self.technologies[tech_id]
        if not tech.can_research(self.completed_techs):
            return False
            
        # 消耗科技点数
        if self.tech_points >= tech.cost:
            self.tech_points -= tech.cost
            tech.complete()
            self.completed_techs.add(tech_id)
            
            # 检查时代变迁
            self._check_era_progression()
            
            return True
        
        return False
    
    def auto_discover(self) -> List[str]:
        """自动发现科技（基于概率）"""
        discovered = []
        probabilities = self.generate_discovery_probability()
        
        for tech_id, prob in probabilities.items():
            if random.random() < prob:
                if self.discover_technology(tech_id):
                    discovered.append(tech_id)
        
        return discovered
    
    def _check_era_progression(self):
        """检查时代变迁"""
        completed_in_era = {}
        
        for tech_id, tech in self.technologies.items():
            if tech.is_completed:
                if tech.era not in completed_in_era:
                    completed_in_era[tech.era] = 0
                completed_in_era[tech.era] += 1
        
        # 石器时代 -> 新石器时代：完成2个石器时代科技
        if (self.current_era == Era.PALEOLITHIC and 
            completed_in_era.get(Era.PALEOLITHIC, 0) >= 2):
            self.current_era = Era.NEOLITHIC
        
        # 新石器时代 -> 冶金时代：完成3个新石器时代科技
        elif (self.current_era == Era.NEOLITHIC and 
              completed_in_era.get(Era.NEOLITHIC, 0) >= 3):
            self.current_era = Era.METALWORKING
        
        # 冶金时代 -> 工业时代：完成4个冶金时代科技
        elif (self.current_era == Era.METALWORKING and 
              completed_in_era.get(Era.METALWORKING, 0) >= 4):
            self.current_era = Era.INDUSTRIAL
        
        # 工业时代 -> 信息时代：完成3个工业时代科技
        elif (self.current_era == Era.INDUSTRIAL and 
              completed_in_era.get(Era.INDUSTRIAL, 0) >= 3):
            self.current_era = Era.INFORMATION
    
    def get_available_techs(self) -> List[str]:
        """获取可研究的科技列表"""
        return [tech_id for tech_id, tech in self.technologies.items() 
                if tech.can_research(self.completed_techs)]
    
    def get_research_progress(self) -> Dict[str, float]:
        """获取所有科技的研究进度"""
        return {tech_id: tech.progress for tech_id, tech in self.technologies.items()}
    
    def get_completed_techs_in_era(self, era: Era) -> List[str]:
        """获取指定时代已完成的科技"""
        return [tech_id for tech_id, tech in self.technologies.items() 
                if tech.era == era and tech.is_completed]
    
    def get_total_effects(self) -> TechEffect:
        """获取所有已完成科技的累计效果"""
        total_effects = TechEffect()
        
        for tech_id in self.completed_techs:
            if tech_id in self.technologies:
                tech = self.technologies[tech_id]
                total_effects.economic_bonus += tech.effects.economic_bonus
                total_effects.military_bonus += tech.effects.military_bonus
                total_effects.social_bonus += tech.effects.social_bonus
                total_effects.cultural_bonus += tech.effects.cultural_bonus
                total_effects.population_capacity += tech.effects.population_capacity
                total_effects.production_efficiency += tech.effects.production_efficiency
                total_effects.trade_efficiency += tech.effects.trade_efficiency
        
        return total_effects
    
    def save_state(self) -> Dict:
        """保存科技树状态"""
        return {
            "completed_techs": list(self.completed_techs),
            "current_era": self.current_era.value,
            "tech_points": self.tech_points,
            "research_rate": self.research_rate,
            "population": self.population,
            "resources": {r.value: v for r, v in self.resources.items()},
            "cultural_value": self.cultural_value,
            "trade_value": self.trade_value,
            "tech_progress": {tech_id: tech.progress for tech_id, tech in self.technologies.items()}
        }
    
    def load_state(self, state: Dict):
        """加载科技树状态"""
        self.completed_techs = set(state.get("completed_techs", []))
        self.current_era = Era(state.get("current_era", Era.PALEOLITHIC.value))
        self.tech_points = state.get("tech_points", 0)
        self.research_rate = state.get("research_rate", 1.0)
        self.population = state.get("population", 0)
        self.cultural_value = state.get("cultural_value", 0)
        self.trade_value = state.get("trade_value", 0)
        
        # 恢复资源
        resources_dict = state.get("resources", {})
        self.resources = {ResourceType(k): v for k, v in resources_dict.items()}
        
        # 恢复研究进度
        tech_progress = state.get("tech_progress", {})
        for tech_id, progress in tech_progress.items():
            if tech_id in self.technologies:
                tech = self.technologies[tech_id]
                tech.progress = progress
                if progress >= 100.0:
                    tech.is_completed = True
                    tech.is_researching = False
                elif progress > 0.0:
                    tech.is_researching = True