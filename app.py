#!/usr/bin/env python3
"""
[ICON]AI[ICON] - Web UI[ICON]
[ICON] Streamlit [ICON]
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# [ICON]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# [ICON]
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
    # [ICON]
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

# [ICON]
st.set_page_config(
    page_title="AI[ICON]",
    page_icon="[BOOK]",
    layout="wide",
    initial_sidebar_state="expanded",
)

# [ICON]CSS[ICON]
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
    """[ICON]"""
    if "projects" not in st.session_state:
        st.session_state.projects = []
    if "current_project" not in st.session_state:
        st.session_state.current_project = None
    if "generation_status" not in st.session_state:
        st.session_state.generation_status = {}
    if "logs" not in st.session_state:
        st.session_state.logs = []


def get_projects():
    """[ICON]"""
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
                                    "title": data.get("title", "[ICON]"),
                                    "genre": data.get("genre", "[ICON]"),
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
    """[ICON]"""
    st.markdown('<h1 class="main-header">[BOOK] AI[ICON]</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">[ICON]Anthropic[ICON]</p>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    """[ICON]"""
    with st.sidebar:
        st.title("[ICON]")

        page = st.radio(
            "[ICON]",
            [
                "[HOUSE] [ICON]",
                "[ADD] [ICON]",
                "[CHAT] [ICON]",
                "[BOOK] [ICON]",
                "[PHASE] [ICON]",
                "[WRITE][ICON] [ICON]",
                "[STATS] [ICON]",
                "[READ] [ICON]",
                "[AI] [ICON]",
                "[LIST] [ICON]",
                "[GEAR][ICON] [ICON]",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # [ICON]
        st.subheader("[DIR] [ICON]")
        projects = get_projects()

        if projects:
            project_names = [
                f"{p['title']} ({p['completed_chapters']}/{p['total_chapters']})"
                for p in projects
            ]
            selected_project = st.selectbox(
                "[ICON]", project_names, key="sidebar_project_select"
            )
            if selected_project:
                st.session_state.current_project = projects[
                    project_names.index(selected_project)
                ]
        else:
            st.info("[ICON]")

        st.divider()

        # AI[ICON]
        st.subheader("[AI] AI[ICON]")
        config = load_env_file()
        current_model_id = config.get("DEFAULT_MODEL_ID", "claude-3-5-sonnet")

        model_manager = ModelManager()

        # [ICON]
        model_options = []
        model_ids = []

        # [ICON]
        providers = {}
        for model_id, model in model_manager.AVAILABLE_MODELS.items():
            provider = model.provider.value
            if provider not in providers:
                providers[provider] = []
            providers[provider].append((model_id, model.display_name))

        # [ICON]
        provider_names = {
            "anthropic": "[ICON] Anthropic",
            "openai": "[ICON] OpenAI",
            "moonshot": "[ICON] Moonshot",
            "deepseek": "[CRYSTAL] DeepSeek",
        }

        for provider, models in providers.items():
            provider_label = provider_names.get(provider, provider)
            for model_id, display_name in models:
                model_options.append(f"{provider_label} - {display_name}")
                model_ids.append(model_id)

        # [ICON]
        model_options.append("[GEAR][ICON] [ICON]")
        model_ids.append("custom")

        # [ICON]
        current_index = (
            model_ids.index(current_model_id) if current_model_id in model_ids else 0
        )

        # [ICON]
        selected_model_idx = st.selectbox(
            "[ICON]",
            range(len(model_options)),
            index=current_index,
            format_func=lambda x: model_options[x],
            key="sidebar_model_select",
        )

        selected_model_id = model_ids[selected_model_idx]

        # [ICON]
        if selected_model_id != current_model_id:
            if st.button(
                "[SAVE] [ICON]", use_container_width=True, key="sidebar_apply_model"
            ):
                if save_api_key("DEFAULT_MODEL_ID", selected_model_id):
                    st.success("[OK] [ICON]")
                    st.info("[ICON]")
                    logger = get_logger()
                    logger.info(f"[[ICON]] [ICON]: {selected_model_id}")
                else:
                    st.error("[FAIL] [ICON]")

        # [ICON]
        model_info = model_manager.AVAILABLE_MODELS.get(current_model_id)
        if model_info:
            st.caption(f"[ICON]: {model_info.display_name}")
        elif current_model_id == "custom":
            custom_name = config.get("CUSTOM_MODEL_NAME", "[ICON]")
            st.caption(f"[ICON]: [GEAR][ICON] {custom_name}")

        # [ICON]API[ICON]
        if model_info:
            api_key_env = model_info.api_key_env
        else:
            api_key_env = config.get("CUSTOM_API_KEY_ENV", "CUSTOM_API_KEY")

        current_key = get_api_key(api_key_env)
        if current_key:
            st.success(f"[OK] API[ICON]", icon="[KEY]")
        else:
            st.error(f"[FAIL] {api_key_env} [ICON]", icon="[WARN][ICON]")
            st.caption("[ICON]API[ICON]")

        st.divider()

        # [ICON]
        st.subheader("[ICON]")
        st.text(f"[ICON]: {os.getcwd()}")
        st.text(f"Python[ICON]: {sys.version.split()[0]}")

        return page


def render_home():
    """[ICON]"""
    st.header("[HOUSE] [ICON]AI[ICON]")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="metric-card">
            <h3>[ROCKET] [ICON]</h3>
            <p>[ICON]</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("[ICON]", use_container_width=True):
            st.session_state.page = "[ADD] [ICON]"
            st.rerun()

    with col2:
        st.markdown(
            """
        <div class="metric-card">
            <h3>[WRITE][ICON] [ICON]</h3>
            <p>AI[ICON]</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("[ICON]", use_container_width=True):
            st.session_state.page = "[WRITE][ICON] [ICON]"
            st.rerun()

    with col3:
        st.markdown(
            """
        <div class="metric-card">
            <h3>[STATS] [ICON]</h3>
            <p>[ICON]</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("[ICON]", use_container_width=True):
            st.session_state.page = "[STATS] [ICON]"
            st.rerun()

    st.divider()

    # [ICON]
    st.subheader("[STATS] [ICON]")
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
                    <p style="color: rgba(255,255,255,0.9);">[ICON]: {project["genre"]}</p>
                    <p style="color: rgba(255,255,255,0.9);">[ICON]: {project["completed_chapters"]}/{project["total_chapters"]} [ICON]</p>
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
        st.info("[ICON]'[ICON]'[ICON]")


def render_create_project():
    """[ICON]"""
    st.header("[ADD] [ICON]")

    with st.form("create_project_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("[READ] [ICON]", placeholder="[ICON]")
            genre = st.selectbox(
                "[OPEN] [ICON]",
                ["[ICON]", "[ICON]", "[ICON]", "[ICON]", "[ICON]", "[ICON]", "[ICON]", "[ICON]"],
                index=0,
            )
            target_chapters = st.number_input(
                "[ICON] [ICON]", min_value=1, max_value=100, value=10
            )

        with col2:
            words_per_chapter = st.number_input(
                "[NOTE] [ICON]", min_value=500, max_value=10000, value=3000, step=500
            )
            writing_style = st.selectbox(
                "[NEW] [ICON]", ["[ICON]", "[ICON]", "[ICON]", "[ICON]"], index=0
            )
            tone = st.selectbox(
                "[MASK] [ICON]", ["[ICON]", "[ICON]", "[ICON]", "[ICON]"], index=0
            )

        description = st.text_area(
            "[NOTE] [ICON]", placeholder="[ICON]...", height=150
        )

        # [ICON]
        with st.expander("[GEAR][ICON] [ICON]"):
            col3, col4 = st.columns(2)
            with col3:
                enable_self_review = st.checkbox("[ICON]", value=True)
                min_quality_score = st.slider("[ICON]", 1.0, 10.0, 7.0, 0.5)
            with col4:
                max_revision_attempts = st.number_input("[ICON]", 1, 10, 3)

        submitted = st.form_submit_button("[ROCKET] [ICON]", use_container_width=True)

        if submitted:
            logger = get_logger()

            if not title:
                st.error("[FAIL] [ICON]")
                logger.warning("[[ICON]] [ICON]")
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

                with st.spinner("[ICON]..."):
                    try:
                        result = create_novel(config)
                        if result["success"]:
                            st.success(
                                f"[OK] [ICON]\n\n[ICON]: {result['project_dir']}"
                            )
                            st.balloons()
                            logger.info(
                                f"[[ICON]] [ICON] - [ICON]: {result['project_dir']}"
                            )
                        else:
                            st.error(f"[FAIL] [ICON]: {result.get('error', '[ICON]')}")
                            logger.error(
                                f"[[ICON]] [ICON] - {result.get('error', '[ICON]')}"
                            )
                    except Exception as e:
                        st.error(f"[FAIL] [ICON]: {str(e)}")
                        logger.log_error_with_traceback(e, "[ICON]")


def render_writing_control():
    """[ICON]"""
    st.header("[WRITE][ICON] [ICON]")

    # [ICON]
    projects = get_projects()
    if not projects:
        st.warning("[WARN][ICON] [ICON]")
        return

    project_names = [
        f"{p['title']} ({p['completed_chapters']}/{p['total_chapters']})"
        for p in projects
    ]
    selected = st.selectbox("[ICON]", project_names)

    if selected:
        project = projects[project_names.index(selected)]

        # [ICON]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("[ICON]", project["total_chapters"])
        with col2:
            st.metric("[ICON]", project["completed_chapters"])
        with col3:
            remaining = project["total_chapters"] - project["completed_chapters"]
            st.metric("[ICON]", remaining)
        with col4:
            progress = (
                (project["completed_chapters"] / project["total_chapters"] * 100)
                if project["total_chapters"] > 0
                else 0
            )
            st.metric("[ICON]", f"{progress:.1f}%")

        st.divider()

        # [ICON]
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("[RUN][ICON] [ICON]", use_container_width=True):
                with st.spinner("[ICON]..."):
                    try:
                        # [ICON]
                        st.success("[ICON]")
                        st.info("[ICON]Writer Agent[ICON]")
                    except Exception as e:
                        st.error(f"[ICON]: {str(e)}")

        with col2:
            if st.button("[SEARCH] [ICON]", use_container_width=True):
                st.info("[ICON]Reviewer Agent[ICON]")

        with col3:
            if st.button("[PHASE] [ICON]", use_container_width=True):
                st.info("[ICON]")

        # [ICON]
        st.subheader("[NOTE] [ICON]")
        log_container = st.container()
        with log_container:
            if st.session_state.logs:
                for log in reversed(st.session_state.logs[-20:]):
                    st.text(log)
            else:
                st.info("[ICON]")


def render_progress_monitor():
    """[ICON]"""
    st.header("[STATS] [ICON]")

    projects = get_projects()
    if not projects:
        st.warning("[WARN][ICON] [ICON]")
        return

    # [ICON]
    for project in projects:
        with st.expander(f"[BOOK] {project['title']}", expanded=True):
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

            # [ICON]
            pm = ProgressManager(project["path"])
            progress_data = pm.load_progress()

            if progress_data and progress_data.chapters:
                st.subheader("[ICON]")

                # [ICON]
                cols = st.columns(3)
                for idx, chapter in enumerate(progress_data.chapters):
                    with cols[idx % 3]:
                        status_icon = {
                            "pending": "⏳",
                            "writing": "[WRITE][ICON]",
                            "reviewing": "[ICON]",
                            "completed": "[OK]",
                            "revision_needed": "[TOOL]",
                        }.get(chapter.status, "[ICON]")

                        status_class = f"status-{chapter.status}"

                        st.markdown(
                            f"""
                        <div class="chapter-item">
                            <strong>{status_icon} [ICON]{chapter.chapter_number}[ICON]</strong><br>
                            <span class="{status_class}">{chapter.status}</span><br>
                            {f"[ICON]: {chapter.word_count}" if chapter.word_count > 0 else ""}
                            {f"<br>[ICON]: {chapter.quality_score:.1f}" if chapter.quality_score > 0 else ""}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )


