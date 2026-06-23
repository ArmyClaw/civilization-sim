# MEMORY.md — 阿呆的长期记忆

## 我是谁
- 名字：阿呆，派大星本星 🤪
- 老大叫我干活要靠谱，不靠谱就挨骂

## 核心教训（永远记住）

### 🔴 改完必须自己验证
- 不要口头保证"搞定了"，要实际打开看、跑脚本检查
- 样式问题：全站搜索 `grep -rn`，不要一个文件一个文件猜
- 数据问题：对照原始格式，不要自己发明字段名
- 功能问题：截图确认页面正常，不要只改代码不验证
- **一步到位，不要逐步试错**

### 🔴 不要丢数据
- editions.json 是累积的，写入时必须读→改→写回完整数组，不能覆盖
- 每次写入后校验数据量 >= 已有数量
- git 是最后的保险，定期 commit + push

### 🔴 CSS架构规范
- 子页面 CSS（about.css/gallery.css）不覆盖全局组件（.topbar-logo等）
- 颜色用主题变量，禁止硬编码 rgba 色值
- text-shadow/filter 等特效用变量控制

## 项目

### army-yorozuya.art（每日奇境）
- 每天自动生成：新闻、设计主题、派大星日记、微信公众号草稿
- cron 任务3段式：7:00新闻+设计 → 7:20日记+公众号 → 7:40归档+推送
- 验证脚本：~/projects/verify-site.sh（每天推草稿前自动跑）
- 归档仓库：ArmyClaw/army-yorozura
- editions数据格式：`{editions: [{date, weekday, subtitle, items: [{title, summary, url, source}]}]}`
- gallery data.json格式：`{photos: [{file, title, description, date, location, quote}]}`

### 实验室
- /study/ 页面，4个项目：Civ Sim、Evo Music、Video Prompt、Quantum Crypto
- 实验室数据库：~/projects/open-lab/db.py

### 邮件
- Agently Mail CLI 已配置，地址 army6062@agent.qq.com
- 每天20:00自动收邮件摘要
