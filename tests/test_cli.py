#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI 命令行接口测试模块

覆盖场景：
- --version 输出
- --list-tokenizers 功能
- 单文件模式正常处理
- 单文件模式失败退出码
- 批处理模式
- JSON 输出格式
- CSV 输出格式
- --filter-fillers 选项
- 无参数时打印帮助
- 错误输出到 stderr
"""

import json
import os
import subprocess
import sys
import pytest


# ────────────────── 辅助函数 ──────────────────

def run_cli(*args, **kwargs):
    """
    运行 CLI 命令并返回 CompletedProcess 对象
    使用 python3 -m cer_tool.cli 方式调用
    """
    cmd = [sys.executable, '-m', 'cer_tool.cli'] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        **kwargs
    )


def create_text_file(path, content):
    """创建文本文件"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


# ────────────────── fixture ──────────────────

@pytest.fixture
def sample_files(tmp_path):
    """创建临时的 ASR 和标注文件对"""
    asr_file = tmp_path / "asr.txt"
    ref_file = tmp_path / "ref.txt"
    create_text_file(str(asr_file), "今天天汽非常好")
    create_text_file(str(ref_file), "今天天气非常好")
    return str(asr_file), str(ref_file)


@pytest.fixture
def batch_dirs(tmp_path):
    """创建临时的批处理目录，包含 3 个文件对"""
    asr_dir = tmp_path / "asr"
    ref_dir = tmp_path / "ref"
    asr_dir.mkdir()
    ref_dir.mkdir()

    pairs = [
        ("今天天汽非常好", "今天天气非常好"),
        ("明天会下雪", "明天会下雨"),
        ("你好世界", "你好世界"),
    ]
    for i, (asr_text, ref_text) in enumerate(pairs, 1):
        create_text_file(str(asr_dir / f"{i:03d}.txt"), asr_text)
        create_text_file(str(ref_dir / f"{i:03d}.txt"), ref_text)

    return str(asr_dir), str(ref_dir)


# ════════════════════════════════════════════════════
# 第一组：版本和帮助
# ════════════════════════════════════════════════════

class TestVersionAndHelp:
    """版本和帮助信息测试"""

    @pytest.mark.basic
    @pytest.mark.cli
    def test_version_output(self):
        """--version 应输出版本号并退出码 0"""
        result = run_cli('--version')
        assert result.returncode == 0
        assert 'CER-Analysis-Tool' in result.stdout
        assert '2.0.0' in result.stdout

    @pytest.mark.basic
    @pytest.mark.cli
    def test_no_args_shows_help(self):
        """无参数时应打印帮助信息并退出码 1"""
        result = run_cli()
        assert result.returncode == 1
        # argparse 的帮助信息中应包含 usage 或 description
        assert 'cer-tool' in result.stdout.lower() or 'usage' in result.stdout.lower()

    @pytest.mark.basic
    @pytest.mark.cli
    def test_list_tokenizers(self):
        """--list-tokenizers 应列出可用分词器并退出码 0"""
        result = run_cli('--list-tokenizers')
        assert result.returncode == 0
        assert 'jieba' in result.stdout.lower()


# ════════════════════════════════════════════════════
# 第二组：单文件模式
# ════════════════════════════════════════════════════

