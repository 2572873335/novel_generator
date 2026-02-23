"""
分层摘要索引器
实现2级摘要层次结构：卷级摘要(L1) + 章级摘要(L2)
支持摘要生成、更新和快速检索
"""

import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import hashlib


@dataclass
class ChapterSummary:
    """章节摘要 (L2)"""

    chapter_number: int
    title: str
    summary: str
    word_count: int
    key_events: List[str]
    characters_involved: List[str]
    locations: List[str]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "title": self.title,
            "summary": self.summary,
            "word_count": self.word_count,
            "key_events": self.key_events,
            "characters_involved": self.characters_involved,
            "locations": self.locations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


@dataclass
class VolumeSummary:
    """卷级摘要 (L1)"""

    volume_number: int
    title: str
    summary: str
    chapter_range: Tuple[int, int]  # (start_chapter, end_chapter)
    total_chapters: int
    total_words: int
    main_plot_points: List[str]
    character_developments: List[str]
    world_changes: List[str]
    created_at: str
    updated_at: str
    chapter_summaries: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "volume_number": self.volume_number,
            "title": self.title,
            "summary": self.summary,
            "chapter_range": list(self.chapter_range),
            "total_chapters": self.total_chapters,
            "total_words": self.total_words,
            "main_plot_points": self.main_plot_points,
            "character_developments": self.character_developments,
            "world_changes": self.world_changes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "chapter_summaries": self.chapter_summaries,
        }


