"""
V7 System Integrator - V7系统集成器

将新的类型检测、模板管理、约束仲裁模块集成到主系统
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional
from core.genre_detector import GenreDetector
from core.constraint_template_manager import ConstraintTemplateManager
from core.constraint_arbiter import ConstraintArbiter


class V7Integrator:
    """
    V7系统集成器

    整合类型检测、模板管理、约束仲裁功能
    """

    def __init__(self):
        self.genre_detector = GenreDetector()
        self.template_manager = ConstraintTemplateManager()
        self.arbiter = ConstraintArbiter()

    def detect_and_setup(
        self, title: str, description: str = "", genre_hint: str = None
    ) -> Dict[str, Any]:
        """
        自动检测类型并设置约束

        Args:
            title: 小说标题
            description: 小说描述
            genre_hint: 类型提示（可选）

        Returns:
            Dict包含: genre, template_name, constraints_prompt, style_check
        """
        # 1. 检测类型
        if genre_hint:
            from core.genre_detector import GenreResult

            result = GenreResult(
                genre=genre_hint,
                confidence=1.0,
                matched_keywords=[genre_hint],
                excluded_keywords=[],
                reasoning=f"使用用户指定的类型: {genre_hint}",
            )
        else:
            text = f"{title} {description}"
            result = self.genre_detector.detect(text)

        # 2. 获取模板
        template = self.template_manager.get_template(result.genre)

        # 3. 生成约束提示词
        constraints_prompt = self.template_manager.get_prompt_section(result.genre)

        # 4. 返回集成结果
        return {
            "genre": result.genre,
            "genre_confidence": result.confidence,
            "template_name": template.name if template else "通用",
            "has_cultivation": template.has_cultivation if template else False,
            "constraints_prompt": constraints_prompt,
            "matched_keywords": result.matched_keywords,
            "reasoning": result.reasoning,
        }

    def check_style_compatibility(self, genre: str, style: str) -> Dict[str, Any]:
        """
        检查类型-风格兼容性

        Args:
            genre: 类型
            style: 风格

        Returns:
            Dict包含: compatible, forbidden, suggestion
        """
        result = self.arbiter.check_style_conflict(genre, style)
        return {
            "compatible": not result.conflict,
            "forbidden": result.forbidden,
            "suggestion": result.suggestion,
            "resolution": result.resolution,
        }

    def check_timeline(self, current_day: int, new_day: int) -> Dict[str, Any]:
        """
        检查时间线一致性

        Args:
            current_day: 当前天数
            new_day: 新的天数

        Returns:
            Dict包含: valid, message, resolution
        """
        result = self.arbiter.check_temporal_conflict(current_day, new_day)
        return {
            "valid": not result.has_conflict,
            "message": result.message,
            "resolution": result.resolution,
        }


def create_integrator() -> V7Integrator:
    """创建V7集成器"""
    return V7Integrator()


if __name__ == "__main__":
    integrator = V7Integrator()

    print("=" * 60)
    print("V7 Integrator Test")
    print("=" * 60)

    # 测试1: 自动检测
    print("\n[Test 1: Auto Detect]")
    result = integrator.detect_and_setup(
        "后室探险：SCP收容失效", "主角意外进入后室世界，需要躲避各种致命实体"
    )
    print(f"Genre: {result['genre']}")
    print(f"Template: {result['template_name']}")
    print(f"Has Cultivation: {result['has_cultivation']}")

    # 测试2: 风格兼容性
    print("\n[Test 2: Style Compatibility]")
    check = integrator.check_style_compatibility("xianxia", "blood-punch")
    print(f"xianxia + blood-punch: {check}")

    check = integrator.check_style_compatibility("xianxia", "sweet")
    print(f"xianxia + sweet: {check}")

    # 测试3: 时间线检查
    print("\n[Test 3: Timeline Check]")
    check = integrator.check_timeline(3, 1)
    print(f"Day 3 -> Day 1: {check}")

    check = integrator.check_timeline(1, 5)
    print(f"Day 1 -> Day 5: {check}")
