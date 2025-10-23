# Cer-MatchingTools-V1-架构设计文档

## 1. 系统概述

### 1.1 架构设计理念
本文档采用技术层次切分法，从前端表示层、业务逻辑层、算法引擎层、数据访问层的角度描述ASR字准确率对比工具的技术架构，为系统实现提供清晰的技术指导。

### 1.2 设计目标
- **分层解耦**：各技术层职责明确，降低耦合度
- **技术先进**：采用现代软件架构模式和设计原则
- **可扩展性**：支持新技术栈的无缝集成
- **高性能**：优化各层间的数据传输和处理效率
- **易维护**：清晰的技术边界和标准化的接口

### 1.3 技术栈总览

| 技术层次 | 技术选型 | 核心组件 | 职责范围 |
|---------|---------|---------|---------|
| **前端表示层** | Tkinter + ttk | GUI界面、CLI工具 | 用户交互、数据展示 |
| **业务逻辑层** | Python OOP | 业务引擎、流程控制 | 业务规则、工作流管理 |
| **算法引擎层** | NLP库 + 自研算法 | 分词器、CER计算 | 算法实现、模型管理 |
| **数据访问层** | 标准库 + Pandas | 文件处理、数据转换 | 数据I/O、格式转换 |

## 2. 系统架构总览

### 2.1 技术架构分层图

```
┌─────────────────────────────────────────────────────────────┐
│                     前端表示层 (Presentation Layer)          │
├─────────────────┬─────────────────┬─────────────────────────┤
│   GUI界面层      │   CLI工具层      │    UI控制器层            │
│   ├─ 主窗口     │   ├─ 参数解析   │    ├─ 事件处理           │
│   ├─ 对话框     │   ├─ 批处理     │    ├─ 状态管理           │
│   └─ 控件组件   │   └─ 进度显示   │    └─ 数据绑定           │
└─────────────────┴─────────────────┴─────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Logic Layer)         │
├─────────────────┬─────────────────┬─────────────────────────┤
│   业务服务层     │   工作流控制层   │    业务模型层            │
│   ├─ 文件管理   │   ├─ 任务调度   │    ├─ 业务实体           │
│   ├─ 批量处理   │   ├─ 流程编排   │    ├─ 业务规则           │
│   └─ 结果导出   │   └─ 异常处理   │    └─ 数据验证           │
└─────────────────┴─────────────────┴─────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    算法引擎层 (Algorithm Engine Layer)       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   分词器引擎     │   计算引擎       │    算法管理层            │
│   ├─ Jieba     │   ├─ CER算法    │    ├─ 工厂模式           │
│   ├─ THULAC    │   ├─ 编辑距离   │    ├─ 单例管理           │
│   └─ HanLP     │   └─ 统计分析   │    └─ 策略模式           │
└─────────────────┴─────────────────┴─────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    数据访问层 (Data Access Layer)           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   文件访问层     │   数据处理层     │    存储管理层            │
│   ├─ 编码检测   │   ├─ 格式转换   │    ├─ 内存管理           │
│   ├─ 文件读写   │   ├─ 数据清洗   │    ├─ 缓存机制           │
│   └─ 路径处理   │   └─ 结构化处理 │    └─ 临时文件           │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 3. 前端表示层技术设计

### 3.1 GUI界面层技术架构

#### 3.1.1 主窗口架构设计
```python
# 主窗口类结构
class ASRComparisonTool:
    """主窗口控制器，采用MVC模式"""
    
    def __init__(self):
        self.root = tk.Tk()                    # 根窗口
        self.ui_components = {}                # UI组件注册表
        self.event_handlers = {}               # 事件处理器映射
        self.data_models = {}                  # 数据模型绑定
        
    # UI组件工厂方法
    def create_ui_components(self):
        """组件化UI构建"""
        pass
        
    # 事件处理分发器
    def handle_events(self):
        """统一事件处理机制"""
        pass
```

#### 3.1.2 UI组件技术实现

**分词器选择组件**
```python
class TokenizerSelector:
    """分词器选择器组件"""
    
    def __init__(self, parent_frame):
        self.frame = ttk.LabelFrame(parent_frame, text="分词器选择")
        self.combobox = ttk.Combobox(self.frame, state="readonly")
        self.status_label = ttk.Label(self.frame)
        self.info_button = ttk.Button(self.frame)
        
    def update_status(self, tokenizer_info):
        """动态更新分词器状态显示"""
        pass
        
    def bind_events(self, callback):
        """事件绑定机制"""
        pass
```

**文件管理组件**
```python
class FileManager:
    """文件管理器组件"""
    
    def __init__(self, parent_frame):
        self.canvas = tk.Canvas(parent_frame)
        self.scrollbar = ttk.Scrollbar(parent_frame)
        self.drag_handler = DragDropHandler()
        
    def render_file_list(self, files):
        """文件列表渲染引擎"""
        pass
        
    def handle_file_operations(self):
        """文件操作处理器"""
        pass