class SummaryIndexer:
    """
    分层摘要索引器

    层级结构：
    - L1: 卷级摘要 (每10-20章一个卷)
    - L2: 章级摘要 (每章一个摘要)

    功能：
    1. 自动生成章节摘要
    2. 聚合生成卷级摘要
    3. 支持摘要更新
    4. 快速摘要检索
    5. 摘要质量评估
    """

    def __init__(self, project_dir: str, chapters_per_volume: int = 10):
        self.project_dir = Path(project_dir)
        self.chapters_per_volume = chapters_per_volume

        # 创建摘要目录
        self.summary_dir = self.project_dir / "summaries"
        self.summary_dir.mkdir(exist_ok=True)

        self.chapter_summaries_dir = self.summary_dir / "chapters"
        self.chapter_summaries_dir.mkdir(exist_ok=True)

        self.volume_summaries_dir = self.summary_dir / "volumes"
        self.volume_summaries_dir.mkdir(exist_ok=True)

        # 内存索引
        self.chapter_index: Dict[int, ChapterSummary] = {}
        self.volume_index: Dict[int, VolumeSummary] = {}

        # 加载现有摘要
        self._load_existing_summaries()

    def _load_existing_summaries(self):
        """加载现有摘要"""
        # 加载章节摘要
        for summary_file in self.chapter_summaries_dir.glob("chapter-*.json"):
            try:
                chapter_num = int(summary_file.stem.split("-")[1])
                with open(summary_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    summary = ChapterSummary(
                        chapter_number=data["chapter_number"],
                        title=data["title"],
                        summary=data["summary"],
                        word_count=data["word_count"],
                        key_events=data["key_events"],
                        characters_involved=data["characters_involved"],
                        locations=data["locations"],
                        created_at=data["created_at"],
                        updated_at=data["updated_at"],
                        metadata=data.get("metadata", {}),
                    )
                    self.chapter_index[chapter_num] = summary
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"加载章节摘要失败 {summary_file}: {e}")

        # 加载卷级摘要
        for summary_file in self.volume_summaries_dir.glob("volume-*.json"):
            try:
                volume_num = int(summary_file.stem.split("-")[1])
                with open(summary_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    summary = VolumeSummary(
                        volume_number=data["volume_number"],
                        title=data["title"],
                        summary=data["summary"],
                        chapter_range=tuple(data["chapter_range"]),
                        total_chapters=data["total_chapters"],
                        total_words=data["total_words"],
                        main_plot_points=data["main_plot_points"],
                        character_developments=data["character_developments"],
                        world_changes=data["world_changes"],
                        created_at=data["created_at"],
                        updated_at=data["updated_at"],
                        chapter_summaries=data.get("chapter_summaries", []),
                    )
                    self.volume_index[volume_num] = summary
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                print(f"加载卷级摘要失败 {summary_file}: {e}")

    def generate_chapter_summary(
        self,
        chapter_number: int,
        content: str,
        title: str = "",
        metadata: Dict[str, Any] = None,
    ) -> ChapterSummary:
        """
        生成章节摘要

        Args:
            chapter_number: 章节号
            content: 章节内容
            title: 章节标题（可选）
            metadata: 额外元数据

        Returns:
            生成的章节摘要
        """
        if metadata is None:
            metadata = {}

        # 提取关键信息
        word_count = len(content)

        # 简单实现：提取前3句话作为摘要
        sentences = self._extract_sentences(content)
        summary = " ".join(sentences[:3]) if sentences else content[:200]

        # 提取关键事件（简单实现：包含"！"的句子）
        key_events = [s for s in sentences if "！" in s or "。" in s][:5]

        # 提取角色（简单实现：提取常见人名模式）
        characters = self._extract_characters(content)

        # 提取地点（简单实现：包含"宗"、"门"、"山"等的地点）
        locations = self._extract_locations(content)

        now = datetime.now().isoformat()

        summary_obj = ChapterSummary(
            chapter_number=chapter_number,
            title=title or f"第{chapter_number}章",
            summary=summary,
            word_count=word_count,
            key_events=key_events,
            characters_involved=characters,
            locations=locations,
            created_at=now,
            updated_at=now,
            metadata=metadata,
        )

        # 保存到内存索引
        self.chapter_index[chapter_number] = summary_obj

        # 保存到文件
        self._save_chapter_summary(summary_obj)

        # 检查是否需要更新卷级摘要
        self._update_volume_summary(chapter_number)

        return summary_obj

    def _extract_sentences(self, text: str) -> List[str]:
        """提取句子"""
        # 简单实现：按中文标点分割
        import re

        sentences = re.split(r"[。！？；]", text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_characters(self, text: str) -> List[str]:
        """提取角色名称"""
        # 简单实现：提取常见中文人名模式
        import re

        # 常见中文姓氏
        common_surnames = [
            "赵",
            "钱",
            "孙",
            "李",
            "周",
            "吴",
            "郑",
            "王",
            "林",
            "陈",
            "张",
            "刘",
        ]
        patterns = [rf"{surname}[\u4e00-\u9fff]{{1,2}}" for surname in common_surnames]

        characters = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            characters.extend(matches)

        return list(set(characters))[:10]  # 去重并限制数量

    def _extract_locations(self, text: str) -> List[str]:
        """提取地点名称"""
        # 简单实现：提取包含特定后缀的地点
        import re

        location_suffixes = [
            "宗",
            "门",
            "派",
            "教",
            "山",
            "谷",
            "洞",
            "殿",
            "宫",
            "阁",
            "楼",
        ]
        patterns = [rf"[\u4e00-\u9fff]{{2,4}}{suffix}" for suffix in location_suffixes]

        locations = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            locations.extend(matches)

        return list(set(locations))[:10]  # 去重并限制数量

    def _save_chapter_summary(self, summary: ChapterSummary):
        """保存章节摘要到文件"""
        summary_file = (
            self.chapter_summaries_dir / f"chapter-{summary.chapter_number:03d}.json"
        )

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary.to_dict(), f, ensure_ascii=False, indent=2)

    def _update_volume_summary(self, chapter_number: int):
        """更新卷级摘要"""
        volume_num = self._get_volume_number(chapter_number)

        # 获取该卷的所有章节
        start_chapter = (volume_num - 1) * self.chapters_per_volume + 1
        end_chapter = min(
            volume_num * self.chapters_per_volume, max(self.chapter_index.keys())
        )

        # 收集该卷的章节摘要
        volume_chapters = []
        for chap in range(start_chapter, end_chapter + 1):
            if chap in self.chapter_index:
                volume_chapters.append(self.chapter_index[chap])

        if not volume_chapters:
            return

        # 生成或更新卷级摘要
        if volume_num in self.volume_index:
            # 更新现有卷级摘要
            self._update_existing_volume_summary(volume_num, volume_chapters)
        else:
            # 创建新卷级摘要
            self._create_new_volume_summary(
                volume_num, volume_chapters, start_chapter, end_chapter
            )

    def _get_volume_number(self, chapter_number: int) -> int:
        """根据章节号计算卷号"""
        return (chapter_number - 1) // self.chapters_per_volume + 1

    def _update_existing_volume_summary(
        self, volume_num: int, chapters: List[ChapterSummary]
    ):
        """更新现有卷级摘要"""
        volume_summary = self.volume_index[volume_num]

        # 更新统计信息
        volume_summary.total_chapters = len(chapters)
        volume_summary.total_words = sum(chap.word_count for chap in chapters)

        # 更新章节摘要列表
        volume_summary.chapter_summaries = [chap.to_dict() for chap in chapters]

        # 重新生成摘要
        volume_summary.summary = self._generate_volume_summary_text(chapters)

        # 提取关键信息
        volume_summary.main_plot_points = self._extract_volume_plot_points(chapters)
        volume_summary.character_developments = (
            self._extract_volume_character_developments(chapters)
        )
        volume_summary.world_changes = self._extract_volume_world_changes(chapters)

        volume_summary.updated_at = datetime.now().isoformat()

        # 保存
        self._save_volume_summary(volume_summary)

    def _create_new_volume_summary(
        self,
        volume_num: int,
        chapters: List[ChapterSummary],
        start_chapter: int,
        end_chapter: int,
    ):
        """创建新卷级摘要"""
        now = datetime.now().isoformat()

        volume_summary = VolumeSummary(
            volume_number=volume_num,
            title=f"第{volume_num}卷",
            summary=self._generate_volume_summary_text(chapters),
            chapter_range=(start_chapter, end_chapter),
            total_chapters=len(chapters),
            total_words=sum(chap.word_count for chap in chapters),
            main_plot_points=self._extract_volume_plot_points(chapters),
            character_developments=self._extract_volume_character_developments(
                chapters
            ),
            world_changes=self._extract_volume_world_changes(chapters),
            created_at=now,
            updated_at=now,
            chapter_summaries=[chap.to_dict() for chap in chapters],
        )

        self.volume_index[volume_num] = volume_summary
        self._save_volume_summary(volume_summary)

    def _generate_volume_summary_text(self, chapters: List[ChapterSummary]) -> str:
        """生成卷级摘要文本"""
        if not chapters:
            return ""

        # 简单实现：合并前3章的摘要
        summary_parts = []
        for chap in chapters[:3]:
            summary_parts.append(f"第{chap.chapter_number}章：{chap.summary[:100]}...")

        return " ".join(summary_parts)

    def _extract_volume_plot_points(self, chapters: List[ChapterSummary]) -> List[str]:
        """提取卷级关键情节点"""
        plot_points = []
        for chap in chapters:
            plot_points.extend(chap.key_events[:2])  # 每章取前2个关键事件

        return plot_points[:10]  # 限制数量

    def _extract_volume_character_developments(
        self, chapters: List[ChapterSummary]
    ) -> List[str]:
        """提取卷级角色发展"""
        # 统计角色出现频率
        character_counts = {}
        for chap in chapters:
            for char in chap.characters_involved:
                character_counts[char] = character_counts.get(char, 0) + 1

        # 返回出现频率最高的角色
        sorted_chars = sorted(
            character_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [f"{char}（出现{count}次）" for char, count in sorted_chars[:5]]

    def _extract_volume_world_changes(
        self, chapters: List[ChapterSummary]
    ) -> List[str]:
        """提取卷级世界变化"""
        # 收集所有地点
        all_locations = set()
        for chap in chapters:
            all_locations.update(chap.locations)

        return list(all_locations)[:5]  # 返回前5个地点

    def _save_volume_summary(self, summary: VolumeSummary):
        """保存卷级摘要到文件"""
        summary_file = (
            self.volume_summaries_dir / f"volume-{summary.volume_number:03d}.json"
        )

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary.to_dict(), f, ensure_ascii=False, indent=2)

    def get_chapter_summary(self, chapter_number: int) -> Optional[ChapterSummary]:
        """获取章节摘要"""
        return self.chapter_index.get(chapter_number)

    def get_volume_summary(self, volume_number: int) -> Optional[VolumeSummary]:
        """获取卷级摘要"""
        return self.volume_index.get(volume_number)

    def get_volume_for_chapter(self, chapter_number: int) -> Optional[VolumeSummary]:
        """获取章节所属的卷级摘要"""
        volume_num = self._get_volume_number(chapter_number)
        return self.get_volume_summary(volume_num)

    def search_summaries(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索摘要

        Args:
            query: 搜索查询
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        results = []

        # 搜索章节摘要
        for chap_num, summary in self.chapter_index.items():
            relevance = self._calculate_relevance(query, summary.summary)
            if relevance > 0.1:  # 相关度阈值
                results.append(
                    {
                        "type": "chapter",
                        "chapter_number": chap_num,
                        "title": summary.title,
                        "summary": summary.summary,
                        "relevance": relevance,
                        "source": "chapter_summary",
                    }
                )

        # 搜索卷级摘要
        for vol_num, summary in self.volume_index.items():
            relevance = self._calculate_relevance(query, summary.summary)
            if relevance > 0.1:  # 相关度阈值
                results.append(
                    {
                        "type": "volume",
                        "volume_number": vol_num,
                        "title": summary.title,
                        "summary": summary.summary,
                        "relevance": relevance,
                        "source": "volume_summary",
                    }
                )

        # 按相关度排序
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return results[:max_results]

    def _calculate_relevance(self, query: str, text: str) -> float:
        """计算相关度（简单实现）"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())

        if not query_words:
            return 0.0

        intersection = query_words.intersection(text_words)
        return len(intersection) / len(query_words)

    def get_recent_summaries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近更新的摘要"""
        all_summaries = []

        # 收集章节摘要
        for chap_num, summary in self.chapter_index.items():
            all_summaries.append(
                {
                    "type": "chapter",
                    "chapter_number": chap_num,
                    "title": summary.title,
                    "summary": summary.summary[:100] + "..."
                    if len(summary.summary) > 100
                    else summary.summary,
                    "updated_at": summary.updated_at,
                }
            )

        # 收集卷级摘要
        for vol_num, summary in self.volume_index.items():
            all_summaries.append(
                {
                    "type": "volume",
                    "volume_number": vol_num,
                    "title": summary.title,
                    "summary": summary.summary[:100] + "..."
                    if len(summary.summary) > 100
                    else summary.summary,
                    "updated_at": summary.updated_at,
                }
            )

        # 按更新时间排序
        all_summaries.sort(key=lambda x: x["updated_at"], reverse=True)

        return all_summaries[:limit]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """获取摘要统计信息"""
        total_chapters = len(self.chapter_index)
        total_volumes = len(self.volume_index)

        if total_chapters == 0:
            return {
                "total_chapters": 0,
                "total_volumes": 0,
                "avg_words_per_chapter": 0,
                "coverage_percentage": 0.0,
            }

        # 计算平均字数
        total_words = sum(summary.word_count for summary in self.chapter_index.values())
        avg_words = total_words / total_chapters

        # 计算覆盖率（如果有目标章节数）
        target_chapters = self._get_target_chapters()
        coverage = total_chapters / target_chapters if target_chapters > 0 else 1.0

        return {
            "total_chapters": total_chapters,
            "total_volumes": total_volumes,
            "total_words": total_words,
            "avg_words_per_chapter": avg_words,
            "coverage_percentage": coverage * 100,
        }

    def _get_target_chapters(self) -> int:
        """获取目标章节数"""
        # 从项目配置中读取
        config_file = self.project_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("target_chapters", 0)
            except (json.JSONDecodeError, KeyError):
                pass

        return 0

    def export_summaries(self, format: str = "json") -> str:
        """导出所有摘要"""
        if format == "json":
            data = {
                "chapter_summaries": [s.to_dict() for s in self.chapter_index.values()],
                "volume_summaries": [s.to_dict() for s in self.volume_index.values()],
                "statistics": self.get_summary_statistics(),
                "exported_at": datetime.now().isoformat(),
            }
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format == "markdown":
            return self._export_to_markdown()
        else:
            raise ValueError(f"不支持的格式: {format}")

    def _export_to_markdown(self) -> str:
        """导出为Markdown格式"""
        lines = ["# 小说摘要报告", ""]

        # 统计信息
        stats = self.get_summary_statistics()
        lines.append("## 统计信息")
        lines.append(f"- 总章节数: {stats['total_chapters']}")
        lines.append(f"- 总卷数: {stats['total_volumes']}")
        lines.append(f"- 总字数: {stats['total_words']}")
        lines.append(f"- 平均每章字数: {stats['avg_words_per_chapter']:.0f}")
        lines.append(f"- 覆盖率: {stats['coverage_percentage']:.1f}%")
        lines.append("")

        # 卷级摘要
        if self.volume_index:
            lines.append("## 卷级摘要")
            for vol_num in sorted(self.volume_index.keys()):
                volume = self.volume_index[vol_num]
                lines.append(f"### {volume.title}")
                lines.append(
                    f"**章节范围**: 第{volume.chapter_range[0]}-{volume.chapter_range[1]}章"
                )
                lines.append(f"**总章节**: {volume.total_chapters}")
                lines.append(f"**总字数**: {volume.total_words}")
                lines.append("")
                lines.append(f"**摘要**: {volume.summary}")
                lines.append("")

                if volume.main_plot_points:
                    lines.append("**关键情节**:")
                    for point in volume.main_plot_points:
                        lines.append(f"- {point}")
                    lines.append("")

        # 最近章节摘要
        recent = self.get_recent_summaries(5)
        if recent:
            lines.append("## 最近更新章节")
            for item in recent:
                lines.append(f"### {item['title']}")
                lines.append(f"**类型**: {item['type']}")
                lines.append(f"**更新时间**: {item['updated_at']}")
                lines.append(f"**摘要**: {item['summary']}")
                lines.append("")

        return "\n".join(lines)


# 测试函数
def test_summary_indexer():
    """测试摘要索引器"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        indexer = SummaryIndexer(tmpdir, chapters_per_volume=3)

        # 生成测试章节摘要
        test_chapters = [
            (
                1,
                "第一章：青云宗入门",
                """
            林风站在青云宗山门前，心中充满期待。今天是青云宗三年一度的入门测试。
            测试分为三关：测根骨、测心性、测实战。林风顺利通过前两关。
            在第三关遇到了强劲对手王猛，经过激烈战斗，林风险胜，成功加入青云宗。
            """,
            ),
            (
                2,
                "第二章：初入宗门",
                """
            林风成为青云宗外门弟子，分配到杂役房工作。
            他认识了同门师兄李浩，李浩告诉他青云宗的规矩和修炼体系。
            林风领取了基础功法《青云诀》，开始正式修炼。
            """,
            ),
            (
                3,
                "第三章：首次任务",
                """
            林风接到第一个宗门任务：采集十株紫云草。
            在紫云山脉中，他遇到了守护妖兽紫云蟒。
            经过苦战，林风成功击败紫云蟒，采集到紫云草，还意外发现了一处古修洞府。
            """,
            ),
        ]

        for chap_num, title, content in test_chapters:
            summary = indexer.generate_chapter_summary(chap_num, content, title)
            print(f"生成摘要: 第{chap_num}章 - {title}")
            print(f"  摘要: {summary.summary[:100]}...")
            print()

        # 测试搜索
        print("搜索'青云宗':")
        results = indexer.search_summaries("青云宗", max_results=3)
        for i, result in enumerate(results, 1):
            print(
                f"{i}. [{result['type']}] {result['title']} (相关度: {result['relevance']:.2f})"
            )

        # 测试统计
        stats = indexer.get_summary_statistics()
        print(f"\n统计信息: {stats}")

        # 测试导出
        markdown_report = indexer.export_summaries("markdown")
        print(f"\nMarkdown报告长度: {len(markdown_report)} 字符")

        return len(indexer.chapter_index) == 3 and len(indexer.volume_index) == 1


if __name__ == "__main__":
    success = test_summary_indexer()
    if success:
        print("\n✅ SummaryIndexer 测试通过")
    else:
        print("\n❌ SummaryIndexer 测试失败")
