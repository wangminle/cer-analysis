#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心指标计算测试模块

覆盖场景：
- 编辑操作统计（替换/删除/插入的精确回溯）
- CER 计算（基本和参数化）
- WER 计算
- accuracy 计算
- 详细指标 (detailed_metrics) 一致性
- 文本标准化 (normalize_chinese_text) 各配置
- 预处理流程 (preprocess_text)
- 差异展示 (show_differences, highlight_errors)
- 内置编辑距离（无 Levenshtein 库时的备选算法）
- get_tokenizer_info
"""

import pytest
from cer_tool.metrics import ASRMetrics


# ────────────────── 共享 fixture ──────────────────

@pytest.fixture(scope="module")
def metrics():
    """共享的 jieba ASRMetrics 实例"""
    return ASRMetrics(tokenizer_name='jieba')


# ════════════════════════════════════════════════════
# 第一组：编辑操作精确回溯
# ════════════════════════════════════════════════════

class TestEditOps:
    """DP 路径回溯算法精确性测试（合并自 test_edit_ops_accurate.py）"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_pure_substitution(self, metrics):
        """纯替换错误：abcdef → axcxef → S=2, D=0, I=0"""
        s, d, i = metrics._calculate_edit_ops_with_backtrack("abcdef", "axcxef")
        assert (s, d, i) == (2, 0, 0)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_pure_deletion(self, metrics):
        """纯删除错误：abcdef → abef → S=0, D=2, I=0"""
        s, d, i = metrics._calculate_edit_ops_with_backtrack("abcdef", "abef")
        assert (s, d, i) == (0, 2, 0)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_pure_insertion(self, metrics):
        """纯插入错误：abef → abcdef → S=0, D=0, I=2"""
        s, d, i = metrics._calculate_edit_ops_with_backtrack("abef", "abcdef")
        assert (s, d, i) == (0, 0, 2)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_mixed_edit_ops(self, metrics):
        """混合错误：kitten → sitting 总编辑距离=3"""
        s, d, i = metrics._calculate_edit_ops_with_backtrack("kitten", "sitting")
        assert s + d + i == 3

    @pytest.mark.basic
    @pytest.mark.unit
    def test_chinese_single_substitution(self, metrics):
        """中文单字替换：很好 → 不好 → S=1"""
        s, d, i = metrics._calculate_edit_ops_with_backtrack("今天天气很好", "今天天气不好")
        assert (s, d, i) == (1, 0, 0)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_ref_to_empty(self, metrics):
        """有内容→空：全部删除"""
        s, d, i = metrics._calculate_edit_ops_with_backtrack("abc", "")
        assert (s, d, i) == (0, 3, 0)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_identical_strings(self, metrics):
        """完全相同：S=D=I=0"""
        s, d, i = metrics._calculate_edit_ops_with_backtrack("hello", "hello")
        assert (s, d, i) == (0, 0, 0)


# ════════════════════════════════════════════════════
# 第二组：CER 计算（参数化）
# ════════════════════════════════════════════════════

