#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界条件测试模块

覆盖场景：
- 空文本（空字符串、仅空白、仅标点）
- 完全相同文本
- 完全不同文本
- 超长文本
- 特殊字符（emoji、数字、混合语言）
- 语气词过滤边界
- calculate_cer 与 calculate_detailed_metrics 一致性
"""

import pytest
from cer_tool.metrics import ASRMetrics


# ────────────────── 共享 fixture ──────────────────

@pytest.fixture(scope="module")
def metrics():
    """共享的 jieba ASRMetrics 实例（module 级复用，减少初始化开销）"""
    return ASRMetrics(tokenizer_name='jieba')


# ════════════════════════════════════════════════════
# 第一组：空文本边界
# ════════════════════════════════════════════════════

class TestEmptyTextBoundary:
    """空文本边界条件测试"""

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_both_empty(self, metrics):
        """双方都是空字符串 → CER=0.0, accuracy=1.0（完全匹配）"""
        cer = metrics.calculate_cer("", "")
        assert cer == 0.0, f"双空 CER 应为 0.0，实际={cer}"

        result = metrics.calculate_detailed_metrics("", "")
        assert result['cer'] == 0.0
        assert result['accuracy'] == 1.0
        assert result['ref_length'] == 0
        assert result['hyp_length'] == 0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_empty_ref_nonempty_hyp(self, metrics):
        """空参考 + 非空假设 → CER=1.0, accuracy=0.0"""
        cer = metrics.calculate_cer("", "你好世界")
        assert cer == 1.0, f"空ref非空hyp CER 应为 1.0，实际={cer}"

        result = metrics.calculate_detailed_metrics("", "你好世界")
        assert result['cer'] == 1.0
        assert result['accuracy'] == 0.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_nonempty_ref_empty_hyp(self, metrics):
        """非空参考 + 空假设 → CER=1.0, accuracy=0.0"""
        cer = metrics.calculate_cer("今天天气很好", "")
        assert cer == 1.0, f"非空ref空hyp CER 应为 1.0，实际={cer}"

        result = metrics.calculate_detailed_metrics("今天天气很好", "")
        assert result['cer'] == 1.0
        assert result['accuracy'] == 0.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_whitespace_only_ref(self, metrics):
        """仅空白字符的参考文本 → 预处理后为空"""
        cer = metrics.calculate_cer("   \t\n  ", "有内容")
        assert cer == 1.0, f"空白ref CER 应为 1.0，实际={cer}"

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_both_whitespace_only(self, metrics):
        """双方都是空白字符 → 预处理后都空 → CER=0.0"""
        cer = metrics.calculate_cer("   ", "  \t ")
        assert cer == 0.0, f"双空白 CER 应为 0.0，实际={cer}"


# ════════════════════════════════════════════════════
# 第二组：仅标点边界
# ════════════════════════════════════════════════════

class TestPunctuationBoundary:
    """仅标点符号的边界条件测试"""

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_punctuation_only_ref(self, metrics):
        """仅标点的参考文本 + 有内容的假设文本
        标点被预处理移除后 ref 为空 → CER=1.0
        """
        result = metrics.calculate_detailed_metrics("，。！？、", "有内容")
        assert result['cer'] == 1.0
        assert result['accuracy'] == 0.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_both_punctuation_only(self, metrics):
        """双方都是仅标点 → 预处理后双空 → CER=0.0"""
        result = metrics.calculate_detailed_metrics("，。！", "？、；")
        assert result['cer'] == 0.0
        assert result['accuracy'] == 1.0


# ════════════════════════════════════════════════════
# 第三组：完全相同 / 完全不同
# ════════════════════════════════════════════════════

class TestExactMatchAndMismatch:
    """完全匹配和完全不匹配的测试"""

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_identical_text(self, metrics):
        """完全相同的文本 → CER=0.0, accuracy=1.0"""
        text = "今天天气非常好适合出门散步"
        cer = metrics.calculate_cer(text, text)
        assert cer == 0.0

        result = metrics.calculate_detailed_metrics(text, text)
        assert result['accuracy'] == 1.0
        assert result['substitutions'] == 0
        assert result['deletions'] == 0
        assert result['insertions'] == 0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_completely_different(self, metrics):
        """完全不同的文本（无共同字符）→ CER > 0"""
        result = metrics.calculate_detailed_metrics("甲乙丙", "丁戊己")
        assert result['cer'] > 0
        assert result['accuracy'] < 1.0
        # 等长字符串全替换时，CER ≈ 1.0
        assert result['substitutions'] == 3

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_single_char_match(self, metrics):
        """单字符完全匹配"""
        cer = metrics.calculate_cer("好", "好")
        assert cer == 0.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_single_char_mismatch(self, metrics):
        """单字符完全不匹配 → CER=1.0"""
        cer = metrics.calculate_cer("好", "坏")
        assert cer == 1.0


# ════════════════════════════════════════════════════
# 第四组：超长文本与性能安全
# ════════════════════════════════════════════════════

class TestLongTextBoundary:
    """超长文本边界测试"""

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_long_identical_text(self, metrics):
        """超长相同文本（10000字）→ CER=0.0 且不崩溃"""
        long_text = "今天天气很好" * 1667  # ~10002 字
        cer = metrics.calculate_cer(long_text, long_text)
        assert cer == 0.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_long_vs_short(self, metrics):
        """超长参考 vs 短假设 → CER 高但不崩溃"""
        long_ref = "测试文本" * 500  # 2000 字
        short_hyp = "测试"
        result = metrics.calculate_detailed_metrics(long_ref, short_hyp)
        assert 0 < result['cer'] <= 1.0
        assert result['accuracy'] >= 0.0


# ════════════════════════════════════════════════════
# 第五组：特殊字符
# ════════════════════════════════════════════════════

class TestSpecialCharacterBoundary:
    """特殊字符边界测试"""

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_numbers_only(self, metrics):
        """纯数字文本对比"""
        cer = metrics.calculate_cer("12345", "12345")
        assert cer == 0.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_mixed_chinese_english(self, metrics):
        """中英文混合文本"""
        result = metrics.calculate_detailed_metrics("hello世界", "hello世界")
        assert result['cer'] == 0.0
        assert result['accuracy'] == 1.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_mixed_with_differences(self, metrics):
        """中英文混合文本有差异"""
        result = metrics.calculate_detailed_metrics("hello世界", "hallo世界")
        assert result['cer'] > 0
        assert result['accuracy'] < 1.0


# ════════════════════════════════════════════════════
# 第六组：一致性验证
# ════════════════════════════════════════════════════

class TestConsistency:
    """calculate_cer 与 calculate_detailed_metrics 一致性验证"""

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_cer_consistency_normal(self, metrics):
        """正常文本：两个方法返回的 CER 应一致"""
        ref = "今天天气非常好"
        hyp = "今天天汽非常好"
        cer_simple = metrics.calculate_cer(ref, hyp)
        result = metrics.calculate_detailed_metrics(ref, hyp)
        assert abs(cer_simple - result['cer']) < 1e-6, \
            f"CER 不一致: calculate_cer={cer_simple}, detailed={result['cer']}"

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_cer_consistency_empty(self, metrics):
        """空文本：两个方法返回的 CER 应一致"""
        for ref, hyp in [("", ""), ("", "abc"), ("abc", "")]:
            cer_simple = metrics.calculate_cer(ref, hyp)
            result = metrics.calculate_detailed_metrics(ref, hyp)
            assert abs(cer_simple - result['cer']) < 1e-6, \
                f"({ref!r}, {hyp!r}) CER 不一致: simple={cer_simple}, detailed={result['cer']}"

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_accuracy_range(self, metrics):
        """accuracy 值域验证：应在 [0.0, 1.0] 或允许 CER>1 时为负数"""
        # 正常情况 accuracy 在 [0, 1]
        result = metrics.calculate_detailed_metrics("你好", "你好")
        assert 0.0 <= result['accuracy'] <= 1.0

        result = metrics.calculate_detailed_metrics("你好", "他坏")
        assert result['accuracy'] >= 0.0 or result['cer'] > 1.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_cer_nonnegative(self, metrics):
        """CER 值域验证：CER >= 0"""
        test_cases = [
            ("", ""), ("", "a"), ("a", ""), ("abc", "abc"),
            ("今天", "明天"), ("你好世界", "你好")
        ]
        for ref, hyp in test_cases:
            cer = metrics.calculate_cer(ref, hyp)
            assert cer >= 0.0, f"({ref!r}, {hyp!r}) CER={cer} < 0"
