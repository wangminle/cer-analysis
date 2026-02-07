#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本 - V2 修复版
提供便捷的测试运行命令和测试环境检查

修复内容：
- 使用 sys.executable 替代硬编码的 'python'
- 修正测试路径（从项目根目录运行 pytest）
- 修正 --cov 路径为 dev/src
"""

import sys
import subprocess
import importlib
from pathlib import Path


def check_dependencies():
    """检查测试依赖"""
    print("检查测试依赖...")
    
    # 必需依赖（V2：移除 jiwer 和 pandas 的强制检查）
    required_deps = ['jieba', 'pytest']
    missing_required = []
    
    for dep in required_deps:
        try:
            importlib.import_module(dep)
            print(f"✓ {dep} - 已安装")
        except ImportError:
            print(f"✗ {dep} - 未安装")
            missing_required.append(dep)
    
    # 可选依赖
    optional_deps = ['thulac', 'hanlp', 'jiwer', 'pandas']
    available_optional = []
    
    for dep in optional_deps:
        try:
            importlib.import_module(dep)
            print(f"✓ {dep} - 已安装（可选）")
            available_optional.append(dep)
        except ImportError:
            print(f"⚠ {dep} - 未安装（可选）")
    
    if missing_required:
        print(f"\n错误：缺少必需依赖: {', '.join(missing_required)}")
        print("请运行: pip install " + " ".join(missing_required))
        return False
    
    print(f"\n可用分词器: jieba" + (f", {', '.join([d for d in available_optional if d in ['thulac', 'hanlp']])}" if any(d in available_optional for d in ['thulac', 'hanlp']) else ""))
    return True


def get_project_root() -> Path:
    """获取项目根目录（tests/ 的父目录）"""
    return Path(__file__).parent.parent


def run_tests(test_type="all", verbose=True):
    """运行测试"""
    if not check_dependencies():
        return False
    
    project_root = get_project_root()
    tests_dir = project_root / "tests"
    
    # 使用 sys.executable 确保使用当前 Python 解释器
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    # 根据测试类型选择标记过滤
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "basic":
        cmd.extend(["-m", "basic"])
    elif test_type == "boundary":
        cmd.extend(["-m", "boundary"])
    elif test_type == "cli":
        cmd.extend(["-m", "cli"])
    elif test_type == "slow":
        cmd.extend(["-m", "slow"])
    elif test_type == "optional":
        cmd.extend(["-m", "optional"])
    elif test_type == "all":
        pass  # 不添加标记过滤，运行全部
    else:
        print(f"未知测试类型: {test_type}")
        return False
    
    print(f"\n运行命令: {' '.join(cmd)}")
    print(f"工作目录: {tests_dir}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=str(tests_dir), check=True)
        print("\n测试完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n测试失败，退出代码: {e.returncode}")
        return False


def run_coverage():
    """运行覆盖率测试"""
    print("运行覆盖率测试...")
    
    project_root = get_project_root()
    tests_dir = project_root / "tests"
    cov_source = str(project_root / "dev" / "src")
    
    # 使用 sys.executable 确保使用当前 Python 解释器
    cmd = [
        sys.executable, "-m", "pytest",
        str(tests_dir),
        f"--cov={cov_source}",
        "--cov-report=html",
        "--cov-report=term"
    ]
    
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
        print("\n覆盖率报告已生成到 htmlcov/ 目录")
        return True
    except subprocess.CalledProcessError:
        print("覆盖率测试失败")
        return False


def show_help():
    """显示帮助信息"""
    help_text = """
测试运行脚本使用方法:

python3 tests/run_tests.py [测试类型]

测试类型:
  all          - 运行所有测试（默认）
  basic        - 只运行基础测试（仅依赖 jieba）
  unit         - 只运行单元测试
  integration  - 只运行集成测试
  boundary     - 只运行边界条件测试
  cli          - 只运行CLI工具测试
  slow         - 只运行慢速测试
  optional     - 只运行可选分词器测试
  coverage     - 运行覆盖率测试
  check        - 只检查依赖环境
  help         - 显示此帮助信息

示例:
  python3 tests/run_tests.py basic
  python3 tests/run_tests.py coverage
  python3 tests/run_tests.py check
"""
    print(help_text)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        test_type = "all"
    else:
        test_type = sys.argv[1].lower()
    
    if test_type in ["help", "-h", "--help"]:
        show_help()
        return
    
    if test_type == "check":
        check_dependencies()
        return
    
    if test_type == "coverage":
        success = run_coverage()
        sys.exit(0 if success else 1)
        return
    
    success = run_tests(test_type)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
