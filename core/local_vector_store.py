"""
本地向量存储模块
使用 SQLite + TF-IDF/BM25 实现轻量级语义相似度检索
"""

import json
import math
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import jieba

    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


@dataclass
class SearchResult:
    """搜索结果"""

    doc_id: int
    text: str
    metadata: Dict[str, Any]
    score: float
    created_at: str


class LocalVectorStore:
    """
    本地向量存储类
    使用 TF-IDF 和 BM25 算法实现语义相似度检索
    """

    # 字符n-gram范围（用于中文）
    NGRAM_MIN = 1
    NGRAM_MAX = 3

    # BM25参数
    BM25_K1 = 1.5
    BM25_B = 0.75

    def __init__(self, db_path: str):
        """
        初始化本地向量存储

        Args:
            db_path: SQLite数据库路径
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 文档表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    doc_length INTEGER DEFAULT 0
                )
            """)

            # 词汇表（用于TF-IDF）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary (
                    word TEXT PRIMARY KEY,
                    idf REAL NOT NULL,
                    doc_freq INTEGER DEFAULT 0
                )
            """)

            # 文档词频表（用于TF-IDF和BM25）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doc_terms (
                    doc_id INTEGER NOT NULL,
                    word TEXT NOT NULL,
                    tf INTEGER NOT NULL,
                    PRIMARY KEY (doc_id, word),
                    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_doc_terms_word 
                ON doc_terms(word)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_doc_terms_doc_id 
                ON doc_terms(doc_id)
            """)

            conn.commit()

    def _tokenize(self, text: str) -> List[str]:
        """
        分词处理
        优先使用jieba，fallback到字符n-gram

        Args:
            text: 待分词文本

        Returns:
            词列表
        """
        # 清理文本
        text = text.strip()

        if JIEBA_AVAILABLE:
            # 使用jieba分词
            tokens = list(jieba.cut(text))
            # 过滤停用词和单字符
            tokens = [t.strip() for t in tokens if len(t.strip()) >= 1]
        else:
            # 使用字符n-gram（适合中文）
            tokens = []
            # 提取连续中文字符
            chinese_pattern = re.compile(r"[\u4e00-\u9fff]+")
            chinese_matches = chinese_pattern.findall(text)

            for segment in chinese_matches:
                # 生成1-gram, 2-gram, 3-gram
                for n in range(self.NGRAM_MIN, self.NGRAM_MAX + 1):
                    for i in range(len(segment) - n + 1):
                        tokens.append(segment[i : i + n])

            # 也添加英文/数字词
            english_pattern = re.compile(r"[a-zA-Z0-9]+")
            english_matches = english_pattern.findall(text)
            tokens.extend(english_matches)

        return tokens

    def _compute_tf(self, tokens: List[str]) -> Dict[str, int]:
        """
        计算词频

        Args:
            tokens: 词列表

        Returns:
            词频字典
        """
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        return tf

    def _update_idf(self, conn: sqlite3.Connection, word: str, total_docs: int):
        """
        更新IDF值

        Args:
            conn: 数据库连接
            word: 词汇
            total_docs: 总文档数
        """
        cursor = conn.cursor()

        # 获取文档频率
        cursor.execute(
            """
            SELECT doc_freq FROM vocabulary WHERE word = ?
        """,
            (word,),
        )

        row = cursor.fetchone()
        if row:
            doc_freq = row["doc_freq"] + 1
            # IDF = log((N - n + 0.5) / (n + 0.5) + 1)
            idf = math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
            cursor.execute(
                """
                UPDATE vocabulary SET idf = ?, doc_freq = ? WHERE word = ?
            """,
                (idf, doc_freq, word),
            )
        else:
            # IDF = log((N - 1 + 0.5) / (1 + 0.5) + 1)
            idf = math.log((total_docs - 1 + 0.5) / (1 + 0.5) + 1)
            cursor.execute(
                """
                INSERT INTO vocabulary (word, idf, doc_freq) VALUES (?, ?, 1)
            """,
                (word, idf),
            )

    def _recalculate_all_idf(self):
        """重新计算所有词汇的IDF值"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 获取总文档数
            cursor.execute("SELECT COUNT(*) as cnt FROM documents")
            total_docs = cursor.fetchone()["cnt"]

            if total_docs == 0:
                return

            # 获取所有词汇及其文档频率
            cursor.execute("SELECT word, doc_freq FROM vocabulary")
            for row in cursor.fetchall():
                word = row["word"]
                doc_freq = row["doc_freq"]
                # IDF = log((N - n + 0.5) / (n + 0.5) + 1)
                idf = math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
                cursor.execute(
                    "UPDATE vocabulary SET idf = ? WHERE word = ?", (idf, word)
                )

            conn.commit()

    def add(self, text: str, metadata: Dict[str, Any]) -> int:
        """
        添加文档到向量存储

        Args:
            text: 文档文本
            metadata: 元数据

        Returns:
            文档ID
        """
        tokens = self._tokenize(text)
        tf = self._compute_tf(tokens)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 获取当前文档总数
            cursor.execute("SELECT COUNT(*) as cnt FROM documents")
            total_docs = cursor.fetchone()["cnt"] + 1  # +1 for new document

            # 插入文档
            cursor.execute(
                """
                INSERT INTO documents (text, metadata_json, created_at, doc_length)
                VALUES (?, ?, ?, ?)
            """,
                (
                    text,
                    json.dumps(metadata, ensure_ascii=False),
                    datetime.now().isoformat(),
                    len(text),
                ),
            )

            doc_id = cursor.lastrowid

            # 插入词频记录并更新IDF
            for word, freq in tf.items():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO doc_terms (doc_id, word, tf)
                    VALUES (?, ?, ?)
                """,
                    (doc_id, word, freq),
                )

                # 更新IDF（使用同一连接）
                self._update_idf(conn, word, total_docs)

            conn.commit()

        return doc_id

    def _compute_tfidf(self, text: str) -> Dict[str, float]:
        """
        计算文本的TF-IDF向量

        Args:
            text: 文本

        Returns:
            TF-IDF向量字典 {word: tfidf_score}
        """
        tokens = self._tokenize(text)
        tf = self._compute_tf(tokens)

        # 获取总文档数
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM documents")
            total_docs = cursor.fetchone()["cnt"]

            # 计算TF-IDF
            tfidf = {}
            for word, term_freq in tf.items():
                # TF = 1 + log(tf)
                tf_score = 1 + math.log(term_freq) if term_freq > 0 else 0

                # 获取IDF
                cursor.execute("SELECT idf FROM vocabulary WHERE word = ?", (word,))
                row = cursor.fetchone()
                idf = row["idf"] if row else 0

                tfidf[word] = tf_score * idf

        return tfidf

    def _cosine_similarity(
        self, vec1: Dict[str, float], vec2: Dict[str, float]
    ) -> float:
        """
        计算余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            余弦相似度
        """
        if not vec1 or not vec2:
            return 0.0

        # 找出公共词汇
        common_words = set(vec1.keys()) & set(vec2.keys())

        if not common_words:
            return 0.0

        # 计算点积
        dot_product = sum(vec1[word] * vec2[word] for word in common_words)

        # 计算模长
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _get_doc_terms(self, doc_id: int) -> Dict[str, int]:
        """获取文档的词频"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT word, tf FROM doc_terms WHERE doc_id = ?
            """,
                (doc_id,),
            )

            return {row["word"]: row["tf"] for row in cursor.fetchall()}

    def _compute_bm25(
        self, query: str, doc_id: int, doc_length: int, avg_doc_length: float
    ) -> float:
        """
        计算BM25分数

        Args:
            query: 查询文本
            doc_id: 文档ID
            doc_length: 文档长度
            avg_doc_length: 平均文档长度

        Returns:
            BM25分数
        """
        query_tokens = self._tokenize(query)
        doc_terms = self._get_doc_terms(doc_id)

        if not doc_terms:
            return 0.0

        score = 0.0

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM documents")
            N = cursor.fetchone()["cnt"]

            for token in query_tokens:
                # 获取词频
                tf = doc_terms.get(token, 0)

                if tf == 0:
                    continue

                # 获取文档频率
                cursor.execute(
                    "SELECT doc_freq FROM vocabulary WHERE word = ?", (token,)
                )
                row = cursor.fetchone()
                if not row:
                    continue

                df = row["doc_freq"]

                # IDF
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

                # BM25公式
                tf_component = (tf * (self.BM25_K1 + 1)) / (
                    tf
                    + self.BM25_K1
                    * (1 - self.BM25_B + self.BM25_B * doc_length / avg_doc_length)
                )

                score += idf * tf_component

        return score

    def search(
        self, query: str, k: int = 5, method: str = "tfidf"
    ) -> List[SearchResult]:
        """
        搜索相似文档

        Args:
            query: 查询文本
            k: 返回结果数量
            method: 排序方法 ("tfidf" 或 "bm25")

        Returns:
            搜索结果列表
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 获取所有文档
            cursor.execute("""
                SELECT id, text, metadata_json, created_at, doc_length 
                FROM documents
            """)

            docs = cursor.fetchall()

            if not docs:
                return []

            # 计算平均文档长度
            avg_doc_length = sum(doc["doc_length"] for doc in docs) / len(docs)

            # 计算查询的TF-IDF向量
            query_tfidf = self._compute_tfidf(query)

            results = []

            for doc in docs:
                if method == "tfidf":
                    # 获取文档的TF-IDF向量
                    doc_tfidf = self._compute_tfidf(doc["text"])
                    score = self._cosine_similarity(query_tfidf, doc_tfidf)
                else:  # bm25
                    score = self._compute_bm25(
                        query, doc["id"], doc["doc_length"], avg_doc_length
                    )

                results.append(
                    SearchResult(
                        doc_id=doc["id"],
                        text=doc["text"],
                        metadata=json.loads(doc["metadata_json"]),
                        score=score,
                        created_at=doc["created_at"],
                    )
                )

            # 排序并返回top-k
            results.sort(key=lambda x: x.score, reverse=True)

            return results[:k]

    def get(self, doc_id: int) -> Optional[SearchResult]:
        """
        获取指定文档

        Args:
            doc_id: 文档ID

        Returns:
            文档或None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, text, metadata_json, created_at
                FROM documents WHERE id = ?
            """,
                (doc_id,),
            )

            row = cursor.fetchone()
            if row:
                return SearchResult(
                    doc_id=row["id"],
                    text=row["text"],
                    metadata=json.loads(row["metadata_json"]),
                    score=1.0,
                    created_at=row["created_at"],
                )
            return None

    def delete(self, doc_id: int) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档ID

        Returns:
            是否成功
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 删除文档
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

            # 删除关联的词频记录
            cursor.execute("DELETE FROM doc_terms WHERE doc_id = ?", (doc_id,))

            conn.commit()

            # 重新计算IDF
            self._recalculate_all_idf()

            return cursor.rowcount > 0

    def count(self) -> int:
        """
        获取文档总数

        Returns:
            文档数量
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM documents")
            return cursor.fetchone()["cnt"]

    def clear(self):
        """清空所有数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM doc_terms")
            cursor.execute("DELETE FROM vocabulary")
            cursor.execute("DELETE FROM documents")
            conn.commit()
