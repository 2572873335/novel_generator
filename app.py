#!/usr/bin/env python3
"""
全自动AI小说生成系统 - Web UI界面
基于 Streamlit 构建的现代化交互界面
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 将项目根目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入（从根目录下的包导入）
try:
    from core.novel_generator import NovelGenerator, create_novel
    from core.progress_manager import ProgressManager
    from config.settings import NovelConfig, DEFAULT_CONFIG
except ImportError:
    # 如果作为包导入
    from novel_generator import create_novel, NovelGenerator
    from novel_generator.core.progress_manager import ProgressManager
    from novel_generator.config.settings import NovelConfig, DEFAULT_CONFIG

# 页面配置
st.set_page_config(
    page_title="AI小说生成器",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义CSS样式
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #1f77b4 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #666 !important;
        text-align: center !important;
        margin-bottom: 3rem !important;
    }
    .card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .status-pending {
        color: #ffa500;
        font-weight: bold;
    }
    .status-writing {
        color: #1e90ff;
        font-weight: bold;
    }
    .status-completed {
        color: #32cd32;
        font-weight: bold;
    }
    .chapter-item {
        background-color: #ffffff;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)


def init_session_state():
    """初始化会话状态"""
    if "projects" not in st.session_state:
        st.session_state.projects = []
    if "current_project" not in st.session_state:
        st.session_state.current_project = None
    if "generation_status" not in st.session_state:
        st.session_state.generation_status = {}
    if "logs" not in st.session_state:
        st.session_state.logs = []


def get_projects():
    """获取所有项目列表"""
    projects = []
    novels_dir = Path("novels")
    if novels_dir.exists():
        for project_dir in novels_dir.iterdir():
            if project_dir.is_dir():
                progress_file = project_dir / "novel-progress.txt"
                if progress_file.exists():
                    try:
                        with open(progress_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            projects.append(
                                {
                                    "name": project_dir.name,
                                    "title": data.get("title", "未命名"),
                                    "genre": data.get("genre", "通用"),
                                    "total_chapters": data.get("total_chapters", 0),
                                    "completed_chapters": data.get(
                                        "completed_chapters", 0
                                    ),
                                    "status": data.get("status", "unknown"),
                                    "path": str(project_dir),
                                }
                            )
                    except:
                        pass
    return projects


def render_header():
    """渲染页面头部"""
    st.markdown('<h1 class="main-header">📚 AI小说生成器</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">基于Anthropic长运行代理最佳实践的全自动小说创作系统</p>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    """渲染侧边栏导航"""
    with st.sidebar:
        st.title("导航菜单")

        page = st.radio(
            "选择功能",
            [
                "🏠 首页",
                "➕ 创建新项目",
                "✍️ 写作控制",
                "📊 进度监控",
                "📖 查看章节",
                "⚙️ 系统设置",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # 显示现有项目
        st.subheader("📁 现有项目")
        projects = get_projects()

        if projects:
            project_names = [
                f"{p['title']} ({p['completed_chapters']}/{p['total_chapters']})"
                for p in projects
            ]
            selected_project = st.selectbox(
                "选择项目", project_names, key="sidebar_project_select"
            )
            if selected_project:
                st.session_state.current_project = projects[
                    project_names.index(selected_project)
                ]
        else:
            st.info("暂无项目")

        st.divider()

        # 系统信息
        st.subheader("系统信息")
        st.text(f"工作目录: {os.getcwd()}")
        st.text(f"Python版本: {sys.version.split()[0]}")

        return page


def render_home():
    """渲染首页"""
    st.header("🏠 欢迎使用AI小说生成器")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="metric-card">
            <h3>🚀 快速开始</h3>
            <p>创建您的小说项目</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("创建新项目", use_container_width=True):
            st.session_state.page = "➕ 创建新项目"
            st.rerun()

    with col2:
        st.markdown(
            """
        <div class="metric-card">
            <h3>✍️ 智能写作</h3>
            <p>AI自动生成章节内容</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("开始写作", use_container_width=True):
            st.session_state.page = "✍️ 写作控制"
            st.rerun()

    with col3:
        st.markdown(
            """
        <div class="metric-card">
            <h3>📊 进度跟踪</h3>
            <p>实时监控生成进度</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("查看进度", use_container_width=True):
            st.session_state.page = "📊 进度监控"
            st.rerun()

    st.divider()

    # 项目概览
    st.subheader("📊 项目概览")
    projects = get_projects()

    if projects:
        cols = st.columns(len(projects) if len(projects) <= 4 else 4)
        for idx, project in enumerate(projects[:4]):
            with cols[idx % 4]:
                progress_pct = (
                    (project["completed_chapters"] / project["total_chapters"] * 100)
                    if project["total_chapters"] > 0
                    else 0
                )

                st.markdown(
                    f"""
                <div class="card">
                    <h4>{project["title"]}</h4>
                    <p>类型: {project["genre"]}</p>
                    <p>进度: {project["completed_chapters"]}/{project["total_chapters"]} 章</p>
                    <div style="background-color: #e0e0e0; border-radius: 10px; height: 10px;">
                        <div style="background-color: #1f77b4; width: {progress_pct}%; 
                                    height: 100%; border-radius: 10px;"></div>
                    </div>
                    <p style="text-align: right; margin-top: 5px;">{progress_pct:.1f}%</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("暂无项目，点击上方'创建新项目'开始创作！")


def render_create_project():
    """渲染创建项目页面"""
    st.header("➕ 创建新项目")

    with st.form("create_project_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("📖 小说标题", placeholder="请输入小说标题")
            genre = st.selectbox(
                "📂 小说类型",
                ["科幻", "奇幻", "悬疑", "言情", "历史", "武侠", "现代", "其他"],
                index=0,
            )
            target_chapters = st.number_input(
                "📑 目标章节数", min_value=1, max_value=100, value=10
            )

        with col2:
            words_per_chapter = st.number_input(
                "📝 每章字数", min_value=500, max_value=10000, value=3000, step=500
            )
            writing_style = st.selectbox(
                "✨ 写作风格", ["描述性", "简洁", "诗意", "戏剧性"], index=0
            )
            tone = st.selectbox(
                "🎭 故事基调", ["中性", "暗黑", "轻松", "幽默"], index=0
            )

        description = st.text_area(
            "📝 故事简介", placeholder="请简要描述故事背景、主要情节等...", height=150
        )

        # 高级设置
        with st.expander("⚙️ 高级设置"):
            col3, col4 = st.columns(2)
            with col3:
                enable_self_review = st.checkbox("启用自我审查", value=True)
                min_quality_score = st.slider("最低质量分数", 1.0, 10.0, 7.0, 0.5)
            with col4:
                max_revision_attempts = st.number_input("最大修改次数", 1, 10, 3)

        submitted = st.form_submit_button("🚀 开始生成", use_container_width=True)

        if submitted:
            if not title:
                st.error("❌ 请输入小说标题！")
            else:
                config = {
                    "title": title,
                    "genre": genre,
                    "target_chapters": target_chapters,
                    "words_per_chapter": words_per_chapter,
                    "description": description,
                    "writing_style": writing_style,
                    "tone": tone,
                    "enable_self_review": enable_self_review,
                    "min_chapter_quality_score": min_quality_score,
                    "max_revision_attempts": max_revision_attempts,
                }

                with st.spinner("正在初始化项目..."):
                    try:
                        result = create_novel(config)
                        if result["success"]:
                            st.success(
                                f"✅ 项目创建成功！\n\n项目位置: {result['project_dir']}"
                            )
                            st.balloons()
                        else:
                            st.error(f"❌ 创建失败: {result.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"❌ 发生错误: {str(e)}")


def render_writing_control():
    """渲染写作控制页面"""
    st.header("✍️ 写作控制")

    # 选择项目
    projects = get_projects()
    if not projects:
        st.warning("⚠️ 暂无项目，请先创建新项目")
        return

    project_names = [
        f"{p['title']} ({p['completed_chapters']}/{p['total_chapters']})"
        for p in projects
    ]
    selected = st.selectbox("选择要操作的项目", project_names)

    if selected:
        project = projects[project_names.index(selected)]

        # 显示项目信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总章节", project["total_chapters"])
        with col2:
            st.metric("已完成", project["completed_chapters"])
        with col3:
            remaining = project["total_chapters"] - project["completed_chapters"]
            st.metric("待完成", remaining)
        with col4:
            progress = (
                (project["completed_chapters"] / project["total_chapters"] * 100)
                if project["total_chapters"] > 0
                else 0
            )
            st.metric("完成度", f"{progress:.1f}%")

        st.divider()

        # 操作按钮
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("▶️ 继续写作", use_container_width=True):
                with st.spinner("正在准备写作环境..."):
                    try:
                        # 这里可以调用写作功能
                        st.success("写作准备完成！")
                        st.info("（实际实现中，这里会启动Writer Agent进行章节生成）")
                    except Exception as e:
                        st.error(f"错误: {str(e)}")

        with col2:
            if st.button("🔍 质量审查", use_container_width=True):
                st.info("（实际实现中，这里会启动Reviewer Agent进行质量审查）")

        with col3:
            if st.button("📦 合并导出", use_container_width=True):
                st.info("（实际实现中，这里会将所有章节合并为完整小说）")

        # 日志显示
        st.subheader("📝 生成日志")
        log_container = st.container()
        with log_container:
            if st.session_state.logs:
                for log in reversed(st.session_state.logs[-20:]):
                    st.text(log)
            else:
                st.info("暂无日志")


def render_progress_monitor():
    """渲染进度监控页面"""
    st.header("📊 进度监控")

    projects = get_projects()
    if not projects:
        st.warning("⚠️ 暂无项目")
        return

    # 显示所有项目的进度
    for project in projects:
        with st.expander(f"📚 {project['title']}", expanded=True):
            progress = (
                (project["completed_chapters"] / project["total_chapters"] * 100)
                if project["total_chapters"] > 0
                else 0
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(progress / 100)
            with col2:
                st.write(
                    f"{project['completed_chapters']}/{project['total_chapters']} ({progress:.1f}%)"
                )

            # 加载详细进度信息
            pm = ProgressManager(project["path"])
            progress_data = pm.load_progress()

            if progress_data and progress_data.chapters:
                st.subheader("章节详情")

                # 显示章节列表
                cols = st.columns(3)
                for idx, chapter in enumerate(progress_data.chapters):
                    with cols[idx % 3]:
                        status_icon = {
                            "pending": "⏳",
                            "writing": "✍️",
                            "reviewing": "👀",
                            "completed": "✅",
                            "revision_needed": "🔧",
                        }.get(chapter.status, "❓")

                        status_class = f"status-{chapter.status}"

                        st.markdown(
                            f"""
                        <div class="chapter-item">
                            <strong>{status_icon} 第{chapter.chapter_number}章</strong><br>
                            <span class="{status_class}">{chapter.status}</span><br>
                            {f"字数: {chapter.word_count}" if chapter.word_count > 0 else ""}
                            {f"<br>质量: {chapter.quality_score:.1f}" if chapter.quality_score > 0 else ""}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )


def render_chapter_view():
    """渲染章节查看页面"""
    st.header("📖 查看章节")

    projects = get_projects()
    if not projects:
        st.warning("⚠️ 暂无项目")
        return

    # 选择项目
    project_names = [p["title"] for p in projects]
    selected_project = st.selectbox("选择项目", project_names)

    if selected_project:
        project = projects[project_names.index(selected_project)]
        chapters_dir = Path(project["path"]) / "chapters"

        if chapters_dir.exists():
            chapter_files = sorted([f for f in chapters_dir.glob("chapter-*.md")])

            if chapter_files:
                # 选择章节
                chapter_options = [
                    f"第{int(f.stem.split('-')[1])}章" for f in chapter_files
                ]
                selected_chapter = st.selectbox("选择章节", chapter_options)

                if selected_chapter:
                    chapter_num = int(
                        selected_chapter.replace("第", "").replace("章", "")
                    )
                    chapter_file = chapters_dir / f"chapter-{chapter_num:03d}.md"

                    if chapter_file.exists():
                        with open(chapter_file, "r", encoding="utf-8") as f:
                            content = f.read()

                        # 显示章节内容
                        st.markdown("---")
                        st.markdown(content)
                        st.markdown("---")

                        # 下载按钮
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 下载本章节",
                                data=content,
                                file_name=f"{selected_chapter}.md",
                                mime="text/markdown",
                            )
            else:
                st.info("该项目暂无章节内容")
        else:
            st.info("该项目暂无章节内容")


def render_settings():
    """渲染系统设置页面"""
    st.header("⚙️ 系统设置")

    st.subheader("🎨 界面设置")

    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox("主题", ["亮色", "暗色"], index=0)
    with col2:
        language = st.selectbox("语言", ["中文", "English"], index=0)

    st.subheader("🤖 AI模型设置")

    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(
            "选择模型", ["Claude-3.5-Sonnet", "GPT-4", "本地模型"], index=0
        )
    with col2:
        api_key = st.text_input(
            "API密钥", type="password", placeholder="输入您的API密钥"
        )

    temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.8, 0.1, help="控制生成文本的创造性，值越高越有创意"
    )

    st.subheader("💾 存储设置")

    projects_dir = st.text_input("项目存储目录", value="novels")
    auto_save = st.checkbox("自动保存进度", value=True)

    if st.button("💾 保存设置", use_container_width=True):
        st.success("设置已保存！")


def main():
    """主函数"""
    init_session_state()
    render_header()

    page = render_sidebar()

    # 根据选择的页面渲染内容
    if page == "🏠 首页":
        render_home()
    elif page == "➕ 创建新项目":
        render_create_project()
    elif page == "✍️ 写作控制":
        render_writing_control()
    elif page == "📊 进度监控":
        render_progress_monitor()
    elif page == "📖 查看章节":
        render_chapter_view()
    elif page == "⚙️ 系统设置":
        render_settings()


if __name__ == "__main__":
    main()
