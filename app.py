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
    from core.agent_manager import AgentManager
    from core.model_manager import ModelManager, create_model_manager
    from core.config_manager import save_api_key, get_available_api_keys, load_env_file
    from config.settings import NovelConfig, DEFAULT_CONFIG
except ImportError:
    # 如果作为包导入
    from novel_generator import create_novel, NovelGenerator
    from novel_generator.core.progress_manager import ProgressManager
    from novel_generator.core.agent_manager import AgentManager
    from novel_generator.core.model_manager import ModelManager, create_model_manager
    from novel_generator.core.config_manager import (
        save_api_key,
        get_available_api_keys,
        load_env_file,
    )
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
                "🤖 智能体管理",
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
                <div class="metric-card">
                    <h4 style="color: white;">{project["title"]}</h4>
                    <p style="color: rgba(255,255,255,0.9);">类型: {project["genre"]}</p>
                    <p style="color: rgba(255,255,255,0.9);">进度: {project["completed_chapters"]}/{project["total_chapters"]} 章</p>
                    <div style="background-color: rgba(255,255,255,0.3); border-radius: 10px; height: 10px;">
                        <div style="background-color: white; width: {progress_pct}%; 
                                    height: 100%; border-radius: 10px;"></div>
                    </div>
                    <p style="text-align: right; margin-top: 5px; color: white;">{progress_pct:.1f}%</p>
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

    # 获取可用模型列表
    model_manager = ModelManager()
    available_models = model_manager.get_available_models()

    # 按提供商分组
    providers = {}
    for model in available_models:
        provider = model["provider"]
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)

    # 选择模型提供商
    provider_list = ["anthropic", "openai", "moonshot", "deepseek", "custom"]
    provider_labels = [
        "🅰️ Anthropic (Claude)",
        "🅾️ OpenAI (GPT)",
        "🌙 Moonshot (Kimi)",
        "🔮 DeepSeek",
        "⚙️ 自定义模型",
    ]

    selected_provider_idx = st.selectbox(
        "选择模型提供商",
        range(len(provider_list)),
        format_func=lambda x: provider_labels[x],
    )
    selected_provider = provider_list[selected_provider_idx]

    # 初始化变量
    custom_model_name = ""
    custom_base_url = ""
    custom_api_key_env = "CUSTOM_API_KEY"
    selected_model_id = ""
    selected_model = None
    api_key_env = "API_KEY"

    if selected_provider == "custom":
        # 自定义模型设置
        st.markdown("#### ⚙️ 自定义模型配置")
        custom_model_name = st.text_input(
            "模型名称", placeholder="例如: my-custom-model"
        )
        custom_base_url = st.text_input(
            "API基础URL", placeholder="例如: https://api.custom.com/v1"
        )
        custom_api_key_env = st.text_input(
            "API密钥环境变量名",
            placeholder="例如: CUSTOM_API_KEY",
            value="CUSTOM_API_KEY",
        )

        selected_model_id = "custom"
        api_key_env = custom_api_key_env
    else:
        # 选择具体模型
        provider_models = providers[selected_provider]
        model_options = [m["name"] for m in provider_models]
        model_ids_list = [m["id"] for m in provider_models]

        selected_model_idx = st.selectbox(
            "选择具体模型",
            range(len(model_options)),
            format_func=lambda x: model_options[x],
        )

        selected_model_id = model_ids_list[selected_model_idx]
        selected_model = model_manager.AVAILABLE_MODELS.get(selected_model_id)

        if selected_model:
            st.info(f"📋 {selected_model.description}")
            api_key_env = selected_model.api_key_env

    # API密钥输入
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input(
            f"{api_key_env} 密钥",
            type="password",
            placeholder=f"输入您的 {api_key_env}",
        )
    with col2:
        # 显示密钥状态
        current_key = os.getenv(api_key_env)
        if current_key:
            st.success("✓ 已配置")
        else:
            st.warning("✗ 未配置")

    # Temperature设置
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "Temperature",
            0.0,
            1.0,
            0.8,
            0.1,
            help="控制生成文本的创造性，值越高越有创意",
        )
    with col2:
        max_tokens = st.number_input(
            "最大Token数",
            min_value=1000,
            max_value=8000,
            value=4000,
            step=500,
            help="模型生成的最大token数量",
        )

    # 测试连接按钮
    if st.button("🧪 测试模型连接", use_container_width=True):
        with st.spinner("正在测试模型连接..."):
            try:
                if selected_model_id == "custom":
                    test_manager = create_model_manager(
                        "custom",
                        {
                            "name": custom_model_name
                            if custom_model_name
                            else "custom-model",
                            "display_name": "测试模型",
                            "api_key_env": api_key_env,
                            "base_url": custom_base_url if custom_base_url else None,
                        },
                    )
                else:
                    test_manager = create_model_manager(selected_model_id)

                # 测试生成
                test_prompt = "你好，请用一句话介绍你自己。"
                result = test_manager.generate(
                    test_prompt, temperature=0.7, system_prompt="你是一个友好的AI助手。"
                )

                if result.startswith("[错误]"):
                    st.error(result)
                else:
                    st.success("✅ 模型连接成功！")
                    with st.expander("查看测试结果"):
                        st.markdown(f"**提示:** {test_prompt}")
                        st.markdown(f"**回复:** {result}")
            except Exception as e:
                st.error(f"❌ 测试失败: {str(e)}")

    st.divider()

    st.subheader("💾 存储设置")

    projects_dir = st.text_input("项目存储目录", value="novels")
    auto_save = st.checkbox("自动保存进度", value=True)

    # 保存所有设置
    if st.button("💾 保存设置", use_container_width=True):
        success_count = 0
        error_messages = []

        # 保存API密钥
        if api_key and api_key_env:
            if save_api_key(api_key_env, api_key):
                success_count += 1
                st.success(f"✅ {api_key_env} 已保存到 .env 文件")
            else:
                error_messages.append(f"保存 {api_key_env} 失败")

        # 保存自定义模型配置
        if selected_model_id == "custom":
            if custom_model_name and save_api_key(
                "CUSTOM_MODEL_NAME", custom_model_name
            ):
                success_count += 1
            if custom_base_url and save_api_key("CUSTOM_BASE_URL", custom_base_url):
                success_count += 1
            if custom_api_key_env != "CUSTOM_API_KEY" and save_api_key(
                "CUSTOM_API_KEY_ENV", custom_api_key_env
            ):
                success_count += 1
        else:
            # 保存默认模型设置
            save_api_key("DEFAULT_MODEL_ID", selected_model_id)

        # 保存温度和token设置
        save_api_key("DEFAULT_TEMPERATURE", str(temperature))
        save_api_key("DEFAULT_MAX_TOKENS", str(int(max_tokens)))

        if success_count > 0 and not error_messages:
            st.success(f"✅ 成功保存 {success_count} 项设置！")
            st.info("📄 配置已保存到项目根目录的 .env 文件")
        elif error_messages:
            st.error("❌ 部分设置保存失败：" + "; ".join(error_messages))
        else:
            st.info("💡 没有需要保存的更改")


