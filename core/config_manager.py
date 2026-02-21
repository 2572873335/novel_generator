"""
配置管理器
支持从环境变量和.env文件加载配置
"""

import os
from pathlib import Path
from typing import Dict, Optional


def load_env_file(env_path: Optional[str] = None) -> Dict[str, str]:
    """
    加载 .env 文件

    Args:
        env_path: .env文件路径，默认查找项目根目录

    Returns:
        配置字典
    """
    config = {}

    # 如果未指定路径，查找项目根目录
    if env_path is None:
        # 获取当前文件所在目录 (core/)
        # config_manager.py -> core/ -> 项目根目录
        current_dir = Path(__file__).parent.parent
        env_path = current_dir / ".env"
    else:
        env_path = Path(env_path)

    # 检查文件是否存在
    if not env_path.exists():
        # 尝试查找 .env.example
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            print(f"⚠️  未找到 {env_path}，请复制 .env.example 为 .env 并配置API密钥")
        return config

    # 读取.env文件
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith("#"):
                    continue

                # 解析键值对
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # 去除引号
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        value = value[1:-1]

                    config[key] = value
                    # 同时设置到环境变量
                    os.environ[key] = value

        print(f"✅ 已加载配置文件: {env_path}")

    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")

    return config


def get_api_key(key_name: str) -> Optional[str]:
    """
    获取API密钥

    优先级：
    1. 环境变量
    2. .env文件

    Args:
        key_name: API密钥名称（如 ANTHROPIC_API_KEY）

    Returns:
        API密钥或None
    """
    # 首先检查环境变量
    value = os.getenv(key_name)
    if value:
        return value

    # 如果没有，尝试加载.env文件
    config = load_env_file()
    return config.get(key_name)


def check_api_key(key_name: str) -> bool:
    """
    检查API密钥是否已配置

    Args:
        key_name: API密钥名称

    Returns:
        是否已配置
    """
    return get_api_key(key_name) is not None


def get_available_api_keys() -> Dict[str, bool]:
    """
    获取所有可用的API密钥状态

    Returns:
        字典，包含各API密钥的配置状态
    """
    keys = {
        "ANTHROPIC_API_KEY": "Anthropic (Claude)",
        "OPENAI_API_KEY": "OpenAI (GPT)",
        "MOONSHOT_API_KEY": "Moonshot (Kimi)",
        "DEEPSEEK_API_KEY": "DeepSeek",
        "CUSTOM_API_KEY": "自定义模型",
    }

    return {name: check_api_key(key) for key, name in keys.items()}


def save_api_key(key_name: str, key_value: str, env_path: Optional[str] = None) -> bool:
    """
    保存API密钥到.env文件

    Args:
        key_name: API密钥名称
        key_value: API密钥值
        env_path: .env文件路径

    Returns:
        是否保存成功
    """
    try:
        # 确定.env文件路径
        if env_path is None:
            # config_manager.py -> core/ -> 项目根目录
            current_dir = Path(__file__).parent.parent
            env_path = current_dir / ".env"
        else:
            env_path = Path(env_path)

        # 读取现有配置
        config = {}
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.split("\n"):
                    line = line.strip()
                    if line and "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        config[k.strip()] = v.strip()

        # 更新密钥
        config[key_name] = key_value

        # 写回文件
        with open(env_path, "w", encoding="utf-8") as f:
            # 写入注释
            f.write("# AI小说生成器配置文件\n")
            f.write("# 此文件包含敏感的API密钥，请勿提交到Git仓库\n\n")

            # 写入默认模型设置
            model_settings = [
                "DEFAULT_MODEL_ID",
                "DEFAULT_TEMPERATURE",
                "DEFAULT_MAX_TOKENS",
                "CUSTOM_MODEL_NAME",
                "CUSTOM_BASE_URL",
                "CUSTOM_API_KEY_ENV",
            ]
            has_model_settings = any(k in config for k in model_settings)
            if has_model_settings:
                f.write("# ============================================\n")
                f.write("# 模型设置\n")
                f.write("# ============================================\n")
                for key in model_settings:
                    if key in config:
                        f.write(f"{key}={config[key]}\n")
                f.write("\n")

            # 按提供商分组写入API密钥
            providers = {
                "Anthropic Claude 系列": ["ANTHROPIC_API_KEY"],
                "OpenAI GPT 系列": ["OPENAI_API_KEY"],
                "Moonshot Kimi 系列": ["MOONSHOT_API_KEY"],
                "DeepSeek 系列": ["DEEPSEEK_API_KEY"],
                "自定义模型": ["CUSTOM_API_KEY"],
            }

            for provider, keys in providers.items():
                f.write(f"# ============================================\n")
                f.write(f"# {provider}\n")
                f.write(f"# ============================================\n")
                for key in keys:
                    if key in config:
                        f.write(f"{key}={config[key]}\n")
                f.write("\n")

        # 同时更新环境变量
        os.environ[key_name] = key_value

        print(f"✅ 已保存 {key_name} 到 {env_path}")
        return True

    except Exception as e:
        print(f"❌ 保存API密钥失败: {e}")
        return False


# 初始化时自动加载.env文件
_auto_loaded = False


def auto_load_env():
    """自动加载.env文件（仅在首次导入时执行）"""
    global _auto_loaded
    if not _auto_loaded:
        load_env_file()
        _auto_loaded = True


# 模块加载时自动执行
auto_load_env()
