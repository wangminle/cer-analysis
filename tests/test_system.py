#!/usr/bin/env python3
"""
系统功能验证测试
验证所有分词器和核心功能是否正常工作
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))

from asr_metrics_refactored import ASRMetrics
from text_tokenizers import get_available_tokenizers, get_tokenizer, get_tokenizer_info

def test_tokenizers():
    """测试所有可用的分词器"""
    print("=" * 50)
    print("分词器测试")
    print("=" * 50)
    
    available = get_available_tokenizers()
    print(f"可用分词器: {available}")
    
    for tokenizer_name in available:
        print(f"\n--- 测试 {tokenizer_name} 分词器 ---")
        try:
            # 获取分词器信息
            info = get_tokenizer_info(tokenizer_name)
            print(f"信息: {info}")
            
            # 创建分词器实例
            tokenizer = get_tokenizer(tokenizer_name)
            
            # 测试分词功能
            test_text = "我来到北京清华大学学习"
            words = tokenizer.cut(test_text)
            print(f"分词结果: {words}")
            
            # 测试词性标注
            pos_result = tokenizer.posseg(test_text)
            print(f"词性标注: {pos_result}")
            
            # 测试精确分词
            token_result = tokenizer.tokenize(test_text)
            print(f"精确分词: {token_result}")
            
        except Exception as e:
            print(f"错误: {str(e)}")

def test_asr_metrics():
    """测试ASR指标计算"""
    print("\n" + "=" * 50)
    print("ASR指标计算测试")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        ("我来到北京清华大学", "我来到北京清大学", "缺字错误"),
        ("今天天气很好", "今天天气不好", "替换错误"),
        ("人工智能技术发展", "人工智能技术发展很快", "插入错误"),
        ("中文语音识别系统", "中文语音识别", "删除错误"),
    ]
    
    available_tokenizers = get_available_tokenizers()
    
    for tokenizer_name in available_tokenizers:
        print(f"\n--- 使用 {tokenizer_name} 分词器 ---")
        
        try:
            metrics = ASRMetrics(tokenizer_name)
            
            for ref, hyp, error_type in test_cases:
                print(f"\n{error_type}:")
                print(f"参考: {ref}")
                print(f"识别: {hyp}")
                
                # 计算各种指标
                cer = metrics.calculate_cer(ref, hyp)
                wer = metrics.calculate_wer(ref, hyp)
                acc = metrics.calculate_accuracy(ref, hyp)
                
                print(f"CER: {cer:.2%}, WER: {wer:.2%}, 准确率: {acc:.2%}")
                
                # 显示差异
                diff = metrics.show_differences(ref, hyp)
                print(f"差异: {diff}")
                
        except Exception as e:
            print(f"错误: {str(e)}")

def test_optional_tokenizers():
    """测试可选分词器（THULAC和HanLP）"""
    print("\n" + "=" * 50)
    print("可选分词器测试")
    print("=" * 50)
    
    optional_tokenizers = ['thulac', 'hanlp']
    
    for tokenizer_name in optional_tokenizers:
        print(f"\n--- 测试 {tokenizer_name} ---")
        
        try:
            info = get_tokenizer_info(tokenizer_name)
            if info['available']:
                print(f"{tokenizer_name} 可用")
                tokenizer = get_tokenizer(tokenizer_name)
                test_text = "北京大学是一所著名的学府"
                words = tokenizer.cut(test_text)
                print(f"分词结果: {words}")
            else:
                print(f"{tokenizer_name} 不可用: {info.get('error', '未知错误')}")
        except Exception as e:
            print(f"{tokenizer_name} 测试失败: {str(e)}")

if __name__ == "__main__":
    print("CER-MatchingTools 系统功能验证测试")
    print("当前支持的分词器: jieba(必需), thulac(可选), hanlp(可选)")
    
    # 运行测试
    test_tokenizers()
    test_asr_metrics()
    test_optional_tokenizers()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("如果看到错误，请检查相应依赖是否已安装:")
    print("- THULAC: pip install thulac")
    print("- HanLP: pip install hanlp")
    print("=" * 50) 