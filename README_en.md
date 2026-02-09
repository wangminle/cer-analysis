# ASR Character Accuracy Comparison Tool

A Python-based tool for batch comparing character accuracy rates between ASR (Automatic Speech Recognition) transcription results and standard text, with multi-tokenizer support.

## ✨ Core Features

### 🎯 Multi-Tokenizer Support
- **Jieba Tokenizer**: Default choice, high-speed segmentation, suitable for daily use
- **THULAC Tokenizer**: Developed by Tsinghua University, high-precision segmentation, suitable for professional analysis
- **HanLP Tokenizer**: Deep learning model, highest precision, suitable for research environments

### 🚀 Smart Features
- ✅ **Automatic Tokenizer Detection**: Detects installed tokenizers at startup
- ✅ **Smart Fallback Mechanism**: Automatically fallback to jieba when tokenizers are unavailable
- ✅ **Real-time Status Display**: GUI shows tokenizer status and version information
- ✅ **Dependency-free Demo**: Complete architecture demonstration without additional dependencies

### 📊 Advanced Functions
- Batch import ASR transcription result documents and standard annotation documents
- Drag-and-drop to establish one-to-one correspondence between ASR results and annotation files
- Automatically calculate Character Accuracy Rate
- Count document character information
- Support exporting statistical results in TXT or CSV format
- Support multiple text encodings (UTF-8, GBK, GB2312, GB18030, ANSI)
- **Filler word filtering**: Optional filtering of filler words like "嗯", "啊"
- **Optimized user interface**: Larger result display area, more user-friendly experience
- **Asynchronous computation**: Background thread processing with real-time progress updates
- **Task cancellation**: Cancel long-running calculations at any time
- **CLI tool**: Command-line interface for batch processing and automation
- **Preprocessing pipeline**: Modular and configurable text preprocessing system

## 📦 Installation & Dependencies

### Installation
```bash
# Option 1: Using pipenv (recommended)
pipenv install              # Install core dependencies
pipenv install --dev        # Install core + dev dependencies

# Option 2: Using pip + pyproject.toml
pip install -e .            # Install core dependencies (editable mode)
pip install -e .[all]       # Install all optional tokenizers
pip install -e .[dev]       # Install dev/test tools
```

#### Dependency Description
**Core Dependencies (Required):**
- `jieba>=0.42.1`: Default Chinese tokenizer

**Recommended:**
- `python-Levenshtein>=0.12.2`: Efficient edit distance calculation (built-in pure Python fallback)

**Optional Tokenizers:**
- `thulac>=0.2.0`: THULAC high-precision tokenizer (`pip install -e .[thulac]`)
- `hanlp>=2.1.0`: HanLP deep learning tokenizer (`pip install -e .[hanlp]`)

## 🎮 Usage

### 1. GUI Mode (Recommended)

```bash
python3 dev/src/main_with_tokenizers.py
```

#### Operation Steps:
1. **Select Tokenizer**: Choose the desired tokenizer in the top dropdown
2. **Check Status**: Confirm tokenizer status shows green ✓, click "Tokenizer Info" for detailed information
3. **Import Files**:
   - Left: Click "Select ASR Files" to batch import ASR transcription results
   - Right: Click "Select Annotation Files" to batch import standard annotation files
4. **Establish Correspondence**: Adjust file order by drag-and-drop
5. **Configure Options**: Check "Filter Filler Words" as needed
6. **Calculate Statistics**: Click "Start Calculation" button
7. **View Results**: Result table shows detailed statistics, including tokenizer type used
8. **Export Data**: Click "Export Results" to save as file

#### Interface Function Description:
- **Tokenizer Selection Area**: Select and manage tokenizers
- **File Selection Area**: Import and manage file lists
- **Control Area**: Statistics button and option configuration
- **Result Display Area**: Detailed statistical result table

### 2. CLI Mode (Command Line Interface)

```bash
# Single file comparison
python3 dev/src/cli.py --asr path/to/asr.txt --ref path/to/ref.txt --tokenizer jieba

# Batch processing
python3 dev/src/cli.py --asr-dir path/to/asr_files/ --ref-dir path/to/ref_files/ --output results.csv

# With filler word filtering
python3 dev/src/cli.py --asr asr.txt --ref ref.txt --filter-fillers --output result.csv

# List available tokenizers
python3 dev/src/cli.py --list-tokenizers
```

#### CLI Features:
- **Single file/Batch processing**: Process one or multiple file pairs
- **Tokenizer selection**: Choose from available tokenizers
- **Filler word filtering**: Optional language filler filtering
- **Export formats**: CSV or TXT output
- **Automation friendly**: Perfect for CI/CD pipelines

### 3. Batch Processing Mode

For GUI-based batch file processing:
```bash
python3 dev/src/main_with_tokenizers.py
```
Then follow the interface operation steps for batch import and processing.

## 🎯 Tokenizer Selection Guide

### Jieba Tokenizer
- **Performance**: ⚡ High Speed
- **Accuracy**: ⭐⭐⭐ Medium
- **Use Cases**: Daily batch processing, quick verification
- **Advantages**: Fast speed, low resource usage, good compatibility

### THULAC Tokenizer
- **Performance**: ⚡⚡ Medium Speed
- **Accuracy**: ⭐⭐⭐⭐ High Precision
- **Use Cases**: Professional analysis, high quality requirements
- **Advantages**: Developed by Tsinghua University, academic standards, accurate POS tagging