```

#### 3.1.3 响应式布局技术

**网格布局管理器**
```python
class ResponsiveLayout:
    """响应式布局管理器"""
    
    def __init__(self, container):
        self.container = container
        self.layout_rules = {}
        
    def apply_grid_layout(self):
        """应用网格布局规则"""
        self.container.columnconfigure(0, weight=1, uniform="group1")
        self.container.columnconfigure(1, weight=1, uniform="group1")
        
    def handle_resize(self, event):
        """窗口调整大小事件处理"""
        pass
```

### 3.2 CLI工具层技术架构

#### 3.2.1 命令行解析器设计
```python
import click

@click.command()
@click.option('--ref', required=True, help='参考文本文件路径')
@click.option('--hyp', required=True, help='假设文本文件路径')
@click.option('--tokenizer', default='jieba', help='分词器类型')
@click.option('--filter-fillers', is_flag=True, help='启用语气词过滤')
@click.option('--output', help='输出文件路径')
@click.option('--format', type=click.Choice(['txt', 'csv']), default='txt')
def cli_main(ref, hyp, tokenizer, filter_fillers, output, format):
    """CLI入口点"""
    pass
```

#### 3.2.2 批处理引擎设计
```python
class BatchProcessor:
    """批处理引擎"""
    
    def __init__(self):
        self.progress_bar = None
        self.error_handler = ErrorHandler()
        
    def process_file_pairs(self, file_pairs, **kwargs):
        """批量处理文件对"""
        with click.progressbar(file_pairs, label='处理中') as bar:
            for pair in bar:
                yield self.process_single_pair(pair, **kwargs)
                
    def generate_report(self, results):
        """生成CLI报告"""
        pass
```

### 3.3 UI控制器层技术架构

#### 3.3.1 事件驱动架构与异步计算模型
```python
class EventDispatcher:
    """事件分发器"""
    
    def __init__(self):
        self.event_handlers = {}
        self.event_queue = queue.Queue()
        
    def register_handler(self, event_type, handler):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def emit_event(self, event_type, data):
        """触发事件"""
        event = Event(event_type, data)
        self.event_queue.put(event)
        
    def process_events(self):
        """处理事件队列"""
        while not self.event_queue.empty():
            event = self.event_queue.get()
            self.dispatch_event(event)

class AsyncCalculationController:
    """异步计算控制器（P2改进）"""
    
    def __init__(self):
        self.calculation_thread = None
        self.result_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.is_calculating = False
        
    def start_calculation(self, worker_func, *args, **kwargs):
        """启动后台计算线程"""
        self.cancel_event.clear()
        self.is_calculating = True
        
        self.calculation_thread = threading.Thread(
            target=worker_func,
            args=args,
            kwargs=kwargs,
            daemon=True
        )
        self.calculation_thread.start()
        
        # 启动结果检查循环
        self.check_results()
        
    def check_results(self):
        """主线程定期检查结果队列"""
        try:
            while True:
                message = self.result_queue.get_nowait()
                self.handle_message(message)
        except queue.Empty:
            pass
            
        if self.is_calculating:
            # 100ms后再次检查
            self.root.after(100, self.check_results)
            
    def cancel_calculation(self):
        """取消计算"""
        self.cancel_event.set()
        
    def handle_message(self, message):
        """处理消息"""
        msg_type, data = message
        if msg_type == 'progress':
            self.update_progress(data)
        elif msg_type == 'complete':
            self.finalize_calculation()
        elif msg_type == 'error':
            self.handle_error(data)
        elif msg_type == 'cancelled':
            self.handle_cancellation()
```

#### 3.3.2 状态管理器
```python
class ApplicationState:
    """应用状态管理器"""
    
    def __init__(self):
        self.state = {
            'selected_tokenizer': 'jieba',
            'asr_files': [],
            'ref_files': [],
            'processing_status': 'idle',
            'results': []
        }
        self.observers = []
        
    def update_state(self, key, value):
        """状态更新机制"""
        old_value = self.state.get(key)
        self.state[key] = value
        self.notify_observers(key, old_value, value)
        
    def notify_observers(self, key, old_value, new_value):
        """观察者模式通知"""
        for observer in self.observers:
            observer.on_state_change(key, old_value, new_value)
```

## 4. 业务逻辑层技术设计

### 4.1 业务服务层架构

#### 4.1.1 文件管理服务
```python
class FileManagementService:
    """文件管理业务服务"""
    
    def __init__(self):
        self.file_validator = FileValidator()
        self.encoding_detector = EncodingDetector()
        
    def import_files(self, file_paths):
        """文件导入业务逻辑"""
        validated_files = []
        for path in file_paths:
            try:
                file_info = self.validate_and_process_file(path)
                validated_files.append(file_info)
            except ValidationError as e:
                self.handle_validation_error(path, e)
        return validated_files
        
    def create_file_pairs(self, asr_files, ref_files):
        """智能文件配对算法"""
        pair_matcher = FilePairMatcher()
        return pair_matcher.match_files(asr_files, ref_files)
