# 社会结构模型设计文档

## 1. 概述

本文档设计文明模拟器中的社会结构数据模型，包含部落、首领、信仰和文化属性等核心组件。

## 2. 核心实体设计

### 2.1 部落 (Tribe)

```python
class Tribe:
    def __init__(self, tribe_id: int, name: str, location: dict):
        self.tribe_id = tribe_id
        self.name = name
        self.location = location  # {'x': int, 'y': int, 'terrain': str}
        self.population = 0
        self.members = []  # List of Member objects
        self.resources = {}  # {'food': int, 'water': int, 'tools': int}
        self.technology_level = 1
        self.relationships = {}  # {other_tribe_id: relationship_score}
        
    def add_member(self, member):
        """添加成员到部落"""
        self.members.append(member)
        self.population += 1
        
    def update_relationship(self, other_tribe_id: int, change: float):
        """更新与其他部落的关系"""
        self.relationships[other_tribe_id] = self.relationships.get(other_tribe_id, 0) + change
```

### 2.2 首领 (Chief)

```python
class Chief:
    def __init__(self, chief_id: int, name: str, tribe: Tribe):
        self.chief_id = chief_id
        self.name = name
        self.tribe = tribe
        self.authority = 50  # 0-100 权力值
        self.skills = {}  # {'leadership': int, 'diplomacy': int, 'military': int}
        self.age = 0
        self.health = 100
        self.experience = 0
        self.achievements = []  # List of achievement strings
        
    def make_decision(self, decision_type: str, context: dict):
        """制定决策"""
        # 根据技能和权威度进行决策
        decision_making_power = self.authority * 0.7 + sum(self.skills.values()) * 0.3
        return {
            'type': decision_type,
            'power': decision_making_power,
            'context': context
        }
```

### 2.3 信仰系统 (Belief System)

```python
class BeliefSystem:
    def __init__(self, belief_id: int, name: str, pantheon: list):
        self.belief_id = belief_id
        self.name = name  # 如"自然崇拜"、"祖先崇拜"
        self.pantheon = pantheon  # 祗列表
        self.doctrines = {}  # 教义
        self.practices = []  # 实践仪式
        self.influence = 0  # 在部落中的影响力
        self.converts = []  # 皈依者列表
        
    def add_doctrine(self, doctrine_name: str, content: str):
        """添加教义"""
        self.doctrines[doctrine_name] = content
        
    def convert_member(self, member):
        """皈依成员"""
        if member not in self.converts:
            self.converts.append(member)
            self.influence += 1
```

### 2.4 文化属性 (Culture)

```python
class Culture:
    def __init__(self, culture_id: int, name: str, tribe: Tribe):
        self.culture_id = culture_id
        self.name = name
        self.tribe = tribe
        self.values = {}  # {'family': 8, 'honor': 6, 'innovation': 4}
        self.traditions = []  # 传统习俗
        self.art_forms = []  # 艺术形式
        self.language = "proto"  # 语言发展阶段
        self.customs = {}  # 习俗字典
        
    def evolve(self, external_influence: float = 0):
        """文化演化"""
        # 根据外部影响和文化内部互动演化
        evolution_rate = 0.1 + external_influence * 0.05
        for value in self.values.values():
            value += random.uniform(-evolution_rate, evolution_rate)
            value = max(0, min(10, value))  # 限制在0-10范围内
```

### 2.5 成员 (Member)

```python
class Member:
    def __init__(self, member_id: int, name: str, age: int, gender: str, tribe: Tribe):
        self.member_id = member_id
        self.name = name
        self.age = age
        self.gender = gender
        self.tribe = tribe
        self.profession = "gatherer"  # 职业
        self.skills = {}  # {'hunting': int, 'crafting': int, 'healing': int}
        self.beliefs = []  # 信仰列表
        self.relationships = {}  # 与其他成员的关系
        self.contribution = 0  # 对部落的贡献值
        self.personality_traits = {}  # 性格特质
        
    def learn_skill(self, skill_name: str, amount: int):
        """学习技能"""
        self.skills[skill_name] = self.skills.get(skill_name, 0) + amount
        
    def contribute_to_tribe(self, contribution_type: str, amount: int):
        """贡献部落"""
        self.contribution += amount
        # 更新部落资源
        if contribution_type in self.tribe.resources:
            self.tribe.resources[contribution_type] += amount
```

## 3. 关系系统

### 3.1 部落间关系

