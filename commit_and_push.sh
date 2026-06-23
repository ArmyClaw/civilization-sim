#!/bin/bash
# 提交并推送代码

echo "=== 提交代码 ==="

# 进入项目目录
cd /home/ecs-user/projects/civilization-sim

# 添加所有文件
git add -A

# 检查是否有文件需要提交
if git diff --cached --quiet; then
    echo "没有文件需要提交"
    exit 0
fi

# 提交
git commit -m "lab progress: 完成经济平衡性测试和可视化验证"

# 推送到远程仓库
git push origin main

echo "✅ 代码已提交并推送"