```

#### 4.1.2 批量处理服务
```python
class BatchProcessingService:
    """批量处理业务服务"""
    
    def __init__(self):
        self.task_scheduler = TaskScheduler()
        self.progress_tracker = ProgressTracker()
        
    def execute_batch_calculation(self, file_pairs, config):
        """批量计算编排"""
        tasks = self.create_calculation_tasks(file_pairs, config)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for task in tasks:
                future = executor.submit(self.execute_single_task, task)
                futures.append(future)
                
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                self.progress_tracker.update_progress(len(results), len(futures))
                
        return results
```

#### 4.1.3 结果导出服务
```python
class ResultExportService:
    """结果导出业务服务"""
    
    def __init__(self):
        self.formatters = {
            'txt': TextFormatter(),
            'csv': CSVFormatter(),
            'json': JSONFormatter()
        }
        
    def export_results(self, results, format_type, output_path):
        """结果导出统一接口"""
        formatter = self.formatters.get(format_type)
        if not formatter:
            raise UnsupportedFormatError(f"不支持的格式: {format_type}")
            
        formatted_data = formatter.format(results)
        self.write_to_file(formatted_data, output_path)
        
    def generate_report(self, results, template='default'):
        """报告生成器"""
        report_generator = ReportGenerator()
        return report_generator.create_report(results, template)
```

### 4.2 工作流控制层架构

#### 4.2.1 任务调度器
```python
class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.running_tasks = {}
        self.completed_tasks = []
        
    def submit_task(self, task, priority=0):
        """提交任务到调度队列"""
        task.priority = priority
        task.status = TaskStatus.PENDING
        self.task_queue.put((priority, task))
        
    def execute_next_task(self):
        """执行下一个任务"""
        if not self.task_queue.empty():
            priority, task = self.task_queue.get()
            self.run_task(task)
            
    def run_task(self, task):
        """运行单个任务"""
        try:
            task.status = TaskStatus.RUNNING
            self.running_tasks[task.id] = task
            
            result = task.execute()
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            self.completed_tasks.append(task)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = e
            self.handle_task_error(task, e)
        finally:
            del self.running_tasks[task.id]
```

#### 4.2.2 流程编排引擎
```python
class WorkflowOrchestrator:
    """工作流编排引擎"""
    
    def __init__(self):
        self.workflow_definition = {}
        self.execution_context = {}
        
    def define_workflow(self, workflow_name, steps):
        """定义工作流程"""
        self.workflow_definition[workflow_name] = {
            'steps': steps,
            'dependencies': self.analyze_dependencies(steps)
        }
        
    def execute_workflow(self, workflow_name, input_data):
        """执行工作流程"""
        workflow = self.workflow_definition[workflow_name]
        context = ExecutionContext(input_data)
        
        for step in workflow['steps']:
            step_result = self.execute_step(step, context)
            context.add_result(step.name, step_result)
            
        return context.get_final_result()
        
    def execute_step(self, step, context):
        """执行单个步骤"""
        step_executor = self.get_step_executor(step.type)
        return step_executor.execute(step, context)
```

### 4.3 业务模型层架构

#### 4.3.1 领域实体设计
```python
@dataclass
class FileEntity:
    """文件实体"""
    path: str
    name: str
    size: int
    encoding: str
    content: str
    hash: str
    created_at: datetime
    
    def validate(self):
        """实体验证"""
        if not os.path.exists(self.path):
            raise EntityValidationError("文件不存在")
        # 其他验证逻辑

@dataclass  
class CalculationResult:
    """计算结果实体"""
    asr_file: str
    ref_file: str
    cer_score: float
    error_details: Dict
    tokenizer_used: str
    filter_enabled: bool
    calculated_at: datetime
    
    def to_dict(self):
        """转换为字典"""
        return asdict(self)
```

#### 4.3.2 业务规则引擎
```python
class BusinessRuleEngine:
    """业务规则引擎"""
    
    def __init__(self):
        self.rules = []
        
    def add_rule(self, rule):
        """添加业务规则"""
        self.rules.append(rule)
        
    def validate(self, entity):
        """执行业务规则验证"""
        violations = []
        for rule in self.rules:
            if not rule.evaluate(entity):
                violations.append(rule.violation_message)
        return violations

class FileValidationRule:
    """文件验证规则"""
    
    def evaluate(self, file_entity):
        """评估规则"""
        return (file_entity.size > 0 and 
                file_entity.size < 100 * 1024 * 1024 and  # 100MB限制
                file_entity.encoding in ['utf-8', 'gbk', 'gb2312'])
                
    @property
    def violation_message(self):
        return "文件大小或编码不符合要求"
```

## 5. 算法引擎层技术设计

### 5.1 分词器引擎架构

#### 5.1.1 分词器抽象层设计
```python
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TokenizationResult:
    """分词结果封装"""
    tokens: List[Tuple[str, int, int]]  # (token, start_pos, end_pos)
    processing_time: float
    metadata: Dict[str, Any]