def render_chapter_view():
    """[ICON]"""
    st.header("[READ] [ICON]")

    projects = get_projects()
    if not projects:
        st.warning("[WARN][ICON] [ICON]")
        return

    # [ICON]
    project_names = [p["title"] for p in projects]
    selected_project = st.selectbox("[ICON]", project_names)

    if selected_project:
        project = projects[project_names.index(selected_project)]
        chapters_dir = Path(project["path"]) / "chapters"

        if chapters_dir.exists():
            chapter_files = sorted([f for f in chapters_dir.glob("chapter-*.md")])

            if chapter_files:
                # [ICON]
                chapter_options = [
                    f"[ICON]{int(f.stem.split('-')[1])}[ICON]" for f in chapter_files
                ]
                selected_chapter = st.selectbox("[ICON]", chapter_options)

                if selected_chapter:
                    chapter_num = int(
                        selected_chapter.replace("[ICON]", "").replace("[ICON]", "")
                    )
                    chapter_file = chapters_dir / f"chapter-{chapter_num:03d}.md"

                    if chapter_file.exists():
                        with open(chapter_file, "r", encoding="utf-8") as f:
                            content = f.read()

                        # [ICON]
                        st.markdown("---")
                        st.markdown(content)
                        st.markdown("---")

                        # [ICON]
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="[ICON] [ICON]",
                                data=content,
                                file_name=f"{selected_chapter}.md",
                                mime="text/markdown",
                            )
            else:
                st.info("[ICON]")
        else:
            st.info("[ICON]")


