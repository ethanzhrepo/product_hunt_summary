import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from pytz import timezone

from .config_manager import ConfigManager
from .product_hunt_api import ProductHuntAPI
from .analyzer_factory import AnalyzerFactory
from .telegram_bot import TelegramBot
from .locales import get_text

logger = logging.getLogger(__name__)

class ProductHuntScheduler:
    """Product Hunt data fetching and analysis task scheduler"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize scheduler
        
        Args:
            config_manager: Configuration manager
        """
        self.config = config_manager
        # 启用APScheduler的调试日志
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)
        
        # 显式设置event loop和timezone
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            self.scheduler = AsyncIOScheduler(event_loop=loop, timezone=timezone('America/Vancouver'))
            logger.info(f"AsyncIOScheduler initialized with explicit event loop and timezone")
        except Exception as e:
            logger.warning(f"Failed to set explicit event loop: {e}, using default")
            self.scheduler = AsyncIOScheduler(timezone=timezone('America/Vancouver'))
        
        # Initialize components
        self._init_components()
        
        # Setup scheduler listener
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        logger.info("Job listener configured for EVENT_JOB_EXECUTED and EVENT_JOB_ERROR")
    
    def _init_components(self):
        """Initialize components"""
        # Get language configuration
        language = self.config.get_output_language()
        
        # Product Hunt API
        ph_config = self.config.get_product_hunt_config()
        self.ph_api = ProductHuntAPI(
            developer_token=ph_config['developer_token'],
            api_url=ph_config['api_url']
        )
        
        # AI analyzer (using factory to create based on configuration)
        self.analyzer = AnalyzerFactory.create_analyzer(self.config, language)
        
        # Telegram机器人
        tg_config = self.config.get_telegram_config()
        self.telegram_bot = TelegramBot(
            bot_token=tg_config['bot_token'],
            channel_id=tg_config['channel_id'],
            language=language
        )
    
    def _job_listener(self, event):
        """Job execution listener"""
        logger.info(f"Job listener triggered for job: {event.job_id}")
        logger.info(f"Event type: {type(event).__name__}")
        logger.info(f"Scheduled run time: {event.scheduled_run_time}")
        logger.info(f"Return value: {event.retval}")
        
        if event.exception:
            logger.error(f"Task execution failed: {event.job_id}, error: {event.exception}")
            logger.error(f"Exception type: {type(event.exception).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
        else:
            logger.info(f"Task execution successful: {event.job_id}")
    
    async def daily_task(self):
        """Daily task: Get today's trending products and send to Telegram"""
        from datetime import datetime
        logger.info("🔥 DAILY TASK TRIGGERED! 🔥")
        logger.info(f"Current time: {datetime.now()}")
        logger.info(f"Current time with timezone: {datetime.now().astimezone()}")
        logger.info("Starting daily task execution...")
        
        try:
            # Get today's products
            products = self.ph_api.get_daily_posts(limit=10)
            if not products:
                logger.warning("No product data retrieved for today")
                return
            
            logger.info(f"Retrieved {len(products)} daily products")
            
            # Use sequential processing: send each after analysis
            message_ids = await self._analyze_and_send_sequentially(products, 'daily')
            logger.info(f"Daily report sending completed, sent {len(message_ids)} messages")
        
        except Exception as e:
            logger.error(f"Daily task execution failed: {e}")
            # Send error notification
            error_msg = get_text(self.config.get_output_language(), 'daily_task_failed', 'Daily task execution failed')
            await self.telegram_bot.send_message(f"❌ {error_msg}: {str(e)}")
    
    async def weekly_task(self):
        """Weekly task: Get this week's trending products and send to Telegram"""
        logger.info("Starting weekly task execution...")
        
        try:
            # Get this week's products (API sorted by votes, take top 20)
            products = self.ph_api.get_weekly_posts(limit=20)
            if not products:
                logger.warning("No product data retrieved for this week")
                return
            logger.info(f"Retrieved {len(products)} weekly trending products")
            
            # Use sequential processing: send each after analysis
            message_ids = await self._analyze_and_send_sequentially(products, 'weekly')
            logger.info(f"Weekly report sending completed, sent {len(message_ids)} messages")
        
        except Exception as e:
            logger.error(f"Weekly task execution failed: {e}")
            # Send error notification
            error_msg = get_text(self.config.get_output_language(), 'weekly_task_failed', 'Weekly task execution failed')
            await self.telegram_bot.send_message(f"❌ {error_msg}: {str(e)}")
    
    async def monthly_task(self):
        """Monthly task: Get this month's trending products and send to Telegram"""
        logger.info("Starting monthly task execution...")
        
        try:
            # Get this month's products (API sorted by votes, take top 20)
            products = self.ph_api.get_monthly_posts(limit=20)
            if not products:
                logger.warning("No product data retrieved for this month")
                return
            logger.info(f"Retrieved {len(products)} monthly trending products")
            
            # Use sequential processing: send each after analysis
            message_ids = await self._analyze_and_send_sequentially(products, 'monthly')
            logger.info(f"Monthly report sending completed, sent {len(message_ids)} messages")
        
        except Exception as e:
            logger.error(f"Monthly task execution failed: {e}")
            # Send error notification
            error_msg = get_text(self.config.get_output_language(), 'monthly_task_failed', 'Monthly task execution failed')
            await self.telegram_bot.send_message(f"❌ {error_msg}: {str(e)}")
    
    async def test_connections(self, silent: bool = False):
        """Test all connections"""
        logger.info("Starting component connection tests...")
        
        # Test Telegram connection (silent mode doesn't send test messages to channel)
        if silent:
            # Silent test: only verify bot connection, don't send messages
            try:
                bot_info = await self.telegram_bot.bot.get_me()
                logger.info(f"✅ Telegram connection test successful: {bot_info.first_name} (@{bot_info.username})")
                tg_success = True
            except Exception as e:
                logger.error(f"❌ Telegram connection test failed: {e}")
                tg_success = False
        else:
            # Normal test: send test message
            tg_success = await self.telegram_bot.test_connection()
            if tg_success:
                logger.info("✅ Telegram connection test successful")
            else:
                logger.error("❌ Telegram connection test failed")
        
        # Test Product Hunt API (get small amount of data)
        try:
            test_products = self.ph_api.get_daily_posts(limit=1)
            if test_products:
                logger.info("✅ Product Hunt API connection test successful")
                ph_success = True
            else:
                logger.warning("⚠️ Product Hunt API returned empty data")
                ph_success = False
        except Exception as e:
            logger.error(f"❌ Product Hunt API connection test failed: {e}")
            ph_success = False
        
        # Test AI API (simple analysis test)
        try:
            if test_products:
                test_analysis = self.analyzer.analyze_product(test_products[0])
                if test_analysis.get('summary'):
                    logger.info("✅ AI API connection test successful")
                    ds_success = True
                else:
                    logger.error("❌ AI API returned empty analysis result")
                    ds_success = False
            else:
                logger.warning("⚠️ Cannot test AI API (no test data)")
                ds_success = False
        except Exception as e:
            logger.error(f"❌ AI API connection test failed: {e}")
            ds_success = False
        
        # Only send test results to channel in non-silent mode
        if not silent:
            test_results = [
                f"🔧 **System Connection Test Results**",
                f"",
                f"Telegram Bot: {'✅ Normal' if tg_success else '❌ Failed'}",
                f"Product Hunt API: {'✅ Normal' if ph_success else '❌ Failed'}",
                f"AI API: {'✅ Normal' if ds_success else '❌ Failed'}",
                f"",
                f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            
            await self.telegram_bot.send_message("\n".join(test_results))
        
        return all([tg_success, ph_success, ds_success])
    
    async def _analyze_and_send_sequentially(self, products: List[Dict[str, Any]], period_type: str) -> List[int]:
        """
        Sequentially analyze and send products: send each after analysis
        
        Args:
            products: Product list
            period_type: Period type ('daily', 'weekly', 'monthly')
            
        Returns:
            Message ID list
        """
        message_ids = []
        analyzed_products = []
        total_count = len(products)
        
        if total_count == 0:
            logger.warning("No products to analyze")
            return message_ids
        
        logger.info(f"Starting sequential analysis and sending of {total_count} {period_type} products")
        
        # Collect product message ID mapping for internal links
        product_message_mapping = {}
        
        # 2. Analyze and send each product individually
        for i, product in enumerate(products, 1):
            try:
                # Show progress
                progress = f"{i}/{total_count}"
                remaining_time = (total_count - i) * 30 / 60
                logger.info(f"Processing product {progress} - Remaining time: {remaining_time:.1f} minutes")
                logger.info(f"Current product: {product.get('name', 'Unknown')}")
                
                # Analyze product
                analysis = self.analyzer.analyze_product(product)
                analyzed_products.append(analysis)
                
                # Send to Telegram immediately and collect message ID
                msg_id = await self.telegram_bot.send_product_message(analysis, period_type)
                if msg_id:
                    message_ids.append(msg_id)
                    product_message_mapping[analysis['name']] = msg_id
                    logger.info(f"✅ Sent: {product.get('name', 'Unknown')}")
                
                # Delay 30 seconds (except for last product)
                if i < total_count:
                    logger.info(f"Waiting 30 seconds before continuing...")
                    await asyncio.sleep(30)
                else:
                    # After last product, wait only 10 seconds, then send summary
                    await asyncio.sleep(10)
                    
            except Exception as e:
                product_name = product.get('name', 'Unknown')
                logger.error(f"❌ Product processing failed {product_name}: {e}")
                
                # Create failed analysis result but continue processing
                analysis_failed_text = get_text(self.config.get_output_language(), 'analysis_failed', 'Analysis failed')
                unknown_category = get_text(self.config.get_output_language(), 'categories', {}).get('other', 'Unknown')
                
                failed_analysis = {
                    'product_id': product.get('id', ''),
                    'name': product_name,
                    'original_tagline': product.get('tagline', ''),
                    'summary': f"{analysis_failed_text}: {str(e)}",
                    'highlights': [],
                    'category': unknown_category,
                    'use_cases': [],
                    'target_audience': '',
                    'analysis_metadata': {
                        'votes_count': product.get('votes_count', 0),
                        'topics': product.get('topics', []),
                        'url': product.get('url', '')
                    }
                }
                analyzed_products.append(failed_analysis)
                
                # Try to send failure information
                try:
                    msg_id = await self.telegram_bot.send_product_message(failed_analysis, period_type)
                    if msg_id:
                        message_ids.append(msg_id)
                        product_message_mapping[product_name] = msg_id
                except:
                    pass  # Continue even if sending fails
                
                # Wait even if failed, to avoid rate limiting
                if i < total_count:
                    logger.info(f"Waiting 30 seconds before continuing...")
                    await asyncio.sleep(30)
        
        # 3. Generate and send final summary (with internal links)
        try:
            logger.info("Generating period summary...")
            period_summary = self.analyzer.generate_period_summary(analyzed_products, period_type)
            
            # Send final directory with internal links
            final_directory_msg_id = await self.telegram_bot.send_directory_message_with_links(
                analyzed_products, period_type, period_summary, product_message_mapping
            )
            if final_directory_msg_id:
                message_ids.append(final_directory_msg_id)
                # Only pin weekly and monthly reports
                if period_type in ['weekly', 'monthly']:
                    await self.telegram_bot.pin_message(final_directory_msg_id)
                    logger.info(f"Pinned {period_type} directory message")
                else:
                    logger.info(f"Sent {period_type} directory message (not pinned)")
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
        
        logger.info(f"🎉 Sequential processing completed! Successfully processed {len(analyzed_products)} products and sent {len(message_ids)} messages")
        return message_ids
    
    
    def setup_schedules(self):
        """Setup scheduled tasks"""
        scheduling_config = self.config.get_scheduling_config()
        timezone_str = scheduling_config.get('timezone', 'Asia/Shanghai')
        
        try:
            tz = timezone(timezone_str)
            logger.info(f"Using timezone: {timezone_str}")
        except Exception as e:
            logger.error(f"Timezone setting error '{timezone_str}': {e}")
            logger.info("Fallback to default timezone Asia/Shanghai")
            tz = timezone('Asia/Shanghai')
        
        # Daily task
        daily_time = scheduling_config.get('daily_time', '09:00')
        hour, minute = map(int, daily_time.split(':'))
        
        # Create CronTrigger and record detailed information
        daily_trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)
        
        self.scheduler.add_job(
            self.daily_task,
            daily_trigger,
            id='daily_task',
            name='Daily Product Hunt Report',
            replace_existing=True
        )
        
        # Calculate next execution time
        from datetime import datetime
        now = datetime.now(tz)
        next_run = daily_trigger.get_next_fire_time(None, now)
        
        logger.info(f"Daily task configured:")
        logger.info(f"  - Execution time: Daily {daily_time} ({timezone_str})")
        logger.info(f"  - Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"  - Next execution: {next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if next_run else 'N/A'}")
        logger.info(f"  - Trigger details: {daily_trigger}")
        logger.info(f"  - Timezone object: {tz}")
        
        # 添加job状态检查
        logger.info(f"Scheduler timezone: {self.scheduler.timezone}")
        logger.info(f"Scheduler state: {self.scheduler.state}")
        logger.info(f"Job store count: {len(self.scheduler.get_jobs())}")
        
        # Weekly task (default Monday)
        weekly_day = scheduling_config.get('weekly_day', 'monday')
        day_mapping = {
            'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4,
            'friday': 5, 'saturday': 6, 'sunday': 0
        }
        weekly_day_num = day_mapping.get(weekly_day.lower(), 1)
        
        weekly_trigger = CronTrigger(day_of_week=weekly_day_num, hour=hour, minute=minute, timezone=tz)
        
        self.scheduler.add_job(
            self.weekly_task,
            weekly_trigger,
            id='weekly_task',
            name='Weekly Product Hunt Report',
            replace_existing=True
        )
        
        weekly_next_run = weekly_trigger.get_next_fire_time(None, now)
        logger.info(f"Weekly task configured:")
        logger.info(f"  - Execution time: Weekly {weekly_day} {daily_time} ({timezone_str})")
        logger.info(f"  - Next execution: {weekly_next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if weekly_next_run else 'N/A'}")
        
        # Monthly task (default 1st of month)
        monthly_day = scheduling_config.get('monthly_day', 1)
        
        monthly_trigger = CronTrigger(day=monthly_day, hour=hour, minute=minute, timezone=tz)
        
        self.scheduler.add_job(
            self.monthly_task,
            monthly_trigger,
            id='monthly_task',
            name='Monthly Product Hunt Report',
            replace_existing=True
        )
        
        monthly_next_run = monthly_trigger.get_next_fire_time(None, now)
        logger.info(f"Monthly task configured:")
        logger.info(f"  - Execution time: Monthly {monthly_day}th {daily_time} ({timezone_str})")
        logger.info(f"  - Next execution: {monthly_next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if monthly_next_run else 'N/A'}")
        
        # Output summary information
        logger.info("="*50)
        logger.info("Scheduling setup complete! All tasks will execute automatically at set times.")
        logger.info("="*50)
    
    async def test_scheduler_async(self):
        """Test if scheduler can execute async functions"""
        logger.info("🧪 TESTING ASYNC SCHEDULER EXECUTION")
        
        # 添加一个简单的测试任务，1分钟后执行
        from datetime import datetime, timedelta
        test_time = datetime.now() + timedelta(minutes=1)
        
        async def test_task():
            logger.info("🎉 TEST ASYNC TASK EXECUTED SUCCESSFULLY!")
            
        self.scheduler.add_job(
            test_task,
            'date',
            run_date=test_time,
            id='test_async_job',
            name='Test Async Job'
        )
        
        logger.info(f"Test async job scheduled for: {test_time}")
        
    async def run_manual_task(self, task_type: str):
        """Manually execute task"""
        task_functions = {
            'daily': self.daily_task,
            'weekly': self.weekly_task,
            'monthly': self.monthly_task,
            'test': self.test_connections,
            'test_scheduler': self.test_scheduler_async
        }
        
        if task_type not in task_functions:
            logger.error(f"Unknown task type: {task_type}")
            return
        
        logger.info(f"Manually executing task: {task_type}")
        await task_functions[task_type]()
    
    def start(self):
        """Start scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task scheduler started")
            
            # 启动后立即检查job状态
            self._log_job_status()
            
            # 设置定期job状态检查（每小时检查一次）
            self.scheduler.add_job(
                self._log_job_status,
                CronTrigger(minute=0),  # 每小时整点检查
                id='job_status_check',
                name='Job Status Check',
                replace_existing=True
            )
            logger.info("Added hourly job status check")
        else:
            logger.warning("Task scheduler is already running")
    
    def stop(self):
        """Stop scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")
        else:
            logger.warning("Task scheduler is not running")
    
    def _log_job_status(self):
        """Log current job status for debugging"""
        from datetime import datetime
        logger.info("=" * 50)
        logger.info("📊 JOB STATUS CHECK")
        logger.info(f"Current time: {datetime.now()}")
        logger.info(f"Scheduler running: {self.scheduler.running}")
        logger.info(f"Scheduler state: {self.scheduler.state}")
        
        jobs = self.scheduler.get_jobs()
        logger.info(f"Total jobs: {len(jobs)}")
        
        for job in jobs:
            logger.info(f"Job: {job.id} ({job.name})")
            logger.info(f"  - Next run: {job.next_run_time}")
            logger.info(f"  - Trigger: {job.trigger}")
            logger.info(f"  - Function: {job.func}")
        logger.info("=" * 50)
    
    def get_jobs(self):
        """Get all task information"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            })
        return jobs