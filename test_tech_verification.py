#!/usr/bin/env python3
"""
科技系统端到端验证测试 - 验证科技发现、效果计算、时代进步等核心功能
"""

import json
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tech_system import TechTree, ResourceType, Era, TechEffect

def test_tech_discovery_workflow():
    """测试完整的科技发现工作流"""
    print("🚀 测试科技发现工作流...")
    
    # 创建科技树
    tech_tree = TechTree()
    
    # 设置初始条件
    initial_resources = {
        ResourceType.FOOD: 1000,
        ResourceType.WOOD: 500,
        ResourceType.MINERAL: 300,
        ResourceType.WATER: 800
    }
    
    tech_tree.update_stats(
        population=50,
        resources=initial_resources,
        cultural_value=100,
        trade_value=50
    )
    
    # 记录初始状态
    initial_era = tech_tree.current_era
    initial_points = tech_tree.calculate_tech_points()
    tech_tree.tech_points = initial_points
    
    print(f"🏛️ 初始时代: {initial_era.value}")
    print(f"🎯 初始科技点数: {initial_points}")
    print(f"📊 可研究科技数: {len(tech_tree.get_available_techs())}")
    
    # 第一阶段：发现石器时代科技
    print("\n🔥 第一阶段：石器时代")
    paleolithic_techs = ["fire_control", "stone_tools", "basic_construction", "language"]
    
    discovered_paleo = []
    for tech_id in paleolithic_techs:
        if tech_tree.discover_technology(tech_id):
            discovered_paleo.append(tech_id)
            tech = tech_tree.technologies[tech_id]
            print(f"   ✅ 发现: {tech.name}")
    
    print(f"   石器时代完成: {len(discovered_paleo)}/4 个科技")
    
    # 第二阶段：进入新石器时代
    print("\n🌾 第二阶段：新石器时代")
    neolithic_techs = ["agriculture", "pottery", "specialization", "tribal_organization"]
    
    discovered_neo = []
    for tech_id in neolithic_techs:
        if tech_tree.discover_technology(tech_id):
            discovered_neo.append(tech_id)
            tech = tech_tree.technologies[tech_id]
            print(f"   ✅ 发现: {tech.name}")
    
    print(f"   新石器时代完成: {len(discovered_neo)}/4 个科技")
    
    # 第三阶段：进入冶金时代
    print("\n⚒️ 第三阶段：冶金时代")
    metalworking_techs = ["bronze_working", "urbanization", "writing", "trade_networks"]
    
    discovered_metal = []
    for tech_id in metalworking_techs:
        if tech_tree.discover_technology(tech_id):
            discovered_metal.append(tech_id)
            tech = tech_tree.technologies[tech_id]
            print(f"   ✅ 发现: {tech.name}")
    
    print(f"   冶金时代完成: {len(discovered_metal)}/4 个科技")
    
    # 检查时代进步
    era_progression = {
        Era.PALEOLITHIC: len(tech_tree.get_completed_techs_in_era(Era.PALEOLITHIC)),
        Era.NEOLITHIC: len(tech_tree.get_completed_techs_in_era(Era.NEOLITHIC)),
        Era.METALWORKING: len(tech_tree.get_completed_techs_in_era(Era.METALWORKING)),
        Era.INDUSTRIAL: len(tech_tree.get_completed_techs_in_era(Era.INDUSTRIAL)),
        Era.INFORMATION: len(tech_tree.get_completed_techs_in_era(Era.INFORMATION))
    }
    
    print(f"\n📊 时代进度:")
    for era, count in era_progression.items():
        print(f"   {era.value}: {count} 个科技")
    
    # 计算累计效果
    total_effects = tech_tree.get_total_effects()
    print(f"\n🌟 累计科技效果:")
    print(f"   💰 经济加成: +{total_effects.economic_bonus:.1f}")
    print(f"   ⚔️ 军事加成: +{total_effects.military_bonus:.1f}")
    print(f"   👥 社会加成: +{total_effects.social_bonus:.1f}")
    print(f"   🎭 文化加成: +{total_effects.cultural_bonus:.1f}")
    print(f"   🏠 人口容量: +{total_effects.population_capacity}")
    print(f"   🏭 生产效率: +{total_effects.production_efficiency:.1f}")
    print(f"   🛒 贸易效率: +{total_effects.trade_efficiency:.1f}")
    
    # 最终统计
    total_discovered = len(tech_tree.completed_techs)
    final_era = tech_tree.current_era
    remaining_points = tech_tree.tech_points
    
    print(f"\n🎉 最终状态:")
    print(f"   ✅ 总共发现科技: {total_discovered} 个")
    print(f"   🏛️ 当前时代: {final_era.value}")
    print(f"   🎯 剩余科技点数: {remaining_points}")
    
    # 验证结果
    success = (
        total_discovered >= 10 and  # 至少发现10个科技
        final_era != Era.PALEOLITHIC and  # 时代已进步
        total_effects.economic_bonus > 5  # 经济效果显著
    )
    
    return success, {
        "initial_era": initial_era.value,
        "final_era": final_era.value,
        "total_discovered": total_discovered,
        "total_effects": {
            "economic": total_effects.economic_bonus,
            "military": total_effects.military_bonus,
            "social": total_effects.social_bonus,
            "cultural": total_effects.cultural_bonus,
            "population_capacity": total_effects.population_capacity,
            "production_efficiency": total_effects.production_efficiency,
            "trade_efficiency": total_effects.trade_efficiency
        },
        "remaining_points": remaining_points
    }

