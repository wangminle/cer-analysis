#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分词器单元测试模块

覆盖场景：
- get_available_tokenizers 可用性检测
- get_tokenizer 工厂方法
- get_tokenizer_info 信息获取
- Jieba 分词器功能（cut / posseg / tokenize）
- 分词器基类接口（validate_text / get_info）
- 工厂类单例与缓存
- 异常处理（无效分词器名称、None 输入）
- THULAC / HanLP 可选分词器（按环境跳过）
"""

import pytest
from cer_tool.tokenizers import (
    get_available_tokenizers, get_tokenizer, get_tokenizer_info,
    get_cached_tokenizer_info,
    TokenizerFactory, BaseTokenizer,
    TokenizerError, TokenizerInitError, TokenizerProcessError,
    JiebaTokenizer,
)


# ────────────────── fixture ──────────────────

@pytest.fixture(scope="module")
def jieba_tok():
    """获取 jieba 分词器实例"""
    return get_tokenizer('jieba')


# ════════════════════════════════════════════════════
# 第一组：可用性检测
# ════════════════════════════════════════════════════

class TestAvailability:
    """分词器可用性检测测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_available_tokenizers_is_list(self):
        """get_available_tokenizers 返回列表"""
        available = get_available_tokenizers()
        assert isinstance(available, list)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_jieba_always_available(self):
        """jieba 分词器应始终可用"""
        available = get_available_tokenizers()
        assert 'jieba' in available

    @pytest.mark.basic
    @pytest.mark.unit
    def test_supported_tokenizer_names(self):
        """支持的分词器名称应包含 jieba/thulac/hanlp"""
        expected = {'jieba', 'thulac', 'hanlp'}
        registered = set(TokenizerFactory._available_tokenizers.keys())
        assert expected == registered


# ════════════════════════════════════════════════════
# 第二组：工厂方法与单例
# ════════════════════════════════════════════════════

class TestFactory:
    """工厂类测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_tokenizer_jieba(self):
        """工厂方法获取 jieba 分词器"""
        tok = get_tokenizer('jieba')
        assert tok is not None
        assert tok.is_initialized

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_tokenizer_invalid_name(self):
        """传入不存在的分词器名称 → 抛出异常"""
        with pytest.raises((ValueError, TokenizerInitError)):
            get_tokenizer('nonexistent')

    @pytest.mark.basic
    @pytest.mark.unit
    def test_singleton_returns_same_instance(self):
        """同名分词器应返回同一缓存实例"""
        tok1 = get_tokenizer('jieba')
        tok2 = get_tokenizer('jieba')
        assert tok1 is tok2

    @pytest.mark.basic
    @pytest.mark.unit
    def test_factory_singleton(self):
        """TokenizerFactory 自身是单例"""
        f1 = TokenizerFactory()
        f2 = TokenizerFactory()
        assert f1 is f2


# ════════════════════════════════════════════════════
# 第三组：分词器信息获取
# ════════════════════════════════════════════════════

class TestTokenizerInfo:
    """分词器信息获取测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_tokenizer_info_jieba(self):
        """获取 jieba 分词器信息"""
        info = get_tokenizer_info('jieba')
        assert isinstance(info, dict)
        assert info.get('available') is True

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_tokenizer_info_invalid(self):
        """获取无效分词器信息 → 返回 available=False"""
        info = get_tokenizer_info('nonexistent')
        assert isinstance(info, dict)
        assert info.get('available') is False

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_cached_tokenizer_info_after_get(self):
        """获取分词器后，缓存信息应可用"""
        # 确保 jieba 已被获取
        get_tokenizer('jieba')
        cached_info = get_cached_tokenizer_info('jieba')
        assert cached_info is not None
        assert cached_info.get('available') is True
        assert cached_info.get('cached') is True

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_cached_info_before_init(self):
        """未初始化的分词器缓存信息应为 None（如果未使用过）"""
        info = get_cached_tokenizer_info('nonexistent')
        assert info is None


# ════════════════════════════════════════════════════
# 第四组：Jieba 分词器核心功能
# ════════════════════════════════════════════════════