```python
class TribalRelationship:
    def __init__(self, tribe1: Tribe, tribe2: Tribe):
        self.tribe1 = tribe1
        self.tribe2 = tribe2
        self.relationship_type = "neutral"  # ally, neutral, enemy, trading
        self.trade_agreements = []  # 贸易协议
        self.conflicts = []  # 冲突历史
        self.alliance_strength = 0  # 联盟强度
        
    def update_relationship(self, event_type: str, impact: float):
        """根据事件更新关系"""
        if event_type == "trade":
            self.relationship_type = "trading"
            self.alliance_strength += impact
        elif event_type == "conflict":
            self.relationship_type = "enemy"
            self.alliance_strength -= impact
```

### 3.2 社会阶层

```python
class SocialHierarchy:
    def __init__(self, tribe: Tribe):
        self.tribe = tribe
        self.classes = {
            'chief': [],  # 首领
            'elder': [],  # 长老
            'warrior': [],  # 战士
            'craftsman': [],  # 工匠
            'farmer': [],  # 农夫
            'gatherer': [],  # 采集者
            'child': []   # 儿童
        }
        
    def promote_member(self, member: Member, new_class: str):
        """提升成员阶层"""
        if member in self.classes.get(member.profession, []):
            self.classes[member.profession].remove(member)
        if new_class in self.classes:
            self.classes[new_class].append(member)
            member.profession = new_class
```

## 4. 动态系统

### 4.1 社会演化

```python
class SocialEvolution:
    @staticmethod
    def evolve_tribe(tribe: Tribe, external_factors: dict):
        """部落社会演化"""
        # 人口增长
        growth_rate = tribe.resources.get('food', 0) * 0.01
        tribe.population = int(tribe.population * (1 + growth_rate))
        
        # 技术发展
        if tribe.resources.get('tools', 0) > 50:
            tribe.technology_level += 0.1
            
        # 关系演化
        for other_tribe_id, relationship in tribe.relationships.items():
            if relationship > 20:
                tribe.relationships[other_tribe_id] = min(100, relationship + 1)
            elif relationship < -20:
                tribe.relationships[other_tribe_id] = max(-100, relationship - 1)
```

### 4.2 传播系统

```python
class DiffusionSystem:
    @staticmethod
    def spread_belief(belief: BeliefSystem, source_tribe: Tribe, target_tribe: Tribe):
        """信仰传播"""
        # 计算传播成功率
        source_influence = belief.influence * source_tribe.technology_level
        target_resistance = target_tribe.resources.get('tools', 0) * 0.1
        
        if source_influence > target_resistance:
            # 成功传播
            for member in target_tribe.members:
                if random.random() < 0.3:  # 30%成功率
                    if member not in belief.converts:
                        belief.converts.append(member)
```

## 5. 数据持久化

### 5.1 存储结构

```python
class SocialDataRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        
    def save_tribe(self, tribe: Tribe):
        """保存部落数据"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO tribes 
            (tribe_id, name, x, y, terrain, population, tech_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (tribe.tribe_id, tribe.name, tribe.location['x'], 
              tribe.location['y'], tribe.location['terrain'],
              tribe.population, tribe.technology_level))
        
    def load_tribe(self, tribe_id: int) -> Tribe:
        """加载部落数据"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tribes WHERE tribe_id = ?", (tribe_id,))
        row = cursor.fetchone()
        if row:
            return Tribe(row[0], row[1], {'x': row[2], 'y': row[3], 'terrain': row[4]})
        return None
```

## 6. 初始化示例

```python
# 创建初始部落
tribe1 = Tribe(1, "火焰部落", {'x': 100, 'y': 200, 'terrain': 'mountain'})
tribe2 = Tribe(2, "森林部落", {'x': 300, 'y': 150, 'terrain': 'forest'})

# 创建首领
chief1 = Chief(1, "雷石", tribe1)
chief1.skills = {'leadership': 80, 'diplomacy': 60, 'military': 70}

# 创建信仰系统
nature_worship = BeliefSystem(1, "自然崇拜", ["太阳神", "月亮神", "大地母"])
nature_worship.add_doctrine("生命循环", "一切生命都在自然循环中重生")

# 创建文化
tribe_culture = Culture(1, "山地文化", tribe1)
tribe_culture.values = {'family': 9, 'honor': 7, 'innovation': 3}

# 创建成员
member1 = Member(1, "阿火", 25, "male", tribe1)
member1.profession = "warrior"
member1.learn_skill("combat", 70)

# 初始化关系
relationship = TribalRelationship(tribe1, tribe2)
relationship.relationship_type = "neutral"
```

## 7. 系统集成

社会结构模型将与以下系统集成：
- 经济系统：资源分配和贸易
- 地形系统：部落选址和扩张
- 外交系统：部落间互动和谈判
- 技术系统：工具制作和知识传承

这个设计提供了完整的社会结构框架，支持复杂的社会互动、文化演化和发展路径。