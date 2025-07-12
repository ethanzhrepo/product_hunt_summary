#!/bin/bash

# Product Hunt Summary 项目环境设置脚本
# 使用conda创建独立的Python环境

set -e  # 遇到错误立即退出

echo "🚀 开始设置Product Hunt Summary项目环境..."

# 检查conda是否已安装
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: conda未安装。请先安装Anaconda或Miniconda。"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 当前工作目录: $SCRIPT_DIR"

# 环境名称
ENV_NAME="product_hunt_summary"

# 检查环境是否已存在
if conda env list | grep -q "^$ENV_NAME "; then
    echo "⚠️  环境 '$ENV_NAME' 已存在。"
    read -p "是否要删除现有环境并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  删除现有环境..."
        conda env remove -n "$ENV_NAME" -y
    else
        echo "❌ 取消安装。"
        exit 1
    fi
fi

# 创建conda环境
echo "🏗️  创建conda环境: $ENV_NAME"
conda env create -f environment.yml

# 激活环境
echo "🔄 激活环境..."
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# 验证安装
echo "✅ 验证安装..."
python --version
pip list | grep -E "(openai|telegram|apscheduler|pyyaml|requests)"

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，填入必要的API密钥和配置信息："
    echo "   - PH_DEV_TOKEN: Product Hunt开发者令牌"
    echo "   - DEEPSEEK_API_KEY: DeepSeek API密钥"
    echo "   - TELEGRAM_BOT_TOKEN: Telegram机器人令牌"
    echo "   - TELEGRAM_CHANNEL_ID: Telegram频道ID"
else
    echo "✅ 环境变量文件已存在"
fi

echo ""
echo "🎉 环境设置完成！"
echo ""
echo "接下来的步骤："
echo "1. 编辑 .env 文件，填入API密钥和配置"
echo "2. 运行 ./start.sh 启动应用"
echo ""
echo "手动激活环境命令:"
echo "   conda activate $ENV_NAME"
echo ""
echo "查看配置说明:"
echo "   cat .env.example"