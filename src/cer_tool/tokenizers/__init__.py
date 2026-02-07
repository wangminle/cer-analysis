#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分词器模块 - CER-Analysis-Tool V2
支持多种中文分词器：jieba、THULAC、HanLP
"""

# 导入基础类和异常
from .base import (
    BaseTokenizer,
    TokenizerError,
    TokenizerInitError, 
    TokenizerProcessError
)

# 导入具体分词器实现
from .jieba_tokenizer import JiebaTokenizer
from .thulac_tokenizer import ThulacTokenizer
from .hanlp_tokenizer import HanlpTokenizer

# 导入工厂类
from .factory import TokenizerFactory

# 导出的便捷函数
from .factory import (
    get_available_tokenizers, 
    get_tokenizer, 
    get_tokenizer_info,
    get_cached_tokenizer_info
)

# 导出模块
__all__ = [
    'BaseTokenizer',
    'TokenizerError', 
    'TokenizerInitError',
    'TokenizerProcessError',
    'JiebaTokenizer',
    'ThulacTokenizer', 
    'HanlpTokenizer',
    'TokenizerFactory',
    'get_available_tokenizers',
    'get_tokenizer',
    'get_tokenizer_info',
    'get_cached_tokenizer_info'
]