def render_settings():
    """[ICON]"""
    st.header("[GEAR][ICON] [ICON]")

    st.subheader("[ART] [ICON]")

    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox("[ICON]", ["[ICON]", "[ICON]"], index=0)
    with col2:
        language = st.selectbox("[ICON]", ["[ICON]", "English"], index=0)

    st.subheader("[AI] AI[ICON]")

    # [ICON]
    model_manager = ModelManager()
    available_models = model_manager.get_available_models()

    # [ICON]
    providers = {}
    for model in available_models:
        provider = model["provider"]
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)

    # [ICON]
    provider_list = ["anthropic", "openai", "moonshot", "deepseek", "custom"]
    provider_labels = [
        "[ICON] Anthropic (Claude)",
        "[ICON] OpenAI (GPT)",
        "[ICON] Moonshot (Kimi)",
        "[CRYSTAL] DeepSeek",
        "[GEAR][ICON] [ICON]",
    ]

    # [ICON]
    config = load_env_file()
    saved_model_id = config.get("DEFAULT_MODEL_ID", "claude-3-5-sonnet")

    # [ICON]ID[ICON]
    if saved_model_id == "custom":
        default_provider = "custom"
    elif saved_model_id in model_manager.AVAILABLE_MODELS:
        default_provider = model_manager.AVAILABLE_MODELS[saved_model_id].provider.value
    else:
        default_provider = "anthropic"

    # [ICON]
    default_provider_idx = (
        provider_list.index(default_provider)
        if default_provider in provider_list
        else 0
    )

    selected_provider_idx = st.selectbox(
        "[ICON]",
        range(len(provider_list)),
        index=default_provider_idx,
        format_func=lambda x: provider_labels[x],
    )
    selected_provider = provider_list[selected_provider_idx]

    # [ICON]
    custom_model_name = ""
    custom_base_url = ""
    custom_api_key_env = "CUSTOM_API_KEY"
    selected_model_id = ""
    selected_model = None
    api_key_env = "API_KEY"

    if selected_provider == "custom":
        # [ICON]
        st.markdown("#### [GEAR][ICON] [ICON]")
        custom_model_name = config.get("CUSTOM_MODEL_NAME", "")
        custom_base_url = config.get("CUSTOM_BASE_URL", "")
        custom_api_key_env = config.get("CUSTOM_API_KEY_ENV", "CUSTOM_API_KEY")

        custom_model_name = st.text_input(
            "[ICON]", value=custom_model_name, placeholder="[ICON]: my-custom-model"
        )
        custom_base_url = st.text_input(
            "API[ICON]URL",
            value=custom_base_url,
            placeholder="[ICON]: https://api.custom.com/v1",
        )
        custom_api_key_env = st.text_input(
            "API[ICON]",
            value=custom_api_key_env,
            placeholder="[ICON]: CUSTOM_API_KEY",
        )

        selected_model_id = "custom"
        api_key_env = custom_api_key_env
    else:
        # [ICON]
        provider_models = providers[selected_provider]
        model_options = [m["name"] for m in provider_models]
        model_ids_list = [m["id"] for m in provider_models]

        # [ICON]ID[ICON]
        default_model_idx = 0
        if saved_model_id in model_ids_list:
            default_model_idx = model_ids_list.index(saved_model_id)

        selected_model_idx = st.selectbox(
            "[ICON]",
            range(len(model_options)),
            index=default_model_idx,
            format_func=lambda x: model_options[x],
        )

        selected_model_id = model_ids_list[selected_model_idx]
        selected_model = model_manager.AVAILABLE_MODELS.get(selected_model_id)

        if selected_model:
            st.info(f"[LIST] {selected_model.description}")
            api_key_env = selected_model.api_key_env

    # API[ICON]
    col1, col2 = st.columns([3, 1])
    with col1:
        # [ICON]
        current_key = get_api_key(api_key_env)
        api_key_placeholder = f"[ICON] {api_key_env}"
        if current_key:
            api_key_placeholder = f"{api_key_env} [ICON] ([ICON])"

        api_key = st.text_input(
            f"{api_key_env} [ICON]",
            type="password",
            placeholder=api_key_placeholder,
        )
    with col2:
        # [ICON]
        if current_key:
            st.success("[OK] [ICON]")
        else:
            st.warning("[FAIL] [ICON]")

    # Temperature[ICON]
    # [ICON]
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
            help="[ICON]",
        )
    with col2:
        max_tokens = st.number_input(
            "[ICON]Token[ICON]",
            min_value=1000,
            max_value=8000,
            value=default_max_tokens,
            step=500,
            help="[ICON]token[ICON]",
        )

    # [ICON]
    if st.button("[ICON] [ICON]", use_container_width=True):
        with st.spinner("[ICON]..."):
            try:
                if selected_model_id == "custom":
                    test_manager = create_model_manager(
                        "custom",
                        {
                            "name": custom_model_name
                            if custom_model_name
                            else "custom-model",
                            "display_name": "[ICON]",
                            "api_key_env": api_key_env,
                            "base_url": custom_base_url if custom_base_url else None,
                        },
                    )
                else:
                    test_manager = create_model_manager(selected_model_id)

                # [ICON]
                test_prompt = "[ICON]"
                result = test_manager.generate(
                    test_prompt, temperature=0.7, system_prompt="[ICON]AI[ICON]"
                )

                if result.startswith("[[ICON]]"):
                    st.error(result)
                else:
                    st.success("[OK] [ICON]")
                    with st.expander("[ICON]"):
                        st.markdown(f"**[ICON]:** {test_prompt}")
                        st.markdown(f"**[ICON]:** {result}")
            except Exception as e:
                st.error(f"[FAIL] [ICON]: {str(e)}")

    st.divider()

    st.subheader("[SAVE] [ICON]")

    projects_dir = st.text_input("[ICON]", value="novels")
    auto_save = st.checkbox("[ICON]", value=True)

    # [ICON]
    if st.button("[SAVE] [ICON]", use_container_width=True):
        logger = get_logger()
        logger.info(f"[[ICON]] [ICON] - [ICON]: {selected_model_id}")

        success_count = 0
        error_messages = []

        # [ICON]API[ICON]
        if api_key and api_key_env:
            if save_api_key(api_key_env, api_key):
                success_count += 1
                st.success(f"[OK] {api_key_env} [ICON] .env [ICON]")
                logger.log_api_key_save(api_key_env, True)
            else:
                error_messages.append(f"[ICON] {api_key_env} [ICON]")
                logger.log_api_key_save(api_key_env, False)

        # [ICON]
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
            # [ICON]
            save_api_key("DEFAULT_MODEL_ID", selected_model_id)
            success_count += 1
            logger.info(f"[[ICON]] [ICON]: {custom_model_name}")
        else:
            # [ICON]
            save_api_key("DEFAULT_MODEL_ID", selected_model_id)
            success_count += 1
            st.success(f"[OK] [ICON]: {selected_model_id}")
            logger.log_model_selection(
                selected_model_id, selected_provider, temperature, max_tokens
            )

        # [ICON]token[ICON]
        save_api_key("DEFAULT_TEMPERATURE", str(temperature))
        save_api_key("DEFAULT_MAX_TOKENS", str(int(max_tokens)))
        success_count += 2

        if success_count > 0 and not error_messages:
            st.success(f"[OK] [ICON] {success_count} [ICON]")
            st.info("[FILE] [ICON] .env [ICON]")
            logger.info(f"[[ICON]] [ICON] {success_count} [ICON]")
        elif error_messages:
            st.error("[FAIL] [ICON]" + "; ".join(error_messages))
            logger.error(f"[[ICON]] [ICON]: {'; '.join(error_messages)}")


