#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HanLP分词器集成
"""

import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_import():
    """测试基本导入"""
    print("1. 测试基本导入...")
    try:
        from text_tokenizers import get_available_tokenizers, get_tokenizer_info
        print("   ✅ 基本导入成功")
        return True
    except Exception as e:
        print(f"   ❌ 基本导入失败: {e}")
        return False

def test_available_tokenizers():
    """测试可用分词器列表"""
    print("2. 测试可用分词器列表...")
    try:
        from text_tokenizers import get_available_tokenizers
        tokenizers = get_available_tokenizers()
        print(f"   可用分词器: {tokenizers}")
        
        if 'hanlp' in tokenizers:
            print("   ✅ HanLP分词器已启用")
            return True
        else:
            print("   ⚠️ HanLP分词器未启用（可能是依赖问题）")
            return False
    except Exception as e:
        print(f"   ❌ 获取分词器列表失败: {e}")
        return False

def test_hanlp_info():
    """测试HanLP分词器信息"""
    print("3. 测试HanLP分词器信息...")
    try:
        from text_tokenizers import get_tokenizer_info
        info = get_tokenizer_info('hanlp')
        print(f"   HanLP信息: {info}")
        
        if info.get('available', False):
            print("   ✅ HanLP分词器可用")
            return True
        else:
            print(f"   ❌ HanLP分词器不可用: {info.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"   ❌ 获取HanLP信息失败: {e}")
        return False

def test_hanlp_tokenizer():
    """测试HanLP分词器功能"""
    print("4. 测试HanLP分词器功能...")
    try:
        from text_tokenizers import get_tokenizer
        tokenizer = get_tokenizer('hanlp')
        
        # 测试分词
        test_text = "商品和服务。"
        words = tokenizer.cut(test_text)
        print(f"   分词结果: {words}")
        
        # 测试词性标注
        words_pos = tokenizer.posseg(test_text)
        print(f"   词性标注: {words_pos}")
        
        print("   ✅ HanLP分词器功能正常")
        return True
        
    except Exception as e:
        print(f"   ❌ HanLP分词器功能测试失败: {e}")
        return False

def test_main_application():
    """测试主应用程序"""
    print("5. 测试主应用程序集成...")
    try:
        from asr_metrics_refactored import ASRMetrics
        
        # 尝试创建HanLP版本的ASRMetrics
        asr_metrics = ASRMetrics(tokenizer_name="hanlp")
        
        # 测试CER计算
        reference = "商品和服务"
        hypothesis = "商品服务"
        cer = asr_metrics.calculate_cer(reference, hypothesis)
        print(f"   CER计算结果: {cer}")
        
        print("   ✅ 主应用程序集成成功")
        return True
        
    except Exception as e:
        print(f"   ❌ 主应用程序集成失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("HanLP分词器集成测试")
    print("=" * 60)
    
    tests = [
        test_basic_import,
        test_available_tokenizers,
        test_hanlp_info,
        test_hanlp_tokenizer,
        test_main_application
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！HanLP分词器集成成功！")
    elif passed >= total // 2:
        print("⚠️ 部分测试通过，需要进一步检查")
    else:
        print("❌ 大部分测试失败，需要修复问题")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 