def render_agent_management():
    """渲染智能体管理页面"""
    st.header("🤖 智能体管理")

    # 初始化 AgentManager
    agent_manager = AgentManager(".")

    # 获取可用智能体
    available_agents = agent_manager.get_available_agents()

    st.subheader("📋 可用智能体")

    # 显示智能体列表
    if available_agents:
        cols = st.columns(3)
        for idx, agent in enumerate(available_agents):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(
                        f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <h4 style="margin: 0; color: white;">{agent["name"]}</h4>
                        <p style="margin: 5px 0; font-size: 0.9em; opacity: 0.9;">{agent["description"][:50]}...</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

    st.divider()

    # 创建新项目使用完整工作流
    st.subheader("🚀 完整智能体工作流")
    st.info("使用所有智能体协作完成小说创作")

    # 选择项目
    projects = get_projects()
    if projects:
        project_names = [p["title"] for p in projects]
        selected_project = st.selectbox(
            "选择要处理的项目", project_names, key="agent_project_select"
        )

        if selected_project:
            project = projects[project_names.index(selected_project)]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("项目", project["title"])
            with col2:
                st.metric(
                    "进度",
                    f"{project['completed_chapters']}/{project['total_chapters']}",
                )
            with col3:
                progress = (
                    (project["completed_chapters"] / project["total_chapters"] * 100)
                    if project["total_chapters"] > 0
                    else 0
                )
                st.metric("完成度", f"{progress:.1f}%")

            if st.button("▶️ 启动完整工作流", use_container_width=True, type="primary"):
                with st.spinner("正在协调智能体..."):
                    # 读取项目配置
                    progress_file = Path(project["path"]) / "novel-progress.txt"
                    if progress_file.exists():
                        with open(progress_file, "r", encoding="utf-8") as f:
                            config = json.load(f)

                        # 运行完整工作流
                        result = agent_manager.run_coordinator_workflow(config)

                        if result["success"]:
                            st.success(
                                f"✅ 工作流完成！共执行 {result['total_steps']} 个步骤"
                            )

                            # 显示执行结果
                            with st.expander("查看执行详情"):
                                for step_result in result["results"]:
                                    st.markdown(f"**{step_result['step']}**")
                                    st.text(
                                        step_result["result"]["result"][:200] + "..."
                                    )
                        else:
                            st.error("❌ 工作流执行失败")
    else:
        st.warning("⚠️ 暂无项目，请先创建新项目")

    st.divider()

    # 自定义智能体工作流
    st.subheader("⚙️ 自定义智能体工作流")
    st.info("选择特定智能体执行特定任务")

    if available_agents:
        agent_names = [a["name"] for a in available_agents]
        selected_agents = st.multiselect("选择要执行的智能体", agent_names)

        if selected_agents:
            st.write("执行顺序:")
            for idx, agent in enumerate(selected_agents, 1):
                st.write(f"{idx}. {agent}")

            task_description = st.text_area(
                "任务描述", placeholder="描述需要智能体完成的任务..."
            )

            if st.button("▶️ 执行选定智能体", use_container_width=True):
                if task_description:
                    with st.spinner("正在执行智能体..."):
                        # 创建并执行工作流
                        workflow = agent_manager.create_agent_workflow(
                            selected_agents, {"task": task_description}
                        )
                        result = agent_manager.execute_workflow(workflow)

                        if result["success"]:
                            st.success(f"✅ 已执行 {len(selected_agents)} 个智能体")

                            # 显示结果
                            for idx, res in enumerate(result["results"], 1):
                                with st.expander(f"智能体 {idx}: {res['agent']}"):
                                    st.text(res["result"])
                        else:
                            st.error("❌ 执行失败")
                else:
                    st.error("请输入任务描述")


def main():
    """主函数"""
    init_session_state()
    render_header()

    # 检查是否有页面切换请求
    if "page" in st.session_state:
        current_page = st.session_state.page
        del st.session_state.page  # 清除状态避免重复跳转
    else:
        current_page = None

    page = render_sidebar()

    # 优先使用按钮跳转的页面
    if current_page:
        page = current_page

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
    elif page == "🤖 智能体管理":
        render_agent_management()
    elif page == "⚙️ 系统设置":
        render_settings()


if __name__ == "__main__":
    main()
