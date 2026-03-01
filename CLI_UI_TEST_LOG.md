# CLI-UI 集成测试记录

## 测试环境
- 日期: 2026-03-02
- 项目: novel_generator
- 测试目标: 验证 CLI 远程控制 UI 的各项功能

---

## 第一阶段：UI 启动

### 1.1 启动 PyQt6 UI
```bash
python -m ui.producer_dashboard novels/深空协议_量子黎明
```
状态: ✅ UI 已启动，监听 9999 端口

---

## 第二阶段：基础功能测试

### 2.1 测试通知功能
```bash
python tools/ui_cli.py notify "测试消息"
```
结果: ✅ 成功 - 状态栏显示 "🤖 AI: 测试消息"

### 2.2 测试视图切换
```bash
python tools/ui_cli.py switch_view preprod
python tools/ui_cli.py switch_view production
python tools/ui_cli.py switch_view vault
python tools/ui_cli.py switch_view market
```
结果: ✅ 成功 - 视图正常切换

---

## 第三阶段：文本填充测试

### 3.1 切换到前期筹备页
```bash
python tools/ui_cli.py switch_view preprod
```
结果: ✅ 成功

### 3.2 填充标题
```bash
python tools/ui_cli.py fill_text edit_title "深空协议：量子黎明"
```
结果: ✅ 成功

### 3.3 填充题材
```bash
python tools/ui_cli.py fill_text edit_genre "科幻"
```
结果: ✅ 成功

### 3.4 填充大纲
```bash
python tools/ui_cli.py fill_text edit_outline "公元2187年，人类文明面临存亡危机..."
```
结果: ✅ 成功

### 3.5 填充人物
```bash
python tools/ui_cli.py fill_text edit_chars "主角：陈锐，32岁，量子工程师"
```
结果: ✅ 成功

---

## 第四阶段：开始生成测试

### 4.1 点击开始写作按钮
```bash
python tools/ui_cli.py click_button btn_start
```
结果: ✅ 成功 - 项目保存并开始生成

### 4.2 生成进度
- 第1章: 等待生成中...
- 第2章: 生成中...
- ...
- 第9章: 生成完成
- 第10章: 生成完成

### 4.3 生成的章节文件
```
novels/深空协议_量子黎明/chapters/
  - chapter_006.md (7,279 bytes)
  - chapter_007.md (13,581 bytes)
  - chapter_008.md (10,457 bytes)
  - chapter_009.md (17,235 bytes)
  - chapter_010.md (15,523 bytes)
```

---

## 第五阶段：黄金三章评估测试

### 5.1 点击黄金三章评估按钮
```bash
python tools/ui_cli.py click_button btn_golden_check
```
结果: ✅ 成功 - 触发评估Worker

---

## 第六阶段：技能集市 CLI 控制测试

### 6.1 切换到技能集市视图
```bash
python tools/ui_cli.py switch_view market
```
结果: ✅ 成功

### 6.2 填写技能名称
```bash
python tools/ui_cli.py fill_text edit_skill_name "auto-test-skill"
```
结果: ✅ 成功

### 6.3 填写技能内容
```bash
python tools/ui_cli.py fill_text edit_skill_content "这是一个由自动化测试创建的绝密网文工作流"
```
结果: ✅ 成功

### 6.4 点击创建按钮
```bash
python tools/ui_cli.py click_button btn_create_skill
```
结果: ✅ 成功 - 文件已创建

### 6.5 验证文件创建
```bash
ls -la user_data/custom_skills/auto-test-skill/
```
结果: ✅ 成功 - SKILL.md 文件已创建

---

## 测试总结

| 功能 | 命令 | 状态 |
|------|------|------|
| 通知 | `notify` | ✅ |
| 视图切换 | `switch_view` | ✅ |
| 填充文本 | `fill_text` | ✅ |
| 点击按钮 | `click_button` | ✅ |
| 开始生成 | `click_button btn_start` | ✅ |
| 章节生成 | 10章完成 | ✅ |
| 黄金评估 | `click_button btn_golden_check` | ✅ |
| 技能创建 | `fill_text` + `click_button btn_create_skill` | ✅ |

---

## CLI 命令参考

### 基础命令
```bash
# 通知
python tools/ui_cli.py notify "消息内容"

# 视图切换
python tools/ui_cli.py switch_view preprod
python tools/ui_cli.py switch_view production
python tools/ui_cli.py switch_view vault
python tools/ui_cli.py switch_view market

# 填充文本（使用变量名）
python tools/ui_cli.py fill_text edit_title "标题"
python tools/ui_cli.py fill_text edit_genre "科幻"
python tools/ui_cli.py fill_text edit_outline "大纲内容"
python tools/ui_cli.py fill_text edit_chars "人物设定"
python tools/ui_cli.py fill_text edit_skill_name "技能名称"
python tools/ui_cli.py fill_text edit_skill_content "技能内容"

# 点击按钮（使用变量名）
python tools/ui_cli.py click_button btn_start
python tools/ui_cli.py click_button btn_pause
python tools/ui_cli.py click_button btn_resume
python tools/ui_cli.py click_button btn_golden_check
python tools/ui_cli.py click_button btn_create_skill
```

### 动态反射示例
```bash
# 任何使用变量名的UI元素都可以通过以下方式操作：
python tools/ui_cli.py fill_text <变量名> <内容>
python tools/ui_cli.py click_button <变量名>
```

### 技能集市自动化示例
```bash
# 完整流程：创建新技能
python tools/ui_cli.py switch_view market
python tools/ui_cli.py fill_text edit_skill_name "my-new-skill"
python tools/ui_cli.py fill_text edit_skill_content "# 我的新技能\n\n技能描述..."
python tools/ui_cli.py click_button btn_create_skill
```

---

## 生成结果统计

- 项目: 深空协议：量子黎明
- 题材: 科幻
- 目标章节: 50章
- 已生成章节: 10章
- 生成状态: 正常
