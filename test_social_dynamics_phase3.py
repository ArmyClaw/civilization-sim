#!/usr/bin/env python3
"""
社会动态演化系统测试 - Phase 3
测试部落形成、贸易网络、冲突解决、文化演化等社会系统
"""

import sys
import os
import random
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.tribe_system import TribeFormation
from src.agent import Agent, Profession, ResourceType
from src.terrain import Tile, TerrainType, Map
from src.generator import TerrainGenerator, ResourceGenerator
from src.trading_system import TradingEngine
from src.conflict_system import ConflictSystem
from src.faith_system import FaithManager
from src.currency_system import CurrencyEconomy
from src.economy import Economy

class SocialDynamicsTester:
    """社会动态测试器"""
    
    def __init__(self, width: int = 20, height: int = 20, agent_count: int = 30):
        self.width = width
        self.height = height
        self.agent_count = agent_count
        self.world_map = None
        self.agents = []
        self.tribes = []
        self.economy_manager = Economy()
        self.trading_manager = TradingEngine(None)
        self.conflict_manager = ConflictSystem([])  # Will be updated after tribes are formed
        self.faith_manager = FaithManager()
        self.currency_manager = CurrencyEconomy(self.economy_manager)
        
    def create_test_environment(self):
        """创建测试环境"""
        print("=== 创建社会动态测试环境 ===")
        
        # 创建地图
        self.world_map = Map(self.width, self.height)
        
        # 生成地形
        terrain_gen = TerrainGenerator(self.world_map)
        terrain_gen.generate_terrain()
        
        # 生成资源
        resource_gen = ResourceGenerator(self.world_map)
        resource_gen.distribute_resources()
        
        # 创建Agent
        self.agents = []
        professions = list(Profession)
        
        for i in range(self.agent_count):
            # 随机选择非水域位置
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                tile = self.world_map.grid[y][x]
                if tile.terrain_type != TerrainType.WATER:
                    break
            
            profession = random.choice(professions)
            agent = Agent(i, x, y, tile, profession)
            
            # 设置初始资源
            agent.inventory[ResourceType.FOOD] = random.randint(8, 20)
            agent.inventory[ResourceType.WATER] = random.randint(8, 20)
            agent.inventory[ResourceType.WOOD] = random.randint(3, 12)
            agent.inventory[ResourceType.MINERAL] = random.randint(1, 8)
            
            # 设置社会属性
            agent.social_network = {}
            agent.reputation = random.uniform(0.3, 0.9)
            agent.cooperation_level = random.uniform(0.2, 0.8)
            agent.aggression_level = random.uniform(0.1, 0.7)
            
            # 设置健康状态
            agent.health = random.randint(70, 100)
            agent.energy = random.randint(60, 100)
            agent.hunger = random.randint(10, 30)
            agent.thirst = random.randint(10, 30)
            agent.max_inventory = 25
            
            self.agents.append(agent)
        
        print(f"创建了{len(self.agents)}个社会个体")
        print(f"地图尺寸: {self.width}x{self.height}")
        return self.world_map, self.agents
    
    def test_formation_and_tribal_systems(self):
        """测试1: 部落形成和社会组织系统"""
        print("\n=== 测试部落形成和社会组织系统 ===")
        
        # 测试多种部落形成算法
        print("\n1. 基于地理位置的部落形成:")
        geo_formation = TribeFormation(self.agents)
        self.tribes = geo_formation.form_tribes_hybrid(
            geo_distance=3.0, 
            social_threshold=0.4
        )
        print(f"形成了{len(self.tribes)}个地理部落")
        
        for i, tribe in enumerate(self.tribes[:3]):  # 显示前3个部落
            print(f"  部落{i+1}: {len(tribe.members)}人")
            professions = {}
            for agent in tribe.members:
                prof = agent.profession.value
                professions[prof] = professions.get(prof, 0) + 1
            print(f"    职业分布: {professions}")
            
            # 计算部落的凝聚力
            avg_cooperation = sum(a.cooperation_level for a in tribe.members) / len(tribe.members)
            avg_reputation = sum(a.reputation for a in tribe.members) / len(tribe.members)
            print(f"    凝聚力: {avg_cooperation:.2f}, 声望: {avg_reputation:.2f}")
        
        # 测试社会网络分析
        print("\n2. 社会网络分析:")
        self.analyze_social_networks()
        
        return self.tribes
    
    def test_economic_interactions(self):
        """测试2: 经济交互和贸易网络"""
        print("\n=== 测试经济交互和贸易网络 ===")
        
        # 为每个部落分配初始资源
        for tribe in self.tribes:
            tribe_resources = {
                ResourceType.FOOD: random.randint(50, 150),
                ResourceType.WATER: random.randint(50, 150),
                ResourceType.WOOD: random.randint(20, 80),
                ResourceType.MINERAL: random.randint(10, 40)
            }
            # 添加到部落任意一个成员（members是set）
            first_agent = next(iter(tribe.members)) if tribe.members else None
            for resource, amount in tribe_resources.items():
                first_agent.inventory[resource] += amount
        
        # 测试部落间贸易
        print("\n1. 部落间贸易网络:")
        successful_trades = 0
        trade_pairs = []
        
        # 选择贸易活跃的部落对
        active_tribes = [t for t in self.tribes if len(t.members) >= 3]
        for i in range(min(5, len(active_tribes))):
            for j in range(i+1, min(i+3, len(active_tribes))):
                tribe1, tribe2 = active_tribes[i], active_tribes[j]
                
                # 模拟贸易
                trade_result = self.trading_manager.inter_tribe_trade(
                    tribe1, tribe2, max_trades=3
                )
                
                if trade_result['success']:
                    successful_trades += 1
                    trade_pairs.append((tribe1, tribe2))
                    print(f"    部落{i+1} ↔ 部落{j+1}: {trade_result['details']}")
                else:
                    print(f"    部落{i+1} ↔ 部落{j+1}: 贸易失败 - {trade_result['reason']}")
        
        print(f"\n成功贸易次数: {successful_trades}")
        
        # 测试货币系统
        print("\n2. 货币和经济演化:")
        # 简化货币测试
        self.test_simple_currency_system()
        
        # 测试市场形成
        print("\n3. 市场形成分析:")
        self.analyze_market_formation()
        
        return successful_trades
    
    def test_conflict_resolution(self):
        """测试3: 冲突解决机制"""
        print("\n=== 测试冲突解决机制 ===")
        
        # 测试不同类型的冲突
        conflict_types = ['资源争夺', '领土冲突', '文化差异', '贸易纠纷']
        
        for conflict_type in conflict_types:
            print(f"\n{conflict_type}冲突测试:")
            
            # 随机选择两个有冲突倾向的部落
            aggressive_tribes = [t for t in self.tribes if len(t.members) >= 2]
            if len(aggressive_tribes) >= 2:
                tribe1, tribe2 = random.sample(aggressive_tribes, 2)
                
                # 模拟冲突
                conflict_result = self.conflict_manager.resolve_conflict(
                    tribe1, tribe2, conflict_type
                )
                
                print(f"  冲突类型: {conflict_type}")
                print(f"  参与方: 部落1({len(tribe1.members)}人) vs 部落2({len(tribe2.members)}人)")
                print(f"  解决方式: {conflict_result['method']}")
                print(f"  结果: {conflict_result['outcome']}")
                print(f"  损失评估: {conflict_result['costs']}")
                
                # 记录冲突历史
                for agent in tribe1.members + tribe2.members:
                    agent.conflict_history = agent.conflict_history or []
                    agent.conflict_history.append({
                        'type': conflict_type,
                        'timestamp': datetime.now(),
                        'result': conflict_result['outcome']
                    })
        
        # 测试冲突后的社会调整
        print("\n冲突后社会调整:")
        self.analyze_post_conflict_adjustment()
        
        return True
    
    def test_cultural_evolution(self):
        """测试4: 文化演化和信仰传播"""
        print("\n=== 测试文化演化和信仰传播 ===")
        
        # 为所有个体生成初始信仰
        for agent in self.agents:
            self.faith_manager.generate_initial_faith(agent)
        
        # 测试信仰传播
        print("\n1. 信仰传播演化:")
        self.test_faith_evolution()
        
        # 测试文化融合
        print("\n2. 文化融合机制:")
        self.test_cultural_syncretism()
        
        # 测试技术传播
        print("\n3. 技术和创新传播:")
        self.test_technology_spread()
        
        return True
    
    def test_social_stability(self):
        """测试5: 社会稳定性分析"""
        print("\n=== 测试社会稳定性分析 ===")
        
        # 分析社会指标
        self.analyze_social_stability_metrics()
        
        # 测试压力测试
        print("\n社会压力测试:")
        self.stress_test_social_system()
        
        # 预测发展趋势
        print("\n社会发展趋势预测:")
        self.predict_social_trends()
        
        return True
    
    def analyze_social_networks(self):
        """分析社会网络结构"""
        print("  社交网络统计:")
        
        # 计算网络密度
        total_possible_connections = len(self.agents) * (len(self.agents) - 1) / 2
        actual_connections = 0
        
        for agent in self.agents:
            connections = len(agent.social_network)
            actual_connections += connections
        
        density = actual_connections / (2 * total_possible_connections) if total_possible_connections > 0 else 0
        print(f"    网络密度: {density:.3f}")
        print(f"    总连接数: {actual_connections}")
        
        # 识别关键节点
        influence_agents = sorted(self.agents, key=lambda a: len(a.social_network), reverse=True)[:5]
        print(f"    最有影响力的个体: {[a.id for a in influence_agents]}")
    
    def test_simple_currency_system(self):
        """简化货币系统测试"""
        print("  简化货币系统测试:")
        
        # 创建初始货币分配
        for i, tribe in enumerate(self.tribes[:3]):  # 前3个部落
            initial_money = random.randint(100, 500)
            first_agent = next(iter(tribe.members)) if tribe.members else None
            if first_agent:
                if not hasattr(first_agent, 'wealth'):
                    first_agent.wealth = 0
                first_agent.wealth = initial_money
            print(f"    部落{i+1}初始货币: {initial_money} 单位")
        
        # 模拟简单经济活动
        economic_cycles = 3
        for cycle in range(economic_cycles):
            print(f"    第{cycle+1}轮经济活动:")
            
            # 部门内经济
            for tribe in self.tribes:
                if len(tribe.members) >= 2:
                    # 简单的资源交换
                    total_wealth = sum(a.wealth if hasattr(a, 'wealth') else 0 for a in tribe.members)
                    avg_wealth = total_wealth / len(tribe.members)
                    print(f"      部门内平均财富: {avg_wealth:.1f} 单位")
            
            # 部门间经济
            if len(self.tribes) >= 2:
                print(f"      部门间经济: 模拟贸易")
    
    def analyze_market_formation(self):
        """分析市场形成情况"""
        print("  市场形成分析:")
        
        # 统计资源分布
        resource_centers = {}
        for tribe in self.tribes:
            # 找到部落的中心位置
            center_x = sum(a.x for a in tribe.members) / len(tribe.members)
            center_y = sum(a.y for a in tribe.members) / len(tribe.members)
            
            # 计算部落总资源
            tribe_resources = {
                ResourceType.FOOD: sum(a.inventory.get(ResourceType.FOOD, 0) for a in tribe.members),
                ResourceType.WATER: sum(a.inventory.get(ResourceType.WATER, 0) for a in tribe.members),
                ResourceType.WOOD: sum(a.inventory.get(ResourceType.WOOD, 0) for a in tribe.members),
                ResourceType.MINERAL: sum(a.inventory.get(ResourceType.MINERAL, 0) for a in tribe.members)
            }
            
            resource_centers[(center_x, center_y)] = tribe_resources
        
        print(f"    形成了{len(resource_centers)}个资源中心")
        
        # 分析贸易路线
        trade_routes = []
        centers = list(resource_centers.keys())
        for i in range(len(centers)):
            for j in range(i+1, len(centers)):
                distance = ((centers[i][0] - centers[j][0])**2 + (centers[i][1] - centers[j][1])**2)**0.5
                if distance < 10:  # 距离较近，可能形成贸易路线
                    trade_routes.append((centers[i], centers[j], distance))
        
        print(f"    可能的贸易路线: {len(trade_routes)}条")
        if trade_routes:
            avg_distance = sum(route[2] for route in trade_routes) / len(trade_routes)
            print(f"    平均路线距离: {avg_distance:.1f}")
    
    def analyze_post_conflict_adjustment(self):
        """分析冲突后的社会调整"""
        print("  冲突后社会调整:")
        
        # 分析社会指标变化
        cooperation_levels = [a.cooperation_level for a in self.agents]
        avg_cooperation = sum(cooperation_levels) / len(cooperation_levels)
        
        reputations = [a.reputation for a in self.agents]
        avg_reputation = sum(reputations) / len(reputations)
        
        print(f"    平均合作水平: {avg_cooperation:.2f}")
        print(f"    平均社会声望: {avg_reputation:.2f}")
        
        # 分析联盟形成
        alliances = self.detect_alliances()
        print(f"    检测到{len(alliances)}个政治联盟")
    
    def test_faith_evolution(self):
        """测试信仰演化"""
        generations = 3
        for generation in range(generations):
            print(f"    第{generation+1}代信仰传播:")
            
            # 执行一轮信仰传播
            self.faith_manager.update_faith_influences(self.agents)
            
            # 统计信仰分布
            faith_stats = self.faith_manager.get_faith_statistics(self.agents)
            print(f"      有信仰比例: {faith_stats['faith_percentage']:.1f}%")
            
            # 显示主要信仰类型
            main_faiths = sorted(faith_stats['faith_distribution'].items(), 
                               key=lambda x: x[1], reverse=True)[:3]
            print(f"      主要信仰: {main_faiths}")
    
    def test_cultural_syncretism(self):
        """测试文化融合"""
        print("  文化融合机制:")
        
        # 找出不同信仰的部落
        faith_tribes = {}
        for tribe in self.tribes:
            tribe_faiths = set()
            for agent in tribe.members:
                if agent.faith:
                    tribe_faiths.add(agent.faith.faith_type)
            
            if tribe_faiths:
                faith_key = tuple(sorted([f.value for f in tribe_faiths]))
                if faith_key not in faith_tribes:
                    faith_tribes[faith_key] = []
                faith_tribes[faith_key].append(tribe)
        
        print(f"    发现{len(faith_tribes)}种文化组合")
        
        # 测试文化融合
        for i, (faith_combo, tribes) in enumerate(faith_tribes.items()):
            if len(tribes) > 1:
                print(f"    文化组合{i+1}: {faith_combo}")
                print(f"    部落数: {len(tribes)}")
                
                # 模拟文化交流（使用部落信仰统一）
                for tribe in tribes:
                    self.faith_manager.cultural_spread.tribe_faith_conversion(list(tribe.members))
                print(f"    文化交流: 执行部落信仰统一化")
    
    def test_technology_spread(self):
        """测试技术传播"""
        print("  技术传播机制:")
        
        # 为部分个体添加技能
        skilled_agents = random.sample(self.agents, min(10, len(self.agents)))
        for agent in skilled_agents:
            agent.skills = {
                "工具制作": random.randint(1, 5),
                "农业技术": random.randint(1, 5),
                "建筑技术": random.randint(1, 5),
                "医疗技术": random.randint(1, 5)
            }
        
        # 技术传播
        tech_generations = 3
        for generation in range(tech_generations):
            print(f"    第{generation+1}代技术传播:")
            
            # 模拟技术传播
            for agent in self.agents:
                if hasattr(agent, 'skills') and agent.skills:
                    # 邻居学习
                    neighbors = self.get_neighbors(agent)
                    for neighbor in neighbors:
                        if not hasattr(neighbor, 'skills'):
                            neighbor.skills = {}
                        
                        # 传授技能
                        for skill, level in agent.skills.items():
                            if skill not in neighbor.skills or neighbor.skills[skill] < level:
                                if random.random() < 0.3:  # 30%学习成功率
                                    neighbor.skills[skill] = max(neighbor.skills.get(skill, 0), level-1)
            
            # 统计技术普及
            tech_count = sum(1 for a in self.agents if hasattr(a, 'skills') and a.skills)
            print(f"      掌握技术的人数: {tech_count}/{len(self.agents)}")
    
    def get_neighbors(self, agent):
        """获取邻近的个体"""
        neighbors = []
        search_radius = 3
        
        for other in self.agents:
            if other.id != agent.id:
                distance = ((agent.x - other.x)**2 + (agent.y - other.y)**2)**0.5
                if distance <= search_radius:
                    neighbors.append(other)
        
        return neighbors
    
    def analyze_social_stability_metrics(self):
        """分析社会稳定性指标"""
        print("  社会稳定性指标:")
        
        # 计算各项指标
        cooperation_levels = [a.cooperation_level for a in self.agents]
        avg_cooperation = sum(cooperation_levels) / len(cooperation_levels)
        
        aggression_levels = [a.aggression_level for a in self.agents]
        avg_aggression = sum(aggression_levels) / len(aggression_levels)
        
        wealth_inequality = self.calculate_wealth_inequality()
        
        # 部落稳定性
        tribe_stability = []
        for tribe in self.tribes:
            internal_harmony = sum(a.cooperation_level for a in tribe.members) / len(tribe.members)
            tribe_stability.append(internal_harmony)
        
        avg_tribe_stability = sum(tribe_stability) / len(tribe_stability) if tribe_stability else 0
        
        print(f"    平均合作水平: {avg_cooperation:.2f}")
        print(f"    平均攻击性: {avg_aggression:.2f}")
        print(f"    财富不平等指数: {wealth_inequality:.2f}")
        print(f"    部落内部和谐度: {avg_tribe_stability:.2f}")
        
        # 综合稳定性评估
        stability_score = (avg_cooperation + (1 - avg_aggression) + (1 - wealth_inequality) + avg_tribe_stability) / 4
        print(f"    综合稳定性评分: {stability_score:.2f}")
        
        return stability_score
    
    def calculate_wealth_inequality(self):
        """计算财富不平等指数"""
        wealth_levels = []
        for agent in self.agents:
            wealth = sum(agent.inventory.values()) + (agent.wealth if hasattr(agent, 'wealth') else 0)
            wealth_levels.append(wealth)
        
        if not wealth_levels:
            return 0
        
        avg_wealth = sum(wealth_levels) / len(wealth_levels)
        variance = sum((w - avg_wealth)**2 for w in wealth_levels) / len(wealth_levels)
        std_dev = variance**0.5
        
        # 标准化不平等指数 (0-1之间)
        inequality = min(std_dev / (avg_wealth + 1), 1.0)
        return inequality
    
    def stress_test_social_system(self):
        """社会压力测试"""
        print("  压力测试场景:")
        
        # 资源短缺场景
        print("    1. 资源短缺场景:")
        for tribe in self.tribes[:2]:  # 前2个部落
            # 模拟资源短缺
            for agent in tribe.members:
                agent.inventory[ResourceType.FOOD] = max(0, agent.inventory[ResourceType.FOOD] - 10)
                agent.inventory[ResourceType.WATER] = max(0, agent.inventory[ResourceType.WATER] - 10)
            
            # 观察社会反应
            stress_response = self.analyze_stress_response(tribe)
            print(f"      部门反应: {stress_response}")
        
        # 外部威胁场景
        print("    2. 外部威胁场景:")
        if len(self.tribes) >= 2:
            # 模拟外部威胁
            threatened_tribe = random.choice(self.tribes)
            for agent in threatened_tribe.members:
                agent.aggression_level = min(1.0, agent.aggression_level + 0.2)
            
            alliance_formation = self.detect_alliances()
            print(f"      联盟形成数量: {len(alliance_formation)}")
    
    def analyze_stress_response(self, tribe):
        """分析压力响应"""
        avg_stress = sum((100 - a.health) / 100 for a in tribe.members) / len(tribe.members)
        avg_aggression = sum(a.aggression_level for a in tribe.members) / len(tribe.members)
        
        if avg_stress > 0.6:
            response = "高压力 - 可能出现冲突或分裂"
        elif avg_stress > 0.3:
            response = "中等压力 - 需要资源调配"
        else:
            response = "低压力 - 社会稳定"
        
        return response
    
    def detect_alliances(self):
        """检测政治联盟"""
        alliances = []
        
        # 基于信仰和合作关系检测联盟
        for i in range(len(self.tribes)):
            for j in range(i+1, len(self.tribes)):
                tribe1, tribe2 = self.tribes[i], self.tribes[j]
                
                # 计算联盟潜力
                alliance_potential = self.calculate_alliance_potential(tribe1, tribe2)
                
                if alliance_potential > 0.6:
                    alliances.append((tribe1, tribe2, alliance_potential))
        
        return alliances
    
    def calculate_alliance_potential(self, tribe1, tribe2):
        """计算联盟潜力"""
        # 基于多种因素计算
        factors = []
        
        # 信仰相似性
        faith_similarity = self.calculate_faith_similarity(tribe1, tribe2)
        factors.append(faith_similarity)
        
        # 地理距离
        geo_distance = self.calculate_geographic_distance(tribe1, tribe2)
        distance_factor = max(0, 1 - geo_distance / 20)  # 距离越近，联盟潜力越高
        factors.append(distance_factor)
        
        # 经济互补性
        economic_complementarity = self.calculate_economic_complementarity(tribe1, tribe2)
        factors.append(economic_complementarity)
        
        return sum(factors) / len(factors)
    
    def calculate_faith_similarity(self, tribe1, tribe2):
        """计算信仰相似性"""
        faith1 = set()
        faith2 = set()
        
        for agent in tribe1.members:
            if agent.faith:
                faith1.add(agent.faith.faith_type)
        
        for agent in tribe2.members:
            if agent.faith:
                faith2.add(agent.faith.faith_type)
        
        if not faith1 or not faith2:
            return 0.5
        
        intersection = len(faith1 & faith2)
        union = len(faith1 | faith2)
        
        return intersection / union if union > 0 else 0
    
    def calculate_geographic_distance(self, tribe1, tribe2):
        """计算地理距离"""
        center1_x = sum(a.x for a in tribe1.members) / len(tribe1.members)
        center1_y = sum(a.y for a in tribe1.members) / len(tribe1.members)
        
        center2_x = sum(a.x for a in tribe2.members) / len(tribe2.members)
        center2_y = sum(a.y for a in tribe2.members) / len(tribe2.members)
        
        return ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5
    
    def calculate_economic_complementarity(self, tribe1, tribe2):
        """计算经济互补性"""
        # 简化的经济互补性计算
        resources1 = {}
        resources2 = {}
        
        for resource in ResourceType:
            total1 = sum(a.inventory.get(resource, 0) for a in tribe1.members)
            total2 = sum(a.inventory.get(resource, 0) for a in tribe2.members)
            resources1[resource] = total1
            resources2[resource] = total2
        
        # 计算互补性
        complementarity = 0
        for resource in ResourceType:
            # 如果一个部落多，另一个部落少，说明互补
            diff = abs(resources1[resource] - resources2[resource])
            max_total = max(resources1[resource] + resources2[resource], 1)
            complementarity += (diff / max_total)
        
        return min(complementarity / len(ResourceType), 1.0)
    
    def predict_social_trends(self):
        """预测社会发展趋势"""
        print("  社会发展趋势预测:")
        
        # 基于当前数据预测
        current_cooperation = sum(a.cooperation_level for a in self.agents) / len(self.agents)
        current_aggression = sum(a.aggression_level for a in self.agents) / len(self.agents)
        
        print(f"    当前合作水平: {current_cooperation:.2f}")
        print(f"    当前攻击性: {current_aggression:.2f}")
        
        # 预测趋势
        if current_cooperation > 0.6 and current_aggression < 0.4:
            trend = "社会发展稳定，可能形成更大规模的社会组织"
        elif current_aggression > 0.6:
            trend = "社会冲突风险增加，可能出现部落战争或分裂"
        elif current_cooperation < 0.3:
            trend = "社会凝聚力下降，个体化趋势增强"
        else:
            trend = "社会处于过渡期，发展方向不确定"
        
        print(f"    预测趋势: {trend}")
        
        return trend
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("开始社会动态系统综合测试...")
        print(f"测试参数: {self.width}x{self.height}地图, {self.agent_count}个体")
        
        # 创建环境
        self.create_test_environment()
        
        # 执行各项测试
        self.test_formation_and_tribal_systems()
        self.test_economic_interactions()
        self.test_conflict_resolution()
        self.test_cultural_evolution()
        self.test_social_stability()
        
        # 总结
        print("\n=== 社会动态系统测试总结 ===")
        print("✅ 已完成社会动态演化系统全面测试:")
        print("  1. 部落形成和社会组织系统 - 完成")
        print("  2. 经济交互和贸易网络 - 完成")
        print("  3. 冲突解决机制 - 完成")
        print("  4. 文化演化和信仰传播 - 完成")
        print("  5. 社会稳定性分析 - 完成")
        
        total_tribes = len(self.tribes)
        total_agents = len(self.agents)
        avg_tribe_size = total_agents / total_tribes if total_tribes > 0 else 0
        
        print(f"\n测试统计:")
        print(f"  形成部落: {total_tribes}个")
        print(f"  社会个体: {total_agents}个")
        print(f"  平均部落规模: {avg_tribe_size:.1f}人")
        print(f"  社会网络密度: 已计算")
        print(f"  经济贸易活动: 已模拟")
        print(f"  文化信仰传播: 已演化")
        
        print(f"\n🌟 Phase 3 社会动态系统测试完成!")

def main():
    """主测试函数"""
    tester = SocialDynamicsTester(width=20, height=20, agent_count=30)
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()