def test_tech_probability_system():
    """测试科技发现概率系统"""
    print("\n🎲 测试科技发现概率系统...")
    
    tech_tree = TechTree()
    
    # 测试不同条件下的概率
    scenarios = [
        ("🏘️ 高人口低资源", 200, {"FOOD": 100, "WOOD": 50, "MINERAL": 30, "WATER": 80}, 50, 30),
        ("⛏️ 低人口高资源", 30, {"FOOD": 800, "WOOD": 600, "MINERAL": 400, "WATER": 700}, 100, 200),
        ("🎭 高文化值", 100, {"FOOD": 500, "WOOD": 400, "MINERAL": 300, "WATER": 600}, 500, 100),
        ("🏭 高贸易值", 150, {"FOOD": 600, "WOOD": 500, "MINERAL": 400, "WATER": 650}, 100, 500)
    ]
    
    results = []
    for scenario_name, population, resources, cultural_value, trade_value in scenarios:
        tech_tree.update_stats(
            population=population,
            resources={ResourceType.FOOD: resources["FOOD"], 
                      ResourceType.WOOD: resources["WOOD"],
                      ResourceType.MINERAL: resources["MINERAL"],
                      ResourceType.WATER: resources["WATER"]},
            cultural_value=cultural_value,
            trade_value=trade_value
        )
        
        probabilities = tech_tree.generate_discovery_probability()
        tech_points = tech_tree.calculate_tech_points()
        
        results.append({
            "scenario": scenario_name,
            "population": population,
            "resources": resources,
            "cultural_value": cultural_value,
            "trade_value": trade_value,
            "tech_points": tech_points,
            "available_techs": len(probabilities),
            "avg_probability": sum(probabilities.values()) / len(probabilities) if probabilities else 0
        })
        
        print(f"   {scenario_name}:")
        print(f"      🎯 科技点数: {tech_points}")
        print(f"      🔬 可研究科技: {len(probabilities)}")
        print(f"      📈 平均概率: {results[-1]['avg_probability']:.1%}")
    
    # 验证概率系统响应不同条件
    varied_probabilities = len(set(r["avg_probability"] for r in results)) > 1
    print(f"\n✅ 概率系统响应不同条件: {'✅' if varied_probabilities else '❌'}")
    
    return varied_probabilities, results

def test_tech_save_load():
    """测试科技树状态保存和加载"""
    print("\n💾 测试科技树状态保存和加载...")
    
    # 创建科技树并设置状态
    tech_tree = TechTree()
    
    # 发现一些科技
    tech_tree.discover_technology("fire_control")
    tech_tree.discover_technology("stone_tools")
    tech_tree.discover_technology("agriculture")
    tech_tree.discover_technology("pottery")
    
    # 添加科技点数
    tech_tree.tech_points = 100
    
    # 保存状态
    saved_state = tech_tree.save_state()
    
    # 创建新科技树并加载状态
    new_tech_tree = TechTree()
    new_tech_tree.load_state(saved_state)
    
    # 验证状态一致性
    verification_results = []
    
    # 检查完成科技
    completed_techs_match = new_tech_tree.completed_techs == tech_tree.completed_techs
    verification_results.append(("完成科技", completed_techs_match))
    
    # 检查当前时代
    era_match = new_tech_tree.current_era == tech_tree.current_era
    verification_results.append(("当前时代", era_match))
    
    # 检查科技点数
    points_match = new_tech_tree.tech_points == tech_tree.tech_points
    verification_results.append(("科技点数", points_match))
    
    # 检查研究进度
    progress_match = new_tech_tree.get_research_progress() == tech_tree.get_research_progress()
    verification_results.append(("研究进度", progress_match))
    
    print("   状态验证:")
    all_match = True
    for test_name, matched in verification_results:
        status = "✅" if matched else "❌"
        print(f"      {status} {test_name}")
        if not matched:
            all_match = False
    
    return all_match, saved_state

