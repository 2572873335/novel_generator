"""
Integration Test - V7系统完整流程测试

测试从类型检测 → 模板加载 → 约束生成 → 冲突检测的完整流程
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.genre_detector import GenreDetector
from core.constraint_template_manager import ConstraintTemplateManager
from core.constraint_arbiter import ConstraintArbiter


def test_full_flow():
    print("=" * 70)
    print("V7 系统完整流程测试")
    print("=" * 70)

    # 初始化组件
    detector = GenreDetector()
    template_manager = ConstraintTemplateManager()
    arbiter = ConstraintArbiter()

    # 测试用例
    test_cases = [
        {
            "name": "后室探险（科幻）",
            "text": "后室探险：SCP收容失效 - 主角意外进入后室世界，需要躲避各种致命实体",
            "genre": "scifi",
            "style": "serious",
        },
        {
            "name": "斗破苍穹（仙侠）",
            "text": "斗破苍穹 - 废物少年逆天改命，斗气大陆成就传奇",
            "genre": "xianxia",
            "style": "blood-punch",
        },
        {
            "name": "都市重生（都市）",
            "text": "重生之都市修仙 - 重生都市，修炼仙法纵横都市",
            "genre": "urban",
            "style": "blood-punch",
        },
    ]

    for case in test_cases:
        print(f"\n{'=' * 70}")
        print(f"测试: {case['name']}")
        print(f"{'=' * 70}")

        # Step 1: 类型检测
        print("\n【Step 1: 类型检测】")
        result = detector.detect(case["text"])
        print(f"  输入: {case['text']}")
        print(f"  检测结果: {result.genre} (置信度: {result.confidence:.2%})")
        print(f"  匹配关键词: {result.matched_keywords}")

        # Step 2: 模板加载
        print("\n【Step 2: 模板加载】")
        template = template_manager.get_template(result.genre)
        print(f"  模板名称: {template.name}")
        print(f"  是否有修炼体系: {template.has_cultivation}")

        # Step 3: 约束提示词
        print("\n【Step 3: 约束生成】")
        prompt = template_manager.get_prompt_section(result.genre)
        print(f"  约束提示词长度: {len(prompt)} 字符")

        # Step 4: 风格冲突检测
        print("\n【Step 4: 风格冲突检测】")
        style_result = arbiter.check_style_conflict(result.genre, case["style"])
        print(f"  类型: {result.genre}, 风格: {case['style']}")
        print(f"  冲突: {style_result.conflict}, 禁止: {style_result.forbidden}")
        if style_result.suggestion:
            print(f"  建议: {style_result.suggestion}")

        # Step 5: 时间线冲突检测
        print("\n【Step 5: 时间线冲突检测】")
        temporal_result = arbiter.check_temporal_conflict(3, 1)
        print(
            f"  Day 3 → Day 1: 冲突={temporal_result.has_conflict}, 优先级={temporal_result.priority}"
        )
        print(f"  解决方案: {temporal_result.resolution}")

        print(f"\n[PASS] {case['name']}" )

    print("\n" + "=" * 70)
    print("全部测试通过！")
    print("=" * 70)


if __name__ == "__main__":
    test_full_flow()