class BaseTokenizer(ABC):
    """分词器基类"""
    
    def __init__(self):
        self.is_initialized = False
        self.model_info = {}
        
    @abstractmethod
    def initialize(self) -> bool:
        """初始化分词器"""
        pass
        
    @abstractmethod
    def tokenize(self, text: str) -> TokenizationResult:
        """分词接口"""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """检查可用性"""
        pass
        
    def get_info(self) -> Dict[str, Any]:
        """获取分词器信息"""
        return {
            'name': self.__class__.__name__,
            'version': getattr(self, 'version', 'unknown'),
            'is_available': self.is_available(),
            'model_info': self.model_info
        }
```

#### 5.1.2 具体分词器实现
```python
class JiebaTokenizer(BaseTokenizer):
    """Jieba分词器实现"""
    
    def __init__(self):
        super().__init__()
        self.jieba_instance = None
        self.version = None
        
    def initialize(self) -> bool:
        """延迟初始化"""
        try:
            import jieba
            import jieba.posseg as posseg
            
            self.jieba_instance = jieba
            self.posseg = posseg
            self.version = jieba.__version__
            self.is_initialized = True
            
            # 预加载模型
            jieba.initialize()
            
            return True
        except ImportError as e:
            self.initialization_error = str(e)
            return False
            
    def tokenize(self, text: str) -> TokenizationResult:
        """Jieba分词实现"""
        if not self.is_initialized:
            raise TokenizerNotInitializedError("Jieba分词器未初始化")
            
        start_time = time.time()
        
        # 执行分词
        tokens_with_pos = []
        start_pos = 0
        
        for token in self.jieba_instance.cut(text, cut_all=False):
            end_pos = start_pos + len(token)
            tokens_with_pos.append((token, start_pos, end_pos))
            start_pos = end_pos
            
        processing_time = time.time() - start_time
        
        return TokenizationResult(
            tokens=tokens_with_pos,
            processing_time=processing_time,
            metadata={'algorithm': 'jieba', 'cut_all': False}
        )

class HanlpTokenizer(BaseTokenizer):
    """HanLP分词器实现"""
    
    def __init__(self):
        super().__init__()
        self.hanlp_instance = None
        self.model = None
        
    def initialize(self) -> bool:
        """HanLP初始化"""
        try:
            import hanlp
            
            self.hanlp_instance = hanlp
            # 使用轻量级模型
            self.model = hanlp.load(hanlp.pretrained.tok.FINE_ELECTRA_SMALL_ZH)
            self.version = hanlp.__version__
            self.is_initialized = True
            
            return True
        except Exception as e:
            self.initialization_error = str(e)
            return False
            
    def tokenize(self, text: str) -> TokenizationResult:
        """HanLP分词实现"""
        if not self.is_initialized:
            raise TokenizerNotInitializedError("HanLP分词器未初始化")
            
        start_time = time.time()
        
        # HanLP返回的结果包含位置信息
        tokens = self.model(text)
        
        # 转换为标准格式
        tokens_with_pos = []
        if hasattr(tokens, 'spans'):
            for span in tokens.spans:
                tokens_with_pos.append((span.text, span.start, span.end))
        else:
            # 降级处理
            tokens_with_pos = self._calculate_positions(text, tokens)
            
        processing_time = time.time() - start_time
        
        return TokenizationResult(
            tokens=tokens_with_pos,
            processing_time=processing_time,
            metadata={'algorithm': 'hanlp', 'model': 'FINE_ELECTRA_SMALL_ZH'}
        )
```

#### 5.1.3 分词器工厂和管理器
```python
class TokenizerFactory:
    """分词器工厂"""
    
    _tokenizer_registry = {
        'jieba': JiebaTokenizer,
        'thulac': ThulacTokenizer,
        'hanlp': HanlpTokenizer
    }
    
    @classmethod
    def create_tokenizer(cls, tokenizer_type: str) -> BaseTokenizer:
        """创建分词器实例"""
        tokenizer_class = cls._tokenizer_registry.get(tokenizer_type)
        if not tokenizer_class:
            raise UnsupportedTokenizerError(f"不支持的分词器: {tokenizer_type}")
            
        tokenizer = tokenizer_class()
        if not tokenizer.initialize():
            raise TokenizerInitializationError(f"{tokenizer_type}分词器初始化失败")
            
        return tokenizer
        
    @classmethod
    def get_available_tokenizers(cls) -> List[str]:
        """获取可用分词器列表"""
        available = []
        for name, tokenizer_class in cls._tokenizer_registry.items():
            tokenizer = tokenizer_class()
            if tokenizer.initialize():
                available.append(name)
        return available