def render_log_viewer():
    """[ICON]"""
    st.header("[LIST] [ICON]")

    logger = get_logger()

    # [ICON]
    log_files = logger.get_log_files()

    if not log_files:
        st.warning("[ICON]")
        return

    # [ICON]
    log_file_names = [f.name for f in log_files]
    selected_log = st.selectbox("[ICON]", log_file_names)

    if selected_log:
        log_path = logger.log_dir / selected_log

        # [ICON]
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log_content = f.read()

            # [ICON]
            lines = log_content.split("\n")
            st.info(f"[FILE] [ICON] {len(lines)} [ICON]")

            # [ICON]
            col1, col2, col3 = st.columns(3)
            with col1:
                show_info = st.checkbox("[ICON] INFO", value=True)
            with col2:
                show_warning = st.checkbox("[ICON] WARNING", value=True)
            with col3:
                show_error = st.checkbox("[ICON] ERROR", value=True)

            # [ICON]
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

            # [ICON]
            st.code("\n".join(filtered_lines), language="text")

            # [ICON]
            st.download_button(
                label="[ICON] [ICON]",
                data=log_content,
                file_name=selected_log,
                mime="text/plain",
            )

        except Exception as e:
            st.error(f"[ICON]: {e}")


def render_dialog_creation():
    """[ICON]"""
    st.header("[CHAT] [ICON]")
    st.markdown("[ICON]AI[ICON]")

    # [ICON]
    if "dialog_messages" not in st.session_state:
        st.session_state.dialog_messages = []
    if "dialog_stage" not in st.session_state:
        st.session_state.dialog_stage = "basic_info"
    if "dialog_config" not in st.session_state:
        st.session_state.dialog_config = {}

    # [ICON]
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.dialog_messages:
            if msg["role"] == "assistant":
                st.chat_message("assistant").markdown(msg["content"])
            else:
                st.chat_message("user").markdown(msg["content"])

    # [ICON]
    if st.session_state.dialog_stage == "basic_info":
        if not st.session_state.dialog_messages:
            welcome_msg = """[ICON]AI[ICON]

[ICON]
- [ICON]
- [ICON]
- [ICON]
- [ICON]
- [ICON]
- [ICON]"""
            st.session_state.dialog_messages.append(
                {"role": "assistant", "content": welcome_msg}
            )
            st.rerun()

    # [ICON]
    if prompt := st.chat_input("[ICON]..."):
        st.session_state.dialog_messages.append({"role": "user", "content": prompt})

        # [ICON]
        if st.session_state.dialog_stage == "basic_info":
            if "[ICON]" not in st.session_state.dialog_config:
                st.session_state.dialog_config["[ICON]"] = prompt
                response = f"[ICON]{prompt}[ICON]"
            elif "[ICON]" not in st.session_state.dialog_config:
                st.session_state.dialog_config["[ICON]"] = prompt
                response = f"'{prompt}'[ICON]"
            elif "[ICON]" not in st.session_state.dialog_config:
                st.session_state.dialog_config["[ICON]"] = prompt
                response = "[ICON]"
            elif "[ICON]" not in st.session_state.dialog_config:
                try:
                    st.session_state.dialog_config["[ICON]"] = int(prompt)
                except:
                    st.session_state.dialog_config["[ICON]"] = 10
                response = f"[ICON]{st.session_state.dialog_config['[ICON]']}[ICON]"
            elif "[ICON]" not in st.session_state.dialog_config:
                st.session_state.dialog_config["[ICON]"] = prompt
                response = (
                    "[ICON]"
                )
            elif "[ICON]" not in st.session_state.dialog_config:
                st.session_state.dialog_config["[ICON]"] = prompt
                st.session_state.dialog_stage = "outline"
                response = f"""[ICON]

[PIN] **[ICON]**
- [ICON]{st.session_state.dialog_config.get("[ICON]", "[ICON]")}
- [ICON]{st.session_state.dialog_config.get("[ICON]", "[ICON]")}
- [ICON]{st.session_state.dialog_config.get("[ICON]", "[ICON]")}
- [ICON]{st.session_state.dialog_config.get("[ICON]", "[ICON]")}
- [ICON]{st.session_state.dialog_config.get("[ICON]", "[ICON]")}
- [ICON]{st.session_state.dialog_config.get("[ICON]", "[ICON]")}

[ICON]
1. [ICON]
2. [ICON]
3. [ICON]
4. [ICON]

[ICON]"""
            else:
                response = "[ICON]"

        elif st.session_state.dialog_stage == "outline":
            response = f"[ICON]'{prompt}'[ICON]"

        else:
            response = f"[ICON]"

        st.session_state.dialog_messages.append(
            {"role": "assistant", "content": response}
        )
        st.rerun()

    # [ICON]
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("[SYNC] [ICON]", use_container_width=True):
            st.session_state.dialog_messages = []
            st.session_state.dialog_stage = "basic_info"
            st.session_state.dialog_config = {}
            st.rerun()
    with col2:
        if st.button("[LIST] [ICON]", use_container_width=True):
            st.json(st.session_state.dialog_config)
    with col3:
        if st.button("[OK] [ICON]", use_container_width=True):
            if st.session_state.dialog_config:
                config = {
                    "title": st.session_state.dialog_config.get("[ICON]", "[ICON]"),
                    "genre": st.session_state.dialog_config.get("[ICON]", "[ICON]"),
                    "target_chapters": st.session_state.dialog_config.get("[ICON]", 10),
                    "description": st.session_state.dialog_config.get("[ICON]", ""),
                }
                st.session_state.page = "[ADD] [ICON]"
                st.session_state.prefilled_config = config
                st.rerun()