class TestCERCalculation:
    """CER 计算测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    @pytest.mark.parametrize("ref, hyp, expected_cer", [
        ("hello", "hello", 0.0),          # 完全相同
        ("hello", "hallo", 0.2),          # 1/5 = 0.2
        ("abc", "ab", pytest.approx(0.333, abs=0.01)),  # 1/3 ≈ 0.333
        ("你好世界", "你好世界", 0.0),        # 中文完全相同
        ("今天天气很好", "今天天气不好", pytest.approx(1/6, abs=0.01)),  # 1/6
    ])
    def test_cer_parametrized(self, metrics, ref, hyp, expected_cer):
        """参数化 CER 计算验证"""
        cer = metrics.calculate_cer(ref, hyp)
        assert cer == pytest.approx(expected_cer, abs=0.01), \
            f"CER({ref!r}, {hyp!r}) = {cer}, expected {expected_cer}"

    @pytest.mark.basic
    @pytest.mark.unit
    def test_cer_with_filter_fillers(self, metrics):
        """启用语气词过滤后的 CER"""
        ref = "嗯好的啊我知道了"
        hyp = "好的我知道了"
        # 过滤语气词后两者应更接近
        cer_no_filter = metrics.calculate_cer(ref, hyp, filter_fillers=False)
        cer_with_filter = metrics.calculate_cer(ref, hyp, filter_fillers=True)
        # 过滤后 CER 应不大于未过滤
        assert cer_with_filter <= cer_no_filter


# ════════════════════════════════════════════════════
# 第三组：WER / Accuracy 计算
# ════════════════════════════════════════════════════

class TestWERAndAccuracy:
    """WER 和 Accuracy 计算测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_wer_identical(self, metrics):
        """WER：完全相同 → 0.0"""
        wer = metrics.calculate_wer("你好世界", "你好世界")
        assert wer == 0.0

    @pytest.mark.basic
    @pytest.mark.unit
    def test_wer_different(self, metrics):
        """WER：有差异 → > 0"""
        wer = metrics.calculate_wer("今天天气很好", "今天天气不好")
        assert wer > 0

    @pytest.mark.basic
    @pytest.mark.unit
    def test_accuracy_identical(self, metrics):
        """accuracy：完全相同 → 1.0"""
        acc = metrics.calculate_accuracy("你好世界", "你好世界")
        assert acc == 1.0

    @pytest.mark.basic
    @pytest.mark.unit
    def test_accuracy_range(self, metrics):
        """accuracy 值在合理范围内"""
        acc = metrics.calculate_accuracy("今天天气很好", "今天天气不好")
        assert 0.0 <= acc <= 1.0


# ════════════════════════════════════════════════════
# 第四组：文本标准化 (normalize_chinese_text)
# （合并自 test_normalize_strategy.py）
# ════════════════════════════════════════════════════

class TestNormalization:
    """文本标准化功能测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_fullwidth_to_halfwidth(self, metrics):
        """全角字符归一为半角"""
        result = metrics.normalize_chinese_text(
            "ＡＢＣ１２３",
            normalize_width=True,
            normalize_numbers=False,
            remove_punctuation=False
        )
        assert "ABC" in result
        assert "123" in result

    @pytest.mark.basic
    @pytest.mark.unit
    def test_number_normalization(self, metrics):
        """数字归一化：数字序列→0"""
        result = metrics.normalize_chinese_text(
            "今天温度是25度",
            normalize_width=True,
            normalize_numbers=True,
            remove_punctuation=True
        )
        assert "25" not in result  # 数字被归一

    @pytest.mark.basic
    @pytest.mark.unit
    def test_punctuation_removal(self, metrics):
        """标点移除"""
        result = metrics.normalize_chinese_text(
            "你好，世界！",
            normalize_width=True,
            normalize_numbers=False,
            remove_punctuation=True
        )
        assert "，" not in result
        assert "！" not in result

    @pytest.mark.basic
    @pytest.mark.unit
    def test_cer_fullwidth_halfwidth_equivalence(self, metrics):
        """全角和半角数字在 CER 计算中视为等价"""
        cer = metrics.calculate_cer("今天天气很好123", "今天天气很好１２３")
        assert cer == 0.0, f"全半角数字应视为等价，CER={cer}"


# ════════════════════════════════════════════════════
# 第五组：detailed_metrics 完整性
# ════════════════════════════════════════════════════

class TestDetailedMetrics:
    """详细指标完整性测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_all_fields_present(self, metrics):
        """详细指标应包含所有必需字段"""
        result = metrics.calculate_detailed_metrics("你好", "你好")
        required_keys = [
            'cer', 'wer', 'mer', 'wil', 'wip',
            'hits', 'substitutions', 'deletions', 'insertions',
            'ref_length', 'hyp_length', 'accuracy', 'tokenizer'
        ]
        for key in required_keys:
            assert key in result, f"缺少字段: {key}"

    @pytest.mark.basic
    @pytest.mark.unit
    def test_cer_equals_errors_over_ref_length(self, metrics):
        """CER = (S+D+I) / ref_length"""
        result = metrics.calculate_detailed_metrics("我来到北京清华大学", "我来到北京清大学")
        total_errors = result['substitutions'] + result['deletions'] + result['insertions']
        expected_cer = total_errors / result['ref_length']
        assert abs(result['cer'] - expected_cer) < 1e-6

    @pytest.mark.basic
    @pytest.mark.unit
    def test_accuracy_equals_one_minus_cer(self, metrics):
        """accuracy = 1 - CER"""
        result = metrics.calculate_detailed_metrics("今天天气很好", "今天天汽很好")
        assert abs(result['accuracy'] - (1.0 - result['cer'])) < 1e-6

    @pytest.mark.basic
    @pytest.mark.unit
    def test_tokenizer_field(self, metrics):
        """tokenizer 字段应为 jieba"""
        result = metrics.calculate_detailed_metrics("你好", "你好")
        assert result['tokenizer'] == 'jieba'


