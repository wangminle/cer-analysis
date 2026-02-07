#!/usr/bin/env python3
"""
详细的分词器对比测试 - 使用更复杂的测试用例
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from text_tokenizers.tokenizers.factory import TokenizerFactory

def comprehensive_tokenizer_test():
    """全面的分词器测试"""
    
    print("🔍 全面分词器对比测试...")
    
    # 更复杂和多样化的测试文本
    complex_test_texts = [
        # 基础测试
        "我爱北京天安门",
        "中国科学技术大学",
        
        # 歧义词测试
        "研究生命的起源",  # "研究生"还是"研究"+"生命"
        "乒乓球拍卖完了",  # "乒乓球拍"还是"乒乓球"+"拍卖"
        "他说的确实在理",  # "的确"还是"的"+"确实"
        
        # 专有名词测试
        "清华大学计算机系",
        "中国人民解放军",
        "阿里巴巴集团",
        
        # 技术词汇测试
        "机器学习算法优化",
        "深度神经网络模型",
        "自然语言处理技术",
        
        # 混合文本测试
        "iPhone15 Pro Max价格上涨了",
        "COVID-19疫苗接种工作",
        "AI+医疗的发展前景",
        
        # 古文/诗词测试
        "春眠不觉晓，处处闻啼鸟",
        "海内存知己，天涯若比邻",
        
        # 长句子测试
        "在人工智能快速发展的今天，机器学习和深度学习技术在各个领域都有着广泛的应用",
        
        # 标点符号测试
        "你好！请问现在几点了？",
        "苹果、香蕉、橘子都是水果。",
        
        # 数字和单位测试
        "今天气温25摄氏度",
        "这本书售价29.9元",
        "距离目标还有3.5公里"
    ]
    
    try:
        # 获取分词器实例
        thulac_tokenizer = TokenizerFactory.get_tokenizer('thulac')
        hanlp_tokenizer = TokenizerFactory.get_tokenizer('hanlp')
        
        print(f"\n📊 分词器信息:")
        print(f"THULAC: {type(thulac_tokenizer)} (ID: {id(thulac_tokenizer)})")
        print(f"HanLP:  {type(hanlp_tokenizer)} (ID: {id(hanlp_tokenizer)})")
        
        # 统计差异
        total_tests = len(complex_test_texts)
        identical_results = 0
        different_results = 0
        
        print(f"\n📝 详细分词结果对比:")
        print("=" * 80)
        
        for i, text in enumerate(complex_test_texts, 1):
            thulac_result = thulac_tokenizer.cut(text)
            hanlp_result = hanlp_tokenizer.cut(text)
            
            is_identical = thulac_result == hanlp_result
            if is_identical:
                identical_results += 1
            else:
                different_results += 1
            
            # 显示结果
            status = "✅ 相同" if is_identical else "❌ 不同"
            print(f"\n{i:2d}. 文本: {text}")
            print(f"    THULAC: {thulac_result}")
            print(f"    HanLP:  {hanlp_result}")
            print(f"    状态:   {status}")
            
            # 如果不同，详细分析差异
            if not is_identical:
                print(f"    📊 差异分析:")
                print(f"       THULAC词数: {len(thulac_result)}")
                print(f"       HanLP词数:  {len(hanlp_result)}")
                
                # 找出不同的词
                thulac_set = set(thulac_result)
                hanlp_set = set(hanlp_result)
                thulac_only = thulac_set - hanlp_set
                hanlp_only = hanlp_set - thulac_set
                
                if thulac_only:
                    print(f"       THULAC独有: {list(thulac_only)}")
                if hanlp_only:
                    print(f"       HanLP独有:  {list(hanlp_only)}")
        
        print("\n" + "=" * 80)
        print(f"🎯 测试统计:")
        print(f"   总测试数:     {total_tests}")
        print(f"   结果相同:     {identical_results} ({identical_results/total_tests*100:.1f}%)")
        print(f"   结果不同:     {different_results} ({different_results/total_tests*100:.1f}%)")
        
        if identical_results == total_tests:
            print(f"\n⚠️  严重问题: 所有{total_tests}个测试文本的分词结果都完全相同！")
            print("   这表明可能存在以下问题之一:")
            print("   1. HanLP模型实际未生效，使用了fallback机制")
            print("   2. 两个分词器底层使用了相同的分词逻辑")
            print("   3. 存在某种缓存或单例模式问题")
        elif identical_results > total_tests * 0.8:
            print(f"\n⚠️  可疑: {identical_results/total_tests*100:.1f}%的结果相同，比例过高")
        else:
            print(f"\n✅ 正常: 分词器表现出了预期的差异性")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_model_independence():
    """测试模型独立性"""
    
    print(f"\n🔬 测试模型独立性...")
    
    try:
        # 直接使用HanLP和THULAC库进行测试
        import hanlp
        import thulac
        
        # 直接加载模型
        hanlp_model = hanlp.load(hanlp.pretrained.tok.SIGHAN2005_PKU_BERT_BASE_ZH)
        thulac_model = thulac.thulac(seg_only=True)
        
        test_text = "研究生命的起源"
        
        # 直接使用模型
        hanlp_direct = hanlp_model(test_text)
        thulac_direct_raw = thulac_model.cut(test_text, text=True)
        thulac_direct = thulac_direct_raw.split()
        
        print(f"测试文本: {test_text}")
        print(f"HanLP直接调用: {hanlp_direct}")
        print(f"THULAC直接调用: {thulac_direct}")
        print(f"直接调用结果相同: {hanlp_direct == thulac_direct}")
        
        # 与封装版本对比
        thulac_tokenizer = TokenizerFactory.get_tokenizer('thulac')
        hanlp_tokenizer = TokenizerFactory.get_tokenizer('hanlp')
        
        thulac_wrapped = thulac_tokenizer.cut(test_text)
        hanlp_wrapped = hanlp_tokenizer.cut(test_text)
        
        print(f"\nTHULAC封装版本: {thulac_wrapped}")
        print(f"HanLP封装版本:  {hanlp_wrapped}")
        print(f"封装版本结果相同: {thulac_wrapped == hanlp_wrapped}")
        
        print(f"\n🔍 一致性检查:")
        print(f"THULAC直接vs封装: {thulac_direct == thulac_wrapped}")
        print(f"HanLP直接vs封装:  {hanlp_direct == hanlp_wrapped}")
        
    except Exception as e:
        print(f"❌ 独立性测试失败: {str(e)}")

if __name__ == "__main__":
    comprehensive_tokenizer_test()
    test_model_independence() 