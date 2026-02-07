#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分词器架构演示
创建模拟版本来展示架构设计，不依赖外部库
"""

import sys
import os
from typing import List, Tuple, Dict, Any
from abc import ABC, abstractmethod

# 模拟分词器异常类
class TokenizerError(Exception):
    """分词器基础异常类"""
    pass

class TokenizerInitError(TokenizerError):
    """分词器初始化异常"""
    pass

class TokenizerProcessError(TokenizerError):
    """分词器处理异常"""
    pass

# 模拟抽象基类
class BaseTokenizer(ABC):
    """分词器抽象基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('Tokenizer', '').lower()
        self.is_initialized = False
        self.version = "demo-1.0"
    
    @abstractmethod
    def initialize(self) -> bool:
        pass
    
    @abstractmethod
    def cut(self, text: str) -> List[str]:
        pass
    
    @abstractmethod
    def posseg(self, text: str) -> List[Tuple[str, str]]:
        pass
    
    @abstractmethod
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        pass
    
    def validate_text(self, text: str) -> str:
        if not isinstance(text, str):
            raise TokenizerProcessError("输入必须是字符串类型")
        return text.strip()
    
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'initialized': self.is_initialized,
            'available': True,
            'class_name': self.__class__.__name__
        }

# 模拟Jieba分词器
class MockJiebaTokenizer(BaseTokenizer):
    """模拟Jieba分词器，用于演示架构"""
    
    def __init__(self):
        super().__init__()
        self.name = "jieba"
    
    def initialize(self) -> bool:
        try:
            # 模拟初始化过程
            print("  正在初始化Jieba分词器...")
            self.is_initialized = True
            return True
        except Exception as e:
            raise TokenizerInitError(f"Jieba分词器初始化失败: {str(e)}")
    
    def cut(self, text: str) -> List[str]:
        cleaned_text = self.validate_text(text)
        if not cleaned_text:
            return []
        
        # 简单的中文字符分割模拟（仅用于演示）
        import re
        
        # 分割中文字符、英文单词和数字
        pattern = r'[\u4e00-\u9fff]+|[a-zA-Z]+|\d+'
        words = re.findall(pattern, cleaned_text)
        
        # 进一步分割中文字符（每2-3个字符作为一个词）
        result = []
        for word in words:
            if re.match(r'[\u4e00-\u9fff]+', word):
                # 中文字符，按2-3个字符分组
                i = 0
                while i < len(word):
                    if i + 2 < len(word):
                        result.append(word[i:i+2])
                        i += 2
                    else:
                        result.append(word[i:])
                        break
            else:
                result.append(word)
        
        return result
    
    def posseg(self, text: str) -> List[Tuple[str, str]]:
        words = self.cut(text)
        # 简单的词性标注模拟
        result = []
        for word in words:
            if word.isdigit():
                pos = 'm'  # 数词
            elif word.isalpha():
                pos = 'n'  # 名词
            else:
                pos = 'x'  # 其他
            result.append((word, pos))
        return result
    
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        cleaned_text = self.validate_text(text)
        if not cleaned_text:
            return []
        
        words = self.cut(cleaned_text)
        result = []
        current_pos = 0
        
        for word in words:
            start_pos = cleaned_text.find(word, current_pos)
            if start_pos == -1:
                start_pos = current_pos
            end_pos = start_pos + len(word)
            result.append((word, start_pos, end_pos))
            current_pos = end_pos
        
        return result
    
    def get_info(self) -> dict:
        info = super().get_info()
        info.update({
            'description': '模拟Jieba中文分词器',
            'features': ['分词', '词性标注', '精确位置分词'],
            'dependencies': ['jieba (模拟)'],
            'performance': '高速',
            'accuracy': '中等'
        })
        return info

# 模拟THULAC分词器
class MockThulacTokenizer(BaseTokenizer):
    """模拟THULAC分词器，用于演示架构"""
    
    def __init__(self):
        super().__init__()
        self.name = "thulac"
    
    def initialize(self) -> bool:
        try:
            print("  正在初始化THULAC分词器...")
            # 模拟较慢的初始化过程
            import time
            time.sleep(0.5)
            self.is_initialized = True
            return True
        except Exception as e:
            raise TokenizerInitError(f"THULAC分词器初始化失败: {str(e)}")
    
    def cut(self, text: str) -> List[str]:
        cleaned_text = self.validate_text(text)
        if not cleaned_text:
            return []
        
        # 模拟THULAC的分词结果（更细粒度）
        import re
        
        result = []
        # 按单个中文字符分割
        for char in cleaned_text:
            if re.match(r'[\u4e00-\u9fff]', char):
                result.append(char)
            elif char.isalnum():
                result.append(char)
        
        return result
    
    def posseg(self, text: str) -> List[Tuple[str, str]]:
        words = self.cut(text)
        # 模拟THULAC的词性标注
        result = []
        for word in words:
            if word.isdigit():
                pos = 'CD'  # 数词
            elif word.isalpha():
                pos = 'NN'  # 名词
            else:
                pos = 'PU'  # 标点
            result.append((word, pos))
        return result
    
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        cleaned_text = self.validate_text(text)
        words = self.cut(cleaned_text)
        
        result = []
        pos = 0
        for word in words:
            start_pos = pos
            end_pos = pos + len(word)
            result.append((word, start_pos, end_pos))
            pos = end_pos
        
        return result
    
    def get_info(self) -> dict:
        info = super().get_info()
        info.update({
            'description': '模拟THULAC高精度中文分词器',
            'features': ['分词', '词性标注', '精确位置分词'],
            'dependencies': ['thulac (模拟)'],
            'performance': '中等速度',
            'accuracy': '高精度'
        })
        return info

