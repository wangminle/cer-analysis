"""
分词器抽象基类
定义所有分词器需要实现的统一接口
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any


class TokenizerError(Exception):
    """分词器基础异常类"""
    pass


class TokenizerInitError(TokenizerError):
    """分词器初始化异常"""
    pass


class TokenizerProcessError(TokenizerError):
    """分词器处理异常"""
    pass


class BaseTokenizer(ABC):
    """
    分词器抽象基类
    定义所有分词器必须实现的接口
    """
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Tokenizer', '').lower()
        self.is_initialized = False
        self.version = "unknown"
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化分词器
        
        Returns:
            bool: 初始化是否成功
            
        Raises:
            TokenizerInitError: 初始化失败时抛出
        """
        pass
    
    @abstractmethod
    def cut(self, text: str) -> List[str]:
        """
        基础分词功能
        
        Args:
            text (str): 待分词的文本
            
        Returns:
            List[str]: 分词结果列表
            
        Raises:
            TokenizerProcessError: 分词处理失败时抛出
        """
        pass
    
    @abstractmethod
    def posseg(self, text: str) -> List[Tuple[str, str]]:
        """
        词性标注功能
        
        Args:
            text (str): 待标注的文本
            
        Returns:
            List[Tuple[str, str]]: (词语, 词性)的元组列表
            
        Raises:
            TokenizerProcessError: 词性标注失败时抛出
        """
        pass
    
    @abstractmethod
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """
        精确分词，返回词语及其在原文中的位置
        
        Args:
            text (str): 待分词的文本
            
        Returns:
            List[Tuple[str, int, int]]: (词语, 开始位置, 结束位置)的元组列表
            
        Raises:
            TokenizerProcessError: 分词处理失败时抛出
        """
        pass
    
    def validate_text(self, text: str) -> str:
        """
        验证和预处理输入文本
        
        Args:
            text (str): 输入文本
            
        Returns:
            str: 验证后的文本
            
        Raises:
            TokenizerProcessError: 文本验证失败时抛出
        """
        if text is None:
            raise TokenizerProcessError("输入文本不能为None")
        
        if not isinstance(text, str):
            raise TokenizerProcessError(f"输入文本必须是字符串类型，当前类型: {type(text)}")
        
        # 清理文本：去除前后空格
        cleaned_text = text.strip()
        
        # 如果文本为空，返回空字符串
        if not cleaned_text:
            return ""
        
        return cleaned_text
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取分词器信息
        
        Returns:
            Dict[str, Any]: 包含分词器信息的字典
        """
        return {
            'name': self.name,
            'initialized': self.is_initialized,
            'version': self.version,
            'class_name': self.__class__.__name__
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', initialized={self.is_initialized})"
    
    def __repr__(self) -> str:
        return self.__str__() 