import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .locales import get_text

logger = logging.getLogger(__name__)

class AIAnalyzer(ABC):
    """Base class for AI analyzers"""
    
    def __init__(self, language: str = "zh"):
        """
        Initialize AI analyzer
        
        Args:
            language: Output language code
        """
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
    
    @abstractmethod
    def analyze_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze single product, generate summary and analysis
        
        Args:
            product: Product information dictionary
            
        Returns:
            Dictionary containing analysis results
        """
        pass
    
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
    
    @abstractmethod
    def generate_period_summary(self, analyzed_products: List[Dict[str, Any]], period_type: str) -> str:
        """
        Generate periodic summary (daily/weekly/monthly)
        
        Args:
            analyzed_products: List of analyzed products
            period_type: Period type ('daily', 'weekly', 'monthly')
            
        Returns:
            Summary text
        """
        pass
    
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
Product Name: {product['name']}
Tagline: {product['tagline']}
Description: {product.get('description', 'No detailed description')}
Category Tags: {topics_str}
Vote Count: {product['votes_count']}
Comments Count: {product['comments_count']}
Website: {product.get('website', 'No website')}{comments_str}
"""
    
    def _format_products_for_summary(self, analyzed_products: List[Dict[str, Any]]) -> str:
        """Format product list for summary"""
        products_text = []
        
        # Determine display count based on product count: show all for daily (10), top 20 for weekly/monthly
        display_count = len(analyzed_products) if len(analyzed_products) <= 10 else 20
        for i, product in enumerate(analyzed_products[:display_count], 1):
            category_label = get_text(self.language, 'category_label', 'Category')
            votes_label = get_text(self.language, 'votes_label', 'Votes')
            
            product_info = f"""
{i}. {product['name']}
   {category_label}: {product['category']}
   Summary: {product['summary']}
   {votes_label}: {product['analysis_metadata']['votes_count']}
"""
            products_text.append(product_info)
        
        return "\n".join(products_text)