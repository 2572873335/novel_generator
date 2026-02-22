"""
Genre Detector - 类型检测器

基于故事描述/标题自动识别网文类型

支持的类型：
- scifi: 科幻/后室/SCP/末世
- xianxia: 仙侠/玄幻/修练
- urban: 都市/重生/总裁
- suspense: 悬疑/推理/惊悚
- game: 游戏/副本/系统
- historical: 历史/穿越/朝堂
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# 类型特征签名
GENRE_SIGNATURES = {
    "scifi": {
        "keywords": [
            "科幻",
            "后室",
            "SCP",
            "收容",
            "实体",
            "末世",
            "废土",
            "辐射",
            "变异",
            "赛博",
            "赛博朋克",
            "人工智能",
            "AI",
            "太空",
            "星际",
            "维度",
            "平行世界",
            "Backrooms",
            "杏仁水",
            "M.E.G",
            "基金会",
        ],
        "exclude_keywords": ["修仙", "灵气", "金丹", "元婴", "境界", "宗门"],
        "weight": 1.0,
    },
    "xianxia": {
        "keywords": [
            "仙侠",
            "修仙",
            "玄幻",
            "修真",
            "修炼",
            "灵气",
            "法力",
            "金丹",
            "元婴",
            "化神",
            "渡劫",
            "天劫",
            "境界",
            "宗门",
            "功法",
            "秘籍",
            "剑道",
            "刀道",
            "炼丹",
            "炼器",
            "阵法",
            "灵根",
            "体质",
            "血脉",
            "神体",
            "帝族",
            "世家",
            "王朝",
            "斗破",
            "斗气",
            "苍穹",
            "剑来",
            "雪中",
            "悍刀行",
            "凡人",
            "凡人修仙传",
            "完美世界",
            "万古神帝",
            "全职法师",
            "一念永恒",
            "星辰变",
            "盘龙",
            "大主宰",
        ],
        "exclude_keywords": ["后室", "SCP", "收容", "实体", "基金会"],
        "weight": 1.0,
    },
    "urban": {
        "keywords": [
            "都市",
            "重生",
            "总裁",
            "豪门",
            "富二代",
            "美女",
            "校花",
            "杀手",
            "特工",
            "医生",
            "律师",
            "首富",
            "商业",
            "创业",
            "炒股",
            "房地产",
            "互联网",
            "明星",
            "娱乐圈",
            "退役",
            "兵王",
            "赘婿",
            "上门女婿",
            "神医",
            "风水",
            "相术",
        ],
        "exclude_keywords": ["修仙", "灵气", "境界", "宗门"],
        "weight": 1.0,
    },
    "suspense": {
        "keywords": [
            "悬疑",
            "推理",
            "侦探",
            "惊悚",
            "恐怖",
            "鬼魂",
            "灵异",
            "凶杀",
            "破案",
            "FBI",
            "犯罪",
            "杀手",
            "连环杀手",
            "密室",
            "不在场证明",
            "不在场",
            "犯罪心理学",
            "侧写",
            "十日终焉",
            "死亡游戏",
            "无限流",
        ],
        "exclude_keywords": [],
        "weight": 1.0,
    },
    "game": {
        "keywords": [
            "游戏",
            "系统",
            "副本",
            "任务",
            "升级",
            "装备",
            "技能",
            "转职",
            "公会",
            "NPC",
            "玩家",
            "游戏世界",
            "虚拟现实",
            "VR",
            "全息",
            "电竞",
            "职业选手",
            "王者荣耀",
            "LOL",
            "DOTA",
            "魔兽世界",
            "我的世界",
            "明日方舟",
            "舟游",
        ],
        "exclude_keywords": [],
        "weight": 1.0,
    },
    "historical": {
        "keywords": [
            "历史",
            "穿越",
            "古代",
            "朝堂",
            "权谋",
            "争霸",
            "帝王",
            "皇帝",
            "太子",
            "王爷",
            "大臣",
            "科举",
            "武侠",
            "江湖",
            "武林",
            "门派",
            "帮派",
            "大唐",
            "大秦",
            "大明",
            "三国",
            "商朝",
            "周朝",
            "春秋",
            "战国",
        ],
        "exclude_keywords": ["都市", "重生", "总裁"],
        "weight": 1.0,
    },
}


@dataclass
class GenreResult:
    """类型检测结果"""

    genre: str
    confidence: float
    matched_keywords: List[str]
    excluded_keywords: List[str]
    reasoning: str


class GenreDetector:
    """
    类型检测器

    根据故事描述、标题等信息自动识别网文类型
    """

    def __init__(self):
        self.signatures = GENRE_SIGNATURES
        self.min_confidence = 0.3  # 最低置信度阈值

    def detect(self, text: str) -> GenreResult:
        """
        检测文本的类型

        Args:
            text: 故事描述、标题、简介等

        Returns:
            GenreResult: 检测结果
        """
        text = text.lower()

        scores: Dict[str, float] = {}
        matched: Dict[str, List[str]] = {}
        excluded: Dict[str, List[str]] = {}

        for genre, sig in self.signatures.items():
            score = 0.0
            matched_list = []
            excluded_list = []

            # 匹配正向关键词
            for keyword in sig["keywords"]:
                if keyword.lower() in text or keyword in text:
                    score += sig["weight"]
                    matched_list.append(keyword)

            # 匹配排除关键词
            for keyword in sig.get("exclude_keywords", []):
                if keyword.lower() in text or keyword in text:
                    score -= sig["weight"] * 0.5
                    excluded_list.append(keyword)

            scores[genre] = score
            matched[genre] = matched_list
            excluded[genre] = excluded_list

        # 找出最高分
        if not scores or max(scores.values()) == 0:
            # 没有匹配，返回默认类型
            return GenreResult(
                genre="general",
                confidence=0.0,
                matched_keywords=[],
                excluded_keywords=[],
                reasoning="未检测到明确类型特征，使用默认类型",
            )

        # 归一化置信度
        max_score = max(scores.values())
        total_score = sum(scores.values())

        # 计算置信度（相对于最高分的比例）
        if max_score > 0:
            confidence = max_score / (max_score + 1.0)  # 平滑处理
        else:
            confidence = 0.0

        # 找出最高分的类型
        if scores:
            best_genre = max(scores.items(), key=lambda x: x[1])[0]
        else:
            best_genre = "general"
        best_matched = matched.get(best_genre, [])
        best_excluded = excluded.get(best_genre, [])

        # 生成推理
        reasoning = self._generate_reasoning(
            best_genre, best_matched, best_excluded, scores
        )

        return GenreResult(
            genre=best_genre,
            confidence=confidence,
            matched_keywords=best_matched,
            excluded_keywords=best_excluded,
            reasoning=reasoning,
        )

    def detect_from_outline(self, outline: str) -> GenreResult:
        """
        从大纲中检测类型

        Args:
            outline: 故事大纲

        Returns:
            GenreResult: 检测结果
        """
        return self.detect(outline)

    def detect_from_title(self, title: str) -> GenreResult:
        """
        从标题中检测类型

        Args:
            title: 故事标题

        Returns:
            GenreResult: 检测结果
        """
        return self.detect(title)

    def _generate_reasoning(
        self,
        genre: str,
        matched: List[str],
        excluded: List[str],
        scores: Dict[str, float],
    ) -> str:
        """生成推理说明"""

        reasoning = f"检测为【{genre}】类型"

        if matched:
            reasoning += f"，匹配关键词：{', '.join(matched[:5])}"

        if excluded:
            reasoning += f"，排除关键词：{', '.join(excluded[:3])}"

        # 显示其他类型的得分
        other_scores = {k: v for k, v in scores.items() if k != genre and v > 0}
        if other_scores:
            sorted_scores = sorted(
                other_scores.items(), key=lambda x: x[1], reverse=True
            )
            others = [f"{k}({v:.2f})" for k, v in sorted_scores[:2]]
            if others:
                reasoning += f"，备选：{', '.join(others)}"

        return reasoning

    def get_template_name(self, genre: str) -> str:
        """
        获取类型对应的模板名称

        Args:
            genre: 检测出的类型

        Returns:
            str: 模板名称
        """
        template_map = {
            "scifi": "scifi",
            "xianxia": "xianxia",
            "urban": "urban",
            "suspense": "suspense",
            "game": "game",
            "historical": "historical",
            "general": "general",
        }
        return template_map.get(genre, "general")

    def detect_multiple(self, texts: List[str]) -> List[GenreResult]:
        """
        批量检测多个文本

        Args:
            texts: 文本列表

        Returns:
            List[GenreResult]: 检测结果列表
        """
        return [self.detect(text) for text in texts]


# 便捷函数
def detect_genre(text: str) -> GenreResult:
    """快速类型检测"""
    detector = GenreDetector()
    return detector.detect(text)


if __name__ == "__main__":
    # 测试用例
    detector = GenreDetector()

    test_cases = [
        "后室探险：SCP收容失效 - 主角意外进入后室世界，需要躲避各种致命实体",
        "斗破苍穹 - 废物少年逆天改命，斗气大陆成就传奇",
        "重生之都市修仙 - 重生都市，修炼仙法纵横都市",
        "诡秘之主 - 蒸汽朋克与克苏鲁的融合，推理悬疑",
        "全职高手 - 游戏竞技，荣耀战场",
        "穿越到大唐盛世，成为太子争霸天下",
    ]

    print("=" * 60)
    print("GenreDetector 测试")
    print("=" * 60)

    for text in test_cases:
        result = detector.detect(text)
        print(f"\n输入: {text}")
        print(f"结果: {result.genre} (置信度: {result.confidence:.2%})")
        print(f"匹配: {result.matched_keywords}")
        print(f"推理: {result.reasoning}")
