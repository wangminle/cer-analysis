#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分词器版本获取修复
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from text_tokenizers import get_available_tokenizers, get_tokenizer_info
from text_tokenizers.tokenizers.factory import TokenizerFactory

def test_tokenizer_versions():
    """测试所有可用分词器的版本获取"""
    print("🔧 测试分词器版本获取修复效果")
    print("=" * 50)
    
    # 清除现有缓存
    print("清除现有缓存...")
    TokenizerFactory.clear_cache()
    
    # 获取可用分词器
    available_tokenizers = get_available_tokenizers()
    print(f"可用分词器: {available_tokenizers}")
    print()
    
    for tokenizer_name in available_tokenizers:
        print(f"📋 测试 {tokenizer_name} 分词器:")
        try:
            info = get_tokenizer_info(tokenizer_name)
            
            print(f"  分词器名称: {info.get('name', 'N/A')}")
            print(f"  版本: {info.get('version', 'N/A')}")
            print(f"  初始化状态: {info.get('initialized', False)}")
            print(f"  可用性: {info.get('available', False)}")
            
            if info.get('version', 'unknown') == 'unknown':
                print(f"  ⚠️  版本获取失败")
            else:
                print(f"  ✅ 版本获取成功")
                
        except Exception as e:
            print(f"  ❌ 测试失败: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_tokenizer_versions() 