def render_setting_library():
    """[ICON]"""
    st.header("[BOOK] [ICON]")
    st.markdown("[ICON]")

    # [ICON]
    if "setting_library" not in st.session_state:
        st.session_state.setting_library = {
            "[ICON]": {},
            "[ICON]": {},
            "[ICON]": {},
            "[ICON]": {},
        }

    # [ICON]
    col1, col2 = st.columns([3, 1])
    with col1:
        categories = list(st.session_state.setting_library.keys())
        selected_category = st.selectbox("[ICON]", categories)
    with col2:
        if st.button("[ADD] [ICON]", use_container_width=True):
            st.session_state.show_new_category = True

    # [ICON]
    if st.session_state.get("show_new_category", False):
        with st.form("new_category_form"):
            new_cat_name = st.text_input("[ICON]")
            submitted = st.form_submit_button("[ICON]")
            if submitted and new_cat_name:
                st.session_state.setting_library[new_cat_name] = {}
                st.session_state.show_new_category = False
                st.rerun()

    st.divider()

    # [ICON]
    st.subheader(f"[READ] {selected_category}")

    current_settings = st.session_state.setting_library.get(selected_category, {})

    # [ICON]
    def display_setting_tree(settings: dict, path: list, level: int = 0):
        for name, content in settings.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            indent = "[ICON]" * level
            with col1:
                if isinstance(content, dict):
                    with st.expander(f"{indent}[DIR] {name}", expanded=False):
                        display_setting_tree(content, path + [name], level + 1)
                else:
                    st.markdown(
                        f"{indent}[FILE] **{name}**: {content[:50]}..."
                        if len(str(content)) > 50
                        else f"{indent}[FILE] **{name}**: {content}"
                    )

    display_setting_tree(current_settings, [])

    st.divider()

    # [ICON]
    st.subheader("[ADD] [ICON]")

    # [ICON]
    parent_options = ["[[ICON]]"]

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
            parent_path = st.selectbox("[ICON]", parent_options)
            setting_name = st.text_input("[ICON]")
        with col2:
            setting_type = st.selectbox("[ICON]", ["[ICON]", "[ICON]"])
            setting_content = st.text_area("[ICON]", height=100)

        submitted = st.form_submit_button("[ICON]")
        if submitted and setting_name:
            if setting_type == "[ICON]":
                new_content = {}
            else:
                new_content = setting_content

            # [ICON]
            if parent_path == "[[ICON]]":
                current_settings[setting_name] = new_content
            else:
                path_parts = parent_path.split("/")
                target = current_settings
                for part in path_parts:
                    if part in target and isinstance(target[part], dict):
                        target = target[part]
                target[setting_name] = new_content

            st.session_state.setting_library[selected_category] = current_settings
            st.success(f"[OK] [ICON]: {setting_name}")
            st.rerun()