### HanLP Tokenizer
- **Performance**: ⚡ Slower (first use requires model download)
- **Accuracy**: ⭐⭐⭐⭐⭐ Highest Precision
- **Use Cases**: Research environments, highest precision requirements
- **Advantages**: Deep learning models, multi-task support, continuous updates

## 📐 Character Accuracy Calculation Method

Uses the complement of Character Error Rate (CER):

```
Character Accuracy = 1 - CER = 1 - (S + D + I) / N
```

Where:
- **S**: Number of substitution errors
- **D**: Number of deletion errors
- **I**: Number of insertion errors
- **N**: Total number of characters in the standard text

### 🔧 Improved Calculation Process

1. **Tokenization Preprocessing**: Use selected tokenizer for text segmentation
2. **Text Normalization**: Process full/half-width characters, unify numerical expressions
3. **Filler Word Filtering (Optional)**: Filter filler words like "嗯", "啊", "呢"
4. **Character Position Localization**: Precisely locate each character's position in original text
5. **Edit Distance Calculation**: Use Levenshtein distance algorithm
6. **Error Analysis**: Identify substitution, deletion, insertion errors with visualization

## 📁 Project Structure

```
cer-analysis/                            # Project root
├── src/                                 # 🧠 Source code
│   └── cer_tool/                        # Python package
│       ├── __init__.py                  # Package metadata + compatibility wrapper
│       ├── __main__.py                  # python -m cer_tool entry point
│       ├── metrics.py                   # 📊 CER metrics calculation engine
│       ├── cli.py                       # 💻 CLI command-line interface
│       ├── gui.py                       # 🎨 GUI interface (tkinter)
│       ├── preprocessing.py             # 🔄 Preprocessing pipeline
│       ├── file_utils.py                # 📂 File utility functions
│       └── tokenizers/                  # Tokenizer module
│           ├── base.py                  # Abstract base class
│           ├── factory.py               # Factory (singleton + cache)
│           ├── jieba_tokenizer.py       # Jieba implementation
│           ├── thulac_tokenizer.py      # THULAC implementation
│           └── hanlp_tokenizer.py       # HanLP implementation
│
├── tests/                               # 🧪 Tests (127 pytest cases)
│   ├── pytest.ini                       # pytest configuration
│   ├── test_boundary.py                 # Boundary condition tests (20)
│   ├── test_cli.py                      # CLI tests (14)
│   ├── test_preprocessing.py            # Preprocessing tests (25)
│   ├── test_core_metrics.py             # Core metrics tests (33)
│   ├── test_tokenizers_unit.py          # Tokenizer unit tests (23)
│   ├── test_with_pytest_marks.py        # Legacy integration tests (12)
│   └── reports/                         # 📋 Test reports
│
├── docs/                                # 📚 Documentation
├── dev/                                 # 🛠 Development auxiliary
├── assets/                              # 🎨 Static assets
├── release/                             # 📦 Release artifacts
├── ref/                                 # 📋 Reference materials (read-only)
├── pyproject.toml                       # Package definition + dependency layers
├── Pipfile                              # pipenv dependency management
├── CLAUDE.md                            # Project knowledge base (AI context)
└── README.md                            # Project description
```

## 🔧 Troubleshooting

### Common Issues

**Q: How to handle unavailable tokenizers?**
A: Check if corresponding dependencies are installed:
```bash
pip install thulac    # Install THULAC
pip install hanlp     # Install HanLP
```

**Q: Why is HanLP slow on first use?**
A: HanLP needs to download deep learning models, first use requires patience. Recommend using in good network environment.

**Q: How to quickly verify functionality?**
A: Use sample files in the ref/demo directory for testing:
```bash
# Use GUI interface to import sample files from ref/demo directory for testing
python3 dev/src/main_with_tokenizers.py
```

**Q: How to choose the right tokenizer?**
A: Refer to tokenizer selection guide, choose based on speed and accuracy needs:
- For speed: Choose Jieba
- For balance: Choose THULAC
- For precision: Choose HanLP

## 🆕 Version Features

### Current Version Highlights
- 🎯 **Multi-tokenizer Architecture**: Support for three mainstream Chinese tokenizers
- 🚀 **Smart Switching**: Automatic detection and graceful fallback
- 🎨 **Optimized Interface**: More user-friendly experience with async processing
- 📊 **Detailed Statistics**: Enhanced result display and analysis
- 🔧 **Drag-and-Drop Sorting**: Intuitive file correspondence management
- ⚡ **Asynchronous GUI**: Non-blocking interface with background computation
- 🎯 **Task Control**: Real-time progress updates and cancellation support
- 💻 **CLI Tool**: Professional command-line interface for automation
- 🔄 **Preprocessing Pipeline**: Flexible and modular text preprocessing
- 🧪 **Layered Testing**: 127 pytest cases with reports layer separation

### Backward Compatibility
- ✅ Maintain original API interfaces unchanged
- ✅ Default to jieba tokenizer
- ✅ Support original file formats and encodings

## 📞 Technical Support

For issues, please check:
- `ref/demo/` directory - Contains sample files for testing
- `docs/` directory - Detailed technical documentation
- `tests/reports/` directory - Test reports and strategy docs
- `pyproject.toml` - Complete dependency configuration

## 📄 License

This project is released under an open source license, see `LICENSE` file for details.

---

🎉 **Experience multi-tokenizer switching now to improve ASR character accuracy analysis precision and efficiency!** 