# ════════════════════════════════════════════════════
# 第六组：差异展示与高亮
# ════════════════════════════════════════════════════

class TestDifferencesAndHighlight:
    """差异展示和高亮功能测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_show_differences_returns_string(self, metrics):
        """show_differences 返回字符串"""
        diff = metrics.show_differences("今天天气很好", "今天天气不好")
        assert isinstance(diff, str)
        assert len(diff) > 0

    @pytest.mark.basic
    @pytest.mark.unit
    def test_highlight_errors_returns_tuple(self, metrics):
        """highlight_errors 返回两个字符串的元组"""
        ref_highlighted, hyp_highlighted = metrics.highlight_errors("今天天气很好", "今天天气不好")
        assert isinstance(ref_highlighted, str)
        assert isinstance(hyp_highlighted, str)

    @pytest.mark.basic
    @pytest.mark.unit
    def test_highlight_identical_no_markers(self, metrics):
        """完全相同的文本高亮不应包含错误标记"""
        ref_h, hyp_h = metrics.highlight_errors("你好世界", "你好世界")
        # 完全相同时不应有替换/删除/插入标记
        assert "[替换]" not in ref_h
        assert "[插入]" not in hyp_h


# ════════════════════════════════════════════════════
# 第七组：内置编辑距离算法
# ════════════════════════════════════════════════════

class TestBuiltinEditDistance:
    """内置纯 Python 编辑距离算法测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_identical(self, metrics):
        """相同字符串编辑距离=0"""
        assert metrics._calculate_edit_distance("hello", "hello") == 0

    @pytest.mark.basic
    @pytest.mark.unit
    def test_empty_to_nonempty(self, metrics):
        """空→非空 编辑距离=长度"""
        assert metrics._calculate_edit_distance("", "abc") == 3

    @pytest.mark.basic
    @pytest.mark.unit
    def test_nonempty_to_empty(self, metrics):
        """非空→空 编辑距离=长度"""
        assert metrics._calculate_edit_distance("abc", "") == 3

    @pytest.mark.basic
    @pytest.mark.unit
    def test_known_distance(self, metrics):
        """已知编辑距离：kitten→sitting=3"""
        assert metrics._calculate_edit_distance("kitten", "sitting") == 3


# ════════════════════════════════════════════════════
# 第八组：get_tokenizer_info
# ════════════════════════════════════════════════════

class TestTokenizerInfo:
    """分词器信息测试"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_get_tokenizer_info(self, metrics):
        """get_tokenizer_info 返回合理信息"""
        info = metrics.get_tokenizer_info()
        assert isinstance(info, dict)
        assert 'name' in info or 'tokenizer_name' in info or len(info) > 0
