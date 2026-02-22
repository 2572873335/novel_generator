"""
Chapter State Store - YAML-based atomic chapter-level storage
Replaces single-file JSON progress for better performance with >100 chapters
"""

import os
import json
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# Try to import yaml, fall back to json if not available
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class ChapterState:
    """
    Chapter state dataclass - stores runtime state for each chapter

    Attributes:
        chapter_number: Chapter number (1-indexed)
        status: Chapter status (pending, writing, reviewing, completed, revision_needed)
        word_count: Current word count
        quality_score: Quality score (0.0 - 10.0)
        key_events: List of key events in this chapter
        entity_changes: Dictionary of entity state changes (realm, location, faction, etc.)
        created_at: ISO timestamp of creation
        updated_at: ISO timestamp of last update
        notes: Additional notes
    """

    chapter_number: int
    status: str = "pending"
    word_count: int = 0
    quality_score: float = 0.0
    key_events: List[str] = field(default_factory=list)
    entity_changes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    title: str = ""
    notes: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChapterState":
        """Create from dictionary"""
        return cls(**data)

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert to YAML-friendly dictionary (handles nested types)"""
        return {
            "chapter_number": self.chapter_number,
            "status": self.status,
            "word_count": self.word_count,
            "quality_score": self.quality_score,
            "key_events": self.key_events,
            "entity_changes": self.entity_changes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "title": self.title,
            "notes": self.notes,
        }


class ChapterStateStore:
    """
    Chapter State Store - Atomic YAML-based chapter state management

    Features:
        - Per-chapter YAML files for atomic updates
        - Atomic write operations (temp file → rename)
        - Backward compatibility with novel-progress.txt
        - Automatic migration support

    File structure:
        project_dir/
        ├── chapters/
        │   └── states/
        │       ├── chapter-001.yaml
        │       ├── chapter-002.yaml
        │       └── ...
        └── novel-progress.txt  # Kept as index for backward compatibility
    """

    def __init__(self, project_dir: str):
        """
        Initialize ChapterStateStore

        Args:
            project_dir: Path to the novel project directory
        """
        self.project_dir = project_dir
        self.states_dir = os.path.join(project_dir, "chapters", "states")
        self.progress_file = os.path.join(project_dir, "novel-progress.txt")

        # Ensure states directory exists
        os.makedirs(self.states_dir, exist_ok=True)

        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required for chapter state storage. "
                "Install with: pip install pyyaml"
            )

    def _get_state_file_path(self, chapter_num: int) -> str:
        """Get the YAML file path for a chapter"""
        return os.path.join(self.states_dir, f"chapter-{chapter_num:03d}.yaml")

    def _atomic_write(self, file_path: str, content: str) -> bool:
        """
        Atomic write: write to temp file, then rename

        Args:
            file_path: Target file path
            content: Content to write

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temp file in same directory (for atomic rename)
            dir_name = os.path.dirname(file_path)
            fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")

            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(content)

                # Atomic rename (works on same filesystem)
                shutil.move(temp_path, file_path)
                return True
            except Exception:
                # Clean up temp file on failure
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        except Exception as e:
            print(f"Atomic write failed: {e}")
            return False

    def get_chapter(self, chapter_num: int) -> Optional[ChapterState]:
        """
        Get chapter state

        Args:
            chapter_num: Chapter number

        Returns:
            ChapterState if exists, None otherwise
        """
        file_path = self._get_state_file_path(chapter_num)

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data:
                return ChapterState.from_dict(data)
            return None
        except Exception as e:
            print(f"Failed to load chapter {chapter_num}: {e}")
            return None

    def update_chapter(self, chapter_num: int, updates: Dict[str, Any]) -> bool:
        """
        Update chapter state atomically

        Args:
            chapter_num: Chapter number
            updates: Dictionary of updates to apply

        Returns:
            True if successful, False otherwise
        """
        # Load existing state or create new
        existing = self.get_chapter(chapter_num)

        if existing:
            # Update existing state
            state = existing
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            state.updated_at = datetime.now().isoformat()
        else:
            # Create new state
            state = ChapterState(
                chapter_number=chapter_num,
                **updates,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

        # Serialize to YAML
        try:
            content = yaml.dump(
                state.to_yaml_dict(),
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )
        except Exception as e:
            print(f"Failed to serialize chapter {chapter_num}: {e}")
            return False

        # Atomic write
        file_path = self._get_state_file_path(chapter_num)
        return self._atomic_write(file_path, content)

    def get_all_chapters(self) -> List[ChapterState]:
        """
        Get all chapter states

        Returns:
            List of ChapterState objects sorted by chapter number
        """
        if not os.path.exists(self.states_dir):
            return []

        chapters = []

        for filename in os.listdir(self.states_dir):
            if filename.startswith("chapter-") and filename.endswith(".yaml"):
                try:
                    chapter_num = int(filename[8:11])
                    state = self.get_chapter(chapter_num)
                    if state:
                        chapters.append(state)
                except (ValueError, IndexError):
                    continue

        # Sort by chapter number
        chapters.sort(key=lambda x: x.chapter_number)
        return chapters

    def create_chapter(self, chapter_num: int, title: str = "") -> bool:
        """
        Create a new chapter state

        Args:
            chapter_num: Chapter number
            title: Optional chapter title

        Returns:
            True if successful
        """
        return self.update_chapter(
            chapter_num, {"status": "pending", "title": title or f"第{chapter_num}章"}
        )

    def delete_chapter(self, chapter_num: int) -> bool:
        """
        Delete a chapter state

        Args:
            chapter_num: Chapter number

        Returns:
            True if successful
        """
        file_path = self._get_state_file_path(chapter_num)

        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
                return True
            except Exception as e:
                print(f"Failed to delete chapter {chapter_num}: {e}")
                return False
        return True

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all chapter states

        Returns:
            Dictionary with summary statistics
        """
        chapters = self.get_all_chapters()

        total = len(chapters)
        completed = sum(1 for ch in chapters if ch.status == "completed")
        total_words = sum(ch.word_count for ch in chapters)
        avg_quality = (
            sum(ch.quality_score for ch in chapters) / total if total > 0 else 0.0
        )

        return {
            "total_chapters": total,
            "completed_chapters": completed,
            "pending_chapters": total - completed,
            "total_word_count": total_words,
            "average_quality_score": round(avg_quality, 2),
            "last_updated": datetime.now().isoformat(),
        }

    def get_next_pending(self) -> Optional[ChapterState]:
        """
        Get the next pending chapter

        Returns:
            Next pending ChapterState or None
        """
        chapters = self.get_all_chapters()

        for ch in chapters:
            if ch.status == "pending":
                return ch

        return None

    def exists(self, chapter_num: int) -> bool:
        """Check if chapter state exists"""
        return os.path.exists(self._get_state_file_path(chapter_num))


# Backward compatibility alias
class ProgressManager:
    """
    Legacy ProgressManager - wrapper for backward compatibility

    This class provides compatibility with the old ProgressManager API
    while using the new ChapterStateStore under the hood.
    """

    def __init__(self, project_dir: str, progress_file: str = "novel-progress.txt"):
        self.project_dir = project_dir
        self.progress_file = os.path.join(project_dir, progress_file)
        self.store = ChapterStateStore(project_dir)

    def load_progress(self) -> Optional[Dict[str, Any]]:
        """Load progress from YAML stores"""
        chapters = self.store.get_all_chapters()

        if not chapters:
            return None

        # Try to load old JSON progress for metadata
        json_data = {}
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
            except Exception:
                pass

        # Build progress from YAML states
        return {
            "title": json_data.get("title", "Unknown"),
            "genre": json_data.get("genre", "general"),
            "total_chapters": len(chapters),
            "completed_chapters": sum(1 for ch in chapters if ch.status == "completed"),
            "current_chapter": next(
                (ch.chapter_number for ch in chapters if ch.status == "pending"), 1
            ),
            "total_word_count": sum(ch.word_count for ch in chapters),
            "start_date": json_data.get("start_date", datetime.now().isoformat()),
            "last_updated": datetime.now().isoformat(),
            "status": "writing"
            if any(ch.status != "completed" for ch in chapters)
            else "completed",
            "chapters": [ch.to_dict() for ch in chapters],
        }

    def get_chapter_progress(self, chapter_number: int) -> Optional[ChapterState]:
        """Get progress for specific chapter"""
        return self.store.get_chapter(chapter_number)

    def update_chapter_progress(self, chapter_number: int, **kwargs):
        """Update chapter progress"""
        return self.store.update_chapter(chapter_number, kwargs)

    def get_next_pending_chapter(self) -> Optional[ChapterState]:
        """Get next pending chapter"""
        return self.store.get_next_pending()

    def is_novel_complete(self) -> bool:
        """Check if novel is complete"""
        chapters = self.store.get_all_chapters()
        if not chapters:
            return False
        return all(ch.status == "completed" for ch in chapters)