class TokenizerManager:
    """分词器管理器（单例模式）"""
    
    _instance = None
    _tokenizer_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def get_tokenizer(self, tokenizer_type: str) -> BaseTokenizer:
        """获取分词器实例（带缓存）"""
        if tokenizer_type not in self._tokenizer_cache:
            tokenizer = TokenizerFactory.create_tokenizer(tokenizer_type)
            self._tokenizer_cache[tokenizer_type] = tokenizer
            
        return self._tokenizer_cache[tokenizer_type]
        
    def clear_cache(self):
        """清理缓存"""
        self._tokenizer_cache.clear()
```

### 5.2 计算引擎架构

#### 5.2.1 CER计算算法实现
```python
class CERCalculationEngine:
    """CER计算引擎"""
    
    def __init__(self, tokenizer: BaseTokenizer):
        self.tokenizer = tokenizer
        self.edit_distance_calculator = EditDistanceCalculator()
        
    def calculate_cer(self, reference: str, hypothesis: str, 
                     filter_fillers: bool = False) -> CalculationResult:
        """计算字符错误率"""
        
        # 1. 文本预处理
        ref_processed = self.preprocess_text(reference)
        hyp_processed = self.preprocess_text(hypothesis)
        
        # 2. 语气词过滤（可选）
        if filter_fillers:
            ref_processed = self.filter_filler_words(ref_processed)
            hyp_processed = self.filter_filler_words(hyp_processed)
            
        # 3. 计算编辑距离
        distance_result = self.edit_distance_calculator.calculate(
            ref_processed, hyp_processed
        )
        
        # 4. 计算CER
        total_chars = len(ref_processed)
        if total_chars == 0:
            cer_score = 0.0
        else:
            cer_score = distance_result.total_errors / total_chars
            
        # 5. 构建结果
        return CalculationResult(
            cer_score=cer_score,
            reference_length=len(ref_processed),
            hypothesis_length=len(hyp_processed),
            substitutions=distance_result.substitutions,
            deletions=distance_result.deletions,
            insertions=distance_result.insertions,
            tokenizer_used=self.tokenizer.__class__.__name__,
            filter_enabled=filter_fillers
        )

class EditDistanceCalculator:
    """编辑距离计算器"""
    
    def calculate(self, ref: str, hyp: str) -> 'EditDistanceResult':
        """使用动态规划计算编辑距离"""
        m, n = len(ref), len(hyp)
        
        # 创建DP表
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # 初始化边界条件
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        # 填充DP表
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ref[i-1] == hyp[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # 删除
                        dp[i][j-1],    # 插入
                        dp[i-1][j-1]   # 替换
                    )
                    
        # 回溯获取详细操作
        operations = self.backtrack_operations(dp, ref, hyp)
        
        return EditDistanceResult(
            total_errors=dp[m][n],
            operations=operations,
            substitutions=sum(1 for op in operations if op.type == 'substitute'),
            deletions=sum(1 for op in operations if op.type == 'delete'),
            insertions=sum(1 for op in operations if op.type == 'insert')
        )
```

### 5.3 算法管理层架构

#### 5.3.1 策略模式实现
```python
class AlgorithmStrategy(ABC):
    """算法策略基类"""
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """执行算法"""
        pass

class CERCalculationStrategy(AlgorithmStrategy):
    """CER计算策略"""
    
    def __init__(self, tokenizer_type: str):
        self.tokenizer_type = tokenizer_type
        
    def execute(self, reference: str, hypothesis: str, **kwargs):
        """执行CER计算"""
        tokenizer_manager = TokenizerManager()
        tokenizer = tokenizer_manager.get_tokenizer(self.tokenizer_type)
        
        engine = CERCalculationEngine(tokenizer)
        return engine.calculate_cer(reference, hypothesis, **kwargs)

class AlgorithmContext:
    """算法上下文"""
    
    def __init__(self, strategy: AlgorithmStrategy):
        self.strategy = strategy
        
    def set_strategy(self, strategy: AlgorithmStrategy):
        """动态切换策略"""
        self.strategy = strategy
        
    def execute_algorithm(self, *args, **kwargs):
        """执行算法"""
        return self.strategy.execute(*args, **kwargs)
```

## 6. 数据访问层技术设计

### 6.1 文件访问层架构

#### 6.1.1 文件I/O统一接口
```python
class FileAccessInterface(ABC):
    """文件访问接口"""
    
    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """读取文件"""
        pass
        
    @abstractmethod
    def write_file(self, file_path: str, content: str):
        """写入文件"""
        pass
        
    @abstractmethod
    def detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        pass

class TextFileAccessor(FileAccessInterface):
    """文本文件访问器"""
    
    def __init__(self):
        self.encoding_detector = EncodingDetector()
        self.supported_encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'ansi']
        
    def read_file(self, file_path: str) -> str:
        """多编码尝试读取文件"""
        detected_encoding = self.detect_encoding(file_path)
        
        # 首先尝试检测到的编码
        try:
            return self._read_with_encoding(file_path, detected_encoding)
        except UnicodeDecodeError:
            pass
            
        # 尝试其他编码
        for encoding in self.supported_encodings:
            if encoding != detected_encoding:
                try:
                    return self._read_with_encoding(file_path, encoding)
                except UnicodeDecodeError:
                    continue
                    
        raise FileEncodingError(f"无法解码文件: {file_path}")
        
    def _read_with_encoding(self, file_path: str, encoding: str) -> str:
        """使用指定编码读取文件"""
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
            
    def detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        return self.encoding_detector.detect(file_path)

