"""
实体图谱数据结构和查询引擎
用于追踪角色、物品、地点、势力、能力等实体在各章节的时间有效性
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


class EntityType(Enum):
    """实体类型枚举"""

    CHARACTER = "character"
    ITEM = "item"
    LOCATION = "location"
    FACTION = "faction"
    ABILITY = "ability"


@dataclass
class EntityNode:
    """
    实体节点，表示一个具有时间有效性的实体

    Attributes:
        id: 实体唯一标识符
        entity_type: 实体类型
        name: 实体名称
        properties: 实体属性字典
        valid_from: 有效起始章节（包含）
        valid_until: 有效结束章节（None表示仍然有效）
    """

    id: str
    entity_type: EntityType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    valid_from: int = 1
    valid_until: Optional[int] = None

    def is_valid_at(self, chapter: int) -> bool:
        """检查实体在指定章节是否有效"""
        if chapter < self.valid_from:
            return False
        if self.valid_until is not None and chapter > self.valid_until:
            return False
        return True

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "properties": self.properties,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EntityNode":
        """从字典创建"""
        return cls(
            id=data["id"],
            entity_type=EntityType(data["entity_type"]),
            name=data["name"],
            properties=data.get("properties", {}),
            valid_from=data.get("valid_from", 1),
            valid_until=data.get("valid_until"),
        )


@dataclass
class EntityEdge:
    """
    实体边，表示两个实体之间的关系

    Attributes:
        source_id: 源实体ID
        target_id: 目标实体ID
        relation_type: 关系类型（如 "owns", "located_at", "member_of", "has_ability"）
        valid_from: 有效起始章节（包含）
        valid_until: 有效结束章节（None表示仍然有效）
    """

    source_id: str
    target_id: str
    relation_type: str
    valid_from: int = 1
    valid_until: Optional[int] = None

    def is_valid_at(self, chapter: int) -> bool:
        """检查关系在指定章节是否有效"""
        if chapter < self.valid_from:
            return False
        if self.valid_until is not None and chapter > self.valid_until:
            return False
        return True

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EntityEdge":
        """从字典创建"""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=data["relation_type"],
            valid_from=data.get("valid_from", 1),
            valid_until=data.get("valid_until"),
        )


class EntityGraph:
    """
    实体图谱类，用于管理和查询实体及其关系

    支持：
    - 添加实体节点和边
    - 按章节查询实体状态
    - 查询实体的关系
    - 按类型查询所有实体
    - 查询角色的能力
    """

    def __init__(self):
        self._nodes: Dict[str, EntityNode] = {}
        self._edges: List[EntityEdge] = []

    def add_node(self, node: EntityNode) -> None:
        """
        添加实体节点

        Args:
            node: 实体节点
        """
        self._nodes[node.id] = node

    def add_edge(self, edge: EntityEdge) -> None:
        """
        添加实体关系边

        Args:
            edge: 实体边
        """
        self._edges.append(edge)

    def get_node(self, entity_id: str) -> Optional[EntityNode]:
        """
        获取实体节点（不考虑时间有效性）

        Args:
            entity_id: 实体ID

        Returns:
            实体节点，如果不存在则返回None
        """
        return self._nodes.get(entity_id)

    def get_node_state(self, entity_id: str, at_chapter: int) -> Optional[EntityNode]:
        """
        获取实体在指定章节的状态

        Args:
            entity_id: 实体ID
            at_chapter: 章节号

        Returns:
            实体节点，如果不存在或在该章节无效则返回None
        """
        node = self._nodes.get(entity_id)
        if node is None:
            return None
        if not node.is_valid_at(at_chapter):
            return None
        return node

    def get_edges(self, entity_id: str, at_chapter: int) -> List[EntityEdge]:
        """
        获取实体在指定章节的所有关系边

        Args:
            entity_id: 实体ID
            at_chapter: 章节号

        Returns:
            有效的实体边列表
        """
        result = []
        for edge in self._edges:
            if edge.source_id == entity_id or edge.target_id == entity_id:
                if edge.is_valid_at(at_chapter):
                    result.append(edge)
        return result

    def get_all_entities(
        self, at_chapter: int, entity_type: Optional[EntityType] = None
    ) -> List[EntityNode]:
        """
        获取指定章节的所有实体

        Args:
            at_chapter: 章节号
            entity_type: 实体类型过滤（可选）

        Returns:
            有效的实体节点列表
        """
        result = []
        for node in self._nodes.values():
            if not node.is_valid_at(at_chapter):
                continue
            if entity_type is not None and node.entity_type != entity_type:
                continue
            result.append(node)
        return result

    def query_abilities(self, character_id: str, at_chapter: int) -> List[str]:
        """
        查询角色在指定章节拥有的能力

        Args:
            character_id: 角色ID
            at_chapter: 章节号

        Returns:
            能力ID列表
        """
        abilities = []

        # 查找所有从该角色出发的 has_ability 关系
        for edge in self._edges:
            if edge.source_id == character_id and edge.relation_type == "has_ability":
                if edge.is_valid_at(at_chapter):
                    # 确认目标是一个能力实体
                    target_node = self._nodes.get(edge.target_id)
                    if target_node and target_node.entity_type == EntityType.ABILITY:
                        abilities.append(edge.target_id)

        return abilities

    def query_items(self, character_id: str, at_chapter: int) -> List[str]:
        """
        查询角色在指定章节拥有的物品

        Args:
            character_id: 角色ID
            at_chapter: 章节号

        Returns:
            物品ID列表
        """
        items = []

        for edge in self._edges:
            if edge.source_id == character_id and edge.relation_type == "owns":
                if edge.is_valid_at(at_chapter):
                    target_node = self._nodes.get(edge.target_id)
                    if target_node and target_node.entity_type == EntityType.ITEM:
                        items.append(edge.target_id)

        return items

    def query_location(self, entity_id: str, at_chapter: int) -> Optional[str]:
        """
        查询实体在指定章节的位置

        Args:
            entity_id: 实体ID
            at_chapter: 章节号

        Returns:
            位置实体ID，如果不存在则返回None
        """
        for edge in self._edges:
            if edge.source_id == entity_id and edge.relation_type == "located_at":
                if edge.is_valid_at(at_chapter):
                    target_node = self._nodes.get(edge.target_id)
                    if target_node and target_node.entity_type == EntityType.LOCATION:
                        return edge.target_id
        return None

    def query_faction(self, character_id: str, at_chapter: int) -> Optional[str]:
        """
        查询角色在指定章节所属的势力

        Args:
            character_id: 角色ID
            at_chapter: 章节号

        Returns:
            势力实体ID，如果不存在则返回None
        """
        for edge in self._edges:
            if edge.source_id == character_id and edge.relation_type == "member_of":
                if edge.is_valid_at(at_chapter):
                    target_node = self._nodes.get(edge.target_id)
                    if target_node and target_node.entity_type == EntityType.FACTION:
                        return edge.target_id
        return None

    def to_json(self) -> Dict:
        """
        序列化为JSON兼容的字典

        Returns:
            JSON兼容的字典
        """
        return {
            "nodes": [node.to_dict() for node in self._nodes.values()],
            "edges": [edge.to_dict() for edge in self._edges],
        }

    @classmethod
    def from_json(cls, data: Dict) -> "EntityGraph":
        """
        从JSON数据反序列化

        Args:
            data: JSON兼容的字典

        Returns:
            EntityGraph实例
        """
        graph = cls()

        for node_data in data.get("nodes", []):
            node = EntityNode.from_dict(node_data)
            graph.add_node(node)

        for edge_data in data.get("edges", []):
            edge = EntityEdge.from_dict(edge_data)
            graph.add_edge(edge)

        return graph

    def search_entities(self, name: str, chapter: int = None) -> List[EntityNode]:
        """
        根据名称搜索实体节点

        Args:
            name: 实体名称（支持模糊匹配）
            chapter: 章节号，如果提供则返回该章节有效的实体

        Returns:
            匹配的实体节点列表
        """
        results = []

        # 转换为小写进行模糊匹配
        name_lower = name.lower()

        for node in self._nodes.values():
            # 名称匹配
            if name_lower in node.name.lower():
                # 如果提供了章节号，检查实体在该章节是否有效
                if chapter is not None:
                    if node.is_valid_at(chapter):
                        results.append(node)
                else:
                    results.append(node)

        return results

    def __len__(self) -> int:
        """返回实体数量"""
        return len(self._nodes)

    def __repr__(self) -> str:
        return f"EntityGraph(nodes={len(self._nodes)}, edges={len(self._edges)})"