class TestSingleFileMode:
    """单文件对比模式测试"""

    @pytest.mark.basic
    @pytest.mark.cli
    def test_single_pair_success(self, sample_files):
        """正常单文件对比 → 退出码 0，输出包含 CER"""
        asr_file, ref_file = sample_files
        result = run_cli('--asr', asr_file, '--ref', ref_file)
        assert result.returncode == 0
        assert 'CER' in result.stdout or 'cer' in result.stdout.lower()

    @pytest.mark.basic
    @pytest.mark.cli
    def test_single_pair_nonexistent_file(self):
        """不存在的文件 → 退出码 1"""
        result = run_cli('--asr', '/tmp/nonexist_asr.txt', '--ref', '/tmp/nonexist_ref.txt')
        assert result.returncode == 1

    @pytest.mark.basic
    @pytest.mark.cli
    def test_single_pair_json_output_stdout(self, sample_files):
        """单文件模式 --format json（无输出文件）→ JSON 输出到 stdout"""
        asr_file, ref_file = sample_files
        result = run_cli('--asr', asr_file, '--ref', ref_file, '--format', 'json')
        assert result.returncode == 0
        # 验证输出是合法 JSON
        data = json.loads(result.stdout)
        assert 'cer' in data
        assert 'accuracy' in data

    @pytest.mark.basic
    @pytest.mark.cli
    def test_single_pair_csv_output_file(self, sample_files, tmp_path):
        """单文件模式 --output results.csv → CSV 文件生成"""
        asr_file, ref_file = sample_files
        output_file = str(tmp_path / "result.csv")
        result = run_cli('--asr', asr_file, '--ref', ref_file, '--output', output_file)
        assert result.returncode == 0
        assert os.path.exists(output_file)
        # 验证 CSV 内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'cer' in content.lower()

    @pytest.mark.basic
    @pytest.mark.cli
    def test_single_pair_json_output_file(self, sample_files, tmp_path):
        """单文件模式 --output results.json --format json → JSON 文件生成"""
        asr_file, ref_file = sample_files
        output_file = str(tmp_path / "result.json")
        result = run_cli('--asr', asr_file, '--ref', ref_file,
                         '--output', output_file, '--format', 'json')
        assert result.returncode == 0
        assert os.path.exists(output_file)
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert 'results' in data
        assert 'version' in data


# ════════════════════════════════════════════════════
# 第三组：批处理模式
# ════════════════════════════════════════════════════

class TestBatchMode:
    """批处理模式测试"""

    @pytest.mark.basic
    @pytest.mark.cli
    def test_batch_success(self, batch_dirs):
        """批处理正常执行 → 退出码 0"""
        asr_dir, ref_dir = batch_dirs
        result = run_cli('--asr-dir', asr_dir, '--ref-dir', ref_dir)
        assert result.returncode == 0
        assert '批处理完成' in result.stdout or '3' in result.stdout

    @pytest.mark.basic
    @pytest.mark.cli
    def test_batch_nonexistent_dir(self):
        """不存在的批处理目录 → 退出码 1"""
        result = run_cli('--asr-dir', '/tmp/nonexist_dir_asr',
                         '--ref-dir', '/tmp/nonexist_dir_ref')
        assert result.returncode == 1

    @pytest.mark.basic
    @pytest.mark.cli
    def test_batch_json_output(self, batch_dirs, tmp_path):
        """批处理 JSON 输出到文件"""
        asr_dir, ref_dir = batch_dirs
        output_file = str(tmp_path / "batch_result.json")
        result = run_cli('--asr-dir', asr_dir, '--ref-dir', ref_dir,
                         '--output', output_file, '--format', 'json')
        assert result.returncode == 0
        assert os.path.exists(output_file)
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert 'results' in data
        assert len(data['results']) == 3


# ════════════════════════════════════════════════════
# 第四组：选项组合
# ════════════════════════════════════════════════════

class TestOptionCombinations:
    """CLI 选项组合测试"""

    @pytest.mark.basic
    @pytest.mark.cli
    def test_filter_fillers_option(self, sample_files):
        """--filter-fillers 选项不导致崩溃"""
        asr_file, ref_file = sample_files
        result = run_cli('--asr', asr_file, '--ref', ref_file, '--filter-fillers')
        assert result.returncode == 0

    @pytest.mark.basic
    @pytest.mark.cli
    def test_verbose_option(self, sample_files):
        """--verbose 选项应输出更多信息"""
        asr_file, ref_file = sample_files
        result = run_cli('--asr', asr_file, '--ref', ref_file, '--verbose')
        assert result.returncode == 0

    @pytest.mark.basic
    @pytest.mark.cli
    def test_error_to_stderr(self):
        """错误信息应输出到 stderr"""
        result = run_cli('--asr', '/tmp/nonexist.txt', '--ref', '/tmp/nonexist.txt')
        assert result.returncode == 1
        # 错误信息应在 stderr 中
        assert '错误' in result.stderr or 'error' in result.stderr.lower() or len(result.stderr) > 0
