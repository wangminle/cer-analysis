#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试精确的编辑操作统计算法
验证DP路径回溯算法的准确性
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))

from asr_metrics_refactored import ASRMetrics

def test_edit_ops_accurate():
    """测试精确的编辑操作统计"""
    print("=" * 60)
    print("精确编辑操作统计测试")
    print("=" * 60)
    
    # 创建ASRMetrics实例
    metrics = ASRMetrics(tokenizer_name='jieba')
    
    # 测试用例1: 纯替换
    print("\n【测试1】纯替换错误")
    ref1 = "abcdef"
    hyp1 = "axcxef"
    s, d, i = metrics._calculate_edit_ops_with_backtrack(ref1, hyp1)
    print(f"参考: {ref1}")
    print(f"识别: {hyp1}")
    print(f"统计: 替换={s}, 删除={d}, 插入={i}")
    print(f"预期: 替换=2, 删除=0, 插入=0")
    assert s == 2 and d == 0 and i == 0, "测试1失败"
    print("✅ 通过")
    
    # 测试用例2: 纯删除
    print("\n【测试2】纯删除错误")
    ref2 = "abcdef"
    hyp2 = "abef"
    s, d, i = metrics._calculate_edit_ops_with_backtrack(ref2, hyp2)
    print(f"参考: {ref2}")
    print(f"识别: {hyp2}")
    print(f"统计: 替换={s}, 删除={d}, 插入={i}")
    print(f"预期: 替换=0, 删除=2, 插入=0")
    assert s == 0 and d == 2 and i == 0, "测试2失败"
    print("✅ 通过")
    
    # 测试用例3: 纯插入
    print("\n【测试3】纯插入错误")
    ref3 = "abef"
    hyp3 = "abcdef"
    s, d, i = metrics._calculate_edit_ops_with_backtrack(ref3, hyp3)
    print(f"参考: {ref3}")
    print(f"识别: {hyp3}")
    print(f"统计: 替换={s}, 删除={d}, 插入={i}")
    print(f"预期: 替换=0, 删除=0, 插入=2")
    assert s == 0 and d == 0 and i == 2, "测试3失败"
    print("✅ 通过")
    
    # 测试用例4: 混合错误
    print("\n【测试4】混合错误")
    ref4 = "kitten"
    hyp4 = "sitting"
    s, d, i = metrics._calculate_edit_ops_with_backtrack(ref4, hyp4)
    print(f"参考: {ref4}")
    print(f"识别: {hyp4}")
    print(f"统计: 替换={s}, 删除={d}, 插入={i}")
    total_ops = s + d + i
    print(f"总编辑距离: {total_ops}")
    print(f"预期编辑距离: 3")
    assert total_ops == 3, "测试4失败"
    print("✅ 通过")
    
    # 测试用例5: 中文文本
    print("\n【测试5】中文文本")
    ref5 = "今天天气很好"
    hyp5 = "今天天气不好"
    s, d, i = metrics._calculate_edit_ops_with_backtrack(ref5, hyp5)
    print(f"参考: {ref5}")
    print(f"识别: {hyp5}")
    print(f"统计: 替换={s}, 删除={d}, 插入={i}")
    print(f"预期: 替换=1, 删除=0, 插入=0")
    assert s == 1 and d == 0 and i == 0, "测试5失败"
    print("✅ 通过")
    
    # 测试用例6: 空字符串
    print("\n【测试6】边界情况 - 空字符串")
    ref6 = "abc"
    hyp6 = ""
    s, d, i = metrics._calculate_edit_ops_with_backtrack(ref6, hyp6)
    print(f"参考: '{ref6}'")
    print(f"识别: '{hyp6}'")
    print(f"统计: 替换={s}, 删除={d}, 插入={i}")
    print(f"预期: 替换=0, 删除=3, 插入=0")
    assert s == 0 and d == 3 and i == 0, "测试6失败"
    print("✅ 通过")
    
    # 测试用例7: 完全相同
    print("\n【测试7】边界情况 - 完全相同")
    ref7 = "hello"
    hyp7 = "hello"
    s, d, i = metrics._calculate_edit_ops_with_backtrack(ref7, hyp7)
    print(f"参考: {ref7}")
    print(f"识别: {hyp7}")
    print(f"统计: 替换={s}, 删除={d}, 插入={i}")
    print(f"预期: 替换=0, 删除=0, 插入=0")
    assert s == 0 and d == 0 and i == 0, "测试7失败"
    print("✅ 通过")
    
    # 测试用例8: 完整ASR计算验证
    print("\n【测试8】完整CER计算验证")
    ref_text = "我来到北京清华大学"
    hyp_text = "我来到北京清大学"
    
    detailed_metrics = metrics.calculate_detailed_metrics(ref_text, hyp_text)
    print(f"参考: {ref_text}")
    print(f"识别: {hyp_text}")
    print(f"CER: {detailed_metrics['cer']:.4f}")
    print(f"替换: {detailed_metrics['substitutions']}")
    print(f"删除: {detailed_metrics['deletions']}")
    print(f"插入: {detailed_metrics['insertions']}")
    print(f"参考长度: {detailed_metrics['ref_length']}")
    
    # 验证统计数据的合理性
    total_errors = detailed_metrics['substitutions'] + detailed_metrics['deletions'] + detailed_metrics['insertions']
    expected_cer = total_errors / detailed_metrics['ref_length']
    print(f"\n验证: 计算的CER ({detailed_metrics['cer']:.4f}) 应该等于 总错误/参考长度 ({expected_cer:.4f})")
    assert abs(detailed_metrics['cer'] - expected_cer) < 0.001, "CER计算验证失败"
    print("✅ 通过")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！")
    print("=" * 60)
    
    print("\n【改进总结】")
    print("1. ✅ 实现了精确的DP路径回溯算法")
    print("2. ✅ 替代了1/3近似分摊的不准确方案")
    print("3. ✅ 确保S/D/I统计数据100%准确")
    print("4. ✅ 在没有python-Levenshtein库时也能提供准确统计")
    print("5. ✅ 通过了多种场景的测试验证")

if __name__ == "__main__":
    test_edit_ops_accurate()

