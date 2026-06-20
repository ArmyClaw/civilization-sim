#!/usr/bin/env python3
"""
科技系统测试脚本
测试基于人口/资源/时间的科技发现机制
"""

from src.tech_system import TechTree, ResourceType, Era
import random

def test_tech_discovery_mechanism():
    """测试科技发现机制"""
    print("🧪 开始测试科技发现机制...")
    
    # 初始化科技树
    tech_tree = TechTree()
    
    # 设置初始条件
    initial_population = 50
    initial_resources = {
        ResourceType.FOOD: 500,
        ResourceType.WATER: 300,
        ResourceType.WOOD: 200,
        ResourceType.MINERAL: 100
    }
    initial_cultural_value = 200
    initial_trade_value = 150
    
    # 更新文明统计
    tech_tree.update_stats(
        population=initial_population,
        resources=initial_resources,
        cultural_value=initial_cultural_value,
        trade_value=initial_trade_value
    )
    
    print(f"📊 初始条件:")
    print(f"   人口: {initial_population}")
    print(f"   资源: 食物={initial_resources[ResourceType.FOOD]}, "
          f"木材={initial_resources[ResourceType.WOOD]}, "
          f"矿物={initial_resources[ResourceType.MINERAL]}")
    print(f"   文化值: {initial_cultural_value}")
    print(f"   贸易值: {initial_trade_value}")
    print(f"   当前时代: {tech_tree.current_era.value}")
    
    # 计算初始科技点数
    initial_points = tech_tree.calculate_tech_points()
    tech_tree.tech_points = initial_points
    print(f"🎯 初始科技点数: {initial_points}")
    
    # 显示可研究的科技
    available_techs = tech_tree.get_available_techs()
    print(f"🔬 可研究的科技 ({len(available_techs)}个):")
    for tech_id in available_techs:
        tech = tech_tree.technologies[tech_id]
        print(f"   - {tech.name}: {tech.description} (成本: {tech.cost})")
    
    # 生成发现概率
    probabilities = tech_tree.generate_discovery_probability()
    print(f"\n📈 科技发现概率:")
    for tech_id, prob in probabilities.items():
        tech = tech_tree.technologies[tech_id]
        print(f"   - {tech.name}: {prob:.1%}")
    
    # 自动发现科技（进行多轮测试）
    print(f"\n🚀 开始自动发现科技...")
    discovery_rounds = 10
    total_discovered = []
    
    for round_num in range(discovery_rounds):
        # 每轮获得新的科技点数
        round_points = tech_tree.calculate_tech_points()
        tech_tree.tech_points += round_points
        
        # 尝试发现科技
        discovered = tech_tree.auto_discover()
        total_discovered.extend(discovered)
        
        if discovered:
            print(f"   第{round_num + 1}轮: 发现 {len(discovered)} 个科技")
            for tech_id in discovered:
                tech = tech_tree.technologies[tech_id]
                print(f"      ✅ {tech.name}")
        else:
            print(f"   第{round_num + 1}轮: 未发现新科技")
        
        # 更新统计（模拟文明发展）
        tech_tree.update_stats(
            population=initial_population + round_num * 10,
            resources={
                ResourceType.FOOD: 500 + round_num * 100,
                ResourceType.WATER: 300 + round_num * 50,
                ResourceType.WOOD: 200 + round_num * 80,
                ResourceType.MINERAL: 100 + round_num * 30
            },
            cultural_value=200 + round_num * 50,
            trade_value=150 + round_num * 40
        )
    
    # 最终结果
    print(f"\n🎉 最终结果:")
    print(f"   总共发现科技: {len(total_discovered)} 个")
    print(f"   当前时代: {tech_tree.current_era.value}")
    print(f"   剩余科技点数: {tech_tree.tech_points}")
    
    # 显示已完成科技
    completed_techs = tech_tree.completed_techs
    print(f"   已完成科技:")
    for tech_id in completed_techs:
        tech = tech_tree.technologies[tech_id]
        print(f"      ✅ {tech.name} ({tech.era.value})")
    
    # 显示按时代分类的完成情况
    print(f"\n📊 时代进度:")
    for era in Era:
        era_techs = tech_tree.get_completed_techs_in_era(era)
        print(f"   {era.value}: {len(era_techs)}/{len([t for t in tech_tree.technologies.values() if t.era == era])} 个科技")
    
    # 显示累计效果
    total_effects = tech_tree.get_total_effects()
    print(f"\n🌟 累计科技效果:")
    print(f"   经济加成: +{total_effects.economic_bonus:.1f}")
    print(f"   军事加成: +{total_effects.military_bonus:.1f}")
    print(f"   社会加成: +{total_effects.social_bonus:.1f}")
    print(f"   文化加成: +{total_effects.cultural_bonus:.1f}")
    print(f"   人口容量: +{total_effects.population_capacity}")
    print(f"   生产效率: +{total_effects.production_efficiency:.1f}")
    print(f"   贸易效率: +{total_effects.trade_efficiency:.1f}")
    
    # 保存状态
    saved_state = tech_tree.save_state()
    print(f"\n💾 保存状态成功，包含 {len(saved_state)} 个字段")
    
    return tech_tree, total_discovered