class EncodingDetector:
    """编码检测器"""
    
    def detect(self, file_path: str) -> str:
        """检测文件编码"""
        try:
            import chardet
            
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # 读取前10K字节
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
                
        except ImportError:
            # 降级到简单检测
            return self._simple_detect(file_path)
            
    def _simple_detect(self, file_path: str) -> str:
        """简单编码检测"""
        encodings_to_try = ['utf-8', 'gbk', 'gb2312']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    file.read(1000)  # 尝试读取
                return encoding
            except UnicodeDecodeError:
                continue
                
        return 'utf-8'  # 默认编码
```

### 6.2 数据处理层架构

#### 6.2.1 数据转换管道与预处理流水线（P2改进）
```python
from abc import ABC, abstractmethod
from typing import List

class PreprocessingStep(ABC):
    """预处理步骤抽象基类"""
    
    @abstractmethod
    def process(self, text: str) -> str:
        """处理文本"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取步骤名称"""
        pass

class PreprocessingPipeline:
    """预处理流水线（P2新增）"""
    
    def __init__(self, steps: List[PreprocessingStep]):
        """
        初始化流水线
        
        Args:
            steps: 预处理步骤列表，按顺序执行
        """
        self.steps = steps
        
    def process(self, text: str) -> str:
        """
        执行预处理流水线
        
        Args:
            text: 输入文本
            
        Returns:
            处理后的文本
        """
        result = text
        for step in self.steps:
            result = step.process(result)
        return result
    
    def add_step(self, step: PreprocessingStep):
        """动态添加处理步骤"""
        self.steps.append(step)
        
    def get_pipeline_info(self) -> str:
        """获取流水线信息"""
        step_names = [step.get_name() for step in self.steps]
        return " -> ".join(step_names)

# 具体实现示例
class RemovePunctuationStep(PreprocessingStep):
    """移除标点符号步骤"""
    
    def process(self, text: str) -> str:
        import string
        return text.translate(str.maketrans('', '', string.punctuation + '。，、；：？！…—·「」『』【】《》〈〉""''（）'))
    
    def get_name(self) -> str:
        return "移除标点符号"

class NormalizeWidthStep(PreprocessingStep):
    """宽度标准化步骤"""
    
    def process(self, text: str) -> str:
        import unicodedata
        return unicodedata.normalize('NFKC', text)
    
    def get_name(self) -> str:
        return "宽度标准化"

def get_preset_pipeline(preset_name: str) -> PreprocessingPipeline:
    """
    获取预设流水线配置
    
    Args:
        preset_name: 预设名称（'minimal', 'standard', 'aggressive', 'custom_asr', 'research'）
        
    Returns:
        配置好的预处理流水线
    """
    presets = {
        'minimal': [NormalizeWidthStep(), StripWhitespaceStep()],
        'standard': [NormalizeWidthStep(), RemovePunctuationStep(), RemoveMultipleSpacesStep(), StripWhitespaceStep()],
        'aggressive': [NormalizeWidthStep(), NormalizeNumbersStep(), RemovePunctuationStep(), RemoveMultipleSpacesStep(), StripWhitespaceStep()],
    }
    
    steps = presets.get(preset_name, presets['standard'])
    return PreprocessingPipeline(steps)

class DataProcessor:
    """数据处理管道"""
    
    def __init__(self):
        self.processors = []
        
    def add_processor(self, processor):
        """添加处理器"""
        self.processors.append(processor)
        
    def process(self, data):
        """执行处理管道"""
        result = data
        for processor in self.processors:
            result = processor.process(result)
        return result

class TextNormalizer:
    """文本标准化处理器"""
    
    def process(self, text: str) -> str:
        """文本标准化"""
        # 1. 全角转半角
        text = self.full_to_half_width(text)
        
        # 2. 数字标准化
        text = self.normalize_numbers(text)
        
        # 3. 标点符号标准化
        text = self.normalize_punctuation(text)
        
        # 4. 空白字符处理
        text = self.normalize_whitespace(text)
        
        return text
        
    def full_to_half_width(self, text: str) -> str:
        """全角转半角"""
        result = []
        for char in text:
            code = ord(char)
            if 0xFF01 <= code <= 0xFF5E:  # 全角字符范围
                result.append(chr(code - 0xFEE0))
            else:
                result.append(char)
        return ''.join(result)

