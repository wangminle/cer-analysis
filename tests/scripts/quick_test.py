#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证项目结构整理后的功能
"""

import sys
import os
import time

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_project_structure():
    """测试项目结构"""
    print("🔍 测试项目结构...")
    
    # 检查关键文件是否存在
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    tests_dir = os.path.dirname(__file__)
    
    key_files = {
        '主程序': os.path.join(src_dir, 'main_with_tokenizers.py'),
        '计算引擎': os.path.join(src_dir, 'asr_metrics_refactored.py'),
        '分词器模块': os.path.join(src_dir, 'text_tokenizers', '__init__.py'),
        'HanLP集成测试': os.path.join(tests_dir, 'test_hanlp_integration.py'),
        '简单测试': os.path.join(tests_dir, 'simple_test.py'),
    }
    
    all_exist = True
    for name, path in key_files.items():
        if os.path.exists(path):
            print(f"   ✅ {name}: 存在")
        else:
            print(f"   ❌ {name}: 缺失 ({path})")
            all_exist = False
    
    return all_exist

def test_imports():
    """测试核心模块导入"""
    print("\n📦 测试核心模块导入...")
    
    try:
        from text_tokenizers import get_available_tokenizers, get_tokenizer
        print("   ✅ 分词器模块导入成功")
        
        from asr_metrics_refactored import ASRMetrics
        print("   ✅ ASR度量模块导入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        return False

def test_tokenizers():
    """测试分词器功能"""
    print("\n🔤 测试分词器功能...")
    
    try:
        from text_tokenizers import get_available_tokenizers, get_tokenizer
        
        # 获取可用分词器
        tokenizers = get_available_tokenizers()
        print(f"   可用分词器: {tokenizers}")
        
        # 测试每个分词器
        test_text = "测试中文分词功能"
        results = {}
        
        for tokenizer_name in tokenizers:
            try:
                start_time = time.time()
                tokenizer = get_tokenizer(tokenizer_name)
                words = tokenizer.cut(test_text)
                end_time = time.time()
                
                results[tokenizer_name] = {
                    'words': words,
                    'time': end_time - start_time,
                    'status': '✅'
                }
                print(f"   ✅ {tokenizer_name}: {words} (耗时: {end_time - start_time:.4f}秒)")
                
            except Exception as e:
                results[tokenizer_name] = {
                    'error': str(e),
                    'status': '❌'
                }
                print(f"   ❌ {tokenizer_name}: 失败 - {e}")
        
        # 检查HanLP是否可用
        hanlp_available = 'hanlp' in results and results['hanlp']['status'] == '✅'
        if hanlp_available:
            print("   🎉 HanLP分词器工作正常！")
        
        return len(results) > 0 and any(r['status'] == '✅' for r in results.values())
        
    except Exception as e:
        print(f"   ❌ 分词器测试失败: {e}")
        return False

def test_asr_metrics():
    """测试ASR度量计算"""
    print("\n📊 测试ASR度量计算...")
    
    try:
        from asr_metrics_refactored import ASRMetrics
        from text_tokenizers import get_available_tokenizers
        
        tokenizers = get_available_tokenizers()
        if not tokenizers:
            print("   ⚠️ 没有可用的分词器")
            return False
        
        # 使用第一个可用的分词器进行测试
        tokenizer_name = tokenizers[0]
        print(f"   使用分词器: {tokenizer_name}")
        
        asr_metrics = ASRMetrics(tokenizer_name=tokenizer_name)
        
        # 测试CER计算
        reference = "这是一个测试句子"
        hypothesis = "这是个测试句子"
        
        cer = asr_metrics.calculate_cer(reference, hypothesis)
        print(f"   CER计算结果: {cer}")
        
        # 如果HanLP可用，也测试一下
        if 'hanlp' in tokenizers:
            print("   🎯 使用HanLP进行高精度测试...")
            hanlp_metrics = ASRMetrics(tokenizer_name='hanlp')
            hanlp_cer = hanlp_metrics.calculate_cer(reference, hypothesis)
            print(f"   HanLP CER结果: {hanlp_cer}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ASR度量测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 ASR字准统计工具 - 项目结构整理后快速测试")
    print("=" * 60)
    
    tests = [
        ("项目结构", test_project_structure),
        ("模块导入", test_imports), 
        ("分词器功能", test_tokenizers),
        ("ASR度量计算", test_asr_metrics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {e}")
        
        print("-" * 40)
    
    print("=" * 60)
    print(f"📈 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目结构整理成功，功能正常！")
        print("💡 可以运行以下命令启动主程序:")
        print("   cd ../src && python main_with_tokenizers.py")
    elif passed >= total // 2:
        print("⚠️ 部分测试通过，建议检查失败的项目")
    else:
        print("❌ 多项测试失败，需要修复问题")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 