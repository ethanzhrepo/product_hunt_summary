"""
多语言资源文件
支持中文、英文、日文、韩文、西班牙文、法文、德文
"""

# 语言映射：配置代码 -> AI系统语言描述
LANGUAGE_MAPPING = {
    'zh': 'Chinese',
    'en': 'English', 
    'ja': 'Japanese',
    'ko': 'Korean',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German'
}

# 多语言文本资源
LOCALES = {
    'zh': {
        # 消息标签
        'category_label': '分类',
        'votes_label': '票数', 
        'highlights_label': '核心亮点',
        'view_details': '查看详情',
        'trend_summary': '趋势总结',
        'total_products': '个产品',
        'data_source': '数据来源：Product Hunt',
        'use_cases_label': '应用场景',
        'target_audience_label': '目标用户',
        
        # 周期标识
        'daily_prefix': '🌅 日top',
        'weekly_prefix': '📅 周top',
        'monthly_prefix': '📊 月top',
        
        # 周期标题
        'daily_title': '今日Product Hunt热门产品',
        'weekly_title': '本周Product Hunt热门产品', 
        'monthly_title': '本月Product Hunt热门产品',
        'product_directory': '产品目录',
        
        # 周期名称（用于AI分析）
        'daily_period': '今日',
        'weekly_period': '本周',
        'monthly_period': '本月',
        
        # AI系统角色
        'analyst_role': '你是一个专业的产品分析师，擅长分析科技产品趋势并生成简洁的中文报告。',
        'summary_expert_role': '你是一个产品摘要专家，擅长用简洁的中文描述产品核心价值。',
        'categorization_expert_role': '你是一个产品分类专家。',
        
        # AI提示词模板
        'period_summary_instruction': '请基于以下{period_name}Product Hunt热门产品信息，生成一份简洁的中文总结报告',
        'summary_instruction': '请基于以下产品信息，生成一个详细的中文摘要（100-150字）',
        'highlights_instruction': '请基于以下产品信息，提取3-5个核心亮点（每个亮点20-25字）',
        'detailed_analysis_instruction': '请基于以下产品信息，生成详细的产品分析',
        'use_cases_instruction': '请基于以下产品信息，描述2-3个主要应用场景（每个场景15-20字）',
        'target_audience_instruction': '请基于以下产品信息，描述目标用户群体（30字以内）',
        
        # 要求说明
        'summary_requirements': [
            '使用中文',
            '简洁明了，重点突出', 
            '适合在Telegram频道发布',
            '总长度控制在500字以内'
        ],
        
        'summary_product_requirements': [
            '突出产品的核心功能和价值',
            '使用通俗易懂的语言',
            '适合在社交媒体分享',
            '包含产品的创新点和亮点',
            '说明产品解决的问题或满足的需求'
        ],
        
        'detailed_analysis_requirements': [
            '分析产品的技术特色和创新点',
            '评估产品的市场潜力',
            '描述产品的核心价值主张',
            '使用专业但易懂的语言'
        ],
        
        # 分析格式要求
        'analysis_format': [
            '整体趋势分析（100字以内）',
            '热门分类统计',
            '值得关注的亮点产品（3-5个，使用#产品名格式标记）', 
            '技术发展趋势观察'
        ],
        
        # 产品分类
        'categories': {
            'ai_tools': 'AI工具',
            'dev_tools': '开发工具',
            'design_tools': '设计工具',
            'productivity': '生产力工具',
            'social': '社交应用',
            'ecommerce': '电商工具',
            'marketing': '营销工具',
            'education': '教育工具',
            'health_fitness': '健康健身',
            'gaming': '游戏娱乐',
            'fintech': '金融科技',
            'other': '其他'
        },
        
        # 错误消息
        'daily_task_failed': '每日任务执行失败',
        'weekly_task_failed': '每周任务执行失败',
        'monthly_task_failed': '每月任务执行失败',
        'analysis_failed': '分析失败',
        'connection_test': '机器人连接测试成功！'
    },
    
    'en': {
        # Message labels
        'category_label': 'Category',
        'votes_label': 'Votes',
        'highlights_label': 'Key Highlights', 
        'view_details': 'View Details',
        'trend_summary': 'Trend Summary',
        'total_products': 'products',
        'data_source': 'Data Source: Product Hunt',
        'use_cases_label': 'Use Cases',
        'target_audience_label': 'Target Audience',
        
        # Period prefixes
        'daily_prefix': '🌅 Daily Top',
        'weekly_prefix': '📅 Weekly Top',
        'monthly_prefix': '📊 Monthly Top',
        
        # Period titles
        'daily_title': 'Today\'s Product Hunt Hot Products',
        'weekly_title': 'This Week\'s Product Hunt Hot Products',
        'monthly_title': 'This Month\'s Product Hunt Hot Products',
        'product_directory': 'Product Directory',
        
        # Period names (for AI analysis)
        'daily_period': 'today\'s',
        'weekly_period': 'this week\'s',
        'monthly_period': 'this month\'s',
        
        # AI system roles
        'analyst_role': 'You are a professional product analyst who excels at analyzing tech product trends and generating concise English reports.',
        'summary_expert_role': 'You are a product summary expert who excels at describing product core value concisely in English.',
        'categorization_expert_role': 'You are a product categorization expert.',
        
        # AI prompt templates
        'period_summary_instruction': 'Please generate a concise English summary report based on the following {period_name} Product Hunt hot products information',
        'summary_instruction': 'Please generate a detailed English summary (100-150 words) based on the following product information',
        'highlights_instruction': 'Please extract 3-5 key highlights based on the following product information (20-25 words each)',
        'detailed_analysis_instruction': 'Please generate detailed product analysis based on the following product information',
        'use_cases_instruction': 'Please describe 2-3 main use cases based on the following product information (15-20 words each)',
        'target_audience_instruction': 'Please describe the target audience based on the following product information (within 30 words)',
        
        # Requirements
        'summary_requirements': [
            'Use English',
            'Concise and focused',
            'Suitable for Telegram channel publishing', 
            'Control total length within 500 words'
        ],
        
        'summary_product_requirements': [
            'Highlight product\'s core functionality and value',
            'Use easy-to-understand language',
            'Suitable for social media sharing',
            'Include product innovations and highlights',
            'Explain problems solved or needs met'
        ],
        
        'detailed_analysis_requirements': [
            'Analyze technical features and innovations',
            'Evaluate market potential',
            'Describe core value proposition',
            'Use professional but accessible language'
        ],
        
        # Analysis format
        'analysis_format': [
            'Overall trend analysis (within 100 words)',
            'Popular category statistics',
            'Notable highlighted products (3-5 items, use #ProductName format)',
            'Technology development trend observations'
        ],
        
        # Product categories
        'categories': {
            'ai_tools': 'AI Tools',
            'dev_tools': 'Developer Tools', 
            'design_tools': 'Design Tools',
            'productivity': 'Productivity Tools',
            'social': 'Social Apps',
            'ecommerce': 'E-commerce Tools',
            'marketing': 'Marketing Tools',
            'education': 'Education Tools',
            'health_fitness': 'Health & Fitness',
            'gaming': 'Gaming & Entertainment',
            'fintech': 'FinTech',
            'other': 'Other'
        },
        
        # Error messages
        'daily_task_failed': 'Daily task execution failed',
        'weekly_task_failed': 'Weekly task execution failed', 
        'monthly_task_failed': 'Monthly task execution failed',
        'analysis_failed': 'Analysis failed',
        'connection_test': 'Bot connection test successful!'
    },
    
    'ja': {
        # Message labels
        'category_label': 'カテゴリ',
        'votes_label': '票数',
        'highlights_label': '主要なハイライト',
        'view_details': '詳細を見る',
        'trend_summary': 'トレンド要約',
        'total_products': '個の製品',
        'data_source': 'データソース：Product Hunt',
        'use_cases_label': '使用例',
        'target_audience_label': '対象ユーザー',
        
        # Period prefixes  
        'daily_prefix': '🌅 今日のトップ',
        'weekly_prefix': '📅 今週のトップ',
        'monthly_prefix': '📊 今月のトップ',
        
        # Period titles
        'daily_title': '今日のProduct Hunt人気製品',
        'weekly_title': '今週のProduct Hunt人気製品', 
        'monthly_title': '今月のProduct Hunt人気製品',
        'product_directory': '製品ディレクトリ',
        
        # Period names (for AI analysis)
        'daily_period': '今日の',
        'weekly_period': '今週の',
        'monthly_period': '今月の',
        
        # AI system roles
        'analyst_role': 'あなたは技術製品のトレンドを分析し、簡潔な日本語レポートを生成することに長けた専門の製品アナリストです。',
        'summary_expert_role': 'あなたは製品の核心価値を簡潔な日本語で説明することに長けた製品要約の専門家です。',
        'categorization_expert_role': 'あなたは製品分類の専門家です。',
        
        # AI prompt templates
        'period_summary_instruction': '以下の{period_name}Product Hunt人気製品情報に基づいて、簡潔な日本語要約レポートを生成してください',
        'summary_instruction': '以下の製品情報に基づいて、詳細な日本語要約（100-150文字）を生成してください',
        'highlights_instruction': '以下の製品情報に基づいて、3-5個の主要なハイライト（各20-25文字）を抽出してください',
        'detailed_analysis_instruction': '以下の製品情報に基づいて、詳細な製品分析を生成してください',
        'use_cases_instruction': '以下の製品情報に基づいて、2-3個の主要な使用例を記述してください（各15-20文字）',
        'target_audience_instruction': '以下の製品情報に基づいて、対象ユーザーを記述してください（30文字以内）',
        
        # Requirements
        'summary_requirements': [
            '日本語を使用',
            '簡潔で要点を絞った内容',
            'Telegramチャンネル投稿に適している',
            '総文字数を500文字以内に制御'
        ],
        
        'summary_product_requirements': [
            '製品の核心機能と価値を強調',
            '理解しやすい言語を使用',
            'ソーシャルメディア共有に適している',
            '製品の革新性とハイライトを含む',
            '解決する問題や満たすニーズを説明'
        ],
        
        'detailed_analysis_requirements': [
            '技術的特徴と革新性を分析',
            '市場ポテンシャルを評価',
            'コア価値提案を記述',
            '専門的だが理解しやすい言語を使用'
        ],
        
        # Analysis format
        'analysis_format': [
            '全体的なトレンド分析（100文字以内）',
            '人気カテゴリ統計',
            '注目すべき注目製品（3-5個，#製品名形式を使用）',
            '技術発展トレンド観察'
        ],
        
        # Product categories
        'categories': {
            'ai_tools': 'AIツール',
            'dev_tools': '開発ツール',
            'design_tools': 'デザインツール', 
            'productivity': '生産性ツール',
            'social': 'ソーシャルアプリ',
            'ecommerce': 'Eコマースツール',
            'marketing': 'マーケティングツール',
            'education': '教育ツール',
            'health_fitness': 'ヘルス＆フィットネス',
            'gaming': 'ゲーム＆エンターテイメント',
            'fintech': 'フィンテック',
            'other': 'その他'
        },
        
        # Error messages
        'daily_task_failed': '日次タスクの実行に失敗しました',
        'weekly_task_failed': '週次タスクの実行に失敗しました',
        'monthly_task_failed': '月次タスクの実行に失敗しました',
        'analysis_failed': '分析に失敗しました',
        'connection_test': 'ボット接続テスト成功！'
    }
}

def get_text(language_code: str, key: str, default: str = '') -> str:
    """
    获取指定语言的文本
    
    Args:
        language_code: 语言代码 (zh, en, ja, etc.)
        key: 文本键名
        default: 默认值
        
    Returns:
        本地化文本
    """
    if language_code not in LOCALES:
        language_code = 'zh'  # 默认使用中文
    
    return LOCALES.get(language_code, {}).get(key, default)

def get_ai_language(language_code: str) -> str:
    """
    获取AI系统使用的语言描述
    
    Args:
        language_code: 语言代码
        
    Returns:
        AI系统语言描述
    """
    return LANGUAGE_MAPPING.get(language_code, 'Chinese')

def get_available_languages() -> list:
    """获取支持的语言列表"""
    return list(LOCALES.keys())

def is_language_supported(language_code: str) -> bool:
    """检查语言是否支持"""
    return language_code in LOCALES