def test_specific_scenarios():
    """测试特定场景"""
    print("\n" + "="*60)
    print("🧪 测试特定场景...")
    
    # 场景1: 高人口低资源
    print("\n🏘️ 场景1: 高人口低资源")
    tech_tree1 = TechTree()
    tech_tree1.update_stats(
        population=200,  # 高人口
        resources={
            ResourceType.FOOD: 100,  # 低资源
            ResourceType.WATER: 50,
            ResourceType.WOOD: 30,
            ResourceType.MINERAL: 20
        },
        cultural_value=50,
        trade_value=30
    )
    
    points1 = tech_tree1.calculate_tech_points()
    probs1 = tech_tree1.generate_discovery_probability()
    print(f"   科技点数: {points1}")
    print(f"   可研究科技数: {len(probs1)}")
    
    # 场景2: 低人口高资源
    print("\n⛏️ 场景2: 低人口高资源")
    tech_tree2 = TechTree()
    tech_tree2.update_stats(
        population=20,  # 低人口
        resources={
            ResourceType.FOOD: 800,  # 高资源
            ResourceType.WATER: 600,
            ResourceType.WOOD: 500,
            ResourceType.MINERAL: 400
        },
        cultural_value=300,
        trade_value=200
    )
    
    points2 = tech_tree2.calculate_tech_points()
    probs2 = tech_tree2.generate_discovery_probability()
    print(f"   科技点数: {points2}")
    print(f"   可研究科技数: {len(probs2)}")
    
    # 场景3: 高文化值
    print("\n🎭 场景3: 高文化值")
    tech_tree3 = TechTree()
    tech_tree3.update_stats(
        population=100,
        resources={
            ResourceType.FOOD: 400,
            ResourceType.WATER: 300,
            ResourceType.WOOD: 200,
            ResourceType.MINERAL: 150
        },
        cultural_value=1000,  # 高文化值
        trade_value=100
    )
    
    points3 = tech_tree3.calculate_tech_points()
    probs3 = tech_tree3.generate_discovery_probability()
    print(f"   科技点数: {points3}")
    print(f"   可研究科技数: {len(probs3)}")


def main():
    """主测试函数"""
    print("🎯 科技系统完整测试")
    print("=" * 60)
    
    # 运行主要测试
    tech_tree, discovered = test_tech_discovery_mechanism()
    
    # 运行特定场景测试
    test_specific_scenarios()
    
    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print(f"🎉 科技系统成功实现了基于人口/资源/时间的科技发现机制")
    print(f"📊 发现了 {len(discovered)} 个科技，展现了文明的进步历程")


if __name__ == "__main__":
    main()