class FillerWordsFilter:
    """语气词过滤器"""
    
    def __init__(self, tokenizer: BaseTokenizer):
        self.tokenizer = tokenizer
        self.filler_words = {
            '嗯', '啊', '呢', '哦', '额', '那个', '这个', '就是',
            '然后', '所以', '因为', '但是', '可是', '不过', '而且',
            '或者', '比如', '什么的', '之类的', '反正'
        }
        
    def process(self, text: str) -> str:
        """过滤语气词"""
        # 使用分词器进行词性标注
        tokenization_result = self.tokenizer.tokenize(text)
        
        # 根据词性过滤语气词
        filtered_tokens = []
        for token, start, end in tokenization_result.tokens:
            if not self._is_filler_word(token):
                filtered_tokens.append(token)
                
        return ''.join(filtered_tokens)
        
    def _is_filler_word(self, word: str) -> bool:
        """判断是否为语气词"""
        return word in self.filler_words
```

### 6.3 存储管理层架构

#### 6.3.1 内存管理器
```python
class MemoryManager:
    """内存管理器"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.cached_data = {}
        self.usage_stats = {}
        
    def cache_data(self, key: str, data: Any, ttl: int = 3600):
        """缓存数据"""
        if self._get_memory_usage() > self.max_memory_mb:
            self._cleanup_cache()
            
        self.cached_data[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl,
            'access_count': 0
        }
        
    def get_cached_data(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self.cached_data:
            cache_entry = self.cached_data[key]
            
            # 检查TTL
            if time.time() - cache_entry['timestamp'] > cache_entry['ttl']:
                del self.cached_data[key]
                return None
                
            # 更新访问统计
            cache_entry['access_count'] += 1
            return cache_entry['data']
            
        return None
        
    def _cleanup_cache(self):
        """清理缓存"""
        # LRU策略清理缓存
        sorted_items = sorted(
            self.cached_data.items(),
            key=lambda x: (x[1]['access_count'], x[1]['timestamp'])
        )
        
        # 删除最少使用的25%
        items_to_remove = len(sorted_items) // 4
        for i in range(items_to_remove):
            key = sorted_items[i][0]
            del self.cached_data[key]

class TempFileManager:
    """临时文件管理器"""
    
    def __init__(self):
        self.temp_files = []
        self.temp_dir = tempfile.gettempdir()
        
    def create_temp_file(self, prefix: str = 'cer_tool_', suffix: str = '.tmp') -> str:
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            dir=self.temp_dir,
            delete=False
        )
        
        self.temp_files.append(temp_file.name)
        temp_file.close()
        
        return temp_file.name
        
    def cleanup_temp_files(self):
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except OSError:
                pass  # 忽略删除错误
                
        self.temp_files.clear()
        
    def __del__(self):
        """析构时自动清理"""
        self.cleanup_temp_files()
```

## 7. API接口设计

### 7.1 内部API架构

#### 7.1.1 REST风格内部API
```python
class InternalAPIRouter:
    """内部API路由器"""
    
    def __init__(self):
        self.routes = {}
        self.middleware = []
        
    def register_route(self, path: str, handler: Callable):
        """注册API路由"""
        self.routes[path] = handler
        
    def call_api(self, path: str, data: Dict = None) -> APIResponse:
        """调用内部API"""
        if path not in self.routes:
            return APIResponse(
                status=404,
                error="API路径不存在",
                data=None
            )
            
        try:
            # 执行中间件
            for middleware in self.middleware:
                data = middleware.process_request(data)
                
            # 调用处理器
            handler = self.routes[path]
            result = handler(data)
            
            # 处理响应
            for middleware in reversed(self.middleware):
                result = middleware.process_response(result)
                
            return APIResponse(
                status=200,
                error=None,
                data=result
            )
            
        except Exception as e:
            return APIResponse(
                status=500,
                error=str(e),
                data=None
            )

@dataclass
class APIResponse:
    """API响应格式"""
    status: int
    error: Optional[str]
    data: Optional[Any]
    
    def is_success(self) -> bool:
        return self.status == 200
```

#### 7.1.2 具体API实现
```python
class TokenizerAPI:
    """分词器API"""
    
    def __init__(self):
        self.tokenizer_manager = TokenizerManager()
        
    def get_available_tokenizers(self, data: Dict = None) -> Dict:
        """获取可用分词器列表"""
        tokenizers = TokenizerFactory.get_available_tokenizers()
        
        tokenizer_info = []
        for name in tokenizers:
            tokenizer = self.tokenizer_manager.get_tokenizer(name)
            info = tokenizer.get_info()
            tokenizer_info.append(info)
            
        return {
            'available_tokenizers': tokenizers,
            'tokenizer_details': tokenizer_info
        }
        
    def tokenize_text(self, data: Dict) -> Dict:
        """文本分词API"""
        text = data.get('text', '')
        tokenizer_type = data.get('tokenizer', 'jieba')
        
        tokenizer = self.tokenizer_manager.get_tokenizer(tokenizer_type)
        result = tokenizer.tokenize(text)
        
        return {
            'tokens': result.tokens,
            'processing_time': result.processing_time,
            'metadata': result.metadata
        }

class CalculationAPI:
    """计算API"""
    
    def calculate_cer(self, data: Dict) -> Dict:
        """CER计算API"""
        reference = data.get('reference', '')
        hypothesis = data.get('hypothesis', '')
        tokenizer_type = data.get('tokenizer', 'jieba')
        filter_fillers = data.get('filter_fillers', False)
        
        # 创建计算策略
        strategy = CERCalculationStrategy(tokenizer_type)
        context = AlgorithmContext(strategy)
        
        # 执行计算
        result = context.execute_algorithm(
            reference, hypothesis,
            filter_fillers=filter_fillers
        )
        
        return result.to_dict()
        
    def batch_calculate(self, data: Dict) -> Dict:
        """批量计算API"""
        file_pairs = data.get('file_pairs', [])
        config = data.get('config', {})
        
        batch_service = BatchProcessingService()
        results = batch_service.execute_batch_calculation(file_pairs, config)
        
        return {
            'total_processed': len(results),
            'results': [result.to_dict() for result in results],
            'summary': self._generate_summary(results)
        }
```

### 7.2 外部扩展接口

#### 7.2.1 插件系统架构
```python
class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_hooks = defaultdict(list)
        
    def register_plugin(self, plugin: 'PluginInterface'):
        """注册插件"""
        plugin_name = plugin.get_name()
        self.plugins[plugin_name] = plugin
        
        # 注册钩子
        for hook_name in plugin.get_hooks():
            self.plugin_hooks[hook_name].append(plugin)
            
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """执行钩子"""
        results = []
        for plugin in self.plugin_hooks[hook_name]:
            try:
                result = plugin.execute_hook(hook_name, *args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"插件 {plugin.get_name()} 执行钩子 {hook_name} 失败: {e}")
                
        return results

class PluginInterface(ABC):
    """插件接口"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称"""
        pass
        
    @abstractmethod
    def get_version(self) -> str:
        """获取插件版本"""
        pass
        
    @abstractmethod
    def get_hooks(self) -> List[str]:
        """获取支持的钩子列表"""
        pass
        
    @abstractmethod
    def execute_hook(self, hook_name: str, *args, **kwargs):
        """执行钩子"""
        pass

