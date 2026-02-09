#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 文件配对策略测试（与 CLI 保持一致）。"""

import pytest

from cer_tool.gui import build_file_pairs_by_stem


class TestGuiFilePairing:
    """验证 GUI 的同名配对规则与异常场景。"""

    @pytest.mark.basic
    @pytest.mark.unit
    def test_pairs_by_stem_intersection(self):
        """按 stem 交集配对，且按 stem 排序。"""
        asr_files = [
            "/tmp/asr/002.txt",
            "/tmp/asr/001.txt",
        ]
        ref_files = [
            "/tmp/ref/003.txt",
            "/tmp/ref/002.txt",
            "/tmp/ref/001.txt",
        ]

        pairs, asr_only, ref_only, asr_dup, ref_dup = build_file_pairs_by_stem(asr_files, ref_files)

        assert pairs == [
            ("/tmp/asr/001.txt", "/tmp/ref/001.txt"),
            ("/tmp/asr/002.txt", "/tmp/ref/002.txt"),
        ]
        assert asr_only == []
        assert ref_only == ["003"]
        assert asr_dup == []
        assert ref_dup == []

    @pytest.mark.basic
    @pytest.mark.unit
    def test_unmatched_files_are_reported(self):
        """未配对 stem 能被正确归类。"""
        asr_files = ["/tmp/asr/a.txt", "/tmp/asr/b.txt"]
        ref_files = ["/tmp/ref/b.txt", "/tmp/ref/c.txt"]

        pairs, asr_only, ref_only, asr_dup, ref_dup = build_file_pairs_by_stem(asr_files, ref_files)

        assert pairs == [("/tmp/asr/b.txt", "/tmp/ref/b.txt")]
        assert asr_only == ["a"]
        assert ref_only == ["c"]
        assert asr_dup == []
        assert ref_dup == []

    @pytest.mark.basic
    @pytest.mark.unit
    def test_duplicate_stems_are_detected(self):
        """同侧存在重复 stem 时应识别为冲突。"""
        asr_files = [
            "/tmp/asr/x.txt",
            "/tmp/asr_alt/x.txt",
        ]
        ref_files = ["/tmp/ref/x.txt"]

        pairs, asr_only, ref_only, asr_dup, ref_dup = build_file_pairs_by_stem(asr_files, ref_files)

        assert pairs == [("/tmp/asr/x.txt", "/tmp/ref/x.txt")]
        assert asr_only == []
        assert ref_only == []
        assert asr_dup == ["x"]
        assert ref_dup == []
