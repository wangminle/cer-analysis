#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用pytest标记的分层测试示例
演示如何使用basic、optional、slow、network等标记
"""

import sys
import os
import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../dev/src'))

from asr_metrics_refactored import ASRMetrics
from text_tokenizers import get_available_tokenizers, get_tokenizer_info


def is_tokenizer_available(tokenizer_name: str) -> bool:
    """
    检查分词器是否可用
    
    Args:
        tokenizer_name: 分词器名称
        
    Returns:
        bool: 是否可用
    """
    try:
        info = get_tokenizer_info(tokenizer_name)
        return info.get('available', False)
    except:
        return False


# ==================== 基础测试 ====================

@pytest.mark.basic
@pytest.mark.unit
def test_jieba_tokenizer_basic():
    """基础测试 - jieba分词器基本功能"""
    assert is_tokenizer_available('jieba'), "jieba分词器应该总是可用"
    
    metrics = ASRMetrics(tokenizer_name='jieba')
    ref = "今天天气很好"
    hyp = "今天天气很号"
    
    cer = metrics.calculate_cer(ref, hyp)
    assert 0 <= cer <= 1, "CER应该在0-1之间"
    assert cer > 0, "应该有错误"


@pytest.mark.basic
@pytest.mark.unit
def test_edit_distance_calculation():
    """基础测试 - 编辑距离计算"""
    metrics = ASRMetrics(tokenizer_name='jieba')
    
    # 完全相同
    distance = metrics._calculate_edit_distance("hello", "hello")
    assert distance == 0
    
    # 一个替换
    distance = metrics._calculate_edit_distance("hello", "hallo")
    assert distance == 1
    
    # 一个删除
    distance = metrics._calculate_edit_distance("hello", "helo")
    assert distance == 1
    
    # 一个插入
    distance = metrics._calculate_edit_distance("helo", "hello")
    assert distance == 1


@pytest.mark.basic
@pytest.mark.unit
def test_normalize_chinese_text_basic():
    """基础测试 - 中文文本标准化"""
    metrics = ASRMetrics(tokenizer_name='jieba')
    
    # 测试全角转换
    text = "Hello１２３"
    result = metrics.normalize_chinese_text(text, normalize_width=True, remove_punctuation=False)
    assert "123" in result, "全角数字应该被转换为半角"


# ==================== 可选分词器测试 ====================

@pytest.mark.optional
@pytest.mark.unit
@pytest.mark.skipif(not is_tokenizer_available('thulac'), reason="THULAC not installed")
def test_thulac_tokenizer():
    """可选测试 - THULAC分词器"""
    metrics = ASRMetrics(tokenizer_name='thulac')
    
    test_text = "我来到北京清华大学"
    words = metrics.tokenizer.cut(test_text)
    
    assert isinstance(words, list), "分词结果应该是列表"
    assert len(words) > 0, "应该有分词结果"


@pytest.mark.optional
@pytest.mark.network
@pytest.mark.slow
@pytest.mark.skipif(not is_tokenizer_available('hanlp'), reason="HanLP not available")
def test_hanlp_tokenizer():
    """可选+网络+慢速测试 - HanLP分词器"""
    metrics = ASRMetrics(tokenizer_name='hanlp')
    
    test_text = "我来到北京清华大学"
    words = metrics.tokenizer.cut(test_text)
    
    assert isinstance(words, list), "分词结果应该是列表"
    assert len(words) > 0, "应该有分词结果"


# ==================== 集成测试 ====================

@pytest.mark.integration
@pytest.mark.basic
def test_complete_cer_calculation():
    """集成测试 - 完整的CER计算流程"""
    metrics = ASRMetrics(tokenizer_name='jieba')
    
    ref = "今天天气很好，我们去公园"
    hyp = "今天天气不好，我们去公圆"
    
    # 测试完整流程
    detailed = metrics.calculate_detailed_metrics(ref, hyp)
    
    assert 'cer' in detailed
    assert 'accuracy' in detailed
    assert 'substitutions' in detailed
    assert 'deletions' in detailed
    assert 'insertions' in detailed
    
    # 验证准确率和CER的关系
    assert abs(detailed['accuracy'] + detailed['cer'] - 1.0) < 0.001


@pytest.mark.integration
@pytest.mark.basic
def test_highlight_errors():
    """集成测试 - 错误高亮功能"""
    metrics = ASRMetrics(tokenizer_name='jieba')
    
    ref = "今天天气很好"
    hyp = "今天天气不好"
    
    ref_highlighted, hyp_highlighted = metrics.highlight_errors(ref, hyp)
    
    assert '[' in ref_highlighted or '[' in hyp_highlighted, "应该有错误标记"


# ==================== 慢速测试 ====================

@pytest.mark.slow
@pytest.mark.basic
def test_large_text_processing():
    """慢速测试 - 大文本处理"""
    metrics = ASRMetrics(tokenizer_name='jieba')
    
    # 生成大文本
    base_text = "今天天气很好，我们去公园散步。"
    large_ref = base_text * 100  # 约3000字
    large_hyp = base_text * 100
    
    # 应该能处理大文本
    cer = metrics.calculate_cer(large_ref, large_hyp)
    assert cer == 0.0, "相同文本的CER应该为0"


# ==================== 参数化测试 ====================

@pytest.mark.basic
@pytest.mark.unit
@pytest.mark.parametrize("ref,hyp,expected_cer", [
    ("hello", "hello", 0.0),  # 完全相同
    ("hello", "hallo", 0.2),  # 一个替换，5个字符
    ("abc", "ab", 0.333),     # 一个删除，3个字符
])
def test_cer_parametrized(ref, hyp, expected_cer):
    """参数化测试 - 不同CER场景"""
    metrics = ASRMetrics(tokenizer_name='jieba')
    cer = metrics.calculate_cer(ref, hyp)
    assert abs(cer - expected_cer) < 0.01, f"CER应该约为{expected_cer}"


# ==================== fixture示例 ====================

@pytest.fixture
def jieba_metrics():
    """测试fixture - jieba metrics实例"""
    return ASRMetrics(tokenizer_name='jieba')


@pytest.mark.basic
@pytest.mark.unit
def test_with_fixture(jieba_metrics):
    """使用fixture的测试"""
    ref = "测试文本"
    hyp = "测试文本"
    
    cer = jieba_metrics.calculate_cer(ref, hyp)
    assert cer == 0.0


if __name__ == "__main__":
    # 运行测试的几种方式：
    # 1. 运行所有测试: pytest test_with_pytest_marks.py
    # 2. 只运行基础测试: pytest -m "basic" test_with_pytest_marks.py
    # 3. 只运行可选测试: pytest -m "optional" test_with_pytest_marks.py
    # 4. 排除慢速测试: pytest -m "not slow" test_with_pytest_marks.py
    # 5. 运行基础+集成: pytest -m "basic and integration" test_with_pytest_marks.py
    print("请使用pytest命令运行测试")
    print("示例: pytest -m basic test_with_pytest_marks.py")

