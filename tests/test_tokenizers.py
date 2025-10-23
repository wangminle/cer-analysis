#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分词器架构测试脚本
用于验证分词器模块是否正常工作
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))

def test_tokenizers():
    """测试分词器架构"""
    print("=" * 60)
    print("分词器架构测试")
    print("=" * 60)
    
    try:
        # 导入分词器模块
        from text_tokenizers import get_available_tokenizers, get_tokenizer_info, get_tokenizer
        
        print("✓ 分词器模块导入成功")
        
        # 获取可用的分词器列表
        available_tokenizers = get_available_tokenizers()
        print(f"\n可用的分词器: {available_tokenizers}")
        
        if not available_tokenizers:
            print("⚠️  警告: 没有找到可用的分词器")
            return False
        
        # 测试每个可用的分词器
        test_text = "今天天气很好，我们去公园散步吧。"
        
        for tokenizer_name in available_tokenizers:
            print(f"\n{'='*40}")
            print(f"测试分词器: {tokenizer_name}")
            print(f"{'='*40}")
            
            # 获取分词器信息
            try:
                info = get_tokenizer_info(tokenizer_name)
                print(f"分词器信息:")
                print(f"  - 名称: {info.get('name', 'N/A')}")
                print(f"  - 版本: {info.get('version', 'N/A')}")
                print(f"  - 可用性: {'可用' if info.get('available', False) else '不可用'}")
                print(f"  - 描述: {info.get('description', 'N/A')}")
                
                if not info.get('available', False):
                    print(f"  - 错误: {info.get('error', 'N/A')}")
                    continue
                    
            except Exception as e:
                print(f"✗ 获取分词器信息失败: {str(e)}")
                continue
            
            # 测试分词器功能
            try:
                tokenizer = get_tokenizer(tokenizer_name)
                print(f"\n✓ {tokenizer_name} 分词器创建成功")
                
                # 测试基础分词
                try:
                    words = tokenizer.cut(test_text)
                    print(f"基础分词结果: {words}")
                except Exception as e:
                    print(f"✗ 基础分词失败: {str(e)}")
                
                # 测试词性标注
                try:
                    pos_result = tokenizer.posseg(test_text)
                    print(f"词性标注结果: {pos_result[:5]}...")  # 只显示前5个
                except Exception as e:
                    print(f"✗ 词性标注失败: {str(e)}")
                
                # 测试精确分词
                try:
                    tokenize_result = tokenizer.tokenize(test_text)
                    print(f"精确分词结果: {tokenize_result[:5]}...")  # 只显示前5个
                except Exception as e:
                    print(f"✗ 精确分词失败: {str(e)}")
                
            except Exception as e:
                print(f"✗ {tokenizer_name} 分词器测试失败: {str(e)}")
        
        return True
        
    except ImportError as e:
        print(f"✗ 分词器模块导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ 测试过程中出现未知错误: {str(e)}")
        return False


def test_asr_metrics():
    """测试重构后的ASRMetrics类"""
    print("\n" + "=" * 60)
    print("ASRMetrics类测试")
    print("=" * 60)
    
    try:
        from asr_metrics_refactored import ASRMetrics
        print("✓ ASRMetrics类导入成功")
        
        # 测试数据
        reference_text = "今天天气很好"
        hypothesis_text = "今天天气很号"
        
        # 获取可用的分词器
        from text_tokenizers import get_available_tokenizers
        available_tokenizers = get_available_tokenizers()
        
        if not available_tokenizers:
            print("⚠️  警告: 没有可用的分词器进行测试")
            return False
        
        # 测试每个分词器
        for tokenizer_name in available_tokenizers:
            print(f"\n使用分词器: {tokenizer_name}")
            print("-" * 40)
            
            try:
                # 创建ASRMetrics实例
                metrics = ASRMetrics(tokenizer_name=tokenizer_name)
                print(f"✓ 使用{tokenizer_name}创建ASRMetrics成功")
                
                # 计算CER
                cer = metrics.calculate_cer(reference_text, hypothesis_text)
                print(f"字符错误率 (CER): {cer:.4f}")
                
                # 计算准确率
                accuracy = metrics.calculate_accuracy(reference_text, hypothesis_text)
                print(f"准确率: {accuracy:.4f}")
                
                # 计算详细指标
                detailed_metrics = metrics.calculate_detailed_metrics(reference_text, hypothesis_text)
                print(f"详细指标:")
                print(f"  - 参考文本长度: {detailed_metrics['ref_length']}")
                print(f"  - 假设文本长度: {detailed_metrics['hyp_length']}")
                print(f"  - 替换错误: {detailed_metrics['substitutions']}")
                print(f"  - 删除错误: {detailed_metrics['deletions']}")
                print(f"  - 插入错误: {detailed_metrics['insertions']}")
                print(f"  - 使用分词器: {detailed_metrics['tokenizer']}")
                
                # 测试语气词过滤
                cer_filtered = metrics.calculate_cer(reference_text, hypothesis_text, filter_fillers=True)
                print(f"语气词过滤后CER: {cer_filtered:.4f}")
                
            except Exception as e:
                print(f"✗ 使用{tokenizer_name}测试ASRMetrics失败: {str(e)}")
        
        return True
        
    except ImportError as e:
        print(f"✗ ASRMetrics类导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ ASRMetrics测试过程中出现错误: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("开始分词器架构测试...")
    
    # 测试分词器架构
    tokenizer_test_result = test_tokenizers()
    
    # 测试ASRMetrics类
    asr_metrics_test_result = test_asr_metrics()
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    if tokenizer_test_result:
        print("✓ 分词器架构测试: 通过")
    else:
        print("✗ 分词器架构测试: 失败")
    
    if asr_metrics_test_result:
        print("✓ ASRMetrics类测试: 通过")
    else:
        print("✗ ASRMetrics类测试: 失败")
    
    if tokenizer_test_result and asr_metrics_test_result:
        print("\n🎉 所有测试通过！分词器架构工作正常。")
        return True
    else:
        print("\n❌ 部分测试失败，请检查相关问题。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 