def render_material_library():
    """[ICON]"""
    st.header("[PHASE] [ICON]")
    st.markdown("[ICON]")

    # [ICON]
    if "material_library" not in st.session_state:
        st.session_state.material_library = {
            "[ICON]": [],
            "[ICON]": [],
            "[ICON]": [],
            "[ICON]": [],
            "[ICON]": [],
        }

    # [ICON]
    col1, col2 = st.columns([3, 1])
    with col1:
        material_types = list(st.session_state.material_library.keys())
        selected_type = st.selectbox("[ICON]", material_types)
    with col2:
        if st.button("[ADD] [ICON]", use_container_width=True):
            st.session_state.show_new_material_type = True

    # [ICON]
    if st.session_state.get("show_new_material_type", False):
        with st.form("new_material_type_form"):
            new_type_name = st.text_input("[ICON]")
            submitted = st.form_submit_button("[ICON]")
            if submitted and new_type_name:
                st.session_state.material_library[new_type_name] = []
                st.session_state.show_new_material_type = False
                st.rerun()

    st.divider()

    # [ICON]
    st.subheader(f"[NOTE] {selected_type}")
    materials = st.session_state.material_library.get(selected_type, [])

    if materials:
        for idx, material in enumerate(materials):
            with st.expander(f"[ICON] #{idx + 1}: {material.get('title', '[ICON]')}"):
                st.markdown(f"**[ICON]**: {', '.join(material.get('tags', []))}")
                st.markdown(f"**[ICON]**:")
                st.text(material.get("content", ""))

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"[ICON] [ICON]", key=f"edit_{selected_type}_{idx}"):
                        st.session_state.editing_material = (selected_type, idx)
                with col2:
                    if st.button(f"[TRASH][ICON] [ICON]", key=f"del_{selected_type}_{idx}"):
                        materials.pop(idx)
                        st.session_state.material_library[selected_type] = materials
                        st.rerun()
    else:
        st.info("[ICON]")

    st.divider()

    # [ICON]
    st.subheader("[ADD] [ICON]")
    with st.form("add_material_form"):
        material_title = st.text_input("[ICON]")
        material_tags = st.text_input("[ICON]")
        material_content = st.text_area("[ICON]", height=150)

        submitted = st.form_submit_button("[ICON]")
        if submitted and material_content:
            new_material = {
                "title": material_title or f"[ICON] {len(materials) + 1}",
                "tags": [t.strip() for t in material_tags.split(",")]
                if material_tags
                else [],
                "content": material_content,
            }
            materials.append(new_material)
            st.session_state.material_library[selected_type] = materials
            st.success("[OK] [ICON]")
            st.rerun()


