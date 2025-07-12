import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from typing import List, Dict, Any, Optional
from .locales import get_text

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot responsible for sending messages to channels"""
    
    def __init__(self, bot_token: str, channel_id: str, language: str = "zh"):
        """
        Initialize Telegram bot
        
        Args:
            bot_token: Telegram bot token
            channel_id: Channel ID or username (e.g. @channelname or -1001234567890)
            language: Output language code
        """
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.language = language
    
    async def send_message(self, text: str, parse_mode: str = 'Markdown') -> Optional[int]:
        """
        Send message to channel
        
        Args:
            text: Message text
            parse_mode: Parse mode, supports 'Markdown' or 'HTML'
            
        Returns:
            Message ID, returns None if sending fails
        """
        try:
            message = await self.bot.send_message(
                chat_id=self.channel_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=False
            )
            logger.info(f"Message sent successfully, message ID: {message.message_id}")
            return message.message_id
        
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")
            return None
        except Exception as e:
            logger.error(f"Unknown error occurred while sending message: {e}")
            return None
    
    async def pin_message(self, message_id: int) -> bool:
        """
        Pin message
        
        Args:
            message_id: Message ID to pin
            
        Returns:
            Whether pinning was successful
        """
        try:
            await self.bot.pin_chat_message(
                chat_id=self.channel_id,
                message_id=message_id,
                disable_notification=True
            )
            logger.info(f"Message pinned successfully, message ID: {message_id}")
            return True
        
        except TelegramError as e:
            logger.error(f"Failed to pin message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unknown error occurred while pinning message: {e}")
            return False
    
    async def send_product_message(self, product_analysis: Dict[str, Any], period_type: str) -> Optional[int]:
        """
        Send single product analysis message
        
        Args:
            product_analysis: Product analysis result
            period_type: Period type ('daily', 'weekly', 'monthly')
            
        Returns:
            Message ID
        """
        # 获取多语言文本
        prefix = get_text(self.language, f'{period_type}_prefix', '📱')
        category_label = get_text(self.language, 'category_label', '分类')
        votes_label = get_text(self.language, 'votes_label', '票数')
        highlights_label = get_text(self.language, 'highlights_label', '核心亮点')
        view_details = get_text(self.language, 'view_details', '查看详情')
        use_cases_label = get_text(self.language, 'use_cases_label', '应用场景')
        target_audience_label = get_text(self.language, 'target_audience_label', '目标用户')
        
        name = product_analysis['name']
        summary = product_analysis['summary']
        category = product_analysis['category']
        votes = product_analysis['analysis_metadata']['votes_count']
        url = product_analysis['analysis_metadata']['url']
        highlights = product_analysis.get('highlights', [])
        use_cases = product_analysis.get('use_cases', [])
        target_audience = product_analysis.get('target_audience', '')
        original_tagline = product_analysis.get('original_tagline', '')
        
        # 构建产品标题（限制描述长度避免过长）
        if original_tagline and len(original_tagline.strip()) > 0:
            # 限制tagline长度，避免消息过长
            description = original_tagline[:50] + '...' if len(original_tagline) > 50 else original_tagline
            product_title = f"📝 【{name}：{description}】"
        else:
            # 如果没有tagline，只显示产品名
            product_title = f"📝 【{name}】"
        
        # 构建消息文本
        message_parts = [
            product_title,
            f"",
            f"{prefix}",
            f"",
            f"{summary}",
            f"",
        ]
        
        # 添加亮点
        if highlights:
            message_parts.append(f"✨ {highlights_label}：")
            for highlight in highlights[:3]:  # 最多显示3个亮点
                message_parts.append(f"• {highlight}")
            message_parts.append("")
        
        # 添加应用场景
        if use_cases:
            message_parts.append(f"🎯 {use_cases_label}：")
            for use_case in use_cases[:2]:  # 最多显示2个应用场景
                message_parts.append(f"• {use_case}")
            message_parts.append("")
        
        # 添加目标用户
        if target_audience:
            message_parts.append(f"👥 {target_audience_label}：{target_audience}")
            message_parts.append("")
        
        # 添加分类和票数
        message_parts.extend([
            f"🏷️ {category_label}：{category}",
            f"👍 {votes_label}：{votes}",
        ])
        
        # 添加链接
        message_parts.extend([
            "",
            f"🔗 [{view_details}]({url})"
        ])
        
        message_text = "\n".join(message_parts)
        
        return await self.send_message(message_text)
    
    async def send_directory_message(self, analyzed_products: List[Dict[str, Any]], 
                                   period_type: str, period_summary: str) -> Optional[int]:
        """
        发送目录消息（包含周期总结）
        
        Args:
            analyzed_products: 分析后的产品列表
            period_type: 周期类型 ('daily', 'weekly', 'monthly')
            period_summary: 周期总结
            
        Returns:
            消息ID
        """
        # 获取多语言文本
        emoji = get_text(self.language, f'{period_type}_prefix', '📱').split()[0]  # 提取emoji
        title = get_text(self.language, f'{period_type}_title', '产品目录')
        product_directory = get_text(self.language, 'product_directory', '产品目录')
        
        # 构建目录消息
        message_parts = [
            f"{emoji} **{title}**",
            f"",
            f"📋 **{product_directory}：**"
        ]
        
        # 添加产品列表
        display_limit = 10 if period_type == 'daily' else 20
        for i, product in enumerate(analyzed_products[:display_limit], 1):
            name = product['name']
            category = product['category']
            votes = product['analysis_metadata']['votes_count']
            url = product['analysis_metadata']['url']
            
            message_parts.append(f"{i:2d}. [{name}]({url}) | {category} | 👍{votes}")
        
        # 添加总结
        trend_summary = get_text(self.language, 'trend_summary', '趋势总结')
        total_products = get_text(self.language, 'total_products', '个产品')
        data_source = get_text(self.language, 'data_source', '数据来源：Product Hunt')
        
        message_parts.extend([
            "",
            f"📊 **{trend_summary}：**",
            period_summary,
            "",
            f"📱 共 {len(analyzed_products)} {total_products} | {data_source}"
        ])
        
        message_text = "\n".join(message_parts)
        
        return await self.send_message(message_text)
    
    async def send_directory_message_with_links(self, analyzed_products: List[Dict[str, Any]], 
                                              period_type: str, period_summary: str,
                                              message_mapping: Dict[str, int]) -> Optional[int]:
        """
        发送带内部链接的目录消息（产品名称链接到对应的详细消息）
        
        Args:
            analyzed_products: 分析后的产品列表
            period_type: 周期类型 ('daily', 'weekly', 'monthly')
            period_summary: 周期总结
            message_mapping: 产品名到消息ID的映射
            
        Returns:
            消息ID
        """
        # 获取多语言文本
        emoji = get_text(self.language, f'{period_type}_prefix', '📱').split()[0]  # 提取emoji
        title = get_text(self.language, f'{period_type}_title', '产品目录')
        product_directory = get_text(self.language, 'product_directory', '产品目录')
        
        # 构建目录消息
        message_parts = [
            f"{emoji} **{title}**",
            f"",
            f"📋 **{product_directory}：**"
        ]
        
        # 添加产品列表（带内部链接）
        display_limit = 10 if period_type == 'daily' else 20
        for i, product in enumerate(analyzed_products[:display_limit], 1):
            name = product['name']
            category = product['category']
            votes = product['analysis_metadata']['votes_count']
            
            # 如果有消息ID，创建内部链接
            if name in message_mapping:
                msg_id = message_mapping[name]
                # 创建Telegram内部链接（需要从频道ID中提取数字部分）
                channel_id = self.channel_id
                if channel_id.startswith('@'):
                    # 如果是用户名格式，暂时使用产品名称（无法创建内部链接）
                    product_link = f"**{name}**"
                elif channel_id.startswith('-100'):
                    # 超级群组ID格式，移除-100前缀
                    numeric_id = channel_id[4:]
                    product_link = f"[{name}](https://t.me/c/{numeric_id}/{msg_id})"
                else:
                    product_link = f"**{name}**"
            else:
                product_link = f"**{name}**"
            
            message_parts.append(f"{i:2d}. {product_link} | {category} | 👍{votes}")
        
        # 添加总结
        trend_summary = get_text(self.language, 'trend_summary', '趋势总结')
        total_products = get_text(self.language, 'total_products', '个产品')
        data_source = get_text(self.language, 'data_source', '数据来源：Product Hunt')
        
        message_parts.extend([
            "",
            f"📊 **{trend_summary}：**",
            period_summary,
            "",
            f"📱 共 {len(analyzed_products)} {total_products} | {data_source}"
        ])
        
        message_text = "\n".join(message_parts)
        
        return await self.send_message(message_text)
    
    async def send_daily_reports(self, analyzed_products: List[Dict[str, Any]], 
                               period_summary: str) -> List[int]:
        """
        发送每日报告（所有产品消息 + 目录消息）
        
        Args:
            analyzed_products: 分析后的产品列表
            period_summary: 周期总结
            
        Returns:
            消息ID列表
        """
        message_ids = []
        
        # 发送目录消息（先发送，用于置顶）
        directory_msg_id = await self.send_directory_message(
            analyzed_products, 'daily', period_summary
        )
        if directory_msg_id:
            message_ids.append(directory_msg_id)
            # 置顶目录消息
            await self.pin_message(directory_msg_id)
        
        # 等待10秒再发送产品消息，避免Telegram限流
        await asyncio.sleep(10)
        
        # 发送单个产品消息
        for product in analyzed_products:
            msg_id = await self.send_product_message(product, 'daily')
            if msg_id:
                message_ids.append(msg_id)
            # 避免发送过快，Telegram限流保护
            await asyncio.sleep(10)
        
        return message_ids
    
    async def send_weekly_reports(self, analyzed_products: List[Dict[str, Any]], 
                                period_summary: str) -> List[int]:
        """
        发送每周报告
        
        Args:
            analyzed_products: 分析后的产品列表
            period_summary: 周期总结
            
        Returns:
            消息ID列表
        """
        message_ids = []
        
        # 发送目录消息
        directory_msg_id = await self.send_directory_message(
            analyzed_products, 'weekly', period_summary
        )
        if directory_msg_id:
            message_ids.append(directory_msg_id)
            await self.pin_message(directory_msg_id)
        
        await asyncio.sleep(10)
        
        # 发送单个产品消息
        for product in analyzed_products:
            msg_id = await self.send_product_message(product, 'weekly')
            if msg_id:
                message_ids.append(msg_id)
            await asyncio.sleep(10)
        
        return message_ids
    
    async def send_monthly_reports(self, analyzed_products: List[Dict[str, Any]], 
                                 period_summary: str) -> List[int]:
        """
        发送每月报告
        
        Args:
            analyzed_products: 分析后的产品列表
            period_summary: 周期总结
            
        Returns:
            消息ID列表
        """
        message_ids = []
        
        # 发送目录消息
        directory_msg_id = await self.send_directory_message(
            analyzed_products, 'monthly', period_summary
        )
        if directory_msg_id:
            message_ids.append(directory_msg_id)
            await self.pin_message(directory_msg_id)
        
        await asyncio.sleep(10)
        
        # 发送单个产品消息
        for product in analyzed_products:
            msg_id = await self.send_product_message(product, 'monthly')
            if msg_id:
                message_ids.append(msg_id)
            await asyncio.sleep(10)
        
        return message_ids
    
    async def test_connection(self) -> bool:
        """
        测试机器人连接和权限
        
        Returns:
            是否连接成功
        """
        try:
            # 获取机器人信息
            bot_info = await self.bot.get_me()
            logger.info(f"机器人连接成功: {bot_info.first_name} (@{bot_info.username})")
            
            # 测试发送消息
            connection_test = get_text(self.language, 'connection_test', '机器人连接测试成功！')
            test_msg = await self.send_message(f"🤖 {connection_test}")
            if test_msg:
                logger.info("测试消息发送成功")
                return True
            else:
                logger.error("测试消息发送失败")
                return False
        
        except Exception as e:
            logger.error(f"机器人连接测试失败: {e}")
            return False