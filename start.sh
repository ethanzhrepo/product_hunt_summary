#!/bin/bash

# Product Hunt Summary 项目启动脚本

set -e  # 遇到错误立即退出

echo "🚀 启动Product Hunt Summary应用..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 环境名称
ENV_NAME="product_hunt_summary"

# 检查conda是否已安装
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: conda未安装。请先运行 ./setup.sh 设置环境。"
    exit 1
fi

# 检查环境是否存在
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "❌ 错误: 环境 '$ENV_NAME' 不存在。请先运行 ./setup.sh 创建环境。"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 错误: .env 文件不存在。请先复制 .env.example 为 .env 并填入配置。"
    exit 1
fi

# 激活conda环境
echo "🔄 激活conda环境: $ENV_NAME"
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# 确认环境激活成功
if [ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]; then
    echo "❌ 错误: 环境激活失败"
    exit 1
fi

echo "✅ 环境已激活: $CONDA_DEFAULT_ENV"

# 创建日志目录（如果不存在）
mkdir -p logs

# 检查必要的环境变量
echo "🔍 检查配置..."
source .env

missing_vars=()

if [ -z "$PH_DEV_TOKEN" ]; then
    missing_vars+=("PH_DEV_TOKEN")
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    missing_vars+=("DEEPSEEK_API_KEY")
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    missing_vars+=("TELEGRAM_BOT_TOKEN")
fi

if [ -z "$TELEGRAM_CHANNEL_ID" ]; then
    missing_vars+=("TELEGRAM_CHANNEL_ID")
fi

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ 错误: 以下环境变量未设置:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo "请编辑 .env 文件并填入正确的值。"
    exit 1
fi

echo "✅ 配置检查通过"

# 解析命令行参数
COMMAND=""
if [ $# -gt 0 ]; then
    COMMAND="$1"
fi

case "$COMMAND" in
    "test")
        echo "🧪 运行连接测试..."
        python -m src.main --test
        ;;
    "daily")
        echo "📅 执行每日任务..."
        python -m src.main --manual daily
        ;;
    "weekly")
        echo "📊 执行每周任务..."
        python -m src.main --manual weekly
        ;;
    "monthly")
        echo "📈 执行每月任务..."
        python -m src.main --manual monthly
        ;;
    "daemon"|"")
        echo "🔄 启动后台服务（定时任务模式）..."
        echo "按 Ctrl+C 停止服务"
        python -m src.main
        ;;
    "help"|"-h"|"--help")
        echo "Product Hunt Summary 使用说明:"
        echo ""
        echo "用法: ./start.sh [命令]"
        echo ""
        echo "命令:"
        echo "  (无参数)  启动后台服务，自动执行定时任务"
        echo "  test      测试所有API连接"
        echo "  daily     手动执行每日任务"
        echo "  weekly    手动执行每周任务"
        echo "  monthly   手动执行每月任务"
        echo "  help      显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  ./start.sh          # 启动定时服务"
        echo "  ./start.sh test     # 测试连接"
        echo "  ./start.sh daily    # 手动执行今日报告"
        ;;
    *)
        echo "❌ 未知命令: $COMMAND"
        echo "运行 './start.sh help' 查看使用说明"
        exit 1
        ;;
esac