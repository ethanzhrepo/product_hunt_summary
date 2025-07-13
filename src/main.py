#!/usr/bin/env python3

import os
import sys
import logging
import asyncio
import argparse
import signal
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_manager import ConfigManager
from src.scheduler import ProductHuntScheduler

def setup_logging(config_manager: ConfigManager):
    """Setup logging configuration"""
    log_config = config_manager.get_logging_config()
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('file', 'logs/app.log')
    
    # 确保日志目录存在
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # 抑制一些第三方库的日志
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    logging.info(f"Logging system initialized - Level: {log_level}, File: {log_file}")

class Application:
    """Main application class"""
    
    def __init__(self):
        self.config_manager = None
        self.scheduler = None
        self.running = False
        self.stop_event = None
    
    def initialize(self, config_file: str = "config.yml"):
        """Initialize application"""
        try:
            # 加载配置
            self.config_manager = ConfigManager(config_file)
            
            # 设置日志
            setup_logging(self.config_manager)
            
            # 创建调度器
            self.scheduler = ProductHuntScheduler(self.config_manager)
            
            logging.info("Application initialization completed")
            return True
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    async def test_connections(self, silent: bool = False):
        """Test all connections"""
        if not self.scheduler:
            logging.error("Scheduler not initialized")
            return False
        
        success = await self.scheduler.test_connections(silent=silent)
        return success
    
    async def run_manual_task(self, task_type: str):
        """Run manual task"""
        if not self.scheduler:
            logging.error("Scheduler not initialized")
            return
        
        await self.scheduler.run_manual_task(task_type)
    
    async def run_daemon(self):
        """Run background daemon process"""
        if not self.scheduler:
            logging.error("Scheduler not initialized")
            return
        
        try:
            # 设置定时任务
            self.scheduler.setup_schedules()
            
            # 启动调度器
            self.scheduler.start()
            self.running = True
            
            # 显示任务信息
            jobs = self.scheduler.get_jobs()
            logging.info("Scheduled tasks configured:")
            for job in jobs:
                logging.info(f"  - {job['name']} (ID: {job['id']})")
                logging.info(f"    Next execution: {job['next_run_time']}")
            
            # 运行连接测试（静默模式，不发送消息到频道）
            logging.info("Running initial connection test...")
            await self.test_connections(silent=True)
            
            logging.info("Application startup completed, waiting for scheduled tasks...")
            logging.info("Press Ctrl+C to stop the program")
            
            # 保持程序运行 - 使用事件等待而不是循环
            self.stop_event = asyncio.Event()
            await self.stop_event.wait()
                
        except KeyboardInterrupt:
            logging.info("Received stop signal, shutting down application...")
        except Exception as e:
            logging.error(f"Runtime error: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown application"""
        self.running = False
        if self.stop_event:
            self.stop_event.set()
        if self.scheduler:
            self.scheduler.stop()
        logging.info("Application shutdown complete")
    
    def signal_handler(self, signum, frame):
        """Signal handler"""
        logging.info(f"Received signal {signum}, shutting down...")
        self.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Product Hunt Summary Automation')
    parser.add_argument('--config', '-c', default='config.yml', help='Configuration file path')
    parser.add_argument('--test', action='store_true', help='Test all connections')
    parser.add_argument('--manual', choices=['daily', 'weekly', 'monthly'], help='Manually execute specified task')
    
    args = parser.parse_args()
    
    # 创建应用实例
    app = Application()
    
    # 初始化
    if not app.initialize(args.config):
        sys.exit(1)
    
    # 设置信号处理
    signal.signal(signal.SIGINT, app.signal_handler)
    signal.signal(signal.SIGTERM, app.signal_handler)
    
    try:
        if args.test:
            # 测试连接
            success = await app.test_connections()
            sys.exit(0 if success else 1)
        
        elif args.manual:
            # 手动执行任务
            await app.run_manual_task(args.manual)
            sys.exit(0)
        
        else:
            # 运行守护进程
            await app.run_daemon()
    
    except Exception as e:
        logging.error(f"Program exited with exception: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # 检查Python版本
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required")
        sys.exit(1)
    
    # 运行主程序
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Program startup failed: {e}")
        sys.exit(1)