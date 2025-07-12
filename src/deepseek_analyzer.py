import logging
import asyncio
from openai import OpenAI
from typing import List, Dict, Any
from .locales import get_text, get_ai_language

logger = logging.getLogger(__name__)

class DeepSeekAnalyzer:
    """DeepSeek API analyzer for product content analysis and summary generation"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-chat", language: str = "zh"):
        """
        Initialize DeepSeek analyzer
        
        Args:
            api_key: DeepSeek API key
            base_url: API base URL
            model: Model name to use
            language: Output language code
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.language = language
    
    def _create_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """
        Create text progress bar
        
        Args:
            current: Current progress
            total: Total count
            width: Progress bar width
            
        Returns:
            Progress bar string
        """
        percentage = current / total
        filled = int(width * percentage)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {current}/{total} ({percentage:.0%})"
    
    def analyze_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze single product, generate summary and analysis
        
        Args:
            product: Product information dictionary
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Build product description text
            product_text = self._format_product_for_analysis(product)
            
            # Generate product analysis and summary
            summary = self._generate_summary(product_text)
            highlights = self._extract_highlights(product_text)
            category = self._categorize_product(product_text)
            use_cases = self._extract_use_cases(product_text)
            target_audience = self._analyze_target_audience(product_text)
            
            return {
                'product_id': product['id'],
                'name': product['name'],
                'original_tagline': product['tagline'],
                'summary': summary,
                'highlights': highlights,
                'category': category,
                'use_cases': use_cases,
                'target_audience': target_audience,
                'analysis_metadata': {
                    'votes_count': product['votes_count'],
                    'topics': product['topics'],
                    'url': product['url']
                }
            }
        
        except Exception as e:
            logger.error(f"Product analysis failed {product.get('name', 'Unknown')}: {e}")
            analysis_failed_text = get_text(self.language, 'analysis_failed', 'Analysis failed')
            unknown_category = get_text(self.language, 'categories', {}).get('other', 'Unknown')
            return {
                'product_id': product['id'],
                'name': product['name'],
                'original_tagline': product['tagline'],
                'summary': f"{analysis_failed_text}：{str(e)}",
                'highlights': [],
                'category': unknown_category,
                'use_cases': [],
                'target_audience': '',
                'analysis_metadata': {
                    'votes_count': product['votes_count'],
                    'topics': product['topics'],
                    'url': product['url']
                }
            }
    
    async def analyze_products_batch(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch analyze product list (async, with progress bar and delays)
        
        Args:
            products: Product list
            
        Returns:
            Analysis results list
        """
        analyzed_products = []
        total_count = len(products)
        
        if total_count == 0:
            logger.warning("No products to analyze")
            return analyzed_products
        
        # Calculate estimated time
        estimated_time = (total_count - 1) * 30 / 60  # minutes
        logger.info(f"Starting batch analysis of {total_count} products")
        logger.info(f"Estimated total time: {estimated_time:.1f} minutes (30 seconds interval per product)")
        
        for i, product in enumerate(products, 1):
            try:
                # Show progress bar
                progress_bar = self._create_progress_bar(i, total_count)
                remaining_time = (total_count - i) * 30 / 60
                
                logger.info(f"Analyzing product {progress_bar} - Remaining time: {remaining_time:.1f} minutes")
                logger.info(f"Current product: {product.get('name', 'Unknown')}")
                
                # Analyze product
                analysis = self.analyze_product(product)
                analyzed_products.append(analysis)
                
                logger.info(f"✅ Completed: {product.get('name', 'Unknown')}")
                
                # Delay 30 seconds (except for last product)
                if i < total_count:
                    logger.info(f"Waiting 30 seconds before continuing...")
                    await asyncio.sleep(30)
                    
            except Exception as e:
                product_name = product.get('name', 'Unknown')
                logger.error(f"❌ Product analysis failed {product_name}: {e}")
                
                # Create failed analysis result but continue processing other products
                analysis_failed_text = get_text(self.language, 'analysis_failed', 'Analysis failed')
                unknown_category = get_text(self.language, 'categories', {}).get('other', 'Unknown')
                
                analyzed_products.append({
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
                })
                
                # Wait even if failed, to avoid rate limiting
                if i < total_count:
                    logger.info(f"Waiting 30 seconds before continuing...")
                    await asyncio.sleep(30)
        
        logger.info(f"🎉 Batch analysis completed! Successfully processed {len(analyzed_products)} products")
        return analyzed_products
    
    def generate_period_summary(self, analyzed_products: List[Dict[str, Any]], period_type: str) -> str:
        """
        Generate periodic summary (daily/weekly/monthly)
        
        Args:
            analyzed_products: List of analyzed products
            period_type: Period type ('daily', 'weekly', 'monthly')
            
        Returns:
            Summary text
        """
        try:
            # Build summary prompt
            products_summary = self._format_products_for_summary(analyzed_products)
            
            # Get multilingual text
            period_name = get_text(self.language, f'{period_type}_period', 'this period')
            instruction = get_text(self.language, 'period_summary_instruction', 'Please generate a concise summary report based on the following {period_name} Product Hunt trending products')
            analysis_format = get_text(self.language, 'analysis_format', [])
            requirements = get_text(self.language, 'summary_requirements', [])
            
            # Build format instructions
            format_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(analysis_format)])
            requirements_text = "\n".join([f"- {req}" for req in requirements])
            
            prompt = f"""
{instruction.format(period_name=period_name)}：

{products_summary}

请按以下格式生成总结：
{format_text}

要求：
{requirements_text}
"""

            # Get system role description
            analyst_role = get_text(self.language, 'analyst_role', 'You are a professional product analyst.')
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": analyst_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Period summary generation failed: {e}")
            failed_text = get_text(self.language, f'{period_type}_task_failed', 'Task execution failed')
            return f"{failed_text}: {str(e)}"
    
    def _format_product_for_analysis(self, product: Dict[str, Any]) -> str:
        """Format product information for analysis"""
        topics_str = ", ".join(product.get('topics', []))
        
        # Format comment information
        comments_str = ""
        comments = product.get('comments', [])
        if comments:
            comments_str = "\nUser Comments:\n"
            for i, comment in enumerate(comments[:3], 1):  # Show at most 3 comments
                user_name = comment.get('user_name', 'Anonymous')
                comment_body = comment.get('body', '').strip()
                if comment_body:
                    comments_str += f"  {i}. {user_name}: {comment_body}\n"
        
        return f"""
产品名称: {product['name']}
标语: {product['tagline']}
描述: {product.get('description', '无详细描述')}
分类标签: {topics_str}
获得票数: {product['votes_count']}
评论数: {product['comments_count']}
官网: {product.get('website', '无官网')}{comments_str}
"""
    
    def _generate_summary(self, product_text: str) -> str:
        """生成产品摘要"""
        # 获取多语言文本
        instruction = get_text(self.language, 'summary_instruction', '请基于以下产品信息，生成一个简洁的摘要（50字以内）')
        requirements = get_text(self.language, 'summary_product_requirements', [])
        summary_expert_role = get_text(self.language, 'summary_expert_role', 'You are a product summary expert.')
        
        requirements_text = "\n".join([f"- {req}" for req in requirements])
        
        prompt = f"""
{instruction}：

{product_text}

要求：
{requirements_text}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": summary_expert_role},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
    
    def _extract_highlights(self, product_text: str) -> List[str]:
        """提取产品亮点"""
        # 获取多语言文本
        instruction = get_text(self.language, 'highlights_instruction', '请基于以下产品信息，提取3-5个核心亮点（每个亮点15字以内）')
        
        prompt = f"""
{instruction}：

{product_text}

请以列表形式返回，每个亮点一行，格式如：
- 亮点1
- 亮点2
- 亮点3
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_text(self.language, 'categorization_expert_role', 'You are a product analyst.')},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        highlights = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                highlights.append(line[2:])
            elif line and not line.startswith('请') and not line.startswith('以下'):
                highlights.append(line)
        
        return highlights[:5]  # 最多5个亮点
    
    def _categorize_product(self, product_text: str) -> str:
        """产品分类"""
        # 获取多语言类别选项
        categories = get_text(self.language, 'categories', {})
        category_list = "\n".join([f"- {cat}" for cat in categories.values()])
        
        prompt = f"""
请基于以下产品信息，将产品归类到最合适的一个类别：

{product_text}

可选类别：
{category_list}

请只返回类别名称，不需要解释。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_text(self.language, 'categorization_expert_role', 'You are a product categorization expert.')},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
    
    def _format_products_for_summary(self, analyzed_products: List[Dict[str, Any]]) -> str:
        """格式化产品列表用于总结"""
        products_text = []
        
        # 根据产品数量确定显示数量：daily显示全部(10个)，weekly/monthly显示前20个
        display_count = len(analyzed_products) if len(analyzed_products) <= 10 else 20
        for i, product in enumerate(analyzed_products[:display_count], 1):
            category_label = get_text(self.language, 'category_label', '类别')
            votes_label = get_text(self.language, 'votes_label', '票数')
            
            product_info = f"""
{i}. {product['name']}
   {category_label}: {product['category']}
   摘要: {product['summary']}
   {votes_label}: {product['analysis_metadata']['votes_count']}
"""
            products_text.append(product_info)
        
        return "\n".join(products_text)
    
    def _extract_use_cases(self, product_text: str) -> List[str]:
        """提取产品应用场景"""
        instruction = get_text(self.language, 'use_cases_instruction', '请基于以下产品信息，描述2-3个主要应用场景（每个场景15-20字）')
        
        prompt = f"""
{instruction}：

{product_text}

请以列表形式返回，每个应用场景一行，格式如：
- 场景1
- 场景2
- 场景3
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_text(self.language, 'categorization_expert_role', 'You are a product analyst.')},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        use_cases = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                use_cases.append(line[2:])
            elif line and not line.startswith('请') and not line.startswith('以下'):
                use_cases.append(line)
        
        return use_cases[:3]  # 最多3个应用场景
    
    def _analyze_target_audience(self, product_text: str) -> str:
        """分析目标用户群体"""
        instruction = get_text(self.language, 'target_audience_instruction', '请基于以下产品信息，描述目标用户群体（30字以内）')
        
        prompt = f"""
{instruction}：

{product_text}

请只返回用户群体描述，不需要解释。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_text(self.language, 'categorization_expert_role', 'You are a product categorization expert.')},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()