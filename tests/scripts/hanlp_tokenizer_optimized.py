#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HanLP分词器 - 优化版
专门用于分词功能，预下载模型，本地缓存
"""

import os
import time
import threading
from typing import List, Optional, Tuple, Dict, Any


class HanLPTokenizerOptimized:
    """
    优化版HanLP分词器
    特点：
    1. 只加载分词（tok）模型
    2. 预下载并缓存模型到本地
    3. 高性能，适合生产环境
    """
    
    # 类级别的共享实例，实现单例模式
    _shared_tokenizer = None
    _initialization_lock = threading.Lock()
    _is_initialized = False
    
    def __init__(self):
        self.name = "hanlp"
        self.hanlp = None
        self.tokenizer = None
        self.model_name = None
        
    @classmethod 
    def get_instance(cls):
        """获取单例实例"""
        if cls._shared_tokenizer is None:
            with cls._initialization_lock:
                if cls._shared_tokenizer is None:
                    cls._shared_tokenizer = cls()
        return cls._shared_tokenizer
    
    def is_available(self) -> bool:
        """检查HanLP是否可用"""
        try:
            import hanlp
            return True
        except ImportError:
            return False
    
    def initialize(self) -> bool:
        """
        初始化HanLP分词器
        只加载分词模型，不加载其他NLP任务模型
        """
        if self._is_initialized:
            return True
            
        try:
            with self._initialization_lock:
                if self._is_initialized:
                    return True
                
                print("正在初始化HanLP分词器（仅加载分词模型）...")
                
                # 导入HanLP
                import hanlp
                self.hanlp = hanlp
                
                # 推荐的分词模型配置（按优先级排序）
                tokenizer_configs = [
                    {
                        'model': 'COARSE_ELECTRA_SMALL_ZH',
                        'desc': '粗粒度ELECTRA小模型',
                        'size': '45MB',
                        'performance': 'F1: 98.36%',
                        'suitable_for': '通用分词，性能优异'
                    },
                    {
                        'model': 'FINE_ELECTRA_SMALL_ZH', 
                        'desc': '细粒度ELECTRA小模型',
                        'size': '45MB',
                        'performance': 'F1: 98.11%',
                        'suitable_for': '精细分词，细粒度更好'
                    },
                    {
                        'model': 'CTB9_TOK_ELECTRA_SMALL',
                        'desc': 'CTB9训练的ELECTRA小模型',
                        'size': '45MB', 
                        'performance': 'F1: 97.26%',
                        'suitable_for': 'CTB标准分词'
                    }
                ]
                
                # 尝试加载首选的分词模型
                for config in tokenizer_configs:
                    try:
                        model_key = config['model']
                        print(f"  尝试加载 {config['desc']} ({config['size']}, {config['performance']})...")
                        
                        # 获取模型URL
                        model_url = getattr(hanlp.pretrained.tok, model_key)
                        print(f"  模型URL: {model_url}")
                        
                        # 加载分词器
                        start_time = time.time()
                        self.tokenizer = hanlp.load(model_url)
                        load_time = time.time() - start_time
                        
                        self.model_name = config['desc']
                        print(f"  ✅ 成功加载 {config['desc']} (耗时: {load_time:.2f}秒)")
                        print(f"  适用场景: {config['suitable_for']}")
                        
                        # 设置初始化标志
                        HanLPTokenizerOptimized._is_initialized = True
                        return True
                        
                    except Exception as e:
                        print(f"  ❌ 加载 {config['desc']} 失败: {str(e)}")
                        continue
                
                # 如果所有模型都加载失败
                print("❌ 所有HanLP分词模型加载失败")
                return False
                
        except Exception as e:
            print(f"❌ HanLP分词器初始化失败: {str(e)}")
            return False
    
    def cut(self, text: str) -> List[str]:
        """
        分词功能
        
        Args:
            text (str): 输入文本
            
        Returns:
            List[str]: 分词结果
        """
        if not self.tokenizer:
            if not self.initialize():
                raise RuntimeError("HanLP分词器未初始化")
        
        try:
            if not text or not text.strip():
                return []
            
            # 使用HanLP的分词功能
            # 注意：HanLP的分词器返回的是列表，每个元素是一个token
            result = self.tokenizer([text])  # HanLP需要列表输入
            
            # 提取第一个句子的分词结果
            if result and len(result) > 0:
                return result[0]
            else:
                return []
                
        except Exception as e:
            print(f"警告: HanLP分词失败: {str(e)}")
            # 简单的字符级别回退
            return list(text)
    
    def posseg(self, text: str) -> List[Tuple[str, str]]:
        """
        词性标注功能
        注意：此版本专注于分词，词性标注功能有限
        
        Args:
            text (str): 输入文本
            
        Returns:
            List[Tuple[str, str]]: (词, 词性)的列表
        """
        try:
            # 先进行分词
            words = self.cut(text)
            
            # 简单的词性推断（实际使用中可以加载词性标注模型）
            result = []
            for word in words:
                # 简单的词性判断逻辑
                if word.isdigit():
                    pos = 'm'  # 数词
                elif word in ['的', '了', '在', '是', '有', '和', '与']:
                    pos = 'p'  # 介词/助词
                elif len(word) == 1 and not word.isalnum():
                    pos = 'w'  # 标点符号
                else:
                    pos = 'n'  # 默认为名词
                
                result.append((word, pos))
            
            return result
            
        except Exception as e:
            print(f"警告: HanLP词性标注失败: {str(e)}")
            # 回退到简单分词
            words = self.cut(text)
            return [(word, 'n') for word in words]
    
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """
        精确分词，返回词和位置信息
        
        Args:
            text (str): 输入文本
            
        Returns:
            List[Tuple[str, int, int]]: (词, 开始位置, 结束位置)的列表
        """
        try:
            words = self.cut(text)
            result = []
            start = 0
            
            for word in words:
                end = start + len(word)
                result.append((word, start, end))
                start = end
            
            return result
            
        except Exception as e:
            print(f"警告: HanLP精确分词失败: {str(e)}")
            # 简单的字符级别处理
            return [(char, i, i+1) for i, char in enumerate(text)]
    
    def get_info(self) -> Dict[str, Any]:
        """获取分词器信息"""
        return {
            'name': self.name,
            'model_name': self.model_name,
            'is_initialized': self._is_initialized,
            'description': '优化版HanLP分词器，仅加载分词模型',
            'features': ['分词', '有限词性标注', '位置信息'],
            'advantages': ['轻量化', '高性能', '本地缓存', '预下载模型']
        }


def test_hanlp_tokenizer():
    """测试HanLP分词器"""
    print("=== HanLP分词器测试 ===")
    
    # 创建分词器实例
    tokenizer = HanLPTokenizerOptimized.get_instance()
    
    # 检查可用性
    if not tokenizer.is_available():
        print("❌ HanLP不可用，请先安装: pip install hanlp")
        return
    
    # 初始化
    if not tokenizer.initialize():
        print("❌ HanLP分词器初始化失败")
        return
    
    # 测试文本
    test_texts = [
        "商品和服务。",
        "晓美焰来到北京立方庭参观自然语义科技公司",
        "HanLP是一款优秀的中文自然语言处理工具包。",
        "2021年HanLP发布了2.1版本。"
    ]
    
    for text in test_texts:
        print(f"\n原文: {text}")
        
        # 测试分词
        start_time = time.time()
        words = tokenizer.cut(text)
        cut_time = time.time() - start_time
        print(f"分词: {words}")
        print(f"分词耗时: {cut_time:.4f}秒")
        
        # 测试词性标注
        start_time = time.time()
        words_pos = tokenizer.posseg(text)
        pos_time = time.time() - start_time
        print(f"词性: {words_pos}")
        print(f"词性标注耗时: {pos_time:.4f}秒")
        
        # 测试精确分词
        tokens = tokenizer.tokenize(text)
        print(f"精确分词: {tokens}")
    
    # 显示分词器信息
    print(f"\n分词器信息: {tokenizer.get_info()}")


if __name__ == "__main__":
    test_hanlp_tokenizer() 