"""
时间感知RAG检索器
集成LocalVectorStore + EntityGraph，实现时间约束检索和多路径检索
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
import hashlib

try:
    from .local_vector_store import LocalVectorStore
    from .entity_graph import EntityGraph, EntityNode, EntityType
    from .scene_splitter import SceneSplitter, Scene
except ImportError:
    from local_vector_store import LocalVectorStore
    from entity_graph import EntityGraph, EntityNode, EntityType
    from scene_splitter import SceneSplitter, Scene


@dataclass
class RetrievalResult:
    """检索结果"""

    content: str
    source: str  # "semantic" | "entity" | "summary" | "recent"
    chapter: int
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeAwareQuery:
    """时间感知查询"""

    query_text: str
    current_chapter: int
    max_results: int = 10
    token_budget: int = 4000
    include_entities: bool = True
    include_summaries: bool = True
    include_recent: bool = True


class TimeAwareRAG:
    """
    时间感知RAG检索器

    特性：
    1. 时间约束检索：只返回当前章节及之前的内容
    2. 多路径检索：语义 + 实体 + 摘要 + 最近内容
    3. 未来内容屏蔽：防止剧透未来章节
    4. Token预算管理：智能截断和优先级排序
    """

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.vector_store = LocalVectorStore(self.project_dir / "vector_store.db")
        self.entity_graph = EntityGraph()
        self.scene_splitter = SceneSplitter()

        # 加载现有数据
        self._load_existing_data()

        # 缓存最近检索结果
        self.recent_results_cache: Dict[str, List[RetrievalResult]] = {}

    def _load_existing_data(self):
        """加载现有项目数据"""
        # 加载实体图谱
        entity_graph_path = self.project_dir / "entity_graph.json"
        if entity_graph_path.exists():
            self._load_entity_graph(str(entity_graph_path))
        # 加载章节摘要
        self.summary_index = self._load_summary_index()

    def _load_summary_index(self) -> Dict[int, str]:
        """加载章节摘要索引"""
        summary_index = {}
        summary_dir = self.project_dir / "summaries"

        if summary_dir.exists():
            for summary_file in summary_dir.glob("chapter-*.md"):
                try:
                    chapter_num = int(summary_file.stem.split("-")[1])
                    content = summary_file.read_text(encoding="utf-8")
                    summary_index[chapter_num] = content
                except (ValueError, IndexError):
                    continue

        return summary_index

    def _load_entity_graph(self, filepath: str) -> None:
        """从JSON文件加载实体图谱"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载节点
            if "nodes" in data:
                for node_data in data["nodes"]:
                    node = EntityNode.from_dict(node_data)
                    self.entity_graph.add_node(node)

            # 加载边
            if "edges" in data:
                for edge_data in data["edges"]:
                    edge = EntityEdge.from_dict(edge_data)
                    self.entity_graph.add_edge(edge)

        except Exception as e:
            print(f"加载实体图谱失败: {e}")

    def retrieve(self, query: TimeAwareQuery) -> List[RetrievalResult]:
        """
        执行时间感知检索

        流程：
        1. 语义检索（向量相似度）
        2. 实体检索（实体图谱）
        3. 摘要检索（章节摘要）
        4. 最近内容检索（最近章节）
        5. 合并、去重、排序
        6. Token预算管理
        """
        all_results = []

        # 1. 语义检索（时间约束）
        semantic_results = self._semantic_retrieval(query)
        all_results.extend(semantic_results)

        # 2. 实体检索
        if query.include_entities:
            entity_results = self._entity_retrieval(query)
            all_results.extend(entity_results)

        # 3. 摘要检索
        if query.include_summaries:
            summary_results = self._summary_retrieval(query)
            all_results.extend(summary_results)

        # 4. 最近内容检索
        if query.include_recent:
            recent_results = self._recent_content_retrieval(query)
            all_results.extend(recent_results)

        # 5. 合并、去重、排序
        merged_results = self._merge_and_deduplicate(all_results)
        sorted_results = self._sort_by_relevance(merged_results)

        # 6. Token预算管理
        final_results = self._apply_token_budget(sorted_results, query.token_budget)

        return final_results

    def _semantic_retrieval(self, query: TimeAwareQuery) -> List[RetrievalResult]:
        """语义检索（向量相似度）"""
        results = []

        # 从向量存储中检索
        vector_results = self.vector_store.search(
            query_text=query.query_text,
            top_k=query.max_results * 2,  # 检索更多以便过滤
            filters={"chapter": {"$lte": query.current_chapter}},  # 时间约束
        )

        for vec_result in vector_results:
            result = RetrievalResult(
                content=vec_result.get("text", ""),
                source="semantic",
                chapter=vec_result.get("chapter", 1),
                relevance_score=vec_result.get("score", 0.0),
                metadata={
                    "chunk_id": vec_result.get("chunk_id"),
                    "scene_id": vec_result.get("scene_id"),
                    "characters": vec_result.get("characters", []),
                    "location": vec_result.get("location", ""),
                },
            )
            results.append(result)

        return results

    def _entity_retrieval(self, query: TimeAwareQuery) -> List[RetrievalResult]:
        """实体检索（实体图谱）"""
        results = []

        # 从查询中提取实体关键词
        entity_keywords = self._extract_entity_keywords(query.query_text)

        for keyword in entity_keywords:
            # 查询实体图谱
            entities = self.entity_graph.search_entities(
                name=keyword, chapter=query.current_chapter
            )

            for entity in entities:
                # 构建实体描述
                entity_desc = self._build_entity_description(entity)

                result = RetrievalResult(
                    content=entity_desc,
                    source="entity",
                    chapter=entity.valid_from,
                    relevance_score=0.8,  # 实体检索默认高相关度
                    metadata={
                        "entity_id": entity.id,
                        "entity_type": entity.entity_type.value,
                        "entity_name": entity.name,
                        "valid_from": entity.valid_from,
                        "valid_until": entity.valid_until,
                    },
                )
                results.append(result)

        return results

    def _summary_retrieval(self, query: TimeAwareQuery) -> List[RetrievalResult]:
        """摘要检索（章节摘要）"""
        results = []

        # 获取当前及之前章节的摘要
        for chapter in range(1, query.current_chapter + 1):
            if chapter in self.summary_index:
                summary = self.summary_index[chapter]

                # 简单关键词匹配计算相关度
                relevance = self._calculate_keyword_relevance(query.query_text, summary)

                if relevance > 0.1:  # 相关度阈值
                    result = RetrievalResult(
                        content=f"第{chapter}章摘要：{summary}",
                        source="summary",
                        chapter=chapter,
                        relevance_score=relevance,
                        metadata={"summary_type": "chapter"},
                    )
                    results.append(result)

        return results

    def _recent_content_retrieval(self, query: TimeAwareQuery) -> List[RetrievalResult]:
        """最近内容检索（最近3章）"""
        results = []

        recent_chapters = range(
            max(1, query.current_chapter - 3), query.current_chapter + 1
        )

        for chapter in recent_chapters:
            # 尝试从向量存储获取最近章节内容
            chapter_results = self.vector_store.search(
                query_text="",  # 空查询获取所有
                top_k=5,
                filters={"chapter": chapter},
            )

            for vec_result in chapter_results:
                result = RetrievalResult(
                    content=vec_result.get("text", ""),
                    source="recent",
                    chapter=chapter,
                    relevance_score=0.6,  # 最近内容默认中等相关度
                    metadata={
                        "chunk_id": vec_result.get("chunk_id"),
                        "recency_weight": query.current_chapter - chapter + 1,
                    },
                )
                results.append(result)

        return results

    def _extract_entity_keywords(self, text: str) -> List[str]:
        """从文本中提取实体关键词"""
        # 简单实现：提取名词性词汇
        keywords = []
        words = text.split()

        # 中文常见实体后缀
        entity_suffixes = [
            "宗",
            "门",
            "派",
            "教",
            "殿",
            "宫",
            "阁",
            "楼",
            "山",
            "谷",
            "洞",
        ]

        for word in words:
            # 检查是否包含实体特征
            if any(word.endswith(suffix) for suffix in entity_suffixes):
                keywords.append(word)
            elif len(word) >= 2 and word[0].isupper():  # 首字母大写（英文）
                keywords.append(word)

        return keywords

    def _build_entity_description(self, entity: EntityNode) -> str:
        """构建实体描述"""
        desc_parts = []

        # 基本描述
        type_map = {
            EntityType.CHARACTER: "角色",
            EntityType.ITEM: "物品",
            EntityType.LOCATION: "地点",
            EntityType.FACTION: "势力",
            EntityType.ABILITY: "能力",
        }

        desc_parts.append(f"{type_map.get(entity.entity_type, '实体')}：{entity.name}")

        # 添加属性
        for key, value in entity.properties.items():
            if key not in ["id", "name", "type"]:
                desc_parts.append(f"{key}：{value}")

        # 添加时间有效性
        if entity.valid_until:
            desc_parts.append(f"有效章节：{entity.valid_from}-{entity.valid_until}")
        else:
            desc_parts.append(f"从第{entity.valid_from}章起有效")

        return "，".join(desc_parts)

    def _calculate_keyword_relevance(self, query: str, text: str) -> float:
        """计算关键词相关度（简单实现）"""
        query_words = set(query.split())
        text_words = set(text.split())

        if not query_words:
            return 0.0

        intersection = query_words.intersection(text_words)
        return len(intersection) / len(query_words)

    def _merge_and_deduplicate(
        self, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """合并和去重检索结果"""
        seen_content = set()
        merged = []

        for result in results:
            # 创建内容哈希用于去重
            content_hash = hashlib.md5(result.content.encode()).hexdigest()

            if content_hash not in seen_content:
                seen_content.add(content_hash)
                merged.append(result)

        return merged

    def _sort_by_relevance(
        self, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """按相关度排序"""

        def _calculate_composite_score(result: RetrievalResult) -> float:
            """计算综合得分"""
            base_score = result.relevance_score

            # 源类型权重
            source_weights = {
                "semantic": 1.0,
                "entity": 0.9,
                "summary": 0.8,
                "recent": 0.7,
            }

            source_weight = source_weights.get(result.source, 0.5)

            # 章节新鲜度权重（越近权重越高）
            if "recency_weight" in result.metadata:
                recency_weight = result.metadata["recency_weight"] / 4.0  # 归一化
            else:
                recency_weight = 0.5

            return base_score * source_weight * (0.7 + 0.3 * recency_weight)

        return sorted(results, key=_calculate_composite_score, reverse=True)

    def _apply_token_budget(
        self, results: List[RetrievalResult], token_budget: int
    ) -> List[RetrievalResult]:
        """应用token预算管理"""
        selected = []
        current_tokens = 0

        # 简单估算：1个中文字符 ≈ 2个tokens
        for result in results:
            result_tokens = len(result.content) * 2

            if current_tokens + result_tokens <= token_budget:
                selected.append(result)
                current_tokens += result_tokens
            else:
                # 尝试截断
                remaining_tokens = token_budget - current_tokens
                if remaining_tokens >= 20:  # 至少保留10个字符
                    truncated_content = result.content[: remaining_tokens // 2]
                    truncated_result = RetrievalResult(
                        content=truncated_content + "...",
                        source=result.source,
                        chapter=result.chapter,
                        relevance_score=result.relevance_score * 0.8,  # 截断降低相关度
                        metadata=result.metadata,
                    )
                    selected.append(truncated_result)
                break

        return selected

    def index_chapter(
        self, chapter_number: int, content: str, metadata: Dict[str, Any] = None
    ):
        """
        索引章节内容

        Args:
            chapter_number: 章节号
            content: 章节内容
            metadata: 额外元数据
        """
        if metadata is None:
            metadata = {}

        # 1. 场景分割
        scenes = self.scene_splitter.split(content)

        # 2. 索引到向量存储
        for i, scene in enumerate(scenes):
            chunk_metadata = {
                "chapter": chapter_number,
                "scene_id": f"ch{chapter_number}_sc{i + 1}",
                "scene_index": i,
                "characters": scene.characters,
                "location": scene.location,
                "time": scene.time,
                **metadata,
            }

            self.vector_store.add_chunk(text=scene.text, metadata=chunk_metadata)

        # 3. 提取和更新实体
        self._extract_and_update_entities(chapter_number, content)

        # 4. 生成和存储摘要
        summary = self._generate_chapter_summary(chapter_number, content)
        self._store_chapter_summary(chapter_number, summary)

    def _extract_and_update_entities(self, chapter_number: int, content: str):
        """从内容中提取和更新实体"""
        # 这里可以集成更复杂的实体提取逻辑
        # 目前是简单实现

        # 示例：提取宗门名称
        faction_patterns = [r"([\u4e00-\u9fff]{2,4})(宗|门|派|教)"]

        for pattern in faction_patterns:
            import re

            matches = re.findall(pattern, content)
            for match in matches:
                faction_name = match[0] + match[1]

                # 检查实体是否已存在
                existing = self.entity_graph.get_entity_by_name(faction_name)

                if existing:
                    # 更新有效期
                    existing.valid_until = chapter_number
                    self.entity_graph.update_entity(existing)
                else:
                    # 创建新实体
                    entity = EntityNode(
                        id=f"faction_{hashlib.md5(faction_name.encode()).hexdigest()[:8]}",
                        entity_type=EntityType.FACTION,
                        name=faction_name,
                        properties={"extracted_from": f"第{chapter_number}章"},
                        valid_from=chapter_number,
                    )
                    self.entity_graph.add_entity(entity)

    def _generate_chapter_summary(self, chapter_number: int, content: str) -> str:
        """生成章节摘要"""
        # 简单实现：取前200字符作为摘要
        if len(content) > 200:
            return content[:200] + "..."
        return content

    def _store_chapter_summary(self, chapter_number: int, summary: str):
        """存储章节摘要"""
        summary_dir = self.project_dir / "summaries"
        summary_dir.mkdir(exist_ok=True)

        summary_file = summary_dir / f"chapter-{chapter_number:03d}.md"
        summary_file.write_text(summary, encoding="utf-8")

        # 更新内存索引
        self.summary_index[chapter_number] = summary

    def save_state(self):
        """保存状态"""
        # 保存向量存储
        self.vector_store.save()

        # 保存实体图谱
        entity_graph_path = self.project_dir / "entity_graph.json"
        self.entity_graph.save_to_file(str(entity_graph_path))


# 测试函数
def test_time_aware_rag():
    """测试时间感知RAG"""
    import tempfile
    import os

    # 创建临时项目目录
    with tempfile.TemporaryDirectory() as tmpdir:
        rag = TimeAwareRAG(tmpdir)

        # 索引测试章节
        test_content = """
        第1章：青云宗入门测试
        林风站在青云宗山门前，心中充满期待。今天是青云宗三年一度的入门测试，他苦练三年，就是为了这一刻。
        
        测试分为三关：第一关测根骨，第二关测心性，第三关测实战。
        林风顺利通过前两关，在第三关遇到了强劲对手——王猛。
        
        经过激烈战斗，林风险胜，成功加入青云宗。
        """

        rag.index_chapter(1, test_content)

        # 执行查询
        query = TimeAwareQuery(query_text="青云宗入门测试", current_chapter=1)

        results = rag.retrieve(query)

        print(f"检索到 {len(results)} 个结果：")
        for i, result in enumerate(results, 1):
            print(
                f"{i}. [{result.source}] 第{result.chapter}章 (相关度: {result.relevance_score:.2f})"
            )
            print(f"   内容: {result.content[:100]}...")
            print()

        # 保存状态
        rag.save_state()

        return len(results) > 0


if __name__ == "__main__":
    success = test_time_aware_rag()
    if success:
        print("✅ TimeAwareRAG 测试通过")
    else:
        print("❌ TimeAwareRAG 测试失败")
