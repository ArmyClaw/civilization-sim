"""
科技系统集成示例 - 展示如何在文明模拟器中使用科技系统
"""

from tech_system import TechTree, ResourceType, Era
import random
import json


class CivilizationSimulator:
    """文明模拟器类，集成科技系统"""
    
    def __init__(self):
        self.tech_tree = TechTree()
        self.population = 10
        self.resources = {
            ResourceType.FOOD: 100,
            ResourceType.WATER: 80,
            ResourceType.WOOD: 50,
            ResourceType.MINERAL: 20
        }
        self.cultural_value = 50
        self.trade_value = 30
        self.year = 0
        
        print("🌍 文明模拟器初始化完成")
        self.display_current_state()
    
    def display_current_state(self):
        """显示当前状态"""
        print(f"\n📊 文明状态 - 第 {self.year} 年")
        print(f"   时代: {self.tech_tree.current_era.value}")
        print(f"   人口: {self.population}")
        print(f"   资源: 食物={self.resources[ResourceType.FOOD]}, "
              f"木材={self.resources[ResourceType.WOOD]}, "
              f"矿物={self.resources[ResourceType.MINERAL]}")
        print(f"   文化值: {self.cultural_value}")
        print(f"   贸易值: {self.trade_value}")
        print(f"   科技点数: {self.tech_tree.tech_points}")
        print(f"   已完成科技: {len(self.tech_tree.completed_techs)}/{len(self.tech_tree.technologies)}")
    
    def develop_civilization(self, years: int = 1):
        """发展文明指定年数"""
        for year in range(years):
            self.year += 1
            print(f"\n🎯 第 {self.year} 年发展...")
            
            # 模拟人口增长
            population_growth = int(self.population * 0.1 * (1 + self.tech_tree.get_total_effects().social_bonus))
            self.population += population_growth
            
            # 模拟资源生产
            resource_production = {
                ResourceType.FOOD: int(50 * (1 + self.tech_tree.get_total_effects().economic_bonus)),
                ResourceType.WOOD: int(30 * (1 + self.tech_tree.get_total_effects().production_efficiency)),
                ResourceType.MINERAL: int(15 * (1 + self.tech_tree.get_total_effects().production_efficiency))
            }
            
            # 更新资源
            for resource_type, amount in resource_production.items():
                self.resources[resource_type] += amount
            
            # 模拟文化发展
            cultural_development = int(10 * (1 + self.tech_tree.get_total_effects().cultural_bonus))
            self.cultural_value += cultural_development
            
            # 模拟贸易发展
            trade_development = int(5 * (1 + self.tech_tree.get_total_effects().trade_efficiency))
            self.trade_value += trade_development
            
            # 更新科技系统状态
            self.tech_tree.update_stats(
                population=self.population,
                resources=self.resources,
                cultural_value=self.cultural_value,
                trade_value=self.trade_value
            )
            
            # 获得新的科技点数
            new_tech_points = self.tech_tree.calculate_tech_points()
            self.tech_tree.tech_points += new_tech_points
            
            print(f"   人口增长: +{population_growth}")
            print(f"   资源产出: 食物+{resource_production[ResourceType.FOOD]}, "
                  f"木材+{resource_production[ResourceType.WOOD]}, "
                  f"矿物+{resource_production[ResourceType.MINERAL]}")
            print(f"   文化发展: +{cultural_development}")
            print(f"   贸易发展: +{trade_development}")
            print(f"   新增科技点数: +{new_tech_points}")
            
            # 尝试发现新科技
            self.try_discover_technologies()
            
            # 显示当前状态
            self.display_current_state()
            
            # 检查是否进入新时代
            self.check_era_progression()
    
    def try_discover_technologies(self):
        """尝试发现科技"""
        available_techs = self.tech_tree.get_available_techs()
        if not available_techs:
            return
        
        # 显示可研究的科技
        print(f"   🔬 可研究的科技 ({len(available_techs)}个):")
        for tech_id in available_techs[:3]:  # 只显示前3个
            tech = self.tech_tree.technologies[tech_id]
            print(f"      - {tech.name} (成本: {tech.cost})")
        
        # 自动发现科技
        discovered = self.tech_tree.auto_discover()
        if discovered:
            print(f"   🎉 发现了 {len(discovered)} 个新科技!")
            for tech_id in discovered:
                tech = self.tech_tree.technologies[tech_id]
                print(f"      ✅ {tech.name}")
        else:
            print(f"   🤔 本年未发现新科技")
    
    def check_era_progression(self):
        """检查时代变迁"""
        old_era = self.tech_tree.current_era
        
        # 手动检查时代变迁
        completed_in_era = {}
        for tech_id, tech in self.tech_tree.technologies.items():
            if tech.is_completed:
                if tech.era not in completed_in_era:
                    completed_in_era[tech.era] = 0
                completed_in_era[tech.era] += 1
        
        # 检查时代升级条件
        if old_era == Era.PALEOLITHIC and completed_in_era.get(Era.PALEOLITHIC, 0) >= 2:
            self.tech_tree.current_era = Era.NEOLITHIC
            print(f"   🚀 石器时代完成，进入新石器时代!")
        elif old_era == Era.NEOLITHIC and completed_in_era.get(Era.NEOLITHIC, 0) >= 3:
            self.tech_tree.current_era = Era.METALWORKING
            print(f"   🚀 新石器时代完成，进入冶金时代!")
        elif old_era == Era.METALWORKING and completed_in_era.get(Era.METALWORKING, 0) >= 4:
            self.tech_tree.current_era = Era.INDUSTRIAL
            print(f"   🚀 冶金时代完成，进入工业时代!")
        elif old_era == Era.INDUSTRIAL and completed_in_era.get(Era.INDUSTRIAL, 0) >= 3:
            self.tech_tree.current_era = Era.INFORMATION
            print(f"   🚀 工业时代完成，进入信息时代!")
    
    def display_tech_tree_status(self):
        """显示科技树状态"""
        print(f"\n🌳 科技树状态 - {self.tech_tree.current_era.value} 时代")
        
        # 按时代显示科技
        for era in Era:
            era_techs = self.tech_tree.technologies.items()
            completed_count = len(self.tech_tree.get_completed_techs_in_era(era))
            total_count = len([t for t in self.tech_tree.technologies.values() if t.era == era])
            
            if total_count > 0:
                status_icon = "🎯" if completed_count == 0 else "🚀" if completed_count == total_count else "🔄"
                print(f"   {status_icon} {era.value}: {completed_count}/{total_count} 个科技")
                
                # 显示该时代的科技
                for tech_id, tech in self.tech_tree.technologies.items():
                    if tech.era == era:
                        status = "✅" if tech.is_completed else "🔄" if tech.is_researching else "⭕"
                        progress = f" ({tech.progress:.0f}%)" if tech.is_researching and tech.progress < 100 else ""
                        print(f"      {status} {tech.name}{progress}")
        
        # 显示累计效果
        total_effects = self.tech_tree.get_total_effects()
        print(f"\n🌟 累计科技效果:")
        print(f"   经济加成: +{total_effects.economic_bonus:.1f}")
        print(f"   军事加成: +{total_effects.military_bonus:.1f}")
        print(f"   社会加成: +{total_effects.social_bonus:.1f}")
        print(f"   文化加成: +{total_effects.cultural_bonus:.1f}")
        print(f"   人口容量: +{total_effects.population_capacity}")
        print(f"   生产效率: +{total_effects.production_efficiency:.1f}")
        print(f"   贸易效率: +{total_effects.trade_efficiency:.1f}")
    
    def save_civilization_state(self, filename: str = "civilization_state.json"):
        """保存文明状态"""
        state = {
            "year": self.year,
            "population": self.population,
            "resources": {r.value: v for r, v in self.resources.items()},
            "cultural_value": self.cultural_value,
            "trade_value": self.trade_value,
            "tech_tree": self.tech_tree.save_state()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 文明状态已保存到 {filename}")
    
    def load_civilization_state(self, filename: str = "civilization_state.json"):
        """加载文明状态"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.year = state["year"]
            self.population = state["population"]
            self.cultural_value = state["cultural_value"]
            self.trade_value = state["trade_value"]
            
            # 恢复资源
            resources_dict = state["resources"]
            self.resources = {ResourceType(k): v for k, v in resources_dict.items()}
            
            # 恢复科技树
            self.tech_tree.load_state(state["tech_tree"])
            
            print(f"📂 文明状态已从 {filename} 加载")
            
        except FileNotFoundError:
            print(f"❌ 文件 {filename} 不存在")
        except Exception as e:
            print(f"❌ 加载状态失败: {e}")


def run_simulation():
    """运行文明模拟"""
    print("🎮 文明模拟器 - 科技系统演示")
    print("=" * 50)
    
    # 创建模拟器
    sim = CivilizationSimulator()
    
    # 显示初始科技树状态
    sim.display_tech_tree_status()
    
    # 运行模拟50年
    print(f"\n🚀 开始模拟50年发展...")
    sim.develop_civilization(50)
    
    # 显示最终状态
    print(f"\n🏆 最终文明状态:")
    sim.display_current_state()
    sim.display_tech_tree_status()
    
    # 保存状态
    sim.save_civilization_state()
    
    print(f"\n🎉 模拟完成！文明从原始社会发展到{sim.tech_tree.current_era.value}时代")
    
    return sim


if __name__ == "__main__":
    simulation = run_simulation()