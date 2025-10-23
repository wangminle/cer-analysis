#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本
测试优化前后的性能差异
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))

import time
from asr_metrics_refactored import ASRMetrics
from text_tokenizers import get_available_tokenizers
from text_tokenizers.tokenizers.factory import TokenizerFactory

def performance_test():
    """性能测试主函数"""
    print("=" * 60)
    print("ASR分词器性能测试")
    print("=" * 60)
    
    # 测试数据
    test_cases = [
        ("短文本", "今天天气很好", "今天天气很号"),
        ("中等文本", "我来到北京清华大学学习计算机科学技术", "我来到北京清华大学学习计算机科学技"),
        ("长文本", 
         "人工智能是计算机科学的一个重要分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器", 
         "人工智能是计算机科学的一个重要分支它企图了解智能的实质并生产出一种新的能以人类智能相似的方式做出反应的智能机器")
    ]
    
    available_tokenizers = get_available_tokenizers()
    print(f"可用分词器: {available_tokenizers}")
    
    for tokenizer_name in available_tokenizers:
        print(f"\n{'='*40}")
        print(f"测试分词器: {tokenizer_name}")
        print(f"{'='*40}")
        
        # 测试初始化时间
        start_time = time.time()
        metrics = ASRMetrics(tokenizer_name=tokenizer_name)
        init_time = time.time() - start_time
        print(f"初始化时间: {init_time:.4f} 秒")
        
        # 测试计算时间
        for test_name, ref_text, hyp_text in test_cases:
            print(f"\n--- {test_name} ---")
            
            # 测试CER计算时间
            start_time = time.time()
            cer = metrics.calculate_cer(ref_text, hyp_text)
            cer_time = time.time() - start_time
            print(f"CER计算时间: {cer_time:.4f} 秒, 结果: {cer:.4f}")
            
            # 测试详细指标计算时间
            start_time = time.time()
            detailed = metrics.calculate_detailed_metrics(ref_text, hyp_text)
            detailed_time = time.time() - start_time
            print(f"详细指标时间: {detailed_time:.4f} 秒")
            
            # 测试语气词过滤功能
            start_time = time.time()
            cer_filtered = metrics.calculate_cer(ref_text, hyp_text, filter_fillers=True)
            filtered_time = time.time() - start_time
            print(f"语气词过滤时间: {filtered_time:.4f} 秒, 结果: {cer_filtered:.4f}")
    
    print(f"\n{'='*60}")
    print("缓存测试 - 重复初始化同一分词器")
    print(f"{'='*60}")
    
    # 测试缓存效果 - 重复创建同一个分词器
    for tokenizer_name in available_tokenizers[:1]:  # 只测试第一个
        print(f"\n测试 {tokenizer_name} 重复初始化:")
        
        # 第一次初始化
        start_time = time.time()
        metrics1 = ASRMetrics(tokenizer_name=tokenizer_name)
        first_init_time = time.time() - start_time
        print(f"第1次初始化: {first_init_time:.4f} 秒")
        
        # 第二次初始化（应该使用缓存）
        start_time = time.time()
        metrics2 = ASRMetrics(tokenizer_name=tokenizer_name)
        second_init_time = time.time() - start_time
        print(f"第2次初始化: {second_init_time:.4f} 秒")
        
        # 第三次初始化（应该使用缓存）
        start_time = time.time()
        metrics3 = ASRMetrics(tokenizer_name=tokenizer_name)
        third_init_time = time.time() - start_time
        print(f"第3次初始化: {third_init_time:.4f} 秒")
        
        if first_init_time > 0:
            print(f"缓存效果: 第2次比第1次快 {((first_init_time - second_init_time) / first_init_time * 100):.1f}%")
            print(f"缓存效果: 第3次比第1次快 {((first_init_time - third_init_time) / first_init_time * 100):.1f}%")
        else:
            print("缓存效果: 初始化时间太短，无法准确测量差异")

    print(f"\n{'='*60}")
    print("工厂缓存测试")
    print(f"{'='*60}")
    
    # 测试工厂缓存
    start_time = time.time()
    available1 = get_available_tokenizers()
    first_call_time = time.time() - start_time
    print(f"第1次调用 get_available_tokenizers(): {first_call_time:.4f} 秒")
    
    start_time = time.time()
    available2 = get_available_tokenizers()
    second_call_time = time.time() - start_time
    print(f"第2次调用 get_available_tokenizers(): {second_call_time:.4f} 秒")
    
    if first_call_time > 0:
        print(f"缓存效果: 第2次比第1次快 {((first_call_time - second_call_time) / first_call_time * 100):.1f}%")
    
    print(f"\n🎉 性能测试完成！")

if __name__ == "__main__":
    performance_test() 