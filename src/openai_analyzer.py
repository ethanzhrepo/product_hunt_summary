import logging
from openai import OpenAI
from typing import List, Dict, Any
from .ai_analyzer import AIAnalyzer
from .locales import get_text, get_ai_language

logger = logging.getLogger(__name__)

class OpenAIAnalyzer(AIAnalyzer):
    """OpenAI API analyzer for product content analysis and summary generation"""
    
    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o-mini", language: str = "zh"):
        """
        Initialize OpenAI analyzer
        
        Args:
            api_key: OpenAI API key
            base_url: API base URL
            model: Model name to use
            language: Output language code
        """
        super().__init__(language)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
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
                'summary': f"{analysis_failed_text}: {str(e)}",
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
{instruction.format(period_name=period_name)}:

{products_summary}

Please generate a summary in the following format:
{format_text}

Requirements:
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
    
    def _generate_summary(self, product_text: str) -> str:
        """Generate product summary"""
        # Get multilingual text
        instruction = get_text(self.language, 'summary_instruction', 'Please generate a concise summary based on the following product information (within 50 words)')
        requirements = get_text(self.language, 'summary_product_requirements', [])
        summary_expert_role = get_text(self.language, 'summary_expert_role', 'You are a product summary expert.')
        
        requirements_text = "\n".join([f"- {req}" for req in requirements])
        
        prompt = f"""
{instruction}:

{product_text}

Requirements:
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
        """Extract product highlights"""
        # Get multilingual text
        instruction = get_text(self.language, 'highlights_instruction', 'Please extract 3-5 core highlights based on the following product information (each highlight within 15 words)')
        
        prompt = f"""
{instruction}:

{product_text}

Please return as a list, one highlight per line, format:
- Highlight 1
- Highlight 2
- Highlight 3
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
            elif line and not line.startswith('Please') and not line.startswith('Based'):
                highlights.append(line)
        
        return highlights[:5]  # Maximum 5 highlights
    
    def _categorize_product(self, product_text: str) -> str:
        """Product categorization"""
        # Get multilingual category options
        categories = get_text(self.language, 'categories', {})
        category_list = "\n".join([f"- {cat}" for cat in categories.values()])
        
        prompt = f"""
Please categorize the product into the most appropriate category based on the following product information:

{product_text}

Available categories:
{category_list}

Please return only the category name, no explanation needed.
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
    
    def _extract_use_cases(self, product_text: str) -> List[str]:
        """Extract product use cases"""
        instruction = get_text(self.language, 'use_cases_instruction', 'Please describe 2-3 main use cases based on the following product information (15-20 words per scenario)')
        
        prompt = f"""
{instruction}:

{product_text}

Please return as a list, one use case per line, format:
- Use case 1
- Use case 2
- Use case 3
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
            elif line and not line.startswith('Please') and not line.startswith('Based'):
                use_cases.append(line)
        
        return use_cases[:3]  # Maximum 3 use cases
    
    def _analyze_target_audience(self, product_text: str) -> str:
        """Analyze target audience"""
        instruction = get_text(self.language, 'target_audience_instruction', 'Please describe the target audience based on the following product information (within 30 words)')
        
        prompt = f"""
{instruction}:

{product_text}

Please return only the audience description, no explanation needed.
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