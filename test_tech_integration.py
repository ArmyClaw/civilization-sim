#!/usr/bin/env python3
"""
科技系统集成测试 - 验证科技系统与其他模块的协同工作
"""

import json
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tech_system import TechTree, ResourceType, Era
from economy import EconomySystem
from agent import Agent
from tribe_system import TribeSystem

class TechIntegrationTester:
    """科技系统集成测试器"""
    
    def __init__(self):
        self.tech_tree = TechTree()
        self.economy_system = EconomySystem()
        self.tribe_system = TribeSystem()
        
    def setup_initial_state(self):
        """设置初始状态"""
        # 初始化资源
        resources = {
            ResourceType.FOOD: 1000,
            ResourceType.WOOD: 500,
            ResourceType.MINERAL: 300,
            ResourceType.WATER: 800
        }
        
        # 初始化人口
        population = 100
        
        # 初始化经济参数
        economy_params = {
            'initial_population': population,
            'initial_resources': resources,
            'base_production_rate': 1.0,
            'base_trade_efficiency': 0.5
        }
        
        # 初始化部落参数
        tribe_params = {
            'initial_population': population,
            'initial_resources': resources,
            'tribe_count': 3
        }
        
        return resources, population, economy_params, tribe_params
    
    def test_tech_economy_synergy(self):
        """测试科技与经济的协同效应"""
        print("🔬 测试科技与经济协同效应...")
        
        # 设置初始状态
        resources, population, economy_params, tribe_params = self.setup_initial_state()
        
        # 更新科技树状态
        self.tech_tree.update_stats(
            population=population,
            resources=resources,
            cultural_value=100,
            trade_value=50
        )
        
        # 计算初始经济产出
        initial_economy = self.economy_system.calculate_total_output(economy_params)
        print(f"💰 初始经济产出: {initial_economy:.1f}")
        
        # 发现一些基础科技
        self.tech_tree.discover_technology("fire_control")
        self.tech_tree.discover_technology("stone_tools")
        self.tech_tree.discover_technology("agriculture")
        
        # 获取科技效果
        tech_effects = self.tech_tree.get_total_effects()
        print(f"📈 科技效果: 经济+{tech_effects.economic_bonus:.1f}, 生产效率+{tech_effects.production_efficiency:.1f}")
        
        # 应用科技效果到经济系统
        economy_params['base_production_rate'] *= (1 + tech_effects.production_efficiency)
        economy_params['base_trade_efficiency'] *= (1 + tech_effects.trade_efficiency)
        
        # 计算科技提升后的经济产出
        enhanced_economy = self.economy_system.calculate_total_output(economy_params)
        economy_boost = enhanced_economy - initial_economy
        boost_percentage = (economy_boost / initial_economy) * 100
        
        print(f"🚀 科技提升后经济产出: {enhanced_economy:.1f}")
        print(f"📊 经济提升幅度: {boost_percentage:.1f}%")
        
        return economy_boost > 0, boost_percentage
    
    def test_tech_population_capacity(self):
        """测试科技对人口容量的影响"""
        print("\n👥 测试科技对人口容量的影响...")
        
        # 设置初始状态
        resources, population, economy_params, tribe_params = self.setup_initial_state()
        
        # 初始人口容量
        initial_capacity = self.tech_tree.get_total_effects().population_capacity
        print(f"🏠 初始人口容量: {population + initial_capacity}")
        
        # 发现提升人口容量的科技
        self.tech_tree.discover_technology("basic_construction")
        self.tech_tree.discover_technology("agriculture")
        self.tech_tree.discover_technology("urbanization")
        
        # 获取新的人口容量
        new_capacity = self.tech_tree.get_total_effects().population_capacity
        capacity_increase = new_capacity - initial_capacity
        
        print(f"🏘️ 科技提升后人口容量: {population + new_capacity}")
        print(f"📈 人口容量提升: +{capacity_increase}")
        
        return capacity_increase > 0, capacity_increase
    
    def test_tech_tribe_integration(self):
        """测试科技与部落系统的集成"""
        print("\n🏛️ 测试科技与部落系统集成...")
        
        # 设置初始状态
        resources, population, economy_params, tribe_params = self.setup_initial_state()
        
        # 初始化部落系统
        self.tribe_system.initialize_tribes(tribe_params)
        initial_tribe_count = len(self.tribe_system.tribes)
        
        print(f"🏘️ 初始部落数量: {initial_tribe_count}")
        
        # 发现促进部落发展的科技
        self.tech_tree.discover_technology("language")
        self.tech_tree.discover_technology("tribal_organization")
        self.tech_tree.discover_technology("specialization")
        
        # 应用科技效果到部落系统
        tech_effects = self.tech_tree.get_total_effects()
        self.tribe_system.apply_tech_effects(tech_effects)
        
        # 检查部落发展
        developed_tribes = [t for t in self.tribe_system.tribes if t.development_level > 1]
        development_percentage = (len(developed_tribes) / len(self.tribe_system.tribes)) * 100
        
        print(f"🌱 已发展部落: {len(developed_tribes)}/{len(self.tribe_system.tribes)}")
        print(f"📈 发展程度: {development_percentage:.1f}%")
        
        return len(developed_tribes) > 0, development_percentage
    
    def test_tech_era_progression(self):
        """测试时代进步机制"""
        print("\n⏳ 测试时代进步机制...")
        
        # 设置初始状态
        resources, population, economy_params, tribe_params = self.setup_initial_state()
        self.tech_tree.update_stats(
            population=population,
            resources=resources,
            cultural_value=100,
            trade_value=50
        )
        
        # 记录初始时代
        initial_era = self.tech_tree.current_era
        print(f"🏛️ 初始时代: {initial_era.value}")
        
        # 手动完成石器时代的科技
        paleolithic_techs = ["fire_control", "stone_tools", "basic_construction", "language"]
        for tech_id in paleolithic_techs:
            if tech_id in self.tech_tree.technologies:
                self.tech_tree.discover_technology(tech_id)
        
        print(f"✅ 完成 {len(paleolithic_techs)} 个石器时代科技")
        
        # 添加更多资源促进时代进步
        enhanced_resources = resources.copy()
        enhanced_resources[ResourceType.FOOD] = 2000
        enhanced_resources[ResourceType.MINERAL] = 800
        
        self.tech_tree.update_stats(
            population=population + 50,
            resources=enhanced_resources,
            cultural_value=500,
            trade_value=200
        )
        
        # 尝试发现新科技，触发时代进步
        self.tech_tree.discover_technology("agriculture")
        self.tech_tree.discover_technology("pottery")
        
        # 检查时代是否进步
        era_progressed = self.tech_tree.current_era != initial_era
        new_era = self.tech_tree.current_era
        
        print(f"🚀 新时代: {new_era.value}")
        print(f"📊 时代已进步: {'✅' if era_progressed else '❌'}")
        
        return era_progressed, new_era
    
    def test_tech_save_load_cycle(self):
        """测试科技树的保存和加载"""
        print("\n💾 测试科技树保存和加载...")
        
        # 设置状态
        self.tech_tree.update_stats(
            population=100,
            resources={ResourceType.FOOD: 500, ResourceType.WOOD: 300, ResourceType.MINERAL: 200},
            cultural_value=200,
            trade_value=100
        )
        
        # 发现一些科技
        self.tech_tree.discover_technology("fire_control")
        self.tech_tree.discover_technology("stone_tools")
        self.tech_tree.discover_technology("agriculture")
        
        # 保存状态
        saved_state = self.tech_tree.save_state()
        print(f"💾 保存状态: {len(saved_state)} 个字段")
        
        # 创建新的科技树并加载状态
        new_tech_tree = TechTree()
        new_tech_tree.load_state(saved_state)
        
        # 验证加载的状态
        techs_match = new_tech_tree.completed_techs == self.tech_tree.completed_techs
        era_match = new_tech_tree.current_era == self.tech_tree.current_era
        points_match = new_tech_tree.tech_points == self.tech_tree.tech_points
        
        print(f"✅ 科技完成状态匹配: {techs_match}")
        print(f"✅ 时代匹配: {era_match}")
        print(f"✅ 科技点数匹配: {points_match}")
        
        return techs_match and era_match and points_match
    
    def run_all_tests(self):
        """运行所有集成测试"""
        print("🎯 科技系统集成测试开始")
        print("=" * 60)
        
        results = []
        
        # 测试1: 科技与经济协同
        eco_result, eco_boost = self.test_tech_economy_synergy()
        results.append(("科技经济协同", eco_result, f"提升 {eco_boost:.1f}%"))
        
        # 测试2: 人口容量影响
        pop_result, pop_increase = self.test_tech_population_capacity()
        results.append(("人口容量影响", pop_result, f"提升 +{pop_increase}"))
        
        # 测试3: 部落系统集成
        tribe_result, tribe_dev = self.test_tech_tribe_integration()
        results.append(("部落系统集成", tribe_result, f"发展程度 {tribe_dev:.1f}%"))
        
        # 测试4: 时代进步
        era_result, new_era = self.test_tech_era_progression()
        results.append(("时代进步", era_result, f"进入 {new_era.value}"))
        
        # 测试5: 保存加载
        save_result = self.test_tech_save_load_cycle()
        results.append(("保存加载", save_result, "状态完整"))
        
        # 输出测试结果
        print("\n" + "=" * 60)
        print("📊 集成测试结果:")
        all_passed = True
        for test_name, passed, details in results:
            status = "✅" if passed else "❌"
            print(f"   {status} {test_name}: {details}")
            if not passed:
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 所有集成测试通过！科技系统与其他模块协同工作良好")
        else:
            print("⚠️ 部分测试失败，需要检查集成问题")
        
        return all_passed

def main():
    """主函数"""
    tester = TechIntegrationTester()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)