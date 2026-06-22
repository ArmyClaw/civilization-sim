# 🏛️ Civilization Sim — 数字文明模拟器

> 模拟有经济、人口、资源、信仰、科技的虚拟文明，从采集野果到星际旅行。

## 在线地址

https://army-yorozuya.art/study/civilization-sim/

> ⚠️ 目前是项目展示页，Web 交互模拟器开发中。

## 完成进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| Phase 1 | 基础生态（地形、资源、人口） | ✅ 完成 |
| Phase 2 | 经济系统（分工、交换、货币） | ⏳ 进行中 |
| Phase 3 | 社会结构（部落、信仰、文化、冲突） | ✅ 完成 |
| Phase 4 | 科技树（20个节点，石器时代→信息时代） | ✅ 完成 |

## 源码结构

```
civilization-sim/
├── src/                        # 核心引擎
│   ├── terrain.py              # 地形系统（Perlin噪声生成、Tile类型）
│   ├── generator.py            # 地形+资源生成器
│   ├── agent.py                # 基础Agent（人口模型）
│   ├── agent_simple.py         # 简化Agent
│   ├── agent_with_trading.py   # 带交易的Agent
│   ├── agent_with_currency.py  # 带货币的Agent
│   ├── trading_system.py       # 交易系统
│   ├── currency_system.py      # 货币演化
│   ├── economy.py              # 经济系统
│   ├── tribe_system.py         # 部落形成
│   ├── faith_system.py         # 信仰体系
│   ├── conflict_system.py      # 冲突与战争
│   └── tech_system.py          # 科技树系统
├── demo_terrain.py             # 地形生成演示
├── tribe_formation_demo.py     # 部落形成演示
├── trading_demo.py             # 交易系统演示
├── conflict_demo.py            # 冲突系统演示
├── faith_demo.py               # 信仰系统演示
├── economy_demo.py             # 经济系统演示
└── test_*.py                   # 各模块测试
```

## 本地运行

```bash
# 地形生成
python3 demo_terrain.py

# 部落形成与社会演化
python3 tribe_formation_demo.py

# 交易与货币
python3 trading_demo.py

# 科技树集成
python3 src/tech_integration_example.py

# 冲突模拟
python3 conflict_demo.py

# 运行全部测试
python3 test_phase1_terrain.py
python3 test_tribe_implementation.py
python3 test_tech_system.py
```

## 技术栈

- **引擎**: Python 3（纯 Python，无外部依赖）
- **地形**: Perlin/Simplex 噪声
- **可视化**: 计划 Canvas/WebGL
- **在线部署**: 计划 FastAPI 后端 + 前端交互

## 下一步

- [ ] 完成经济系统（Phase 2）
- [ ] 修复 terrain 类型兼容性问题
- [ ] Web API 服务化
- [ ] Canvas 地图可视化
- [ ] 实时模拟器前端

🌱 2026-06-17 开工
