import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any
from .locales import is_language_supported

class ConfigManager:
    """配置管理器，负责加载和管理应用配置"""
    
    def __init__(self, config_file: str = "config.yml"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        # 加载环境变量
        load_dotenv()
        
        # 读取YAML配置文件
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        # 替换环境变量
        self._replace_env_vars(self._config)
    
    def _replace_env_vars(self, obj):
        """递归替换配置中的环境变量"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self._replace_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = self._replace_env_vars(item)
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    def get(self, key_path: str, default=None):
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，支持点分割，如 'product_hunt.api_url'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_product_hunt_config(self) -> Dict[str, Any]:
        """获取Product Hunt配置"""
        return self.get('product_hunt', {})
    
    def get_deepseek_config(self) -> Dict[str, Any]:
        """获取DeepSeek配置"""
        return self.get('deepseek', {})
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """获取Telegram配置"""
        return self.get('telegram', {})
    
    def get_scheduling_config(self) -> Dict[str, Any]:
        """获取调度配置"""
        return self.get('scheduling', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})
    
    def get_language_config(self) -> Dict[str, Any]:
        """获取语言配置"""
        config = self.get('language', {})
        
        # 设置默认值
        if 'output_language' not in config:
            config['output_language'] = 'zh'
        if 'ai_system_language' not in config:
            config['ai_system_language'] = 'Chinese'
        
        # 验证语言代码
        if not is_language_supported(config['output_language']):
            config['output_language'] = 'zh'  # 回退到中文
        
        return config
    
    def get_output_language(self) -> str:
        """获取输出语言代码"""
        return self.get_language_config().get('output_language', 'zh')
    
    def get_ai_system_language(self) -> str:
        """获取AI系统语言描述"""
        return self.get_language_config().get('ai_system_language', 'Chinese')