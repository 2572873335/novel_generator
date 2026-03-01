@echo off
chcp 65001 >nul
echo ==========================================
echo   NovelForge 极压测试: 工作流集市自动化
echo ==========================================

echo.
echo [1/4] 切换到工作流集市页面...
python tools/ui_cli.py switch_view market
timeout /t 1 >nul

echo.
echo [2/4] 填写新工作流名称...
python tools/ui_cli.py fill_text edit_skill_name "auto-test-skill"
timeout /t 1 >nul

echo.
echo [3/4] 填写新工作流内容...
python tools/ui_cli.py fill_text edit_skill_content "这是一个由自动化测试创建的绝密网文工作流。要求：杀伐果断，剧情节奏极快，三章之内必有爽点爆发！"
timeout /t 1 >nul

echo.
echo [4/4] 触发创建按钮...
python tools/ui_cli.py click_button btn_create_skill

echo.
echo ------------------------------------------
echo 测试指令发送完毕！
echo 请检查界面是否已出现该技能。
echo.

echo 验证文件是否创建:
if exist "user_data\custom_skills\auto-test-skill\SKILL.md" (
    echo   [OK] 文件已创建: user_data\custom_skills\auto-test-skill\SKILL.md
) else (
    echo   [FAIL] 文件未创建！
)

echo.
pause
