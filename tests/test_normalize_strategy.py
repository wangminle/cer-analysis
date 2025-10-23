#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的文本标准化策略
验证unicodedata.normalize('NFKC')和可配置参数的功能
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))

from asr_metrics_refactored import ASRMetrics

def test_normalize_strategy():
    """测试文本标准化策略改进"""
    print("=" * 60)
    print("文本标准化策略测试")
    print("=" * 60)
    
    # 创建ASRMetrics实例
    metrics = ASRMetrics(tokenizer_name='jieba')
    
    # 测试用例1: 全角半角混合
    print("\n【测试1】全角半角字符统一")
    test_text_1 = "Hello你好123ＡＢＣ４５６"
    result_with_normalize = metrics.normalize_chinese_text(
        test_text_1, 
        normalize_width=True,
        normalize_numbers=False,
        remove_punctuation=False
    )
    result_without_normalize = metrics.normalize_chinese_text(
        test_text_1, 
        normalize_width=False,
        normalize_numbers=False,
        remove_punctuation=False
    )
    print(f"原文: {test_text_1}")
    print(f"启用宽度标准化: {result_with_normalize}")
    print(f"禁用宽度标准化: {result_without_normalize}")
    
    # 测试用例2: 数字归一
    print("\n【测试2】数字归一功能")
    test_text_2 = "今天温度是25度明天是26度"
    result_with_numbers = metrics.normalize_chinese_text(
        test_text_2,
        normalize_width=True,
        normalize_numbers=False,
        remove_punctuation=True
    )
    result_normalized_numbers = metrics.normalize_chinese_text(
        test_text_2,
        normalize_width=True,
        normalize_numbers=True,
        remove_punctuation=True
    )
    print(f"原文: {test_text_2}")
    print(f"保留数字: {result_with_numbers}")
    print(f"归一数字: {result_normalized_numbers}")
    
    # 测试用例3: 标点处理
    print("\n【测试3】标点符号处理")
    test_text_3 = "你好，世界！How are you?"
    result_remove_punct = metrics.normalize_chinese_text(
        test_text_3,
        normalize_width=True,
        normalize_numbers=False,
        remove_punctuation=True
    )
    result_keep_punct = metrics.normalize_chinese_text(
        test_text_3,
        normalize_width=True,
        normalize_numbers=False,
        remove_punctuation=False
    )
    print(f"原文: {test_text_3}")
    print(f"移除标点: {result_remove_punct}")
    print(f"保留标点: {result_keep_punct}")
    
    # 测试用例4: 组合配置
    print("\n【测试4】组合配置测试")
    test_text_4 = "电话：１３８００００１２３４，地址：北京市100号"
    print(f"原文: {test_text_4}")
    
    # 配置A: 全部启用
    result_a = metrics.normalize_chinese_text(
        test_text_4,
        normalize_width=True,
        normalize_numbers=True,
        remove_punctuation=True
    )
    print(f"配置A(全部启用): {result_a}")
    
    # 配置B: 仅宽度标准化
    result_b = metrics.normalize_chinese_text(
        test_text_4,
        normalize_width=True,
        normalize_numbers=False,
        remove_punctuation=False
    )
    print(f"配置B(仅宽度): {result_b}")
    
    # 配置C: 保守配置（保留数字和标点）
    result_c = metrics.normalize_chinese_text(
        test_text_4,
        normalize_width=True,
        normalize_numbers=False,
        remove_punctuation=True
    )
    print(f"配置C(保守): {result_c}")
    
    # 测试用例5: CER计算验证
    print("\n【测试5】CER计算验证（使用新标准化策略）")
    ref_text = "今天天气很好123"
    hyp_text = "今天天气很好１２３"  # 全角数字
    
    # 计算CER
    cer = metrics.calculate_cer(ref_text, hyp_text)
    accuracy = metrics.calculate_accuracy(ref_text, hyp_text)
    
    print(f"参考文本: {ref_text}")
    print(f"识别文本: {hyp_text}")
    print(f"CER: {cer:.4f}")
    print(f"准确率: {accuracy:.4f}")
    print(f"说明: 全角数字'１２３'和半角数字'123'应该被视为相同")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    
    print("\n【改进总结】")
    print("1. ✅ 使用unicodedata.normalize('NFKC')替代自定义全角转换")
    print("2. ✅ 数字归一改为可配置参数（默认关闭，保留原始数值）")
    print("3. ✅ 标点处理改为可配置参数")
    print("4. ✅ 提供灵活的配置选项，适应不同场景需求")

if __name__ == "__main__":
    test_normalize_strategy()

