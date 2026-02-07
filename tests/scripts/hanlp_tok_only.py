#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HanLP分词器演示 - 仅加载分词模型
专门用于演示如何只使用HanLP的分词功能，而不加载完整的多任务模型
"""

import time
from typing import List, Optional


class HanLPTokenizerLight:
    """轻量化的HanLP分词器，仅加载分词模型"""
    
    def __init__(self):
        self.hanlp = None
        self.tokenizer = None
        self.model_name = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """初始化HanLP分词器，仅加载分词模型"""
        try:
            print("正在导入HanLP...")
            import hanlp
            self.hanlp = hanlp
            
            print("正在加载HanLP分词模型（仅分词功能）...")
            
            # 推荐的轻量化分词模型（按性能和文件大小排序）
            recommended_models = [
                {
                    'key': 'COARSE_ELECTRA_SMALL_ZH',
                    'desc': '粗粒度ELECTRA小模型',
                    'performance': 'F1: 98.36%',
                    'size': '约45MB'
                },
                {
                    'key': 'FINE_ELECTRA_SMALL_ZH', 
                    'desc': '细粒度ELECTRA小模型',
                    'performance': 'F1: 98.11%',
                    'size': '约45MB'
                },
                {
                    'key': 'CTB9_TOK_ELECTRA_SMALL',
                    'desc': 'CTB9 ELECTRA小模型',
                    'performance': 'F1: 97.26%',
                    'size': '约45MB'
                }
            ]
            
            # 尝试加载推荐模型
            for model_info in recommended_models:
                model_key = model_info['key']
                try:
                    if hasattr(hanlp.pretrained.tok, model_key):
                        model_url = getattr(hanlp.pretrained.tok, model_key)
                        print(f"  尝试加载: {model_info['desc']}")
                        print(f"  性能: {model_info['performance']}, 大小: {model_info['size']}")
                        
                        start_time = time.time()
                        self.tokenizer = hanlp.load(model_url)
                        load_time = time.time() - start_time
                        
                        self.model_name = model_key
                        self.is_initialized = True
                        
                        print(f"  ✓ 模型加载成功！用时: {load_time:.2f}秒")
                        print(f"  已加载模型: {model_key}")
                        return True
                        
                except Exception as e:
                    print(f"  ✗ 加载失败: {e}")
                    continue
            
            # 如果推荐模型都失败，尝试其他可用模型
            fallback_models = [
                'LARGE_ALBERT_BASE',
                'SIGHAN2005_PKU_BERT_BASE_ZH',
                'CTB6_CONVSEG'
            ]
            
            print("\n推荐模型均不可用，尝试备用模型...")
            for model_key in fallback_models:
                try:
                    if hasattr(hanlp.pretrained.tok, model_key):
                        model_url = getattr(hanlp.pretrained.tok, model_key)
                        print(f"  尝试备用模型: {model_key}")
                        
                        start_time = time.time()
                        self.tokenizer = hanlp.load(model_url)
                        load_time = time.time() - start_time
                        
                        self.model_name = model_key
                        self.is_initialized = True
                        
                        print(f"  ✓ 备用模型加载成功！用时: {load_time:.2f}秒")
                        return True
                        
                except Exception as e:
                    print(f"  ✗ 备用模型加载失败: {e}")
                    continue
            
            print("❌ 所有HanLP分词模型都无法加载")
            return False
            
        except ImportError:
            print("❌ HanLP库未安装，请运行: pip install hanlp")
            return False
        except Exception as e:
            print(f"❌ HanLP初始化失败: {e}")
            return False
    
    def tokenize_text(self, text: str) -> Optional[List[str]]:
        """对文本进行分词"""
        if not self.is_initialized:
            print("错误：分词器未初始化")
            return None
        
        if not text or not text.strip():
            return []
        
        try:
            # 使用纯分词功能
            result = self.tokenizer(text.strip())
            return result if isinstance(result, list) else list(result)
        except Exception as e:
            print(f"分词失败: {e}")
            return None
    
    def batch_tokenize(self, texts: List[str]) -> Optional[List[List[str]]]:
        """批量分词，提升性能"""
        if not self.is_initialized:
            print("错误：分词器未初始化")
            return None
        
        if not texts:
            return []
        
        try:
            # 批量处理
            results = self.tokenizer(texts)
            return results if isinstance(results, list) else [results]
        except Exception as e:
            print(f"批量分词失败: {e}")
            return None
    
    def get_model_info(self) -> dict:
        """获取当前模型信息"""
        return {
            'model_name': self.model_name,
            'initialized': self.is_initialized,
            'model_type': '纯分词模型（非多任务）',
            'features': ['中文分词'],
            'advantages': [
                '模型体积小（45MB左右）',
                '加载速度快',
                '内存占用少', 
                '不下载不必要的NLP模型'
            ]
        }


def demo_hanlp_tokenizer():
    """演示HanLP轻量化分词器的使用"""
    print("=" * 60)
    print("HanLP轻量化分词器演示")
    print("=" * 60)
    
    # 初始化分词器
    tokenizer = HanLPTokenizerLight()
    
    print("\n1. 初始化分词器...")
    if not tokenizer.initialize():
        print("初始化失败，演示结束")
        return
    
    # 显示模型信息
    print("\n2. 模型信息:")
    model_info = tokenizer.get_model_info()
    for key, value in model_info.items():
        if isinstance(value, list):
            print(f"   {key}: {', '.join(value)}")
        else:
            print(f"   {key}: {value}")
    
    # 单句分词测试
    print("\n3. 单句分词测试:")
    test_sentences = [
        "我爱自然语言处理技术",
        "HanLP是一个很好的中文NLP工具包",
        "今天天气很好，适合出去散步",
        "深度学习在自然语言处理领域取得了巨大进展"
    ]
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"   测试{i}: {sentence}")
        start_time = time.time()
        result = tokenizer.tokenize_text(sentence)
        elapsed = time.time() - start_time
        
        if result:
            print(f"   结果: {' / '.join(result)}")
            print(f"   用时: {elapsed*1000:.2f}毫秒")
        else:
            print("   分词失败")
        print()
    
    # 批量分词测试
    print("4. 批量分词测试:")
    print(f"   批量处理{len(test_sentences)}个句子...")
    start_time = time.time()
    batch_results = tokenizer.batch_tokenize(test_sentences)
    elapsed = time.time() - start_time
    
    if batch_results:
        print(f"   批量分词完成，用时: {elapsed*1000:.2f}毫秒")
        print(f"   平均每句: {elapsed*1000/len(test_sentences):.2f}毫秒")
        
        for i, (sentence, result) in enumerate(zip(test_sentences, batch_results), 1):
            print(f"   句子{i}: {' / '.join(result)}")
    else:
        print("   批量分词失败")
    
    print("\n=" * 60)
    print("演示完成！")
    print("优势总结:")
    print("✓ 只加载分词模型，避免下载不必要的NLP组件")
    print("✓ 模型小巧（约45MB），加载速度快")
    print("✓ 内存占用少，适合生产环境")
    print("✓ 分词精度高（F1值超过97%）")
    print("=" * 60)


if __name__ == "__main__":
    demo_hanlp_tokenizer() 