# 模拟HanLP分词器（不可用状态）
class MockHanlpTokenizer(BaseTokenizer):
    """模拟HanLP分词器，演示不可用状态"""
    
    def __init__(self):
        super().__init__()
        self.name = "hanlp"
    
    def initialize(self) -> bool:
        # 模拟初始化失败
        raise TokenizerInitError("HanLP库未安装，请运行: pip install hanlp")
    
    def cut(self, text: str) -> List[str]:
        raise TokenizerProcessError("HanLP分词器未初始化")
    
    def posseg(self, text: str) -> List[Tuple[str, str]]:
        raise TokenizerProcessError("HanLP分词器未初始化")
    
    def tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        raise TokenizerProcessError("HanLP分词器未初始化")
    
    def get_info(self) -> dict:
        info = super().get_info()
        info.update({
            'description': '模拟HanLP深度学习中文分词器',
            'features': ['分词', '词性标注', '精确位置分词', 'BERT支持'],
            'dependencies': ['hanlp (模拟)'],
            'performance': '较慢（深度学习模型）',
            'accuracy': '最高精度',
            'available': False,
            'error': 'HanLP库未安装'
        })
        return info

# 模拟分词器工厂
class MockTokenizerFactory:
    """模拟分词器工厂类"""
    
    _instance = None
    _tokenizers = {}
    _available_tokenizers = {
        'jieba': MockJiebaTokenizer,
        'thulac': MockThulacTokenizer,
        'hanlp': MockHanlpTokenizer
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockTokenizerFactory, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_available_tokenizers(cls) -> List[str]:
        available = []
        for name, tokenizer_class in cls._available_tokenizers.items():
            try:
                tokenizer = tokenizer_class()
                tokenizer.initialize()
                available.append(name)
            except:
                continue
        return available
    
    @classmethod
    def get_tokenizer(cls, name: str) -> BaseTokenizer:
        if name not in cls._available_tokenizers:
            raise ValueError(f"不支持的分词器: {name}")
        
        if name in cls._tokenizers:
            return cls._tokenizers[name]
        
        tokenizer_class = cls._available_tokenizers[name]
        tokenizer = tokenizer_class()
        tokenizer.initialize()
        cls._tokenizers[name] = tokenizer
        return tokenizer
    
    @classmethod
    def get_tokenizer_info(cls, name: str) -> Dict[str, Any]:
        if name not in cls._available_tokenizers:
            return {'name': name, 'available': False, 'error': f'不支持的分词器: {name}'}
        
        try:
            tokenizer_class = cls._available_tokenizers[name]
            tokenizer = tokenizer_class()
            tokenizer.initialize()
            info = tokenizer.get_info()
            info['available'] = True
            return info
        except Exception as e:
            return {
                'name': name,
                'available': False,
                'error': str(e)
            }

# 模拟ASRMetrics类
class MockASRMetrics:
    """模拟ASRMetrics类，演示分词器集成"""
    
    def __init__(self, tokenizer_name: str = "jieba"):
        self.tokenizer_name = tokenizer_name
        self.tokenizer = None
        self._initialize_tokenizer()
    
    def _initialize_tokenizer(self):
        try:
            self.tokenizer = MockTokenizerFactory.get_tokenizer(self.tokenizer_name)
        except Exception as e:
            print(f"警告: {self.tokenizer_name}分词器初始化失败: {str(e)}")
            print("自动回退到jieba分词器")
            try:
                self.tokenizer_name = "jieba"
                self.tokenizer = MockTokenizerFactory.get_tokenizer("jieba")
            except Exception as fallback_e:
                raise RuntimeError(f"无法初始化任何分词器: {str(fallback_e)}")
    
    def calculate_cer(self, reference: str, hypothesis: str) -> float:
        """简化的CER计算"""
        if not reference or not hypothesis:
            return 1.0 if reference != hypothesis else 0.0
        
        # 使用当前分词器预处理文本
        ref_processed = "".join(self.tokenizer.cut(reference))
        hyp_processed = "".join(self.tokenizer.cut(hypothesis))
        
        # 简化的编辑距离计算
        if ref_processed == hyp_processed:
            return 0.0
        
        # 模拟编辑距离计算
        max_len = max(len(ref_processed), len(hyp_processed))
        if max_len == 0:
            return 0.0
        
        # 简单的字符差异计算
        differences = sum(1 for a, b in zip(ref_processed, hyp_processed) if a != b)
        differences += abs(len(ref_processed) - len(hyp_processed))
        
        return min(differences / len(reference), 1.0)
    
    def get_tokenizer_info(self) -> Dict[str, Any]:
        return self.tokenizer.get_info() if self.tokenizer else {}

def demo_tokenizer_architecture():
    """演示分词器架构"""
    print("=" * 60)
    print("分词器架构演示")
    print("=" * 60)
    
    # 测试分词器工厂
    factory = MockTokenizerFactory()
    
    print("\n1. 获取可用分词器列表:")
    available_tokenizers = factory.get_available_tokenizers()
    print(f"可用分词器: {available_tokenizers}")
    
    print("\n2. 测试各个分词器:")
    test_text = "今天天气很好，我们去公园散步。"
    
    for tokenizer_name in ['jieba', 'thulac', 'hanlp']:
        print(f"\n{'='*40}")
        print(f"测试分词器: {tokenizer_name}")
        print(f"{'='*40}")
        
        # 获取分词器信息
        info = factory.get_tokenizer_info(tokenizer_name)
        print(f"分词器信息:")
        print(f"  名称: {info.get('name', 'N/A')}")
        print(f"  可用性: {'可用' if info.get('available', False) else '不可用'}")
        print(f"  描述: {info.get('description', 'N/A')}")
        
        if not info.get('available', False):
            print(f"  错误: {info.get('error', 'N/A')}")
            continue
        
        # 测试分词器功能
        try:
            tokenizer = factory.get_tokenizer(tokenizer_name)
            
            # 测试基础分词
            words = tokenizer.cut(test_text)
            print(f"基础分词结果: {words[:5]}...")
            
            # 测试词性标注
            pos_result = tokenizer.posseg(test_text)
            print(f"词性标注结果: {pos_result[:3]}...")
            
            # 测试精确分词
            tokenize_result = tokenizer.tokenize(test_text)
            print(f"精确分词结果: {tokenize_result[:3]}...")
            
        except Exception as e:
            print(f"测试失败: {str(e)}")
    
    print("\n3. 测试ASRMetrics集成:")
    print("-" * 40)
    
    # 测试数据
    reference = "今天天气很好"
    hypothesis = "今天天气很号"
    
    for tokenizer_name in available_tokenizers:
        try:
            metrics = MockASRMetrics(tokenizer_name=tokenizer_name)
            cer = metrics.calculate_cer(reference, hypothesis)
            print(f"使用{tokenizer_name}分词器的CER: {cer:.4f}")
        except Exception as e:
            print(f"使用{tokenizer_name}分词器测试失败: {str(e)}")

def demo_gui_integration():
    """演示GUI集成示例"""
    print("\n" + "=" * 60)
    print("GUI集成演示")
    print("=" * 60)
    
    print("\n模拟GUI操作序列:")
    print("1. 应用启动 -> 初始化可用分词器列表")
    
    factory = MockTokenizerFactory()
    available = factory.get_available_tokenizers()
    print(f"   可用分词器: {available}")
    
    print("\n2. 用户选择分词器 -> 更新状态显示")
    for tokenizer in ['jieba', 'thulac', 'hanlp']:
        info = factory.get_tokenizer_info(tokenizer)
        status = "✓" if info.get('available', False) else "✗"
        print(f"   {status} {tokenizer} - {info.get('description', 'N/A')}")
    
    print("\n3. 用户开始计算 -> 使用选定分词器")
    selected_tokenizer = "jieba"
    print(f"   选定分词器: {selected_tokenizer}")
    
    try:
        metrics = MockASRMetrics(tokenizer_name=selected_tokenizer)
        print(f"   ✓ ASRMetrics实例创建成功")
        print(f"   使用分词器: {metrics.tokenizer_name}")
    except Exception as e:
        print(f"   ✗ 创建失败: {str(e)}")

def main():
    """主演示函数"""
    print("分词器架构演示程序")
    print("此演示不依赖外部库，展示完整架构设计")
    
    # 演示分词器架构
    demo_tokenizer_architecture()
    
    # 演示GUI集成
    demo_gui_integration()
    
    print("\n" + "=" * 60)
    print("演示总结")
    print("=" * 60)
    print("✓ 分词器抽象架构: 统一接口设计")
    print("✓ 工厂模式: 动态分词器管理")
    print("✓ 单例模式: 避免重复初始化")
    print("✓ 错误处理: 优雅降级机制")
    print("✓ ASRMetrics集成: 支持可切换分词器")
    print("✓ GUI集成: 用户友好的分词器选择")
    print("\n🎉 分词器架构设计完成！")

if __name__ == "__main__":
    main() 