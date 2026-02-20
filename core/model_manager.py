"""
AI模型管理器
支持多种大语言模型的统一调用接口
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ModelProvider(Enum):
    """模型提供商枚举"""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    MOONSHOT = "moonshot"
    DEEPSEEK = "deepseek"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """模型配置"""

    name: str
    display_name: str
    provider: ModelProvider
    api_key_env: str
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature_range: tuple = (0.0, 1.0)
    supports_system_prompt: bool = True
    description: str = ""


class ModelManager:
    """模型管理器 - 统一调用多种AI模型"""

    # 预定义的模型配置
    AVAILABLE_MODELS = {
        # Anthropic Claude 系列
        "claude-3-5-sonnet": ModelConfig(
            name="claude-3-5-sonnet-20241022",
            display_name="Claude 3.5 Sonnet",
            provider=ModelProvider.ANTHROPIC,
            api_key_env="ANTHROPIC_API_KEY",
            max_tokens=4000,
            description="Claude 3.5 Sonnet - 速度快，质量高，推荐",
        ),
        "claude-3-opus": ModelConfig(
            name="claude-3-opus-20240229",
            display_name="Claude 3 Opus",
            provider=ModelProvider.ANTHROPIC,
            api_key_env="ANTHROPIC_API_KEY",
            max_tokens=4000,
            description="Claude 3 Opus - 最高质量，适合复杂任务",
        ),
        "claude-3-haiku": ModelConfig(
            name="claude-3-haiku-20240307",
            display_name="Claude 3 Haiku",
            provider=ModelProvider.ANTHROPIC,
            api_key_env="ANTHROPIC_API_KEY",
            max_tokens=4000,
            description="Claude 3 Haiku - 速度最快，经济实惠",
        ),
        # OpenAI GPT 系列
        "gpt-4": ModelConfig(
            name="gpt-4",
            display_name="GPT-4",
            provider=ModelProvider.OPENAI,
            api_key_env="OPENAI_API_KEY",
            max_tokens=4000,
            description="GPT-4 - OpenAI旗舰模型",
        ),
        "gpt-4-turbo": ModelConfig(
            name="gpt-4-turbo-preview",
            display_name="GPT-4 Turbo",
            provider=ModelProvider.OPENAI,
            api_key_env="OPENAI_API_KEY",
            max_tokens=4000,
            description="GPT-4 Turbo - 最新版本，更强能力",
        ),
        "gpt-3.5-turbo": ModelConfig(
            name="gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo",
            provider=ModelProvider.OPENAI,
            api_key_env="OPENAI_API_KEY",
            max_tokens=4000,
            description="GPT-3.5 Turbo - 快速经济",
        ),
        # Moonshot Kimi 系列
        "kimi-2.5": ModelConfig(
            name="kimi-k2.5",
            display_name="Kimi 2.5",
            provider=ModelProvider.MOONSHOT,
            api_key_env="MOONSHOT_API_KEY",
            base_url="https://api.moonshot.cn/v1",
            max_tokens=4000,
            description="Kimi 2.5 - Moonshot最新模型，长文本能力强",
        ),
        "kimi-1.5": ModelConfig(
            name="kimi-moonshot-v1-8k",
            display_name="Kimi 1.5",
            provider=ModelProvider.MOONSHOT,
            api_key_env="MOONSHOT_API_KEY",
            base_url="https://api.moonshot.cn/v1",
            max_tokens=4000,
            description="Kimi 1.5 - 性价比高",
        ),
        # DeepSeek 系列
        "deepseek-v3": ModelConfig(
            name="deepseek-chat",
            display_name="DeepSeek V3",
            provider=ModelProvider.DEEPSEEK,
            api_key_env="DEEPSEEK_API_KEY",
            base_url="https://api.deepseek.com/v1",
            max_tokens=4000,
            description="DeepSeek V3 - 国产大模型，中文能力强",
        ),
        "deepseek-coder": ModelConfig(
            name="deepseek-coder",
            display_name="DeepSeek Coder",
            provider=ModelProvider.DEEPSEEK,
            api_key_env="DEEPSEEK_API_KEY",
            base_url="https://api.deepseek.com/v1",
            max_tokens=4000,
            description="DeepSeek Coder - 代码能力强",
        ),
    }

    def __init__(
        self, model_id: str = "claude-3-5-sonnet", custom_config: Optional[Dict] = None
    ):
        """
        初始化模型管理器

        Args:
            model_id: 预定义模型ID 或 "custom"
            custom_config: 自定义模型配置（当 model_id="custom" 时使用）
        """
        self.model_id = model_id

        if model_id == "custom" and custom_config:
            self.config = ModelConfig(
                name=custom_config.get("name", "custom-model"),
                display_name=custom_config.get("display_name", "自定义模型"),
                provider=ModelProvider.CUSTOM,
                api_key_env=custom_config.get("api_key_env", "CUSTOM_API_KEY"),
                base_url=custom_config.get("base_url"),
                max_tokens=custom_config.get("max_tokens", 4000),
                description=custom_config.get("description", "自定义模型"),
            )
        elif model_id in self.AVAILABLE_MODELS:
            self.config = self.AVAILABLE_MODELS[model_id]
        else:
            # 默认使用 Claude
            self.config = self.AVAILABLE_MODELS["claude-3-5-sonnet"]

    @classmethod
    def get_available_models(cls) -> List[Dict[str, str]]:
        """获取所有可用模型的列表"""
        return [
            {
                "id": model_id,
                "name": config.display_name,
                "description": config.description,
                "provider": config.provider.value,
            }
            for model_id, config in cls.AVAILABLE_MODELS.items()
        ]

    @classmethod
    def get_models_by_provider(cls, provider: str) -> List[Dict[str, str]]:
        """按提供商获取模型列表"""
        return [
            {
                "id": model_id,
                "name": config.display_name,
                "description": config.description,
            }
            for model_id, config in cls.AVAILABLE_MODELS.items()
            if config.provider.value == provider
        ]

    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        return os.getenv(self.config.api_key_env)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        生成文本（统一的调用接口）

        Args:
            prompt: 用户提示词
            temperature: 温度参数
            system_prompt: 系统提示词
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        provider = self.config.provider

        if provider == ModelProvider.ANTHROPIC:
            return self._call_anthropic(prompt, temperature, system_prompt, **kwargs)
        elif provider == ModelProvider.OPENAI:
            return self._call_openai(prompt, temperature, system_prompt, **kwargs)
        elif provider == ModelProvider.MOONSHOT:
            return self._call_moonshot(prompt, temperature, system_prompt, **kwargs)
        elif provider == ModelProvider.DEEPSEEK:
            return self._call_deepseek(prompt, temperature, system_prompt, **kwargs)
        elif provider == ModelProvider.CUSTOM:
            return self._call_custom(prompt, temperature, system_prompt, **kwargs)
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")

    def _call_anthropic(
        self, prompt: str, temperature: float, system_prompt: Optional[str], **kwargs
    ) -> str:
        """调用 Anthropic Claude API"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.get_api_key())

            messages = [{"role": "user", "content": prompt}]

            response = client.messages.create(
                model=self.config.name,
                max_tokens=self.config.max_tokens,
                temperature=temperature,
                messages=messages,
                system=system_prompt if system_prompt else "",
            )

            return response.content[0].text
        except ImportError:
            return f"[错误] 请安装 anthropic 包: pip install anthropic"
        except Exception as e:
            return f"[错误] Claude API调用失败: {str(e)}"

    def _call_openai(
        self, prompt: str, temperature: float, system_prompt: Optional[str], **kwargs
    ) -> str:
        """调用 OpenAI API"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.get_api_key())

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.config.name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content
        except ImportError:
            return f"[错误] 请安装 openai 包: pip install openai"
        except Exception as e:
            return f"[错误] OpenAI API调用失败: {str(e)}"

    def _call_moonshot(
        self, prompt: str, temperature: float, system_prompt: Optional[str], **kwargs
    ) -> str:
        """调用 Moonshot Kimi API"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.get_api_key(), base_url=self.config.base_url)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.config.name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content
        except ImportError:
            return f"[错误] 请安装 openai 包: pip install openai"
        except Exception as e:
            return f"[错误] Kimi API调用失败: {str(e)}"

    def _call_deepseek(
        self, prompt: str, temperature: float, system_prompt: Optional[str], **kwargs
    ) -> str:
        """调用 DeepSeek API"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.get_api_key(), base_url=self.config.base_url)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.config.name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content
        except ImportError:
            return f"[错误] 请安装 openai 包: pip install openai"
        except Exception as e:
            return f"[错误] DeepSeek API调用失败: {str(e)}"

    def _call_custom(
        self, prompt: str, temperature: float, system_prompt: Optional[str], **kwargs
    ) -> str:
        """调用自定义模型 API"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.get_api_key(), base_url=self.config.base_url)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.config.name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content
        except ImportError:
            return f"[错误] 请安装 openai 包: pip install openai"
        except Exception as e:
            return f"[错误] 自定义API调用失败: {str(e)}"


# 便捷的工厂函数
def create_model_manager(
    model_id: str = "claude-3-5-sonnet", custom_config: Optional[Dict] = None
) -> ModelManager:
    """创建模型管理器实例"""
    return ModelManager(model_id, custom_config)
