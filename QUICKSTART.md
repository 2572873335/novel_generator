# 快速开始指南

## 1. 系统要求

- Python 3.7+
- 可选: LLM API密钥 (Claude/OpenAI)

## 2. 安装

```bash
# 进入项目目录
cd novel_generator

# 安装依赖 (可选，当前使用模拟LLM)
# pip install -r requirements.txt
```

## 3. 运行演示

```bash
python demo.py
```

这将展示系统的所有核心功能。

## 4. 创建你的第一本小说

### 方法1: 交互式模式（推荐）

```bash
python main.py --interactive
```

按照提示输入：
- 小说标题
- 类型
- 章节数
- 每章字数
- 故事简介

### 方法2: 使用配置文件

创建 `my_novel.json`:

```json
{
  "title": "星际觉醒",
  "genre": "科幻",
  "target_chapters": 10,
  "words_per_chapter": 3000,
  "description": "关于人工智能觉醒的故事"
}
```

运行：

```bash
python main.py --config my_novel.json
```

### 方法3: 命令行参数

```bash
python main.py --title "星际觉醒" --genre "科幻" --chapters 10 --words 3000
```

## 5. 查看进度

```bash
python main.py --progress novels/星际觉醒
```

## 6. 项目输出

生成完成后，你可以在项目目录中找到：

```
novels/星际觉醒/
├── README.md              # 项目说明
├── outline.md             # 小说大纲
├── characters.json        # 角色设定
├── chapter-list.json      # 章节列表
├── novel-progress.txt     # 进度跟踪
├── novel-complete.md      # 完整小说 ⭐
├── chapters/              # 各章节文件
│   ├── chapter-001.md
│   ├── chapter-002.md
│   └── ...
└── reviews/               # 审查报告
    ├── review-001.md
    └── ...
```

## 7. 集成真实LLM

当前系统使用模拟LLM。要集成真实LLM：

### 7.1 安装依赖

```bash
pip install anthropic
```

### 7.2 创建LLM客户端

编辑 `core/novel_generator.py`:

```python
import anthropic

class ClaudeLLMClient:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(self, prompt, **kwargs):
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.8,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

### 7.3 使用真实LLM

在 `novel_generator.py` 中替换 `MockLLMClient`:

```python
# 替换这行
llm_client = MockLLMClient()

# 为
llm_client = ClaudeLLMClient(api_key="your-api-key")
```

## 8. 高级配置

### 8.1 完整配置示例

```json
{
  "title": "星际觉醒",
  "genre": "科幻",
  "target_chapters": 15,
  "words_per_chapter": 3500,
  "description": "关于人工智能觉醒的故事",
  "writing_style": "descriptive",
  "tone": "neutral",
  "enable_self_review": true,
  "min_chapter_quality_score": 7.0,
  "max_revision_attempts": 3
}
```

### 8.2 配置选项说明

| 选项 | 说明 | 可选值 |
|------|------|--------|
| writing_style | 写作风格 | descriptive, concise, poetic, dramatic |
| tone | 基调 | dark, light, neutral, humorous |
| enable_self_review | 启用自我审查 | true, false |
| min_chapter_quality_score | 最低质量分数 | 1.0 - 10.0 |
| max_revision_attempts | 最大修改次数 | 1 - 5 |

## 9. 故障排除

### 问题: 生成内容质量不高

**解决方案:**
- 提高 `min_chapter_quality_score`
- 增加 `max_revision_attempts`
- 提供更详细的 `description`

### 问题: 章节之间不连贯

**解决方案:**
- 检查 `outline.md` 的章节规划
- 确保前一章节已正确保存
- 在配置中启用更严格的连贯性检查

### 问题: 角色不一致

**解决方案:**
- 完善 `characters.json` 中的角色设定
- 在写作提示中强调角色特征
- 增加角色一致性检查频率

## 10. 下一步

1. ✅ 运行演示了解系统
2. ✅ 创建第一本小说
3. ✅ 查看生成的文件
4. ⏭️ 集成真实LLM
5. ⏭️ 自定义代理行为
6. ⏭️ 添加新功能

## 11. 学习资源

- [README.md](README.md) - 详细使用说明
- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构
- [SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md) - 系统总结

## 12. 获取帮助

```bash
# 查看帮助
python main.py --help

# 查看示例配置
cat examples/example_config.json
```

---

**祝你创作愉快！** 🚀