# 示例插件实现
class CustomTokenizerPlugin(PluginInterface):
    """自定义分词器插件"""
    
    def get_name(self) -> str:
        return "custom_tokenizer"
        
    def get_version(self) -> str:
        return "1.0.0"
        
    def get_hooks(self) -> List[str]:
        return ["before_tokenize", "after_tokenize"]
        
    def execute_hook(self, hook_name: str, *args, **kwargs):
        if hook_name == "before_tokenize":
            return self.preprocess_text(args[0])
        elif hook_name == "after_tokenize":
            return self.postprocess_tokens(args[0])
```

## 8. 跨层通信机制

### 8.1 消息总线架构
```python
class MessageBus:
    """消息总线"""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.message_queue = queue.Queue()
        
    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        self.subscribers[event_type].append(handler)
        
    def publish(self, event_type: str, data: Any):
        """发布事件"""
        message = Message(event_type, data, timestamp=time.time())
        self.message_queue.put(message)
        
    def process_messages(self):
        """处理消息队列"""
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self._dispatch_message(message)
            
    def _dispatch_message(self, message: 'Message'):
        """分发消息"""
        handlers = self.subscribers[message.event_type]
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"消息处理器执行失败: {e}")

@dataclass
class Message:
    """消息实体"""
    event_type: str
    data: Any
    timestamp: float
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

### 8.2 依赖注入容器
```python
class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self.services = {}
        self.singletons = {}
        
    def register(self, interface: Type, implementation: Type, 
                singleton: bool = False):
        """注册服务"""
        self.services[interface] = {
            'implementation': implementation,
            'singleton': singleton
        }
        
    def resolve(self, interface: Type):
        """解析依赖"""
        if interface not in self.services:
            raise DependencyNotFoundError(f"未注册的依赖: {interface}")
            
        service_config = self.services[interface]
        implementation = service_config['implementation']
        
        if service_config['singleton']:
            if interface not in self.singletons:
                self.singletons[interface] = self._create_instance(implementation)
            return self.singletons[interface]
        else:
            return self._create_instance(implementation)
            
    def _create_instance(self, implementation: Type):
        """创建实例"""
        # 解析构造函数依赖
        import inspect
        signature = inspect.signature(implementation.__init__)
        
        args = {}
        for param_name, param in signature.parameters.items():
            if param_name != 'self' and param.annotation != inspect.Parameter.empty:
                args[param_name] = self.resolve(param.annotation)
                
        return implementation(**args)
```

---

**文档版本**：V1.4  
**最后更新时间**：2025-10-23 14:58  
**更新说明**：[P2任务完成：添加异步计算控制器架构和预处理流水线设计]  
**维护人员**：开发团队 