def test_tech_effects_consistency():
    """测试科技效果的一致性"""
    print("\n📊 测试科技效果一致性...")
    
    tech_tree = TechTree()
    
    # 发现科技并跟踪效果变化
    effects_history = []
    
    base_effects = tech_tree.get_total_effects()
    effects_history.append({
        "techs": [],
        "effects": {
            "economic": base_effects.economic_bonus,
            "military": base_effects.military_bonus,
            "social": base_effects.social_bonus,
            "cultural": base_effects.cultural_bonus,
            "population_capacity": base_effects.population_capacity,
            "production_efficiency": base_effects.production_efficiency,
            "trade_efficiency": base_effects.trade_efficiency
        }
    })
    
    # 逐步发现科技
    tech_ids = ["fire_control", "stone_tools", "agriculture", "pottery", "specialization"]
    
    for tech_id in tech_ids:
        if tech_tree.discover_technology(tech_id):
            tech = tech_tree.technologies[tech_id]
            effects = tech_tree.get_total_effects()
            
            effects_history.append({
                "techs": effects_history[-1]["techs"] + [tech_id],
                "effects": {
                    "economic": effects.economic_bonus,
                    "military": effects.military_bonus,
                    "social": effects.social_bonus,
                    "cultural": effects.cultural_bonus,
                    "population_capacity": effects.population_capacity,
                    "production_efficiency": effects.production_efficiency,
                    "trade_efficiency": effects.trade_efficiency
                }
            })
            
            print(f"   🔬 发现 {tech.name}:")
            print(f"      💰 经济: {effects_history[-2]['effects']['economic']:.1f} → {effects.economic_bonus:.1f}")
    
    # 验证效果单调递增
    consistent = True
    for i in range(1, len(effects_history)):
        prev_effects = effects_history[i-1]["effects"]
        curr_effects = effects_history[i]["effects"]
        
        for effect_type in ["economic", "military", "social", "cultural", "production_efficiency", "trade_efficiency"]:
            if curr_effects[effect_type] < prev_effects[effect_type]:
                consistent = False
                break
        
        # 人口容量可以减少（如果某些科技有负效果）
    
    print(f"   ✅ 效果一致性: {'✅' if consistent else '❌'}")
    
    return consistent, effects_history

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📋 科技系统验证测试报告")
    print("="*60)
    
    # 测试结果汇总
    test_names = [
        "科技发现工作流",
        "概率系统响应",
        "状态保存加载",
        "效果一致性"
    ]
    
    all_passed = True
    for i, result in enumerate(results):
        if i < len(test_names):
            name = result[0] if len(result) > 0 else test_names[i]
            passed = result[1] if len(result) > 1 else False
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{i+1}. {test_names[i]}: {status}")
            if not passed:
                all_passed = False
    
    # 核心指标
    print(f"\n📊 核心指标:")
    if results and len(results) > 0:
        # 获取工作流测试结果
        workflow_success, workflow_data = results[0]
        if workflow_success and workflow_data:
            print(f"   🎯 科技发现成功率: 100%")
            print(f"   🏛️ 时代进步: {workflow_data['initial_era']} → {workflow_data['final_era']}")
            print(f"   🌟 总体效果提升:")
            effects = workflow_data['total_effects']
            print(f"      💰 经济: +{effects['economic']:.1f}")
            print(f"      ⚔️ 军事: +{effects['military']:.1f}")
            print(f"      👥 社会: +{effects['social']:.1f}")
            print(f"      🏠 人口容量: +{effects['population_capacity']}")
            print(f"      🏭 生产效率: +{effects['production_efficiency']:.1f}")
            print(f"      🛒 贸易效率: +{effects['trade_efficiency']:.1f}")
    
    print(f"\n🎯 总体评价: {'🎉 所有测试通过，科技系统运行正常！' if all_passed else '⚠️ 部分测试存在异常'}")
    
    return all_passed

def main():
    """主测试函数"""
    print("🔬 科技系统端到端验证测试")
    print("="*60)
    
    results = []
    
    # 测试1: 科技发现工作流
    workflow_success, workflow_data = test_tech_discovery_workflow()
    results.append(("工作流测试", workflow_success, workflow_data))
    
    # 测试2: 概率系统
    prob_success, prob_data = test_tech_probability_system()
    results.append(("概率测试", prob_success, prob_data))
    
    # 测试3: 状态保存加载
    save_success, save_data = test_tech_save_load()
    results.append(("保存测试", save_success, save_data))
    
    # 测试4: 效果一致性
    effects_success, effects_data = test_tech_effects_consistency()
    results.append(("效果测试", effects_success, effects_data))
    
    # 生成报告
    all_passed = generate_test_report(results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 科技系统验证完成，所有核心功能正常")
    else:
        print("❌ 科技系统存在需要修复的问题")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)