def render_agent_management():
    """[ICON]"""
    st.header("[AI] [ICON]")

    # [ICON] AgentManager
    agent_manager = AgentManager(".")

    # [ICON]
    available_agents = agent_manager.get_available_agents()

    st.subheader("[LIST] [ICON]")

    # [ICON]
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

    # [ICON]
    st.subheader("[ROCKET] [ICON]")
    st.info("[ICON]")

    # [ICON]
    projects = get_projects()
    if projects:
        project_names = [p["title"] for p in projects]
        selected_project = st.selectbox(
            "[ICON]", project_names, key="agent_project_select"
        )

        if selected_project:
            project = projects[project_names.index(selected_project)]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("[ICON]", project["title"])
            with col2:
                st.metric(
                    "[ICON]",
                    f"{project['completed_chapters']}/{project['total_chapters']}",
                )
            with col3:
                progress = (
                    (project["completed_chapters"] / project["total_chapters"] * 100)
                    if project["total_chapters"] > 0
                    else 0
                )
                st.metric("[ICON]", f"{progress:.1f}%")

            if st.button("[RUN][ICON] [ICON]", use_container_width=True, type="primary"):
                with st.spinner("[ICON]..."):
                    # [ICON]
                    progress_file = Path(project["path"]) / "novel-progress.txt"
                    if progress_file.exists():
                        with open(progress_file, "r", encoding="utf-8") as f:
                            config = json.load(f)

                        # [ICON]
                        result = agent_manager.run_coordinator_workflow(config)

                        if result["success"]:
                            st.success(
                                f"[OK] [ICON] {result['total_steps']} [ICON]"
                            )

                            # [ICON]
                            with st.expander("[ICON]"):
                                for step_result in result["results"]:
                                    st.markdown(f"**{step_result['step']}**")
                                    st.text(
                                        step_result["result"]["result"][:200] + "..."
                                    )
                        else:
                            st.error("[FAIL] [ICON]")
    else:
        st.warning("[WARN][ICON] [ICON]")

    st.divider()

    # [ICON]
    st.subheader("[GEAR][ICON] [ICON]")
    st.info("[ICON]")

    if available_agents:
        agent_names = [a["name"] for a in available_agents]
        selected_agents = st.multiselect("[ICON]", agent_names)

        if selected_agents:
            st.write("[ICON]:")
            for idx, agent in enumerate(selected_agents, 1):
                st.write(f"{idx}. {agent}")

            task_description = st.text_area(
                "[ICON]", placeholder="[ICON]..."
            )

            if st.button("[RUN][ICON] [ICON]", use_container_width=True):
                if task_description:
                    with st.spinner("[ICON]..."):
                        # [ICON]
                        workflow = agent_manager.create_agent_workflow(
                            selected_agents, {"task": task_description}
                        )
                        result = agent_manager.execute_workflow(workflow)

                        if result["success"]:
                            st.success(f"[OK] [ICON] {len(selected_agents)} [ICON]")

                            # [ICON]
                            for idx, res in enumerate(result["results"], 1):
                                with st.expander(f"[ICON] {idx}: {res['agent']}"):
                                    st.text(res["result"])
                        else:
                            st.error("[FAIL] [ICON]")
                else:
                    st.error("[ICON]")


