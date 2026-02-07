#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的分词器测试脚本
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))

try:
    print("正在测试分词器模块导入...")
    from text_tokenizers import get_available_tokenizers, get_tokenizer_info
    print("✓ 分词器模块导入成功!")
    
    print("\n正在获取可用分词器...")
    available_tokenizers = get_available_tokenizers()
    print(f"可用分词器: {available_tokenizers}")
    
    if available_tokenizers:
        print("\n测试第一个可用分词器...")
        tokenizer_name = available_tokenizers[0]
        print(f"正在测试: {tokenizer_name}")
        
        # 获取分词器信息
        info = get_tokenizer_info(tokenizer_name)
        print(f"分词器信息: {info}")
        
        # 测试ASRMetrics
        print("\n正在测试ASRMetrics...")
        from asr_metrics_refactored import ASRMetrics
        
        metrics = ASRMetrics(tokenizer_name=tokenizer_name)
        print(f"✓ ASRMetrics使用{tokenizer_name}创建成功!")
        
        # 简单测试
        ref = "今天天气很好"
        hyp = "今天天气很号"
        cer = metrics.calculate_cer(ref, hyp)
        print(f"测试CER计算: {cer:.4f}")
        
        print("\n🎉 所有测试通过！分词器架构工作正常。")
        
    else:
        print("⚠️ 没有找到可用的分词器。请检查依赖库安装。")

except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc() 