class TestJiebaFunctions:
    """Jieba 分词器核心功能测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_cut_basic(self, jieba_tok):
        """jieba cut：基本分词"""
        words = jieba_tok.cut("今天天气很好")
        assert isinstance(words, list)
        assert len(words) > 0
        # 拼接后应等于原文（不含空格）
        assert "".join(words) == "今天天气很好"

    @pytest.mark.basic
    @pytest.mark.unit
    def test_cut_empty(self, jieba_tok):
        """jieba cut：空字符串"""
        words = jieba_tok.cut("")
        assert isinstance(words, list)
        # 空字符串分词结果应为空列表或仅含空字符串
        assert len("".join(words)) == 0

    @pytest.mark.basic
    @pytest.mark.unit
    def test_posseg_basic(self, jieba_tok):
        """jieba posseg：词性标注"""
        result = jieba_tok.posseg("我喜欢北京天安门")
        assert isinstance(result, list)
        assert len(result) > 0
        # 每个元素应是 (word, pos) 元组
        for item in result:
            assert len(item) == 2
            word, pos = item
            assert isinstance(word, str)
            assert isinstance(pos, str)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_tokenize_basic(self, jieba_tok):
        """jieba tokenize：带位置信息的分词"""
        result = jieba_tok.tokenize("今天天气很好")
        assert isinstance(result, list)
        assert len(result) > 0
        # 每个元素应是 (word, start, end) 元组
        for item in result:
            assert len(item) == 3
            word, start, end = item
            assert isinstance(word, str)
            assert isinstance(start, int)
            assert isinstance(end, int)
            assert start >= 0
            assert end >= start


# ════════════════════════════════════════════════════
# 第五组：基类接口测试
# ════════════════════════════════════════════════════

class TestBaseTokenizerInterface:
    """基类接口测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_validate_text_normal(self, jieba_tok):
        """validate_text：正常文本"""
        result = jieba_tok.validate_text("  你好世界  ")
        assert result == "你好世界"

    @pytest.mark.basic
    @pytest.mark.unit
    def test_validate_text_none(self, jieba_tok):
        """validate_text：None 输入 → 抛出异常"""
        with pytest.raises(TokenizerProcessError, match="不能为None"):
            jieba_tok.validate_text(None)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_validate_text_non_string(self, jieba_tok):
        """validate_text：非字符串输入 → 抛出异常"""
        with pytest.raises(TokenizerProcessError, match="必须是字符串"):
            jieba_tok.validate_text(12345)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_validate_text_empty(self, jieba_tok):
        """validate_text：空字符串 → 返回空字符串"""
        result = jieba_tok.validate_text("   ")
        assert result == ""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_info(self, jieba_tok):
        """get_info：返回分词器信息字典"""
        info = jieba_tok.get_info()
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'initialized' in info
        assert info['initialized'] is True

    @pytest.mark.basic
    @pytest.mark.unit
    def test_str_repr(self, jieba_tok):
        """__str__ 和 __repr__ 不崩溃"""
        s = str(jieba_tok)
        assert isinstance(s, str)
        r = repr(jieba_tok)
        assert isinstance(r, str)


# ════════════════════════════════════════════════════
# 第六组：可选分词器（按环境跳过）
# ════════════════════════════════════════════════════

class TestOptionalTokenizers:
    """可选分词器测试（THULAC / HanLP）"""

    @pytest.mark.optional
    @pytest.mark.unit
    def test_thulac_if_available(self):
        """THULAC 分词器功能（环境中有则测试）"""
        available = get_available_tokenizers()
        if 'thulac' not in available:
            pytest.skip("THULAC 未安装，跳过")
        tok = get_tokenizer('thulac')
        words = tok.cut("今天天气很好")
        assert isinstance(words, list)
        assert len(words) > 0

    @pytest.mark.optional
    @pytest.mark.unit
    def test_hanlp_if_available(self):
        """HanLP 分词器功能（环境中有则测试）"""
        available = get_available_tokenizers()
        if 'hanlp' not in available:
            pytest.skip("HanLP 未安装，跳过")
        tok = get_tokenizer('hanlp')
        words = tok.cut("今天天气很好")
        assert isinstance(words, list)
        assert len(words) > 0
