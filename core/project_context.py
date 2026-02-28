"""
NovelProject - 领域模型抽象
封装所有小说项目的文件系统操作，实现依赖倒置
"""

from pathlib import Path
import json
from typing import Optional


class NovelProject:
    """
    小说项目领域模型
    封装项目目录结构和所有文件IO操作
    """

    def __init__(self, project_dir: str | Path):
        self.path = Path(project_dir)
        self.path.mkdir(parents=True, exist_ok=True)

    # ===== 属性路径 =====

    @property
    def config_path(self) -> Path:
        """项目配置文件路径"""
        return self.path / "project_config.json"

    @property
    def outline_path(self) -> Path:
        """大纲文件路径"""
        return self.path / "outline.md"

    @property
    def characters_path(self) -> Path:
        """人物设定文件路径"""
        return self.path / "characters.json"

    @property
    def chapters_dir(self) -> Path:
        """章节目录"""
        d = self.path / "chapters"
        d.mkdir(exist_ok=True)
        return d

    @property
    def progress_path(self) -> Path:
        """进度文件路径"""
        return self.path / "novel-progress.txt"

    @property
    def emotion_ledger_path(self) -> Path:
        """情绪账本路径"""
        return self.path / "emotion_ledger.json"

    @property
    def world_bible_path(self) -> Path:
        """世界圣经路径"""
        return self.path / "world_bible.json"

    @property
    def suspended_path(self) -> Path:
        """挂起状态文件路径"""
        return self.path / ".suspended.json"

    @property
    def checkpoint_path(self) -> Path:
        """检查点文件路径"""
        return self.path / ".checkpoint.json"

    # ===== 配置读写 =====

    def load_config(self) -> dict:
        """加载项目配置"""
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def save_config(self, config: dict):
        """保存项目配置"""
        self.config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ===== 大纲读写 =====

    def load_outline(self) -> str:
        """加载大纲内容"""
        if self.outline_path.exists():
            try:
                return self.outline_path.read_text(encoding="utf-8")
            except IOError:
                pass
        return ""

    def save_outline(self, content: str):
        """保存大纲内容"""
        self.outline_path.write_text(content, encoding="utf-8")

    # ===== 人物设定读写 =====

    def load_characters(self) -> str:
        """加载人物设定"""
        if self.characters_path.exists():
            try:
                return self.characters_path.read_text(encoding="utf-8")
            except IOError:
                pass
        return ""

    def save_characters(self, content: str):
        """保存人物设定"""
        self.characters_path.write_text(content, encoding="utf-8")

    # ===== 章节操作 =====

    def get_chapter_path(self, chapter_num: int) -> Path:
        """获取指定章节的文件路径"""
        return self.chapters_dir / f"chapter_{chapter_num:04d}.txt"

    def load_chapter(self, chapter_num: int) -> Optional[str]:
        """加载指定章节内容"""
        chapter_path = self.get_chapter_path(chapter_num)
        if chapter_path.exists():
            try:
                return chapter_path.read_text(encoding="utf-8")
            except IOError:
                pass
        return None

    def save_chapter(self, chapter_num: int, content: str):
        """保存指定章节内容"""
        chapter_path = self.get_chapter_path(chapter_num)
        chapter_path.write_text(content, encoding="utf-8")

    def list_chapters(self) -> list[int]:
        """列出所有已存在的章节编号"""
        if not self.chapters_dir.exists():
            return []
        chapters = []
        for f in self.chapters_dir.glob("chapter_*.txt"):
            try:
                num = int(f.stem.replace("chapter_", ""))
                chapters.append(num)
            except ValueError:
                continue
        return sorted(chapters)

    # ===== 进度操作 =====

    def load_progress(self) -> dict:
        """加载进度信息"""
        if self.progress_path.exists():
            try:
                return json.loads(self.progress_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def save_progress(self, progress: dict):
        """保存进度信息"""
        self.progress_path.write_text(
            json.dumps(progress, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ===== 情绪账本操作 =====

    def load_emotion_ledger(self) -> dict:
        """加载情绪账本"""
        if self.emotion_ledger_path.exists():
            try:
                return json.loads(self.emotion_ledger_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def save_emotion_ledger(self, ledger: dict):
        """保存情绪账本"""
        self.emotion_ledger_path.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ===== 世界圣经操作 =====

    def load_world_bible(self) -> dict:
        """加载世界圣经"""
        if self.world_bible_path.exists():
            try:
                return json.loads(self.world_bible_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def save_world_bible(self, bible: dict):
        """保存世界圣经"""
        self.world_bible_path.write_text(
            json.dumps(bible, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ===== 挂起状态操作 =====

    def load_suspended_state(self) -> Optional[dict]:
        """加载挂起状态"""
        if self.suspended_path.exists():
            try:
                return json.loads(self.suspended_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return None

    def save_suspended_state(self, state: dict):
        """保存挂起状态"""
        self.suspended_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def clear_suspended_state(self):
        """清除挂起状态"""
        if self.suspended_path.exists():
            self.suspended_path.unlink()

    # ===== 检查点操作 =====

    def load_checkpoint(self) -> Optional[dict]:
        """加载检查点"""
        if self.checkpoint_path.exists():
            try:
                return json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return None

    def save_checkpoint(self, checkpoint: dict):
        """保存检查点"""
        self.checkpoint_path.write_text(
            json.dumps(checkpoint, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ===== 工具方法 =====

    def exists(self) -> bool:
        """检查项目目录是否存在"""
        return self.path.exists() and self.path.is_dir()

    def is_valid(self) -> bool:
        """检查项目是否有效（至少有配置文件）"""
        return self.config_path.exists()

    def get_title(self) -> str:
        """获取项目标题"""
        config = self.load_config()
        return config.get("title", self.path.name)
