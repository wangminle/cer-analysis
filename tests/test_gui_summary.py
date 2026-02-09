#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 总体准确率边界逻辑测试。"""

import pytest

from cer_tool.gui import calculate_overall_accuracy


class TestGuiOverallAccuracy:
    """验证 GUI 整体统计中的总体准确率计算规则。"""

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_overall_accuracy_normal_case(self):
        """正常分母场景：overall_accuracy = 1 - errors/ref_chars"""
        result = calculate_overall_accuracy(total_errors=3, total_ref_chars=12)
        assert result == pytest.approx(0.75)

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_overall_accuracy_zero_ref_and_zero_error(self):
        """空参考且无错误：总体准确率应为 1.0"""
        assert calculate_overall_accuracy(total_errors=0, total_ref_chars=0) == 1.0

    @pytest.mark.basic
    @pytest.mark.boundary
    def test_overall_accuracy_zero_ref_with_errors(self):
        """空参考但有错误：总体准确率应为 0.0"""
        assert calculate_overall_accuracy(total_errors=2, total_ref_chars=0) == 0.0
