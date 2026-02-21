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
    from core.config_manager import (
        save_api_key,
        get_available_api_keys,
        load_env_file,
        get_api_key,
    )
    from core.log_manager import get_logger, init_logger
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
        get_api_key,
    )
    from novel_generator.core.log_manager import get_logger, init_logger
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
                "💬 对话创作",
                "📚 设定库管理",
                "📦 素材库管理",
                "✍️ 写作控制",
                "📊 进度监控",
                "📖 查看章节",
                "🤖 智能体管理",
                "📋 日志查看",
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

        # 当前使用的AI模型
        st.subheader("🤖 当前AI模型")
        config = load_env_file()
        current_model_id = config.get("DEFAULT_MODEL_ID", "claude-3-5-sonnet")

        model_manager = ModelManager()
        model_info = model_manager.AVAILABLE_MODELS.get(current_model_id)

        if model_info:
            st.info(f"**{model_info.display_name}**\n\n{model_info.description}")
        elif current_model_id == "custom":
            custom_name = config.get("CUSTOM_MODEL_NAME", "自定义模型")
            st.info(f"**⚙️ {custom_name}**\n\n自定义模型")
        else:
            st.warning(f"当前模型: {current_model_id}")

        # 检查API密钥是否配置
        api_key_env = (
            model_info.api_key_env
            if model_info
            else config.get("CUSTOM_API_KEY_ENV", "CUSTOM_API_KEY")
        )
        current_key = get_api_key(api_key_env)
        if current_key:
            st.success(f"✓ API已配置")
        else:
            st.error(f"✗ API未配置")

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
            logger = get_logger()

            if not title:
                st.error("❌ 请输入小说标题！")
                logger.warning("[创建项目] 未输入小说标题")
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

                logger.log_project_creation(title, config)

                with st.spinner("正在初始化项目..."):
                    try:
                        result = create_novel(config)
                        if result["success"]:
                            st.success(
                                f"✅ 项目创建成功！\n\n项目位置: {result['project_dir']}"
                            )
                            st.balloons()
                            logger.info(
                                f"[创建项目] 成功 - 项目位置: {result['project_dir']}"
                            )
                        else:
                            st.error(f"❌ 创建失败: {result.get('error', '未知错误')}")
                            logger.error(
                                f"[创建项目] 失败 - {result.get('error', '未知错误')}"
                            )
                    except Exception as e:
                        st.error(f"❌ 发生错误: {str(e)}")
                        logger.log_error_with_traceback(e, "创建项目")


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

    # 从配置中读取默认模型
    config = load_env_file()
    saved_model_id = config.get("DEFAULT_MODEL_ID", "claude-3-5-sonnet")

    # 根据保存的模型ID确定提供商
    if saved_model_id == "custom":
        default_provider = "custom"
    elif saved_model_id in model_manager.AVAILABLE_MODELS:
        default_provider = model_manager.AVAILABLE_MODELS[saved_model_id].provider.value
    else:
        default_provider = "anthropic"

    # 设置默认选中索引
    default_provider_idx = (
        provider_list.index(default_provider)
        if default_provider in provider_list
        else 0
    )

    selected_provider_idx = st.selectbox(
        "选择模型提供商",
        range(len(provider_list)),
        index=default_provider_idx,
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
        custom_model_name = config.get("CUSTOM_MODEL_NAME", "")
        custom_base_url = config.get("CUSTOM_BASE_URL", "")
        custom_api_key_env = config.get("CUSTOM_API_KEY_ENV", "CUSTOM_API_KEY")

        custom_model_name = st.text_input(
            "模型名称", value=custom_model_name, placeholder="例如: my-custom-model"
        )
        custom_base_url = st.text_input(
            "API基础URL",
            value=custom_base_url,
            placeholder="例如: https://api.custom.com/v1",
        )
        custom_api_key_env = st.text_input(
            "API密钥环境变量名",
            value=custom_api_key_env,
            placeholder="例如: CUSTOM_API_KEY",
        )

        selected_model_id = "custom"
        api_key_env = custom_api_key_env
    else:
        # 选择具体模型
        provider_models = providers[selected_provider]
        model_options = [m["name"] for m in provider_models]
        model_ids_list = [m["id"] for m in provider_models]

        # 根据保存的模型ID确定默认选中的模型
        default_model_idx = 0
        if saved_model_id in model_ids_list:
            default_model_idx = model_ids_list.index(saved_model_id)

        selected_model_idx = st.selectbox(
            "选择具体模型",
            range(len(model_options)),
            index=default_model_idx,
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
        # 检查是否已有密钥配置
        current_key = get_api_key(api_key_env)
        api_key_placeholder = f"输入您的 {api_key_env}"
        if current_key:
            api_key_placeholder = f"{api_key_env} 已配置 (输入新值可覆盖)"

        api_key = st.text_input(
            f"{api_key_env} 密钥",
            type="password",
            placeholder=api_key_placeholder,
        )
    with col2:
        # 显示密钥状态
        if current_key:
            st.success("✓ 已配置")
        else:
            st.warning("✗ 未配置")

    # Temperature设置
    # 从配置读取默认值
    default_temperature = float(config.get("DEFAULT_TEMPERATURE", "0.8"))
    default_max_tokens = int(config.get("DEFAULT_MAX_TOKENS", "4000"))

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "Temperature",
            0.0,
            1.0,
            default_temperature,
            0.1,
            help="控制生成文本的创造性，值越高越有创意",
        )
    with col2:
        max_tokens = st.number_input(
            "最大Token数",
            min_value=1000,
            max_value=8000,
            value=default_max_tokens,
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
        logger = get_logger()
        logger.info(f"[设置] 开始保存配置 - 模型: {selected_model_id}")

        success_count = 0
        error_messages = []

        # 保存API密钥
        if api_key and api_key_env:
            if save_api_key(api_key_env, api_key):
                success_count += 1
                st.success(f"✅ {api_key_env} 已保存到 .env 文件")
                logger.log_api_key_save(api_key_env, True)
            else:
                error_messages.append(f"保存 {api_key_env} 失败")
                logger.log_api_key_save(api_key_env, False)

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
            logger.info(f"[设置] 保存自定义模型配置: {custom_model_name}")
        else:
            # 保存默认模型设置
            save_api_key("DEFAULT_MODEL_ID", selected_model_id)
            logger.log_model_selection(
                selected_model_id, selected_provider, temperature, max_tokens
            )

        # 保存温度和token设置
        save_api_key("DEFAULT_TEMPERATURE", str(temperature))
        save_api_key("DEFAULT_MAX_TOKENS", str(int(max_tokens)))

        if success_count > 0 and not error_messages:
            st.success(f"✅ 成功保存 {success_count} 项设置！")
            st.info("📄 配置已保存到项目根目录的 .env 文件")
            logger.info(f"[设置] 成功保存 {success_count} 项配置")
        elif error_messages:
            st.error("❌ 部分设置保存失败：" + "; ".join(error_messages))
            logger.error(f"[设置] 部分保存失败: {'; '.join(error_messages)}")
        else:
            st.info("💡 没有需要保存的更改")


def render_log_viewer():
    """渲染日志查看页面"""
    st.header("📋 日志查看")

    logger = get_logger()

    # 获取所有日志文件
    log_files = logger.get_log_files()

    if not log_files:
        st.warning("暂无日志文件")
        return

    # 选择日志文件
    log_file_names = [f.name for f in log_files]
    selected_log = st.selectbox("选择日志文件", log_file_names)

    if selected_log:
        log_path = logger.log_dir / selected_log

        # 读取日志内容
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log_content = f.read()

            # 显示日志行数
            lines = log_content.split("\n")
            st.info(f"📄 共 {len(lines)} 行日志")

            # 过滤选项
            col1, col2, col3 = st.columns(3)
            with col1:
                show_info = st.checkbox("显示 INFO", value=True)
            with col2:
                show_warning = st.checkbox("显示 WARNING", value=True)
            with col3:
                show_error = st.checkbox("显示 ERROR", value=True)

            # 过滤日志
            filtered_lines = []
            for line in lines:
                if not line.strip():
                    continue
                if show_info and "[INFO]" in line:
                    filtered_lines.append(line)
                elif show_warning and "[WARNING]" in line:
                    filtered_lines.append(line)
                elif show_error and "[ERROR]" in line:
                    filtered_lines.append(line)
                elif "[CRITICAL]" in line or "[DEBUG]" in line:
                    filtered_lines.append(line)

            # 显示日志内容
            st.code("\n".join(filtered_lines), language="text")

            # 下载按钮
            st.download_button(
                label="📥 下载日志文件",
                data=log_content,
                file_name=selected_log,
                mime="text/plain",
            )

        except Exception as e:
            st.error(f"读取日志文件失败: {e}")


def render_dialog_creation():
    """渲染对话创作页面"""
    st.header("💬 对话创作模式")
    st.markdown("通过对话引导AI帮助你构建小说大纲和设定")

    # 初始化对话历史
    if "dialog_messages" not in st.session_state:
        st.session_state.dialog_messages = []
    if "dialog_stage" not in st.session_state:
        st.session_state.dialog_stage = "basic_info"
    if "dialog_config" not in st.session_state:
        st.session_state.dialog_config = {}

    # 显示对话历史
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.dialog_messages:
            if msg["role"] == "assistant":
                st.chat_message("assistant").markdown(msg["content"])
            else:
                st.chat_message("user").markdown(msg["content"])

    # 根据阶段显示不同的引导
    if st.session_state.dialog_stage == "basic_info":
        if not st.session_state.dialog_messages:
            welcome_msg = """你好！我是你的AI创作助手。让我们通过对话来完成小说的初步设定吧！

首先，请告诉我你想写什么类型的小说？比如：
- 科幻
- 奇幻
- 悬疑
- 言情
- 武侠
- 历史等"""
            st.session_state.dialog_messages.append(
                {"role": "assistant", "content": welcome_msg}
            )
            st.rerun()

    # 用户输入
    if prompt := st.chat_input("请输入你的回复..."):
        st.session_state.dialog_messages.append({"role": "user", "content": prompt})

        # 根据当前阶段处理用户输入
        if st.session_state.dialog_stage == "basic_info":
            if "类型" not in st.session_state.dialog_config:
                st.session_state.dialog_config["类型"] = prompt
                response = f"好的，{prompt}是个很有趣的类型！那你想给小说取什么名字呢？"
            elif "标题" not in st.session_state.dialog_config:
                st.session_state.dialog_config["标题"] = prompt
                response = f"'{prompt}'是个不错的标题！能简单描述一下故事的核心构思吗？"
            elif "构思" not in st.session_state.dialog_config:
                st.session_state.dialog_config["构思"] = prompt
                response = "很棒的故事构思！你计划写多少章呢？"
            elif "章节数" not in st.session_state.dialog_config:
                try:
                    st.session_state.dialog_config["章节数"] = int(prompt)
                except:
                    st.session_state.dialog_config["章节数"] = 10
                response = f"好的，{st.session_state.dialog_config['章节数']}章的规模。你想让故事发生在什么样的世界观背景下？"
            elif "世界观" not in st.session_state.dialog_config:
                st.session_state.dialog_config["世界观"] = prompt
                response = (
                    "很有意思的世界设定！现在让我们来讨论主要人物。主角是什么样的人？"
                )
            elif "主角" not in st.session_state.dialog_config:
                st.session_state.dialog_config["主角"] = prompt
                st.session_state.dialog_stage = "outline"
                response = f"""很好！我们已经收集了基本信息：

📌 **小说信息汇总**
- 类型：{st.session_state.dialog_config.get("类型", "未设定")}
- 标题：{st.session_state.dialog_config.get("标题", "未设定")}
- 核心构思：{st.session_state.dialog_config.get("构思", "未设定")}
- 章节数：{st.session_state.dialog_config.get("章节数", "未设定")}
- 世界观：{st.session_state.dialog_config.get("世界观", "未设定")}
- 主角：{st.session_state.dialog_config.get("主角", "未设定")}

接下来我们可以开始构建详细大纲。你想从哪个方面开始？
1. 故事主线规划
2. 人物关系设计
3. 世界观细节
4. 章节分配

请输入数字选择，或直接描述你的想法。"""
            else:
                response = "好的，让我们继续。你还有什么想补充的吗？"

        elif st.session_state.dialog_stage == "outline":
            response = f"好的，让我帮你思考这个方面。关于'{prompt}'，你有什么具体的想法或要求吗？"

        else:
            response = f"收到！让我继续帮你完善设定。"

        st.session_state.dialog_messages.append(
            {"role": "assistant", "content": response}
        )
        st.rerun()

    # 操作按钮
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 重新开始", use_container_width=True):
            st.session_state.dialog_messages = []
            st.session_state.dialog_stage = "basic_info"
            st.session_state.dialog_config = {}
            st.rerun()
    with col2:
        if st.button("📋 查看当前设定", use_container_width=True):
            st.json(st.session_state.dialog_config)
    with col3:
        if st.button("✅ 完成并创建项目", use_container_width=True):
            if st.session_state.dialog_config:
                config = {
                    "title": st.session_state.dialog_config.get("标题", "未命名"),
                    "genre": st.session_state.dialog_config.get("类型", "通用"),
                    "target_chapters": st.session_state.dialog_config.get("章节数", 10),
                    "description": st.session_state.dialog_config.get("构思", ""),
                }
                st.session_state.page = "➕ 创建新项目"
                st.session_state.prefilled_config = config
                st.rerun()


def render_setting_library():
    """渲染设定库管理页面"""
    st.header("📚 设定库管理")
    st.markdown("管理小说的各类设定，支持多层嵌套结构")

    # 初始化设定库
    if "setting_library" not in st.session_state:
        st.session_state.setting_library = {
            "世界观": {},
            "人物关系": {},
            "组织势力": {},
            "物品装备": {},
        }

    # 选择大类
    col1, col2 = st.columns([3, 1])
    with col1:
        categories = list(st.session_state.setting_library.keys())
        selected_category = st.selectbox("选择设定类别", categories)
    with col2:
        if st.button("➕ 新建类别", use_container_width=True):
            st.session_state.show_new_category = True

    # 新建类别对话框
    if st.session_state.get("show_new_category", False):
        with st.form("new_category_form"):
            new_cat_name = st.text_input("类别名称")
            submitted = st.form_submit_button("创建")
            if submitted and new_cat_name:
                st.session_state.setting_library[new_cat_name] = {}
                st.session_state.show_new_category = False
                st.rerun()

    st.divider()

    # 显示当前类别的设定树
    st.subheader(f"📖 {selected_category}")

    current_settings = st.session_state.setting_library.get(selected_category, {})

    # 递归显示设定树
    def display_setting_tree(settings: dict, path: list, level: int = 0):
        for name, content in settings.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            indent = "　" * level
            with col1:
                if isinstance(content, dict):
                    with st.expander(f"{indent}📁 {name}", expanded=False):
                        display_setting_tree(content, path + [name], level + 1)
                else:
                    st.markdown(
                        f"{indent}📄 **{name}**: {content[:50]}..."
                        if len(str(content)) > 50
                        else f"{indent}📄 **{name}**: {content}"
                    )

    display_setting_tree(current_settings, [])

    st.divider()

    # 添加新设定
    st.subheader("➕ 添加设定")

    # 选择父级（可选）
    parent_options = ["[根目录]"]

    def get_all_paths(settings: dict, prefix: str = ""):
        paths = []
        for name, content in settings.items():
            current_path = f"{prefix}/{name}" if prefix else name
            paths.append(current_path)
            if isinstance(content, dict) and content:
                paths.extend(get_all_paths(content, current_path))
        return paths

    all_paths = get_all_paths(current_settings)
    parent_options.extend(all_paths)

    with st.form("add_setting_form"):
        col1, col2 = st.columns(2)
        with col1:
            parent_path = st.selectbox("父级位置", parent_options)
            setting_name = st.text_input("设定名称")
        with col2:
            setting_type = st.selectbox("设定类型", ["简单文本", "嵌套目录"])
            setting_content = st.text_area("设定内容", height=100)

        submitted = st.form_submit_button("添加设定")
        if submitted and setting_name:
            if setting_type == "嵌套目录":
                new_content = {}
            else:
                new_content = setting_content

            # 添加到正确的位置
            if parent_path == "[根目录]":
                current_settings[setting_name] = new_content
            else:
                path_parts = parent_path.split("/")
                target = current_settings
                for part in path_parts:
                    if part in target and isinstance(target[part], dict):
                        target = target[part]
                target[setting_name] = new_content

            st.session_state.setting_library[selected_category] = current_settings
            st.success(f"✅ 已添加设定: {setting_name}")
            st.rerun()


def render_material_library():
    """渲染素材库管理页面"""
    st.header("📦 素材库管理")
    st.markdown("管理写作素材，包括场景、对话、描写等")

    # 初始化素材库
    if "material_library" not in st.session_state:
        st.session_state.material_library = {
            "场景描写": [],
            "人物对话": [],
            "心理描写": [],
            "动作描写": [],
            "环境描写": [],
        }

    # 选择素材类型
    col1, col2 = st.columns([3, 1])
    with col1:
        material_types = list(st.session_state.material_library.keys())
        selected_type = st.selectbox("选择素材类型", material_types)
    with col2:
        if st.button("➕ 新建类型", use_container_width=True):
            st.session_state.show_new_material_type = True

    # 新建类型对话框
    if st.session_state.get("show_new_material_type", False):
        with st.form("new_material_type_form"):
            new_type_name = st.text_input("类型名称")
            submitted = st.form_submit_button("创建")
            if submitted and new_type_name:
                st.session_state.material_library[new_type_name] = []
                st.session_state.show_new_material_type = False
                st.rerun()

    st.divider()

    # 显示当前类型的素材
    st.subheader(f"📝 {selected_type}")
    materials = st.session_state.material_library.get(selected_type, [])

    if materials:
        for idx, material in enumerate(materials):
            with st.expander(f"素材 #{idx + 1}: {material.get('title', '未命名')}"):
                st.markdown(f"**标签**: {', '.join(material.get('tags', []))}")
                st.markdown(f"**内容**:")
                st.text(material.get("content", ""))

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ 编辑", key=f"edit_{selected_type}_{idx}"):
                        st.session_state.editing_material = (selected_type, idx)
                with col2:
                    if st.button(f"🗑️ 删除", key=f"del_{selected_type}_{idx}"):
                        materials.pop(idx)
                        st.session_state.material_library[selected_type] = materials
                        st.rerun()
    else:
        st.info("暂无素材，请添加新素材")

    st.divider()

    # 添加新素材
    st.subheader("➕ 添加素材")
    with st.form("add_material_form"):
        material_title = st.text_input("素材标题")
        material_tags = st.text_input("标签（用逗号分隔）")
        material_content = st.text_area("素材内容", height=150)

        submitted = st.form_submit_button("添加素材")
        if submitted and material_content:
            new_material = {
                "title": material_title or f"素材 {len(materials) + 1}",
                "tags": [t.strip() for t in material_tags.split(",")]
                if material_tags
                else [],
                "content": material_content,
            }
            materials.append(new_material)
            st.session_state.material_library[selected_type] = materials
            st.success("✅ 素材添加成功！")
            st.rerun()


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
    # 初始化日志管理器
    logger = init_logger()
    logger.info("=" * 60)
    logger.info("AI小说生成器启动")
    logger.info("=" * 60)

    init_session_state()
    render_header()

    # 记录页面访问
    logger.info("用户访问主页面")

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
    logger.info(f"[页面访问] {page}")

    if page == "🏠 首页":
        render_home()
    elif page == "➕ 创建新项目":
        render_create_project()
    elif page == "💬 对话创作":
        render_dialog_creation()
    elif page == "📚 设定库管理":
        render_setting_library()
    elif page == "📦 素材库管理":
        render_material_library()
    elif page == "✍️ 写作控制":
        render_writing_control()
    elif page == "📊 进度监控":
        render_progress_monitor()
    elif page == "📖 查看章节":
        render_chapter_view()
    elif page == "🤖 智能体管理":
        render_agent_management()
    elif page == "📋 日志查看":
        render_log_viewer()
    elif page == "⚙️ 系统设置":
        render_settings()


if __name__ == "__main__":
    main()
