"""
Character State Machine for precise character tracking.

This module tracks character abilities, relationships, and states
with precise timestamps to support "valid abilities at chapter X" queries.

Key features:
- Track abilities with acquire/lose timestamps
- Track relationships with dynamic updates
- Support ability forgetting (injury, curse)
- Query valid abilities at specific chapters
- Maintain character state history
"""

import json
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


class AbilityStatus(Enum):
    """Status of an ability."""

    ACTIVE = "active"
    INACTIVE = "inactive"  # Temporarily unavailable
    LOST = "lost"  # Permanently lost
    FORGOTTEN = "forgotten"  # Intentionally forgotten


class RelationshipType(Enum):
    """Types of relationships between characters."""

    ALLY = "ally"
    ENEMY = "enemy"
    MENTOR = "mentor"
    STUDENT = "student"
    FRIEND = "friend"
    RIVAL = "rival"
    FAMILY = "family"
    ROMANTIC = "romantic"
    BUSINESS = "business"


@dataclass
class AbilityRecord:
    """Record of an ability with timestamps."""

    ability_id: str
    name: str
    description: str
    acquired_at: int  # Chapter number when acquired
    lost_at: Optional[int] = None  # Chapter number when lost (if any)
    status: AbilityStatus = AbilityStatus.ACTIVE
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelationshipRecord:
    """Record of a relationship between characters."""

    target_character_id: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0
    established_at: int  # Chapter number
    changed_at: Optional[int] = None  # Chapter number when last changed
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterState:
    """State of a character at a specific point in time."""

    character_id: str
    name: str
    chapter: int  # Current chapter number
    abilities: List[AbilityRecord] = field(default_factory=list)
    relationships: List[RelationshipRecord] = field(default_factory=list)
    location: Optional[str] = None
    faction: Optional[str] = None
    status: str = "alive"  # alive, injured, dead, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateSnapshot:
    """Snapshot of character states at a specific chapter."""

    chapter: int
    timestamp: datetime
    character_states: Dict[str, CharacterState]  # character_id -> CharacterState
    metadata: Dict[str, Any] = field(default_factory=dict)