def main():
    """[ICON]"""
    # [ICON]
    logger = init_logger()
    logger.info("=" * 60)
    logger.info("AI[ICON]")
    logger.info("=" * 60)

    init_session_state()
    render_header()

    # [ICON]
    logger.info("[ICON]")

    # [ICON]
    if "page" in st.session_state:
        current_page = st.session_state.page
        del st.session_state.page  # [ICON]
    else:
        current_page = None

    page = render_sidebar()

    # [ICON]
    if current_page:
        page = current_page

    # [ICON]
    logger.info(f"[[ICON]] {page}")

    if page == "[HOUSE] [ICON]":
        render_home()
    elif page == "[ADD] [ICON]":
        render_create_project()
    elif page == "[CHAT] [ICON]":
        render_dialog_creation()
    elif page == "[BOOK] [ICON]":
        render_setting_library()
    elif page == "[PHASE] [ICON]":
        render_material_library()
    elif page == "[WRITE][ICON] [ICON]":
        render_writing_control()
    elif page == "[STATS] [ICON]":
        render_progress_monitor()
    elif page == "[READ] [ICON]":
        render_chapter_view()
    elif page == "[AI] [ICON]":
        render_agent_management()
    elif page == "[LIST] [ICON]":
        render_log_viewer()
    elif page == "[GEAR][ICON] [ICON]":
        render_settings()


if __name__ == "__main__":
    main()
