#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分词器模块
支持多种中文分词器：jieba、THULAC、HanLP
"""

# 导入基础类和异常
from .tokenizers.base import (
    BaseTokenizer,
    TokenizerError,
    TokenizerInitError, 
    TokenizerProcessError
)

# 导入具体分词器实现
from .tokenizers.jieba_tokenizer import JiebaTokenizer
from .tokenizers.thulac_tokenizer import ThulacTokenizer
from .tokenizers.hanlp_tokenizer import HanlpTokenizer

# 导入工厂类
from .tokenizers.factory import TokenizerFactory

# 导出的便捷函数
from .tokenizers.factory import (
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