class CharacterStateMachine:
    """State machine for tracking character states across chapters."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the character state machine.

        Args:
            data_dir: Directory to load/save state data (optional)
        """
        self.data_dir = data_dir or Path(".")
        self.state_history: Dict[int, StateSnapshot] = {}  # chapter -> snapshot
        self.current_chapter: int = 0
        self.characters: Dict[str, CharacterState] = {}  # character_id -> current state

        # Load existing data if available
        self._load_state()

    def _load_state(self):
        """Load state from disk if available."""
        state_file = self.data_dir / "character_states.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Load state history
                if "state_history" in data:
                    for chapter_str, snapshot_data in data["state_history"].items():
                        chapter = int(chapter_str)
                        self.state_history[chapter] = self._deserialize_snapshot(
                            snapshot_data
                        )

                # Load current chapter
                self.current_chapter = data.get("current_chapter", 0)

                # Load current character states
                if "characters" in data:
                    for char_id, state_data in data["characters"].items():
                        self.characters[char_id] = self._deserialize_character_state(
                            state_data
                        )

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Failed to load character state: {e}")
                # Start fresh
                self.state_history = {}
                self.current_chapter = 0
                self.characters = {}

    def save_state(self):
        """Save current state to disk."""
        state_file = self.data_dir / "character_states.json"

        data = {
            "current_chapter": self.current_chapter,
            "characters": {
                char_id: self._serialize_character_state(state)
                for char_id, state in self.characters.items()
            },
            "state_history": {
                str(chapter): self._serialize_snapshot(snapshot)
                for chapter, snapshot in self.state_history.items()
            },
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def _serialize_character_state(self, state: CharacterState) -> Dict[str, Any]:
        """Serialize a character state to dictionary."""
        return {
            "character_id": state.character_id,
            "name": state.name,
            "chapter": state.chapter,
            "abilities": [
                {
                    "ability_id": ability.ability_id,
                    "name": ability.name,
                    "description": ability.description,
                    "acquired_at": ability.acquired_at,
                    "lost_at": ability.lost_at,
                    "status": ability.status.value,
                    "tags": ability.tags,
                    "metadata": ability.metadata,
                }
                for ability in state.abilities
            ],
            "relationships": [
                {
                    "target_character_id": rel.target_character_id,
                    "relationship_type": rel.relationship_type.value,
                    "strength": rel.strength,
                    "established_at": rel.established_at,
                    "changed_at": rel.changed_at,
                    "description": rel.description,
                    "metadata": rel.metadata,
                }
                for rel in state.relationships
            ],
            "location": state.location,
            "faction": state.faction,
            "status": state.status,
            "metadata": state.metadata,
        }

    def _deserialize_character_state(self, data: Dict[str, Any]) -> CharacterState:
        """Deserialize a character state from dictionary."""
        abilities = []
        for ability_data in data.get("abilities", []):
            abilities.append(
                AbilityRecord(
                    ability_id=ability_data["ability_id"],
                    name=ability_data["name"],
                    description=ability_data["description"],
                    acquired_at=ability_data["acquired_at"],
                    lost_at=ability_data.get("lost_at"),
                    status=AbilityStatus(ability_data["status"]),
                    tags=ability_data.get("tags", []),
                    metadata=ability_data.get("metadata", {}),
                )
            )

        relationships = []
        for rel_data in data.get("relationships", []):
            relationships.append(
                RelationshipRecord(
                    target_character_id=rel_data["target_character_id"],
                    relationship_type=RelationshipType(rel_data["relationship_type"]),
                    strength=rel_data["strength"],
                    established_at=rel_data["established_at"],
                    changed_at=rel_data.get("changed_at"),
                    description=rel_data.get("description", ""),
                    metadata=rel_data.get("metadata", {}),
                )
            )

        return CharacterState(
            character_id=data["character_id"],
            name=data["name"],
            chapter=data["chapter"],
            abilities=abilities,
            relationships=relationships,
            location=data.get("location"),
            faction=data.get("faction"),
            status=data.get("status", "alive"),
            metadata=data.get("metadata", {}),
        )

    def _serialize_snapshot(self, snapshot: StateSnapshot) -> Dict[str, Any]:
        """Serialize a state snapshot to dictionary."""
        return {
            "chapter": snapshot.chapter,
            "timestamp": snapshot.timestamp.isoformat(),
            "character_states": {
                char_id: self._serialize_character_state(state)
                for char_id, state in snapshot.character_states.items()
            },
            "metadata": snapshot.metadata,
        }

    def _deserialize_snapshot(self, data: Dict[str, Any]) -> StateSnapshot:
        """Deserialize a state snapshot from dictionary."""
        character_states = {}
        for char_id, state_data in data["character_states"].items():
            character_states[char_id] = self._deserialize_character_state(state_data)

        return StateSnapshot(
            chapter=data["chapter"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            character_states=character_states,
            metadata=data.get("metadata", {}),
        )

    def add_character(self, character_id: str, name: str, **kwargs) -> CharacterState:
        """Add a new character to the state machine.

        Args:
            character_id: Unique identifier for the character
            name: Character name
            **kwargs: Additional character attributes

        Returns:
            The created character state
        """
        if character_id in self.characters:
            raise ValueError(f"Character {character_id} already exists")

        state = CharacterState(
            character_id=character_id, name=name, chapter=self.current_chapter, **kwargs
        )

        self.characters[character_id] = state
        return state

    def get_character(self, character_id: str) -> Optional[CharacterState]:
        """Get current state of a character.

        Args:
            character_id: Character identifier

        Returns:
            Character state or None if not found
        """
        return self.characters.get(character_id)

    def update_character(self, character_id: str, **kwargs) -> Optional[CharacterState]:
        """Update character attributes.

        Args:
            character_id: Character identifier
            **kwargs: Attributes to update

        Returns:
            Updated character state or None if not found
        """
        if character_id not in self.characters:
            return None

        state = self.characters[character_id]

        # Update allowed fields
        allowed_fields = {"location", "faction", "status", "metadata"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(state, field, value)
            elif field == "name":
                state.name = value

        return state

    def add_ability(
        self,
        character_id: str,
        ability_id: str,
        name: str,
        description: str = "",
        **kwargs,
    ) -> Optional[AbilityRecord]:
        """Add an ability to a character.

        Args:
            character_id: Character identifier
            ability_id: Unique ability identifier
            name: Ability name
            description: Ability description
            **kwargs: Additional ability attributes

        Returns:
            The created ability record or None if character not found
        """
        if character_id not in self.characters:
            return None

        state = self.characters[character_id]

        # Check if ability already exists
        for ability in state.abilities:
            if ability.ability_id == ability_id:
                # Update existing ability
                ability.name = name
                ability.description = description
                ability.status = AbilityStatus.ACTIVE
                ability.lost_at = None
                for key, value in kwargs.items():
                    if key == "tags":
                        ability.tags = value
                    elif key == "metadata":
                        ability.metadata.update(value)
                    else:
                        setattr(ability, key, value)
                return ability

        # Create new ability
        ability = AbilityRecord(
            ability_id=ability_id,
            name=name,
            description=description,
            acquired_at=self.current_chapter,
            **kwargs,
        )

        state.abilities.append(ability)
        return ability

    def lose_ability(
        self,
        character_id: str,
        ability_id: str,
        status: AbilityStatus = AbilityStatus.LOST,
    ) -> bool:
        """Mark an ability as lost or forgotten.

        Args:
            character_id: Character identifier
            ability_id: Ability identifier
            status: New status (LOST or FORGOTTEN)

        Returns:
            True if ability was found and updated
        """
        if character_id not in self.characters:
            return False

        state = self.characters[character_id]

        for ability in state.abilities:
            if (
                ability.ability_id == ability_id
                and ability.status == AbilityStatus.ACTIVE
            ):
                ability.status = status
                ability.lost_at = self.current_chapter
                return True

        return False

    def restore_ability(self, character_id: str, ability_id: str) -> bool:
        """Restore a lost ability.

        Args:
            character_id: Character identifier
            ability_id: Ability identifier

        Returns:
            True if ability was found and restored
        """
        if character_id not in self.characters:
            return False

        state = self.characters[character_id]

        for ability in state.abilities:
            if ability.ability_id == ability_id and ability.status in [
                AbilityStatus.LOST,
                AbilityStatus.INACTIVE,
            ]:
                ability.status = AbilityStatus.ACTIVE
                ability.lost_at = None
                return True

        return False

    def add_relationship(
        self,
        character_id: str,
        target_character_id: str,
        relationship_type: RelationshipType,
        strength: float = 0.5,
        description: str = "",
        **kwargs,
    ) -> Optional[RelationshipRecord]:
        """Add or update a relationship between characters.

        Args:
            character_id: Source character identifier
            target_character_id: Target character identifier
            relationship_type: Type of relationship
            strength: Relationship strength (0.0 to 1.0)
            description: Relationship description
            **kwargs: Additional relationship attributes

        Returns:
            The created/updated relationship record or None if character not found
        """
        if character_id not in self.characters:
            return None

        state = self.characters[character_id]

        # Check if relationship already exists
        for rel in state.relationships:
            if rel.target_character_id == target_character_id:
                # Update existing relationship
                rel.relationship_type = relationship_type
                rel.strength = max(0.0, min(1.0, strength))
                rel.changed_at = self.current_chapter
                if description:
                    rel.description = description
                for key, value in kwargs.items():
                    if key == "metadata":
                        rel.metadata.update(value)
                    else:
                        setattr(rel, key, value)
                return rel

        # Create new relationship
        relationship = RelationshipRecord(
            target_character_id=target_character_id,
            relationship_type=relationship_type,
            strength=max(0.0, min(1.0, strength)),
            established_at=self.current_chapter,
            description=description,
            **kwargs,
        )

        state.relationships.append(relationship)
        return relationship

    def update_relationship_strength(
        self, character_id: str, target_character_id: str, delta: float
    ) -> bool:
        """Update relationship strength by delta.

        Args:
            character_id: Source character identifier
            target_character_id: Target character identifier
            delta: Change in strength (-1.0 to 1.0)

        Returns:
            True if relationship was found and updated
        """
        if character_id not in self.characters:
            return False

        state = self.characters[character_id]

        for rel in state.relationships:
            if rel.target_character_id == target_character_id:
                new_strength = rel.strength + delta
                rel.strength = max(0.0, min(1.0, new_strength))
                rel.changed_at = self.current_chapter
                return True

        return False

    def get_valid_abilities(
        self, character_id: str, chapter: Optional[int] = None
    ) -> List[AbilityRecord]:
        """Get abilities valid at a specific chapter.

        Args:
            character_id: Character identifier
            chapter: Chapter number (defaults to current chapter)

        Returns:
            List of abilities valid at the specified chapter
        """
        if character_id not in self.characters:
            return []

        target_chapter = chapter if chapter is not None else self.current_chapter
        state = self.characters[character_id]

        valid_abilities = []
        for ability in state.abilities:
            # Ability must be acquired at or before target chapter
            if ability.acquired_at <= target_chapter:
                # Ability must not be lost before target chapter
                if ability.lost_at is None or ability.lost_at > target_chapter:
                    # Ability must be active
                    if ability.status == AbilityStatus.ACTIVE:
                        valid_abilities.append(ability)

        return valid_abilities

    def get_character_at_chapter(
        self, character_id: str, chapter: int
    ) -> Optional[CharacterState]:
        """Get character state at a specific chapter from history.

        Args:
            character_id: Character identifier
            chapter: Chapter number

        Returns:
            Character state at the specified chapter or None if not found
        """
        # Check current state if chapter is current
        if chapter == self.current_chapter:
            return self.characters.get(character_id)

        # Find the closest snapshot at or before the chapter
        snapshot_chapter = None
        for ch in sorted(self.state_history.keys(), reverse=True):
            if ch <= chapter:
                snapshot_chapter = ch
                break

        if snapshot_chapter is None:
            return None

        snapshot = self.state_history[snapshot_chapter]
        return snapshot.character_states.get(character_id)

    def advance_chapter(self, chapter: Optional[int] = None):
        """Advance to a new chapter and take a snapshot.

        Args:
            chapter: New chapter number (defaults to current_chapter + 1)
        """
        if chapter is None:
            chapter = self.current_chapter + 1
        elif chapter <= self.current_chapter:
            raise ValueError(
                f"Cannot advance to chapter {chapter} (current: {self.current_chapter})"
            )

        # Take snapshot of current state
        snapshot = StateSnapshot(
            chapter=self.current_chapter,
            timestamp=datetime.now(),
            character_states={
                char_id: CharacterState(
                    character_id=state.character_id,
                    name=state.name,
                    chapter=state.chapter,
                    abilities=state.abilities.copy(),
                    relationships=state.relationships.copy(),
                    location=state.location,
                    faction=state.faction,
                    status=state.status,
                    metadata=state.metadata.copy(),
                )
                for char_id, state in self.characters.items()
            },
        )

        self.state_history[self.current_chapter] = snapshot

        # Update current chapter
        self.current_chapter = chapter

        # Update all character states to new chapter
        for state in self.characters.values():
            state.chapter = chapter

        # Save state
        self.save_state()

    def get_character_history(
        self, character_id: str
    ) -> List[Tuple[int, CharacterState]]:
        """Get history of a character across chapters.

        Args:
            character_id: Character identifier

        Returns:
            List of (chapter, state) tuples in chronological order
        """
        history = []

        # Add historical states
        for chapter in sorted(self.state_history.keys()):
            snapshot = self.state_history[chapter]
            if character_id in snapshot.character_states:
                history.append((chapter, snapshot.character_states[character_id]))

        # Add current state
        if character_id in self.characters:
            history.append((self.current_chapter, self.characters[character_id]))

        return history

    def export_state(self, format: str = "json") -> Dict[str, Any]:
        """Export current state in specified format.

        Args:
            format: Export format ("json" only supported currently)

        Returns:
            State data in specified format
        """
        if format != "json":
            raise ValueError(f"Unsupported format: {format}")

        return {
            "current_chapter": self.current_chapter,
            "characters": {
                char_id: self._serialize_character_state(state)
                for char_id, state in self.characters.items()
            },
            "state_history": {
                str(chapter): self._serialize_snapshot(snapshot)
                for chapter, snapshot in self.state_history.items()
            },
        }

    def import_state(self, data: Dict[str, Any]):
        """Import state from data.

        Args:
            data: State data in export format
        """
        # Clear current state
        self.state_history = {}
        self.characters = {}

        # Load state history
        if "state_history" in data:
            for chapter_str, snapshot_data in data["state_history"].items():
                chapter = int(chapter_str)
                self.state_history[chapter] = self._deserialize_snapshot(snapshot_data)

        # Load current chapter
        self.current_chapter = data.get("current_chapter", 0)

        # Load current character states
        if "characters" in data:
            for char_id, state_data in data["characters"].items():
                self.characters[char_id] = self._deserialize_character_state(state_data)

        # Save to disk
        self.save_state()
