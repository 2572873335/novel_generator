"""
Scene-based text splitter for novel chapters.

Intelligent chunking based on scene boundaries - natural narrative units for RAG indexing.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Scene:
    """Represents a single scene in a chapter."""
    content: str
    start_line: int
    end_line: int
    chapter: int = 1
    metadata: Dict = field(default_factory=dict)


class SceneSplitter:
    """Splits novel text into scenes based on various delimiter patterns."""
    
    CHINESE_TRANSITIONS = [
        r"此时",
        r"忽然",
        r"就在这时",
        r"突然",
        r"就在此时",
        r"骤然",
        r"猛然",
        r"陡然",
        r"忽的",
        r"猛地",
        r"紧接着",
        r"随后",
        r"下一秒",
        r"片刻之后",
        r"片刻间",
        r"須臾",
        r"转眼间",
        r"刹那时",
    ]
    
    def __init__(self, chapter: int = 1):
        self.chapter = chapter
        self._header_pattern = re.compile(r"^#{1,6}\s+.+", re.MULTILINE)
        self._hr_pattern = re.compile(r"^---+$", re.MULTILINE)
        self._blank_line_pattern = re.compile(r"\n\s*\n\s*\n")
        self._transition_pattern = re.compile(
            r"(?<=[。！？])\s*(" + "|".join(self.CHINESE_TRANSITIONS) + r")",
            re.MULTILINE
        )
    
    def split(self, content: str) -> List[Scene]:
        """Split content into scenes."""
        if not content or not content.strip():
            return []
        
        lines = content.split("\n")
        delimiter_lines = self._detect_delimiters(content)
        delimiter_lines.add(0)
        delimiter_lines.add(len(lines))
        
        sorted_delims = sorted(delimiter_lines)
        scenes = []
        
        for i in range(len(sorted_delims) - 1):
            start = sorted_delims[i]
            end = sorted_delims[i + 1]
            
            if start == end:
                continue
            
            scene_lines = lines[start:end]
            scene_content = "\n".join(scene_lines).strip()
            
            if not scene_content:
                continue
            
            metadata = self._extract_metadata(scene_content)
            
            scene = Scene(
                content=scene_content,
                start_line=start + 1,
                end_line=end,
                chapter=self.chapter,
                metadata=metadata
            )
            scenes.append(scene)
        
        return scenes
    
    def _detect_delimiters(self, content: str) -> set:
        """Detect all scene boundary lines."""
        lines = content.split("\n")
        delimiter_lines = set()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if self._header_pattern.match(stripped):
                delimiter_lines.add(i)
                continue
            
            if self._hr_pattern.match(stripped):
                delimiter_lines.add(i)
                continue
        
        for match in self._blank_line_pattern.finditer(content):
            before = content[:match.start()]
            line_num = before.count("\n")
            delimiter_lines.add(line_num)
        
        for match in self._transition_pattern.finditer(content):
            before = content[:match.start()]
            line_num = before.count("\n")
            if line_num < len(lines) - 1:
                delimiter_lines.add(line_num + 1)
        
        return delimiter_lines
    
    def _extract_metadata(self, scene_content: str) -> Dict:
        """Extract metadata from scene content."""
        metadata = {
            "characters": [],
            "location": None,
            "time_period": None,
            "items": []
        }
        
        name_patterns = [
            r'"([^"]+)"',
            r'(\w+)说道',
            r'(\w+)说道：',
            r'(\w+)道：',
            r'(\w+)问道',
            r'(\w+)答道',
        ]
        
        characters = set()
        for pattern in name_patterns:
            for match in re.finditer(pattern, scene_content):
                name = match.group(1)
                if len(name) >= 2 and len(name) <= 4:
                    characters.add(name)
        
        metadata["characters"] = list(characters)
        
        location_keywords = ["在", "于", "来到", "前往", "回到", "踏入", "走进", "出现在"]
        location_pattern = "|".join(location_keywords)
        location_match = re.search(
            rf'({location_pattern})([^，。！？,.]+)',
            scene_content
        )
        if location_match:
            location = location_match.group(2).strip()
            location = re.sub(r'[的中了]$', '', location)
            if location:
                metadata["location"] = location
        
        time_keywords = [
            r"(\w+时间|\w+时分|\w+时刻)",
            r"(清晨|中午|午后|傍晚|深夜|夜晚|黎明|黄昏|日出|日落)",
            r"(春|夏|秋|冬|年初|年末|月底|月初)",
            r"(第\d+天|第\d+日|修炼了\d+天|过了\d+天)",
        ]
        
        for kw in time_keywords:
            match = re.search(kw, scene_content)
            if match:
                metadata["time_period"] = match.group(1)
                break
        
        item_keywords = [
            r"（([^）]+)）",
            r"手持(.+?)[，]",
            r"拿着(.+?)[，]",
            r"运转(.+?)功",
            r"催动(.+?)[，]",
        ]
        
        items = set()
        for pattern in item_keywords:
            for match in re.finditer(pattern, scene_content):
                item = match.group(1).strip()
                if item and len(item) < 20:
                    items.add(item)
        
        metadata["items"] = list(items)
        
        return metadata


def split_into_scenes(content: str, chapter: int = 1) -> List[Scene]:
    """Quick function to split content into scenes."""
    splitter = SceneSplitter(chapter=chapter)
    return splitter.split(content)


if __name__ == "__main__":
    test_content = """### 场景一
少年站在山巅，望着远方的云海。

###

### 场景二  
青云宗的大门缓缓打开，一位老者走了出来。
"""

    splitter = SceneSplitter()
    scenes = splitter.split(test_content)
    
    assert len(scenes) >= 2, f"Expected 2+ scenes, got {len(scenes)}"
    print(f"QA PASSED: {len(scenes)} scenes detected")
    
    for i, scene in enumerate(scenes):
        print(f"\n--- Scene {i+1} (lines {scene.start_line}-{scene.end_line}) ---")
        print(scene.content[:100] + "..." if len(scene.content) > 100 else scene.content)
        print(f"Metadata: {scene.metadata}")
