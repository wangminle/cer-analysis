#!/usr/bin/env python3
"""
测试thulac和hanlp分词器是否使用了相同的模型
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from text_tokenizers.tokenizers.factory import TokenizerFactory

def test_tokenizer_models():
    """测试分词器是否使用了不同的模型"""
    
    print("🔍 测试分词器模型独立性...")
    
    # 测试文本
    test_texts = [
        "我爱北京天安门",
        "中国科学技术大学",
        "人工智能技术发展",
        "今天天气很好"
    ]
    
    try:
        # 获取分词器实例
        thulac_tokenizer = TokenizerFactory.get_tokenizer('thulac')
        hanlp_tokenizer = TokenizerFactory.get_tokenizer('hanlp')
        
        print(f"\n📊 分词器信息:")
        print(f"THULAC实例ID: {id(thulac_tokenizer)}")
        print(f"HanLP实例ID: {id(hanlp_tokenizer)}")
        print(f"THULAC模型: {type(thulac_tokenizer.thu) if hasattr(thulac_tokenizer, 'thu') else 'None'}")
        print(f"HanLP模型: {type(hanlp_tokenizer.tok_model) if hasattr(hanlp_tokenizer, 'tok_model') else 'None'}")
        
        # 检查模型对象是否相同
        if hasattr(thulac_tokenizer, 'thu') and hasattr(hanlp_tokenizer, 'tok_model'):
            print(f"\n🔍 模型对象检查:")
            print(f"THULAC模型ID: {id(thulac_tokenizer.thu)}")
            print(f"HanLP模型ID: {id(hanlp_tokenizer.tok_model)}")
            print(f"模型是否相同: {thulac_tokenizer.thu is hanlp_tokenizer.tok_model}")
        
        # 测试分词结果
        print(f"\n📝 分词结果对比:")
        results_identical = True
        
        for text in test_texts:
            thulac_result = thulac_tokenizer.cut(text)
            hanlp_result = hanlp_tokenizer.cut(text)
            
            print(f"\n文本: {text}")
            print(f"THULAC: {thulac_result}")
            print(f"HanLP:  {hanlp_result}")
            print(f"结果相同: {thulac_result == hanlp_result}")
            
            if thulac_result != hanlp_result:
                results_identical = False
        
        print(f"\n🎯 测试结论:")
        if results_identical:
            print("⚠️  警告：所有测试文本的分词结果都相同！")
            print("   这可能表明两个分词器使用了相同的模型或算法")
        else:
            print("✅ 正常：两个分词器产生了不同的结果")
            
        # 检查缓存状态
        print(f"\n💾 缓存状态:")
        cache = TokenizerFactory._tokenizers
        print(f"缓存的分词器: {list(cache.keys())}")
        for name, tokenizer in cache.items():
            print(f"{name}: {id(tokenizer)}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_separate_instances():
    """测试创建独立实例是否解决问题"""
    
    print("\n🔄 测试独立实例创建...")
    
    try:
        # 清除缓存
        TokenizerFactory.clear_cache()
        
        # 创建独立实例
        thulac1 = TokenizerFactory.create_tokenizer('thulac')
        thulac2 = TokenizerFactory.create_tokenizer('thulac')
        hanlp1 = TokenizerFactory.create_tokenizer('hanlp')
        hanlp2 = TokenizerFactory.create_tokenizer('hanlp')
        
        print(f"THULAC实例1 ID: {id(thulac1)}")
        print(f"THULAC实例2 ID: {id(thulac2)}")
        print(f"HanLP实例1 ID:  {id(hanlp1)}")
        print(f"HanLP实例2 ID:  {id(hanlp2)}")
        
        print(f"THULAC实例是否相同: {thulac1 is thulac2}")
        print(f"HanLP实例是否相同: {hanlp1 is hanlp2}")
        
        # 测试分词结果
        test_text = "我爱北京天安门"
        thulac1_result = thulac1.cut(test_text)
        hanlp1_result = hanlp1.cut(test_text)
        
        print(f"\n测试文本: {test_text}")
        print(f"THULAC结果: {thulac1_result}")
        print(f"HanLP结果:  {hanlp1_result}")
        print(f"结果相同: {thulac1_result == hanlp1_result}")
        
    except Exception as e:
        print(f"❌ 独立实例测试失败: {str(e)}")

if __name__ == "__main__":
    test_tokenizer_models()
    test_separate_instances() 