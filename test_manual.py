#!/usr/bin/env python3

"""
Product Hunt Summary 手动测试脚本
用于单独执行日、周、月任务的测试脚本
"""

import os
import sys
import logging
import asyncio
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config_manager import ConfigManager
from src.scheduler import ProductHuntScheduler

def setup_logging():
    """设置日志配置"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # 抑制第三方库日志
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)

async def run_task(task_type: str, config_file: str = "config.yml"):
    """
    运行指定的任务
    
    Args:
        task_type: 任务类型 ('daily', 'weekly', 'monthly', 'test', 'all')
        config_file: 配置文件路径
    """
    try:
        # 初始化配置管理器
        config_manager = ConfigManager(config_file)
        
        # 创建调度器
        scheduler = ProductHuntScheduler(config_manager)
        
        print(f"🚀 开始执行 {task_type} 任务...")
        print("=" * 50)
        
        if task_type == 'test':
            # 执行连接测试（非静默模式，会发送测试消息）
            print("🔧 执行连接测试...")
            success = await scheduler.test_connections(silent=False)
            if success:
                print("✅ 所有连接测试通过")
            else:
                print("❌ 部分连接测试失败，请检查配置")
                
        elif task_type == 'daily':
            # 执行每日任务
            print("📅 执行每日任务：获取今日Product Hunt热门产品...")
            await scheduler.daily_task()
            print("✅ 每日任务执行完成")
            
        elif task_type == 'weekly':
            # 执行每周任务
            print("📊 执行每周任务：获取本周Product Hunt热门产品...")
            await scheduler.weekly_task()
            print("✅ 每周任务执行完成")
            
        elif task_type == 'monthly':
            # 执行每月任务
            print("📈 执行每月任务：获取本月Product Hunt热门产品...")
            await scheduler.monthly_task()
            print("✅ 每月任务执行完成")
            
        elif task_type == 'all':
            # 执行所有任务
            print("🎯 执行所有任务...")
            print("\n1. 连接测试...")
            await scheduler.test_connections(silent=False)
            
            print("\n2. 每日任务...")
            await scheduler.daily_task()
            
            print("\n3. 每周任务...")
            await scheduler.weekly_task()
            
            print("\n4. 每月任务...")
            await scheduler.monthly_task()
            
            print("✅ 所有任务执行完成")
            
        else:
            print(f"❌ 未知的任务类型: {task_type}")
            return False
            
        print("=" * 50)
        print("🎉 任务执行成功完成！")
        return True
        
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        logging.error(f"任务执行失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Product Hunt Summary 手动测试脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python test_manual.py --daily              # 执行每日任务
  python test_manual.py --weekly             # 执行每周任务  
  python test_manual.py --monthly            # 执行每月任务
  python test_manual.py --test               # 执行连接测试
  python test_manual.py --all                # 执行所有任务
  python test_manual.py --daily --config custom.yml  # 使用自定义配置文件
        """
    )
    
    # 任务类型参数（互斥）
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument('--daily', '-d', action='store_true', help='执行每日任务')
    task_group.add_argument('--weekly', '-w', action='store_true', help='执行每周任务')
    task_group.add_argument('--monthly', '-m', action='store_true', help='执行每月任务')
    task_group.add_argument('--test', '-t', action='store_true', help='执行连接测试')
    task_group.add_argument('--all', '-a', action='store_true', help='执行所有任务')
    
    # 配置文件参数
    parser.add_argument('--config', '-c', default='config.yml', help='配置文件路径（默认: config.yml）')
    
    args = parser.parse_args()
    
    # 检查Python版本
    if sys.version_info < (3, 9):
        print("错误: 需要Python 3.9或更高版本")
        sys.exit(1)
    
    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        print(f"错误: 配置文件 '{args.config}' 不存在")
        sys.exit(1)
    
    # 设置日志
    setup_logging()
    
    # 确定任务类型
    if args.daily:
        task_type = 'daily'
    elif args.weekly:
        task_type = 'weekly'
    elif args.monthly:
        task_type = 'monthly'
    elif args.test:
        task_type = 'test'
    elif args.all:
        task_type = 'all'
    
    print(f"Product Hunt Summary 手动测试脚本")
    print(f"任务类型: {task_type}")
    print(f"配置文件: {args.config}")
    print("")
    
    # 运行任务
    try:
        success = asyncio.run(run_task(task_type, args.config))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()