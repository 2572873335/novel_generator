# 全自动AI小说生成系统 - 总结

## 系统概述

本系统基于 **Anthropic 长运行代理最佳实践** 构建，实现了全自动的AI小说生成流程。

## 核心特性

### 1. 增量式进展 (Incremental Progress)
- 每次会话只处理一个章节
- 避免尝试一次性完成整个小说
- 确保每个章节的质量

### 2. 清晰工件 (Clear Artifacts)
- **novel-progress.txt** - 进度跟踪
- **chapter-list.json** - 章节规格（Feature List）
- **chapter-XXX.md** - 章节内容
- **review-XXX.md** - 审查报告
- **Git提交** - 版本控制

### 3. 多代理协作
- **Initializer Agent** - 项目初始化
- **Writer Agent** - 逐章写作
- **Reviewer Agent** - 质量审查

### 4. 智能上下文管理
- 自动加载必要的上下文
- 保持角色和情节一致性
- 章节间连贯性保障

## 系统组件

```
novel_generator/
├── agents/                      # 代理模块
│   ├── __init__.py
│   ├── initializer_agent.py    # 初始化代理 (Initializer Agent)
│   ├── writer_agent.py         # 写作代理 (Writer Agent)
│   └── reviewer_agent.py       # 审查代理 (Reviewer Agent)
│
├── core/                        # 核心模块
│   ├── __init__.py
│   ├── novel_generator.py      # 主控制器
│   ├── progress_manager.py     # 进度管理器
│   ├── chapter_manager.py      # 章节管理器
│   └── character_manager.py    # 角色管理器
│
├── config/                      # 配置模块
│   ├── __init__.py
│   └── settings.py             # 配置设置
│
├── examples/                    # 示例
│   └── example_config.json     # 示例配置
│
├── main.py                      # 主入口
├── demo.py                      # 演示脚本
├── README.md                    # 使用说明
├── ARCHITECTURE.md              # 架构文档
├── SYSTEM_SUMMARY.md            # 本文件
└── requirements.txt             # 依赖列表
```

## 工作流程

### 阶段1: 初始化
```
用户配置
    ↓
Initializer Agent
    ↓
├─→ outline.md (大纲)
├─→ characters.json (角色设定)
├─→ chapter-list.json (章节列表)
├─→ style-guide.md (风格指南)
└─→ novel-progress.txt (进度文件)
```

### 阶段2: 写作循环
```
每次会话:
    ↓
读取进度文件
    ↓
获取下一章节
    ↓
加载上下文 (大纲、角色、前一章)
    ↓
创作内容 (LLM生成)
    ↓
自我审查
    ↓
保存章节
    ↓
更新进度
    ↓
Git提交
    ↓
(循环直到完成)
```

### 阶段3: 审查
```
对每个章节:
    ↓
情节连贯性评估
角色一致性评估
写作质量评估
吸引力评估
技术准确性评估
    ↓
生成审查报告
    ↓
判断是否通过
```

### 阶段4: 合并
```
所有章节文件
    ↓
合并为完整小说
    ↓
novel-complete.md
```

## 关键设计模式

### 1. Feature List 模式
对应 Anthropic 文章中的 `feature_list.json`：

```json
{
  "chapter_number": 1,
  "title": "第一章：神秘信号",
  "summary": "天文学家林晓接收到神秘信号",
  "key_plot_points": [
    "林晓发现异常信号",
    "信号来自4光年外",
    "决定深入研究"
  ],
  "characters_involved": ["林晓", "王教授"],
  "word_count_target": 3000,
  "status": "completed"
}
```

### 2. 进度跟踪模式
对应 Anthropic 文章中的 `claude-progress.txt`：

```json
{
  "title": "小说标题",
  "completed_chapters": 5,
  "total_chapters": 20,
  "status": "writing",
  "chapters": [
    {
      "chapter_number": 1,
      "status": "completed",
      "word_count": 3200,
      "quality_score": 8.5
    }
  ]
}
```

### 3. 上下文加载模式
```python
def _load_writing_context(self, chapter_number):
    return {
        'outline': self._load_outline(),
        'characters': self._load_characters(),
        'current_chapter': self._get_chapter_spec(chapter_number),
        'style_guide': self._load_style_guide(),
        'previous_chapter': self._load_previous(chapter_number)
    }
```

## 使用方法

### 交互式模式
```bash
python main.py --interactive
```

### 配置文件模式
```bash
python main.py --config my_novel.json
```

### 命令行模式
```bash
python main.py --title "我的小说" --genre "科幻" --chapters 10
```

### 查看进度
```bash
python main.py --progress novels/my_novel
```

### 运行演示
```bash
python demo.py
```

## 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | 必填 | 小说标题 |
| genre | string | general | 小说类型 |
| target_chapters | int | 10 | 目标章节数 |
| words_per_chapter | int | 3000 | 每章字数 |
| description | string | "" | 故事简介 |
| writing_style | string | descriptive | 写作风格 |
| enable_self_review | bool | true | 启用自我审查 |
| min_chapter_quality_score | float | 7.0 | 最低质量分数 |

## 项目输出结构

```
novels/{title}/
├── README.md                  # 项目说明
├── outline.md                 # 小说大纲
├── characters.json            # 角色设定
├── chapter-list.json          # 章节列表
├── style-guide.md            # 写作风格指南
├── novel-progress.txt        # 进度跟踪
├── generation-report.txt     # 生成报告
├── novel-complete.md         # 完整小说
├── chapters/                 # 章节内容
│   ├── chapter-001.md
│   ├── chapter-002.md
│   └── ...
└── reviews/                  # 审查报告
    ├── review-001.md
    ├── review-002.md
    └── ...
```

## 质量评估维度

1. **情节连贯性** (Plot Coherence) - 是否与大纲一致
2. **角色一致性** (Character Consistency) - 角色行为是否符合设定
3. **写作质量** (Writing Quality) - 文笔、描写、对话
4. **吸引力** (Engagement) - 是否引人入胜
5. **技术准确性** (Technical Accuracy) - 语法、标点、格式

## 扩展点

### 1. 集成真实LLM
```python
class ClaudeLLMClient:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(self, prompt, **kwargs):
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

### 2. 添加新代理
```python
class EditorAgent:
    """编辑代理 - 专门负责润色"""
    def edit_chapter(self, chapter_number):
        # 深度编辑逻辑
        pass
```

### 3. 自定义质量评估
```python
class CustomReviewer(ReviewerAgent):
    def _evaluate_style_consistency(self, content):
        # 自定义风格检查
        pass
```

## 演示结果

运行 `python demo.py` 可以看到：

1. **进度管理器演示** - 展示进度跟踪功能
2. **章节管理器演示** - 展示章节列表和写作提示生成
3. **角色管理器演示** - 展示角色设定和一致性检查
4. **完整工作流程演示** - 展示从初始化到写作的完整流程

## 核心优势

1. ✅ **可靠性** - 每个步骤都有明确的输入输出
2. ✅ **可恢复性** - 任何时候都可以从中断处继续
3. ✅ **可扩展性** - 易于添加新功能
4. ✅ **可维护性** - 清晰的模块划分
5. ✅ **质量保证** - 多维度质量评估

## 参考

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic: Claude 4 Prompting Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multi-context-window-workflows)

## 许可证

MIT License

---

**系统状态**: ✅ 已完成并测试
**最后更新**: 2026-02-20
