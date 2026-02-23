"""
SeniorEditor v2 - Semantic Analysis Edition
èµ·ç‚¹é‡‘ç‰Œèµ„æ·±ç¼–è¾‘ã€Œé”è¯„å®˜ã€v2 - åŸºäºŽLLMçš„è¯­ä¹‰åŒ–å®¡ç¨¿ç³»ç»Ÿ

é›†æˆæ–‡å­¦åˆ†æžã€æƒ…æ„Ÿè¯„åˆ†ã€å™äº‹è§†è§’æ£€æµ‹ã€é»„é‡‘ä¸‰ç« è¯­ä¹‰è¯„ä¼°
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime
import statistics


class ChapterType(Enum):
    """ç« èŠ‚ç±»åž‹æžšä¸¾ï¼ˆè¯­ä¹‰åŒ–åˆ†ç±»ï¼‰"""

    ACTION = "action"  # æˆ˜æ–—å†²çªåž‹ - é«˜å¼ åŠ›ï¼Œå¿«é€ŸèŠ‚å¥
    EMOTIONAL = "emotional"  # æƒ…æ„Ÿè¡¨è¾¾åž‹ - æ·±åº¦æƒ…æ„Ÿï¼Œäººç‰©å…³ç³»
    SETUP = "setup"  # é“ºåž«è®¾å®šåž‹ - ä¸–ç•Œè§‚å±•å¼€ï¼Œä¿¡æ¯ä¼ é€’
    TRANSITION = "transition"  # è¿‡æ¸¡è½¬åž‹åž‹ - æƒ…èŠ‚æŽ¨è¿›ï¼Œåœºæ™¯è½¬æ¢
    CLIMAX = "climax"  # é«˜æ½®çˆ†å‘åž‹ - æ ¸å¿ƒå†²çªï¼Œé‡å¤§è½¬æŠ˜
    RESOLUTION = "resolution"  # è§£å†³æ”¶å°¾åž‹ - å†²çªè§£å†³ï¼Œæƒ…æ„Ÿé‡Šæ”¾


class NarrativePerspective(Enum):
    """å™äº‹è§†è§’æžšä¸¾"""

    FIRST_PERSON = "first_person"  # ç¬¬ä¸€äººç§°
    THIRD_PERSON_LIMITED = "third_person_limited"  # ç¬¬ä¸‰äººç§°æœ‰é™
    THIRD_PERSON_OMNISCIENT = "third_person_omniscient"  # ç¬¬ä¸‰äººç§°å…¨çŸ¥
    SECOND_PERSON = "second_person"  # ç¬¬äºŒäººç§°ï¼ˆç½•è§ï¼‰
    MULTIPLE = "multiple"  # å¤šé‡è§†è§’


class EmotionalTone(Enum):
    """æƒ…æ„ŸåŸºè°ƒæžšä¸¾"""

    JOYFUL = "joyful"  # æ¬¢ä¹
    SAD = "sad"  # æ‚²ä¼¤
    ANGRY = "angry"  # æ„¤æ€’
    FEARFUL = "fearful"  # ææƒ§
    SUSPENSEFUL = "suspenseful"  # æ‚¬ç–‘
    ROMANTIC = "romantic"  # æµªæ¼«
    HEROIC = "heroic"  # è‹±é›„ä¸»ä¹‰
    TRAGIC = "tragic"  # æ‚²å‰§
    COMIC = "comic"  # å–œå‰§
    NEUTRAL = "neutral"  # ä¸­æ€§


@dataclass
class SemanticDimension:
    """è¯­ä¹‰åŒ–è¯„å®¡ç»´åº¦"""

    name: str
    score: float  # 0-10åˆ†
    confidence: float  # 0-1ç½®ä¿¡åº¦
    analysis: str  # è¯­ä¹‰åˆ†æžæ–‡æœ¬
    key_phrases: List[str] = field(default_factory=list)  # å…³é”®çŸ­è¯­
    evidence: List[Dict[str, Any]] = field(default_factory=list)  # è¯æ®ç‰‡æ®µ


@dataclass
class ChapterSemanticAnalysis:
    """ç« èŠ‚è¯­ä¹‰åˆ†æž"""

    chapter_number: int
    chapter_type: ChapterType
    narrative_perspective: NarrativePerspective
    emotional_tones: List[EmotionalTone]
    emotional_intensity: float  # 0-1å¼ºåº¦
    pacing_score: float  # èŠ‚å¥è¯„åˆ† 0-10
    hook_strength: float  # é’©å­å¼ºåº¦ 0-10
    conflict_present: bool
    character_development: float  # è§’è‰²å‘å±•åº¦ 0-10
    world_building: float  # ä¸–ç•Œè§‚æž„å»º 0-10
    semantic_summary: str  # è¯­ä¹‰æ‘˜è¦
    key_scenes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GoldenThreeChaptersAnalysis:
    """é»„é‡‘ä¸‰ç« è¯­ä¹‰åˆ†æž"""

    first_500_words: Dict[str, Any]  # å‰500å­—åˆ†æž
    hook_density: float  # é’©å­å¯†åº¦ï¼ˆæ¯åƒå­—é’©å­æ•°ï¼‰
    protagonist_introduction: Dict[str, Any]  # ä¸»è§’å¼•å…¥åˆ†æž
    conflict_introduction: Dict[str, Any]  # å†²çªå¼•å…¥åˆ†æž
    gold_finger_reveal: Dict[str, Any]  # é‡‘æ‰‹æŒ‡äº®ç›¸åˆ†æž
    info_density_score: float  # ä¿¡æ¯å¯†åº¦è¯„åˆ† 0-10
    retention_prediction: float  # ç•™å­˜çŽ‡é¢„æµ‹ 0-1


@dataclass
class SeniorEditorReportV2:
    """èµ„æ·±ç¼–è¾‘å®¡ç¨¿æŠ¥å‘Š v2ï¼ˆè¯­ä¹‰åŒ–ç‰ˆæœ¬ï¼‰"""

    novel_title: str
    overall_score: float  # ç»¼åˆè¯„åˆ† 0-10
    semantic_dimensions: List[SemanticDimension]  # è¯­ä¹‰åŒ–ç»´åº¦
    golden_three_chapters: GoldenThreeChaptersAnalysis  # é»„é‡‘ä¸‰ç« åˆ†æž
    chapter_analyses: List[ChapterSemanticAnalysis]  # ç« èŠ‚è¯­ä¹‰åˆ†æž
    narrative_consistency: Dict[str, Any]  # å™äº‹ä¸€è‡´æ€§
    emotional_arc: Dict[str, Any]  # æƒ…æ„Ÿå¼§çº¿
    pacing_analysis: Dict[str, Any]  # èŠ‚å¥åˆ†æž
    fatal_flaws: List[Dict[str, Any]]  # è‡´å‘½ç¼ºé™·ï¼ˆè¯­ä¹‰åŒ–ï¼‰
    strengths: List[Dict[str, Any]]  # ä¼˜åŠ¿äº®ç‚¹ï¼ˆè¯­ä¹‰åŒ–ï¼‰
    improvement_plan: List[Dict[str, Any]]  # æ”¹è¿›è®¡åˆ’
    contract_recommendation: str  # ç­¾çº¦å»ºè®®
    market_positioning: Dict[str, Any]  # å¸‚åœºå®šä½åˆ†æž
    editor_insights: str  # ç¼–è¾‘æ·±åº¦æ´žå¯Ÿ


class SeniorEditorV2:
    """
    èµ·ç‚¹é‡‘ç‰Œèµ„æ·±ç¼–è¾‘ã€Œé”è¯„å®˜ã€v2
    åŸºäºŽLLMçš„è¯­ä¹‰åŒ–å®¡ç¨¿ç³»ç»Ÿ

    æ ¸å¿ƒç‰¹æ€§ï¼š
    1. æ–‡å­¦è¯­ä¹‰åˆ†æžï¼ˆéžå…³é”®è¯åŒ¹é…ï¼‰
    2. å™äº‹è§†è§’æ£€æµ‹
    3. æƒ…æ„Ÿå‚ä¸Žåº¦è¯„åˆ†
    4. é»„é‡‘ä¸‰ç« è¯­ä¹‰è¯„ä¼°
    5. ç« èŠ‚ç±»åž‹æ„ŸçŸ¥è¯„ä¼°
    6. å¸‚åœºå®šä½åˆ†æž
    """

    # è¯­ä¹‰åŒ–ç»´åº¦å®šä¹‰
    SEMANTIC_DIMENSIONS = {
        "narrative_engagement": {
            "name": "å™äº‹å¸å¼•åŠ›",
            "weight": 0.25,
            "description": "æ•…äº‹å™è¿°çš„å¸å¼•åŠ›å’Œæ²‰æµ¸æ„Ÿ",
        },
        "emotional_resonance": {
            "name": "æƒ…æ„Ÿå…±é¸£",
            "weight": 0.20,
            "description": "æƒ…æ„Ÿè¡¨è¾¾çš„çœŸå®žæ€§å’Œæ„ŸæŸ“åŠ›",
        },
        "structural_coherence": {
            "name": "ç»“æž„è¿žè´¯æ€§",
            "weight": 0.15,
            "description": "æƒ…èŠ‚ç»“æž„çš„é€»è¾‘æ€§å’Œè¿žè´¯æ€§",
        },
        "character_depth": {
            "name": "è§’è‰²æ·±åº¦",
            "weight": 0.15,
            "description": "è§’è‰²å¡‘é€ çš„ç«‹ä½“æ„Ÿå’Œå‘å±•å¼§çº¿",
        },
        "world_immersion": {
            "name": "ä¸–ç•Œè§‚æ²‰æµ¸",
            "weight": 0.10,
            "description": "ä¸–ç•Œè§‚æž„å»ºçš„å®Œæ•´æ€§å’Œå¯ä¿¡åº¦",
        },
        "market_appeal": {
            "name": "å¸‚åœºå¸å¼•åŠ›",
            "weight": 0.15,
            "description": "ä½œå“çš„å¸‚åœºå®šä½å’Œå•†ä¸šæ½œåŠ›",
        },
    }

    # ç« èŠ‚ç±»åž‹è¯„ä¼°æ¨¡æ¿
    CHAPTER_TYPE_TEMPLATES = {
        ChapterType.ACTION: {
            "pacing_weight": 0.4,
            "conflict_weight": 0.4,
            "emotional_weight": 0.2,
            "ideal_length": 2500,
        },
        ChapterType.EMOTIONAL: {
            "pacing_weight": 0.2,
            "conflict_weight": 0.3,
            "emotional_weight": 0.5,
            "ideal_length": 3000,
        },
        ChapterType.SETUP: {
            "pacing_weight": 0.3,
            "conflict_weight": 0.2,
            "emotional_weight": 0.2,
            "world_building_weight": 0.3,
            "ideal_length": 3500,
        },
        ChapterType.TRANSITION: {
            "pacing_weight": 0.4,
            "conflict_weight": 0.2,
            "emotional_weight": 0.2,
            "character_development_weight": 0.2,
            "ideal_length": 2000,
        },
    }

    def __init__(self, llm_client, project_dir: str):
        """
        åˆå§‹åŒ–SeniorEditor v2

        Args:
            llm_client: LLMå®¢æˆ·ç«¯
            project_dir: é¡¹ç›®ç›®å½•è·¯å¾„
        """
        self.llm = llm_client
        self.project_dir = Path(project_dir)
        self.chapters_dir = self.project_dir / "chapters"
        self.novel_info = {}
        self._load_project_info()

    def _load_project_info(self):
        """åŠ è½½é¡¹ç›®ä¿¡æ¯"""
        progress_file = self.project_dir / "novel-progress.txt"
        if progress_file.exists():
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.novel_info = {
                        "title": data.get("title", "æœªçŸ¥ä½œå“"),
                        "genre": data.get("genre", "æœªçŸ¥ç±»åž‹"),
                        "total_chapters": data.get("total_chapters", 0),
                        "completed_chapters": data.get("completed_chapters", 0),
                        "total_word_count": data.get("total_word_count", 0),
                    }
            except Exception as e:
                print(f"åŠ è½½é¡¹ç›®ä¿¡æ¯å¤±è´¥: {e}")
                self.novel_info = {"title": "æœªçŸ¥ä½œå“", "genre": "æœªçŸ¥ç±»åž‹"}

    def review_novel(
        self, chapter_range: Tuple[int, int] = None
    ) -> SeniorEditorReportV2:
        """
        å¯¹å°è¯´è¿›è¡Œè¯­ä¹‰åŒ–å…¨é¢å®¡ç¨¿

        Args:
            chapter_range: å®¡ç¨¿ç« èŠ‚èŒƒå›´ï¼Œå¦‚(1, 20)

        Returns:
            SeniorEditorReportV2: è¯­ä¹‰åŒ–å®¡ç¨¿æŠ¥å‘Š
        """
        print(f"\n{'=' * 70}")
        print("ðŸ“‹ èµ·ç‚¹é‡‘ç‰Œèµ„æ·±ç¼–è¾‘ã€Œé”è¯„å®˜ã€v2 - è¯­ä¹‰åŒ–å®¡ç¨¿ç³»ç»Ÿ")
        print("=" * 70)
        print(f"ä½œå“: {self.novel_info.get('title', 'æœªçŸ¥')}")
        print(f"ç±»åž‹: {self.novel_info.get('genre', 'æœªçŸ¥')}")
        print("=" * 70)

        # åŠ è½½ç« èŠ‚å†…å®¹
        chapters_content = self._load_chapters(chapter_range)
        if not chapters_content:
            print("âŒ æ— æ³•åŠ è½½ç« èŠ‚å†…å®¹")
            return self._create_empty_report()

        print(f"ðŸ“š åŠ è½½äº† {len(chapters_content)} ä¸ªç« èŠ‚è¿›è¡Œè¯­ä¹‰åˆ†æž")

        # æ‰§è¡Œè¯­ä¹‰åŒ–åˆ†æž
        print("\n[1/6] ðŸ” æ‰§è¡Œç« èŠ‚è¯­ä¹‰åˆ†æž...")
        chapter_analyses = self._analyze_chapters_semantically(chapters_content)

        print("[2/6] ðŸ† è¯„ä¼°é»„é‡‘ä¸‰ç« ...")
        golden_three = self._analyze_golden_three_chapters(chapters_content)

        print("[3/6] ðŸ“Š è¯„ä¼°è¯­ä¹‰åŒ–ç»´åº¦...")
        semantic_dimensions = self._evaluate_semantic_dimensions(
            chapters_content, chapter_analyses
        )

        print("[4/6] ðŸ“ˆ åˆ†æžå™äº‹ä¸€è‡´æ€§...")
        narrative_consistency = self._analyze_narrative_consistency(chapter_analyses)

        print("[5/6] ðŸ’– åˆ†æžæƒ…æ„Ÿå¼§çº¿...")
        emotional_arc = self._analyze_emotional_arc(chapter_analyses)

        print("[6/6] âš¡ åˆ†æžèŠ‚å¥æ¨¡å¼...")
        pacing_analysis = self._analyze_pacing_patterns(chapter_analyses)

        # ç”Ÿæˆç»¼åˆæŠ¥å‘Š
        print("\nðŸ“ ç”Ÿæˆè¯­ä¹‰åŒ–å®¡ç¨¿æŠ¥å‘Š...")
        report = self._generate_semantic_report(
            semantic_dimensions,
            golden_three,
            chapter_analyses,
            narrative_consistency,
            emotional_arc,
            pacing_analysis,
        )

        print(f"\nâœ… å®¡ç¨¿å®Œæˆï¼ç»¼åˆè¯„åˆ†: {report.overall_score:.1f}/10.0")
        return report


    def _load_chapters(self, chapter_range: Tuple[int, int] = None) -> List[Dict[str, Any]]:
        """åŠ è½½ç« èŠ‚å†…å®¹"""
        chapters = []
        
        # ç¡®å®šç« èŠ‚èŒƒå›´
        if chapter_range:
            start, end = chapter_range
        else:
            # é»˜è®¤åŠ è½½å‰20ç« æˆ–æ‰€æœ‰å¯ç”¨ç« èŠ‚
            start = 1
            end = min(20, self.novel_info.get("completed_chapters", 20))
        
        for chapter_num in range(start, end + 1):
            chapter_file = self.chapters_dir / f"chapter-{chapter_num:03d}.md"
            if chapter_file.exists():
                try:
                    with open(chapter_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        chapters.append({
                            "chapter_number": chapter_num,
                            "content": content,
                            "word_count": len(content),
                            "file_path": str(chapter_file)
                        })
                except Exception as e:
                    print(f"åŠ è½½ç« èŠ‚ {chapter_num} å¤±è´¥: {e}")
        
        return chapters
    
    def _analyze_chapters_semantically(self, chapters: List[Dict[str, Any]]) -> List[ChapterSemanticAnalysis]:
        """å¯¹ç« èŠ‚è¿›è¡Œè¯­ä¹‰åˆ†æž"""
        analyses = []
        
        for chapter in chapters[:10]:  # é™åˆ¶åˆ†æžå‰10ç« ä»¥æŽ§åˆ¶æˆæœ¬
            print(f"  åˆ†æžç¬¬{chapter['chapter_number']}ç« ...")
            
            # ä½¿ç”¨LLMè¿›è¡Œè¯­ä¹‰åˆ†æž
            analysis_result = self._llm_semantic_analysis(chapter)
            
            if analysis_result:
                analyses.append(analysis_result)
            else:
                # å›žé€€åˆ†æž
                analyses.append(self._fallback_chapter_analysis(chapter))
        
        return analyses
    
    def _llm_semantic_analysis(self, chapter: Dict[str, Any]) -> Optional[ChapterSemanticAnalysis]:
        """ä½¿ç”¨LLMè¿›è¡Œç« èŠ‚è¯­ä¹‰åˆ†æž"""
        try:
            prompt = self._build_semantic_analysis_prompt(chapter)
            
            response = self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                system_prompt="ä½ æ˜¯ä¸“ä¸šçš„æ–‡å­¦åˆ†æžä¸“å®¶ï¼Œæ“…é•¿ä»Žè¯­ä¹‰å±‚é¢åˆ†æžå°è¯´ç« èŠ‚ã€‚",
                max_tokens=1500
            )
            
            # è§£æžLLMå“åº”
            return self._parse_semantic_analysis_response(response, chapter["chapter_number"])
            
        except Exception as e:
            print(f"LLMè¯­ä¹‰åˆ†æžå¤±è´¥: {e}")
            return None
    
    def _build_semantic_analysis_prompt(self, chapter: Dict[str, Any]) -> str:
        """æž„å»ºè¯­ä¹‰åˆ†æžæç¤ºè¯"""
        chapter_num = chapter["chapter_number"]
        content_preview = chapter["content"][:2000]  # é™åˆ¶å†…å®¹é•¿åº¦
        
        return f"""è¯·å¯¹ä»¥ä¸‹å°è¯´ç« èŠ‚è¿›è¡Œä¸“ä¸šçš„è¯­ä¹‰åˆ†æžï¼š

## ç« èŠ‚ä¿¡æ¯
- ç« èŠ‚ç¼–å·: ç¬¬{chapter_num}ç« 
- å†…å®¹é¢„è§ˆ: {content_preview[:500]}...ï¼ˆå…±{len(chapter['content'])}å­—ï¼‰

## åˆ†æžè¦æ±‚
è¯·ä»Žä»¥ä¸‹ç»´åº¦è¿›è¡Œè¯­ä¹‰åˆ†æžï¼š

### 1. ç« èŠ‚ç±»åž‹è¯†åˆ«
è¯·åˆ¤æ–­æœ¬ç« å±žäºŽå“ªç§ç±»åž‹ï¼š
- æˆ˜æ–—å†²çªåž‹ (ACTION): é«˜å¼ åŠ›ï¼Œå¿«é€ŸèŠ‚å¥ï¼Œæˆ˜æ–—åœºæ™¯ä¸ºä¸»
- æƒ…æ„Ÿè¡¨è¾¾åž‹ (EMOTIONAL): æ·±åº¦æƒ…æ„Ÿï¼Œäººç‰©å…³ç³»å‘å±•
- é“ºåž«è®¾å®šåž‹ (SETUP): ä¸–ç•Œè§‚å±•å¼€ï¼Œä¿¡æ¯ä¼ é€’
- è¿‡æ¸¡è½¬åž‹åž‹ (TRANSITION): æƒ…èŠ‚æŽ¨è¿›ï¼Œåœºæ™¯è½¬æ¢
- é«˜æ½®çˆ†å‘åž‹ (CLIMAX): æ ¸å¿ƒå†²çªï¼Œé‡å¤§è½¬æŠ˜
- è§£å†³æ”¶å°¾åž‹ (RESOLUTION): å†²çªè§£å†³ï¼Œæƒ…æ„Ÿé‡Šæ”¾

### 2. å™äº‹è§†è§’æ£€æµ‹
è¯·åˆ†æžæœ¬ç« ä½¿ç”¨çš„å™äº‹è§†è§’ï¼š
- ç¬¬ä¸€äººç§° (FIRST_PERSON): \"æˆ‘\"çš„è§†è§’
- ç¬¬ä¸‰äººç§°æœ‰é™ (THIRD_PERSON_LIMITED): è·Ÿéšç‰¹å®šè§’è‰²è§†è§’
- ç¬¬ä¸‰äººç§°å…¨çŸ¥ (THIRD_PERSON_OMNISCIENT): ä¸Šå¸è§†è§’
- ç¬¬äºŒäººç§° (SECOND_PERSON): \"ä½ \"çš„è§†è§’ï¼ˆç½•è§ï¼‰
- å¤šé‡è§†è§’ (MULTIPLE): åˆ‡æ¢ä¸åŒè§’è‰²è§†è§’

### 3. æƒ…æ„ŸåŸºè°ƒåˆ†æž
è¯·è¯†åˆ«æœ¬ç« çš„ä¸»è¦æƒ…æ„ŸåŸºè°ƒï¼ˆå¯å¤šé€‰ï¼‰ï¼š
- æ¬¢ä¹ (JOYFUL)
- æ‚²ä¼¤ (SAD)
- æ„¤æ€’ (ANGRY)
- ææƒ§ (FEARFUL)
- æ‚¬ç–‘ (SUSPENSEFUL)
- æµªæ¼« (ROMANTIC)
- è‹±é›„ä¸»ä¹‰ (HEROIC)
- æ‚²å‰§ (TRAGIC)
- å–œå‰§ (COMIC)
- ä¸­æ€§ (NEUTRAL)

### 4. å…³é”®æŒ‡æ ‡è¯„ä¼°ï¼ˆ0-10åˆ†ï¼‰
è¯·ç»™å‡ºä»¥ä¸‹æŒ‡æ ‡çš„è¯„åˆ†ï¼š
- æƒ…æ„Ÿå¼ºåº¦ (emotional_intensity): æƒ…æ„Ÿè¡¨è¾¾çš„å¼ºçƒˆç¨‹åº¦
- èŠ‚å¥è¯„åˆ† (pacing_score): æƒ…èŠ‚æŽ¨è¿›çš„èŠ‚å¥æ„Ÿ
- é’©å­å¼ºåº¦ (hook_strength): å¸å¼•è¯»è€…ç»§ç»­é˜…è¯»çš„èƒ½åŠ›
- è§’è‰²å‘å±•åº¦ (character_development): è§’è‰²æˆé•¿å’Œå˜åŒ–
- ä¸–ç•Œè§‚æž„å»º (world_building): ä¸–ç•Œè§‚ä¿¡æ¯çš„æœ‰æ•ˆä¼ é€’

### 5. è¯­ä¹‰æ‘˜è¦
è¯·ç”¨100å­—å·¦å³æ¦‚æ‹¬æœ¬ç« çš„æ ¸å¿ƒè¯­ä¹‰å†…å®¹ã€‚

### 6. å…³é”®åœºæ™¯
è¯·åˆ—å‡º2-3ä¸ªå…³é”®åœºæ™¯ï¼Œæ¯ä¸ªåœºæ™¯åŒ…å«ï¼š
- åœºæ™¯æè¿°
- æ ¸å¿ƒäº‹ä»¶
- æƒ…æ„Ÿä»·å€¼
- æƒ…èŠ‚ä½œç”¨

## è¾“å‡ºæ ¼å¼
è¯·ä»¥JSONæ ¼å¼è¾“å‡ºåˆ†æžç»“æžœï¼ŒåŒ…å«ä»¥ä¸‹å­—æ®µï¼š
{{
  \"chapter_type\": \"action|emotional|setup|transition|climax|resolution\",
  \"narrative_perspective\": \"first_person|third_person_limited|third_person_omniscient|second_person|multiple\",
  \"emotional_tones\": [\"joyful\", \"sad\", ...],
  \"emotional_intensity\": 0.8,
  \"pacing_score\": 7.5,
  \"hook_strength\": 8.0,
  \"conflict_present\": true,
  \"character_development\": 6.5,
  \"world_building\": 7.0,
  \"semantic_summary\": \"æœ¬ç« çš„è¯­ä¹‰æ‘˜è¦...\",
  \"key_scenes\": [
    {{
      \"description\": \"åœºæ™¯æè¿°\",
      \"core_event\": \"æ ¸å¿ƒäº‹ä»¶\",
      \"emotional_value\": \"æƒ…æ„Ÿä»·å€¼\",
      \"plot_role\": \"æƒ…èŠ‚ä½œç”¨\"
    }}
  ]
}}

è¯·ç›´æŽ¥è¾“å‡ºJSONï¼Œä¸è¦æ·»åŠ é¢å¤–è§£é‡Šã€‚"""
    
    def _parse_semantic_analysis_response(self, response: str, chapter_number: int) -> Optional[ChapterSemanticAnalysis]:
        """è§£æžè¯­ä¹‰åˆ†æžå“åº”"""
        try:
            # å°è¯•æå–JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return None
                
            data = json.loads(json_match.group())
            
            # è½¬æ¢æžšä¸¾ç±»åž‹
            chapter_type = ChapterType(data.get("chapter_type", "transition"))
            narrative_perspective = NarrativePerspective(data.get("narrative_perspective", "third_person_limited"))
            
            emotional_tones = []
            for tone_str in data.get("emotional_tones", []):
                try:
                    emotional_tones.append(EmotionalTone(tone_str))
                except:
                    pass
            
            return ChapterSemanticAnalysis(
                chapter_number=chapter_number,
                chapter_type=chapter_type,
                narrative_perspective=narrative_perspective,
                emotional_tones=emotional_tones,
                emotional_intensity=data.get("emotional_intensity", 0.5),
                pacing_score=data.get("pacing_score", 5.0),
                hook_strength=data.get("hook_strength", 5.0),
                conflict_present=data.get("conflict_present", False),
                character_development=data.get("character_development", 5.0),
                world_building=data.get("world_building", 5.0),
                semantic_summary=data.get("semantic_summary", ""),
                key_scenes=data.get("key_scenes", [])
            )
            
        except Exception as e:
            print(f"è§£æžè¯­ä¹‰åˆ†æžå“åº”å¤±è´¥: {e}")
            return None
    
    def _fallback_chapter_analysis(self, chapter: Dict[str, Any]) -> ChapterSemanticAnalysis:
        """å›žé€€ç« èŠ‚åˆ†æžï¼ˆå½“LLMåˆ†æžå¤±è´¥æ—¶ï¼‰"""
        content = chapter["content"]
        
        # ç®€å•å¯å‘å¼åˆ†æž
        chapter_type = self._detect_chapter_type_heuristic(content)
        narrative_perspective = self._detect_perspective_heuristic(content)
        emotional_tones = self._detect_emotional_tones_heuristic(content)
        
        return ChapterSemanticAnalysis(
            chapter_number=chapter["chapter_number"],
            chapter_type=chapter_type,
            narrative_perspective=narrative_perspective,
            emotional_tones=emotional_tones,
            emotional_intensity=0.5,
            pacing_score=5.0,
            hook_strength=5.0,
            conflict_present="æˆ˜æ–—" in content or "å†²çª" in content or "æŒ‘æˆ˜" in content,
            character_development=5.0,
            world_building=5.0,
            semantic_summary=f"ç¬¬{chapter['chapter_number']}ç« ï¼Œçº¦{len(content)}å­—",
            key_scenes=[]
        )
    
    def _detect_chapter_type_heuristic(self, content: str) -> ChapterType:
        """å¯å‘å¼æ£€æµ‹ç« èŠ‚ç±»åž‹"""
        content_lower = content.lower()
        
        # æˆ˜æ–—å…³é”®è¯
        action_keywords = ["æˆ˜æ–—", "åŽ®æ€", "å¯¹å†³", "æ¯”æ­¦", "æ”»å‡»", "é˜²å¾¡", "å‰‘", "åˆ€", "æ³•æœ¯"]
        if any(keyword in content_lower for keyword in action_keywords):
            return ChapterType.ACTION
        
        # æƒ…æ„Ÿå…³é”®è¯
        emotional_keywords = ["æƒ…æ„Ÿ", "æ„Ÿæƒ…", "çˆ±æƒ…", "å‹æƒ…", "äº²æƒ…", "æ„ŸåŠ¨", "æ³ªæ°´", "å¿ƒè·³"]
        if any(keyword in content_lower for keyword in emotional_keywords):
            return ChapterType.EMOTIONAL
        
        # è®¾å®šå…³é”®è¯
        setup_keywords = ["ä»‹ç»", "è¯´æ˜Ž", "èƒŒæ™¯", "åŽ†å²", "è§„åˆ™", "ä½“ç³»", "ä¸–ç•Œ", "è®¾å®š"]
        if any(keyword in content_lower for keyword in setup_keywords):
            return ChapterType.SETUP
        
        return ChapterType.TRANSITION
    
    def _detect_perspective_heuristic(self, content: str) -> NarrativePerspective:
        """å¯å‘å¼æ£€æµ‹å™äº‹è§†è§’"""
        # æ£€æŸ¥ç¬¬ä¸€äººç§°
        if "æˆ‘" in content[:500] and "æˆ‘ä»¬" not in content[:500]:
            return NarrativePerspective.FIRST_PERSON
        
        # æ£€æŸ¥ç¬¬äºŒäººç§°ï¼ˆç½•è§ï¼‰
        if "ä½ " in content[:500] and "ä½ ä»¬" not in content[:500]:
            return NarrativePerspective.SECOND_PERSON
        
        # é»˜è®¤ç¬¬ä¸‰äººç§°æœ‰é™
        return NarrativePerspective.THIRD_PERSON_LIMITED
    
    def _detect_emotional_tones_heuristic(self, content: str) -> List[EmotionalTone]:
        """å¯å‘å¼æ£€æµ‹æƒ…æ„ŸåŸºè°ƒ"""
        tones = []
        content_lower = content.lower()
        
        # ç®€å•å…³é”®è¯åŒ¹é…
        emotional_mapping = {
            EmotionalTone.JOYFUL: ["é«˜å…´", "å¿«ä¹", "æ¬¢ç¬‘", "å–œæ‚¦", "å¼€å¿ƒ"],
            EmotionalTone.SAD: ["æ‚²ä¼¤", "éš¾è¿‡", "æ³ªæ°´", "ç—›è‹¦", "ä¼¤å¿ƒ"],
            EmotionalTone.ANGRY: ["æ„¤æ€’", "ç”Ÿæ°”", "æ€’ç«", "æ„¤æ…¨", "æš´æ€’"],
            EmotionalTone.FEARFUL: ["ææƒ§", "å®³æ€•", "æƒŠæ", "ç•æƒ§", "ææ€–"],
            EmotionalTone.SUSPENSEFUL: ["æ‚¬å¿µ", "ç´§å¼ ", "æ‚¬ç–‘", "æœªçŸ¥", "è°œå›¢"],
            EmotionalTone.ROMANTIC: ["çˆ±æƒ…", "æµªæ¼«", "ç”œèœœ", "å¿ƒåŠ¨", "æ‹æƒ…"]
        }
        
        for tone, keywords in emotional_mapping.items():
            if any(keyword in content_lower for keyword in keywords):
                tones.append(tone)
        
        if not tones:
            tones.append(EmotionalTone.NEUTRAL)
        
        return tones
    
    def _analyze_golden_three_chapters(self, chapters: List[Dict[str, Any]]) -> GoldenThreeChaptersAnalysis:
        """åˆ†æžé»„é‡‘ä¸‰ç« """
        if len(chapters) < 3:
            return self._create_default_golden_three_analysis()
        
        first_three = chapters[:3]
        
        # åˆ†æžå‰500å­—
        first_500_words = self._analyze_first_500_words(first_three[0]["content"])
        
        # è®¡ç®—é’©å­å¯†åº¦
        hook_density = self._calculate_hook_density(first_three)
        
        # åˆ†æžä¸»è§’å¼•å…¥
        protagonist_intro = self._analyze_protagonist_introduction(first_three)
        
        # åˆ†æžå†²çªå¼•å…¥
        conflict_intro = self._analyze_conflict_introduction(first_three)
        
        # åˆ†æžé‡‘æ‰‹æŒ‡äº®ç›¸
        gold_finger = self._analyze_gold_finger_reveal(first_three)
        
        # è®¡ç®—ä¿¡æ¯å¯†åº¦
        info_density = self._calculate_info_density_score(first_three)
        
        # é¢„æµ‹ç•™å­˜çŽ‡
        retention = self._predict_retention_rate(
            first_500_words, hook_density, protagonist_intro, conflict_intro
        )
        
        return GoldenThreeChaptersAnalysis(
            first_500_words=first_500_words,
            hook_density=hook_density,
            protagonist_introduction=protagonist_intro,
            conflict_introduction=conflict_intro,
            gold_finger_reveal=gold_finger,
            info_density_score=info_density,
            retention_prediction=retention
        )
    
    def _analyze_first_500_words(self, content: str) -> Dict[str, Any]:
        """åˆ†æžå‰500å­—"""
        first_500 = content[:500]
        
        # ç®€å•åˆ†æž
        has_protagonist_name = any(keyword in first_500 for keyword in ["ä¸»è§’", "æž—", "çŽ‹", "æŽ", "å¼ ", "é™ˆ"])
        has_hook = "ï¼Ÿ" in first_500 or "!" in first_500 or "çªç„¶" in first_500 or "æ„å¤–" in first_500
        has_conflict = any(keyword in first_500 for keyword in ["å†²çª", "çŸ›ç›¾", "é—®é¢˜", "æŒ‘æˆ˜", "å±æœº"])
        
        return {
            "has_protagonist_name": has_protagonist_name,
            "has_hook": has_hook,
            "has_conflict": has_conflict,
            "word_count": len(first_500),
            "sentence_count": first_500.count("ã€‚") + first_500.count("ï¼") + first_500.count("ï¼Ÿ"),
            "analysis": "å‰500å­—åˆ†æžï¼ˆå¯å‘å¼ï¼‰"
        }
    
    def _calculate_hook_density(self, chapters: List[Dict[str, Any]]) -> float:
        """è®¡ç®—é’©å­å¯†åº¦ï¼ˆæ¯åƒå­—é’©å­æ•°ï¼‰"""
        total_words = sum(len(ch["content"]) for ch in chapters[:3])
        total_hooks = 0
        
        hook_patterns = [
            r"çªç„¶", r"æ„å¤–", r"æ²¡æƒ³åˆ°", r"ç«Ÿç„¶", r"å±…ç„¶",
            r"ï¼Ÿ", r"ï¼", r"â€¦â€¦", r"ç§˜å¯†", r"è°œå›¢",
            r"å±æœº", r"å±é™©", r"å¨èƒ", r"æŒ‘æˆ˜", r"å†²çª"
        ]
        
        for chapter in chapters[:3]:
            content = chapter["content"]
            for pattern in hook_patterns:
                total_hooks += len(re.findall(pattern, content))
        
        # æ¯åƒå­—é’©å­æ•°
        if total_words > 0:
            return (total_hooks / total_words) * 1000
        return 0.0
    
    def _analyze_protagonist_introduction(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """åˆ†æžä¸»è§’å¼•å…¥"""
        all_content = " ".join(ch["content"] for ch in chapters[:3])
        
        # ç®€å•å¯å‘å¼åˆ†æž
        has_name_early = False
        has_background = False
        has_motivation = False
        
        # æ£€æŸ¥å‰1000å­—æ˜¯å¦æœ‰å¸¸è§å§“æ°
        first_1000 = all_content[:1000]
        common_surnames = ["æž—", "çŽ‹", "æŽ", "å¼ ", "é™ˆ", "åˆ˜", "æ¨", "èµµ", "é»„", "å‘¨"]
        for surname in common_surnames:
            if surname in first_1000:
                has_name_early = True
                break
        
        # æ£€æŸ¥èƒŒæ™¯å…³é”®è¯
        background_keywords = ["ç©¿è¶Š", "é‡ç”Ÿ", "è½¬ä¸–", "å­¤å„¿", "å®¶æ—", "èº«ä¸–", "èƒŒæ™¯"]
        has_background = any(keyword in all_content for keyword in background_keywords)
        
        # æ£€æŸ¥åŠ¨æœºå…³é”®è¯
        motivation_keywords = ["ç›®æ ‡", "æ¢¦æƒ³", "æ„¿æœ›", "å¤ä»‡", "å˜å¼º", "ç”Ÿå­˜", "ä¿æŠ¤"]
        has_motivation = any(keyword in all_content for keyword in motivation_keywords)
        
        return {
            "has_name_early": has_name_early,
            "has_background": has_background,
            "has_motivation": has_motivation,
            "introduction_quality": "ä¸­ç­‰" if has_name_early else "éœ€æ”¹è¿›",
            "recommendations": ["ç¡®ä¿ä¸»è§’åœ¨å‰500å­—å†…å‡ºçŽ°å§“å"] if not has_name_early else []
        }
    
    def _analyze_conflict_introduction(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """åˆ†æžå†²çªå¼•å…¥"""
        all_content = " ".join(ch["content"] for ch in chapters[:3])
        
        has_conflict = any(keyword in all_content for keyword in ["å†²çª", "çŸ›ç›¾", "æˆ˜æ–—", "æŒ‘æˆ˜", "å±æœº", "æ•Œäºº"])
        conflict_early = any(keyword in chapters[0]["content"][:1000] for keyword in ["å†²çª", "çŸ›ç›¾", "æŒ‘æˆ˜"])
        
        conflict_types = []
        if "æˆ˜æ–—" in all_content or "åŽ®æ€" in all_content:
            conflict_types.append("æ­¦åŠ›å†²çª")
        if "é˜´è°‹" in all_content or "ç®—è®¡" in all_content:
            conflict_types.append("æ™ºåŠ›å†²çª")
        if "æƒ…æ„Ÿ" in all_content or "æ„Ÿæƒ…" in all_content:
            conflict_types.append("æƒ…æ„Ÿå†²çª")
        
        return {
            "has_conflict": has_conflict,
            "conflict_early": conflict_early,
            "conflict_types": conflict_types,
            "intensity": "ä¸­ç­‰" if has_conflict else "ä½Ž",
            "recommendations": ["ç¡®ä¿å‰3000å­—å†…å‡ºçŽ°æ ¸å¿ƒå†²çª"] if not conflict_early else []
        }
    
    def _analyze_gold_finger_reveal(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """åˆ†æžé‡‘æ‰‹æŒ‡äº®ç›¸"""
        all_content = " ".join(ch["content"] for ch in chapters[:3])
        
        # é‡‘æ‰‹æŒ‡å¸¸è§æ¨¡å¼
        gold_finger_patterns = [
            r"ç³»ç»Ÿ", r"é‡‘æ‰‹æŒ‡", r"å¤–æŒ‚", r"å¼‚èƒ½", r"ç‰¹æ®Šèƒ½åŠ›",
            r"å¤©èµ‹", r"ä½“è´¨", r"è¡€è„‰", r"ä¼ æ‰¿", r"ç¥žå™¨",
            r"è€çˆ·çˆ·", r"æˆ’æŒ‡", r"çŽ‰ä½©", r"ç©ºé—´", r"æ—¶é—´"
        ]
        
        has_gold_finger = False
        gold_finger_type = None
        
        for pattern in gold_finger_patterns:
            if re.search(pattern, all_content):
                has_gold_finger = True
                gold_finger_type = pattern
                break
        
        reveal_early = False
        if has_gold_finger:
            # æ£€æŸ¥æ˜¯å¦åœ¨å‰ä¸¤ç« å‡ºçŽ°
            first_two_content = " ".join(ch["content"] for ch in chapters[:2])
            for pattern in gold_finger_patterns:
                if re.search(pattern, first_two_content):
                    reveal_early = True
                    break
        
        return {
            "has_gold_finger": has_gold_finger,
            "gold_finger_type": gold_finger_type,
            "reveal_early": reveal_early,
            "recommendations": ["å»ºè®®åœ¨ç¬¬1ç« å±•ç¤ºé‡‘æ‰‹æŒ‡æ ¸å¿ƒåŠŸèƒ½"] if has_gold_finger and not reveal_early else []
        }
    
    def _calculate_info_density_score(self, chapters: List[Dict[str, Any]]) -> float:
        """è®¡ç®—ä¿¡æ¯å¯†åº¦è¯„åˆ†"""
        if not chapters:
            return 5.0
        
        # ç®€å•å¯å‘å¼ï¼šæ£€æŸ¥æ˜¯å¦æœ‰å¤§æ®µè¯´æ˜Žæ–‡
        all_content = " ".join(ch["content"] for ch in chapters[:3])
        
        # è®¡ç®—å¯¹è¯æ¯”ä¾‹ï¼ˆå¯¹è¯é€šå¸¸ä¿¡æ¯å¯†åº¦è¾ƒé«˜ï¼‰
        dialogue_ratio = len(re.findall(r'["ã€Œã€]', all_content)) / max(len(all_content), 1)
        
        # æ£€æŸ¥æ˜¯å¦æœ‰è¿žç»­500å­—æ— æƒ…èŠ‚æŽ¨è¿›ï¼ˆç®€å•å¯å‘å¼ï¼‰
        has_info_dumps = False
        for chapter in chapters[:3]:
            content = chapter["content"]
            # ç®€å•æ£€æŸ¥ï¼šè¿žç»­æ®µè½æ˜¯å¦éƒ½æ˜¯æè¿°æ€§æ–‡å­—
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if len(para) > 200 and "ã€‚" in para and "ï¼" not in para and "ï¼Ÿ" not in para:
                    # å¯èƒ½æ˜¯è¯´æ˜Žæ–‡æ®µè½
                    has_info_dumps = True
                    break
        
        # è¯„åˆ†é€»è¾‘
        score = 7.0  # åŸºç¡€åˆ†
        if dialogue_ratio > 0.2:
            score += 1.0  # å¯¹è¯å¤šï¼Œé€šå¸¸ä¿¡æ¯å¯†åº¦å¥½
        if has_info_dumps:
            score -= 2.0  # æœ‰å¤§æ®µè¯´æ˜Žæ–‡ï¼Œæ‰£åˆ†
        
        return max(0.0, min(10.0, score))
    
    def _predict_retention_rate(self, first_500: Dict[str, Any], hook_density: float,
                               protagonist_intro: Dict[str, Any], conflict_intro: Dict[str, Any]) -> float:
        """é¢„æµ‹ç•™å­˜çŽ‡ï¼ˆ0-1ï¼‰"""
        score = 0.5  # åŸºç¡€ç•™å­˜çŽ‡
        
        # å‰500å­—æœ‰ä¸»è§’å +0.1
        if first_500.get("has_protagonist_name"):
            score += 0.1
        
        # å‰500å­—æœ‰é’©å­ +0.05
        if first_500.get("has_hook"):
            score += 0.05
        
        # é’©å­å¯†åº¦é«˜ +0.1
        if hook_density > 3.0:  # æ¯åƒå­—3ä¸ªé’©å­
            score += 0.1
        
        # ä¸»è§’å¼•å…¥å¥½ +0.1
        if protagonist_intro.get("has_name_early") and protagonist_intro.get("has_motivation"):
            score += 0.1
        
        # å†²çªå¼•å…¥æ—© +0.15
        if conflict_intro.get("conflict_early"):
            score += 0.15
        
        return min(0.95, max(0.1, score))
    
    def _create_default_golden_three_analysis(self) -> GoldenThreeChaptersAnalysis:
        """åˆ›å»ºé»˜è®¤çš„é»„é‡‘ä¸‰ç« åˆ†æž"""
        return GoldenThreeChaptersAnalysis(
            first_500_words={"analysis": "ç« èŠ‚ä¸è¶³ï¼Œæ— æ³•åˆ†æžé»„é‡‘ä¸‰ç« "},
            hook_density=0.0,
            protagonist_introduction={"introduction_quality": "æœªçŸ¥"},
            conflict_introduction={"intensity": "æœªçŸ¥"},
            gold_finger_reveal={"has_gold_finger": False},
            info_density_score=5.0,
            retention_prediction=0.3
        )

    def _evaluate_semantic_dimensions(self, chapters: List[Dict[str, Any]], 
        chapter_analyses: List[ChapterSemanticAnalysis]) -> List[SemanticDimension]:
        """è¯„ä¼°è¯­ä¹‰åŒ–ç»´åº¦"""
        dimensions = []
        
        # æ”¶é›†æ‰€æœ‰ç« èŠ‚çš„æŒ‡æ ‡
        all_pacing_scores = [analysis.pacing_score for analysis in chapter_analyses]
        all_hook_strengths = [analysis.hook_strength for analysis in chapter_analyses]
        all_emotional_intensities = [analysis.emotional_intensity for analysis in chapter_analyses]
        all_character_dev = [analysis.character_development for analysis in chapter_analyses]
        all_world_building = [analysis.world_building for analysis in chapter_analyses]
        
        # è®¡ç®—å™äº‹å¸å¼•åŠ›ï¼ˆåŸºäºŽèŠ‚å¥å’Œé’©å­ï¼‰
        if all_pacing_scores and all_hook_strengths:
            narrative_score = (statistics.mean(all_pacing_scores) * 0.6 + 
                             statistics.mean(all_hook_strengths) * 0.4)
            narrative_dim = SemanticDimension(
                name="å™äº‹å¸å¼•åŠ›",
                score=narrative_score,
                confidence=0.8,
                analysis="åŸºäºŽèŠ‚å¥è¯„åˆ†å’Œé’©å­å¼ºåº¦çš„ç»¼åˆè¯„ä¼°",
                key_phrases=["èŠ‚å¥æŽ§åˆ¶", "æ‚¬å¿µè®¾ç½®", "æƒ…èŠ‚æŽ¨è¿›"],
                evidence=[
                    {"metric": "å¹³å‡èŠ‚å¥è¯„åˆ†", "value": statistics.mean(all_pacing_scores)},
                    {"metric": "å¹³å‡é’©å­å¼ºåº¦", "value": statistics.mean(all_hook_strengths)}
                ]
            )
            dimensions.append(narrative_dim)
        
        # è®¡ç®—æƒ…æ„Ÿå…±é¸£ï¼ˆåŸºäºŽæƒ…æ„Ÿå¼ºåº¦å’ŒåŸºè°ƒå¤šæ ·æ€§ï¼‰
        if all_emotional_intensities and chapter_analyses:
            emotional_score = statistics.mean(all_emotional_intensities) * 10
            # æ£€æŸ¥æƒ…æ„ŸåŸºè°ƒå¤šæ ·æ€§
            all_tones = []
            for analysis in chapter_analyses:
                all_tones.extend([tone.value for tone in analysis.emotional_tones])
            tone_diversity = len(set(all_tones)) / len(EmotionalTone) if all_tones else 0.5
            
            emotional_dim = SemanticDimension(
                name="æƒ…æ„Ÿå…±é¸£",
                score=emotional_score * 0.7 + tone_diversity * 10 * 0.3,
                confidence=0.7,
                analysis="åŸºäºŽæƒ…æ„Ÿå¼ºåº¦å’ŒåŸºè°ƒå¤šæ ·æ€§çš„æƒ…æ„Ÿè¡¨è¾¾è¯„ä¼°",
                key_phrases=["æƒ…æ„Ÿæ·±åº¦", "åŸºè°ƒå˜åŒ–", "è¯»è€…å…±é¸£"],
                evidence=[
                    {"metric": "å¹³å‡æƒ…æ„Ÿå¼ºåº¦", "value": statistics.mean(all_emotional_intensities)},
                    {"metric": "æƒ…æ„ŸåŸºè°ƒå¤šæ ·æ€§", "value": tone_diversity}
                ]
            )
            dimensions.append(emotional_dim)
        
        # è®¡ç®—ç»“æž„è¿žè´¯æ€§ï¼ˆåŸºäºŽç« èŠ‚ç±»åž‹åˆ†å¸ƒå’Œå†²çªè¿žç»­æ€§ï¼‰
        if chapter_analyses:
            # åˆ†æžç« èŠ‚ç±»åž‹åˆ†å¸ƒ
            type_counts = {}
            for analysis in chapter_analyses:
                type_name = analysis.chapter_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            # æ£€æŸ¥å†²çªè¿žç»­æ€§
            conflict_chapters = sum(1 for analysis in chapter_analyses if analysis.conflict_present)
            conflict_continuity = conflict_chapters / len(chapter_analyses)
            
            structural_score = 5.0  # åŸºç¡€åˆ†
            # ç±»åž‹åˆ†å¸ƒè¶Šå‡è¡¡ï¼Œç»“æž„è¶Šå¥½
            if len(type_counts) >= 3:
                structural_score += 2.0
            if conflict_continuity > 0.5:
                structural_score += 1.5
            
            structural_dim = SemanticDimension(
                name="ç»“æž„è¿žè´¯æ€§",
                score=structural_score,
                confidence=0.6,
                analysis="åŸºäºŽç« èŠ‚ç±»åž‹åˆ†å¸ƒå’Œå†²çªè¿žç»­æ€§çš„ç»“æž„è¯„ä¼°",
                key_phrases=["ç±»åž‹å¹³è¡¡", "å†²çªè¿žè´¯", "ç»“æž„è®¾è®¡"],
                evidence=[
                    {"metric": "ç« èŠ‚ç±»åž‹æ•°é‡", "value": len(type_counts)},
                    {"metric": "å†²çªç« èŠ‚æ¯”ä¾‹", "value": conflict_continuity}
                ]
            )
            dimensions.append(structural_dim)
        
        # è®¡ç®—è§’è‰²æ·±åº¦ï¼ˆåŸºäºŽè§’è‰²å‘å±•åº¦ï¼‰
        if all_character_dev:
            character_score = statistics.mean(all_character_dev)
            character_dim = SemanticDimension(
                name="è§’è‰²æ·±åº¦",
                score=character_score,
                confidence=0.7,
                analysis="åŸºäºŽè§’è‰²å‘å±•åº¦çš„è§’è‰²å¡‘é€ è¯„ä¼°",
                key_phrases=["è§’è‰²æˆé•¿", "åŠ¨æœºæ¸…æ™°", "ç«‹ä½“å¡‘é€ "],
                evidence=[
                    {"metric": "å¹³å‡è§’è‰²å‘å±•åº¦", "value": statistics.mean(all_character_dev)}
                ]
            )
            dimensions.append(character_dim)
        
        # è®¡ç®—ä¸–ç•Œè§‚æ²‰æµ¸ï¼ˆåŸºäºŽä¸–ç•Œè§‚æž„å»ºè¯„åˆ†ï¼‰
        if all_world_building:
            world_score = statistics.mean(all_world_building)
            world_dim = SemanticDimension(
                name="ä¸–ç•Œè§‚æ²‰æµ¸",
                score=world_score,
                confidence=0.6,
                analysis="åŸºäºŽä¸–ç•Œè§‚æž„å»ºè¯„åˆ†çš„æ²‰æµ¸æ„Ÿè¯„ä¼°",
                key_phrases=["è®¾å®šå®Œæ•´", "ç»†èŠ‚ä¸°å¯Œ", "å¯ä¿¡åº¦"],
                evidence=[
                    {"metric": "å¹³å‡ä¸–ç•Œè§‚æž„å»º", "value": statistics.mean(all_world_building)}
                ]
            )
            dimensions.append(world_dim)
        
        # è®¡ç®—å¸‚åœºå¸å¼•åŠ›ï¼ˆåŸºäºŽé»„é‡‘ä¸‰ç« åˆ†æžï¼‰
        if len(chapters) >= 3:
            golden_three = self._analyze_golden_three_chapters(chapters)
            market_score = golden_three.retention_prediction * 10
            market_dim = SemanticDimension(
                name="å¸‚åœºå¸å¼•åŠ›",
                score=market_score,
                confidence=0.5,
                analysis="åŸºäºŽé»„é‡‘ä¸‰ç« åˆ†æžå’Œç•™å­˜çŽ‡é¢„æµ‹çš„å¸‚åœºæ½œåŠ›è¯„ä¼°",
                key_phrases=["å¼€ç¯‡å¸å¼•åŠ›", "è¯»è€…ç•™å­˜", "å•†ä¸šæ½œåŠ›"],
                evidence=[
                    {"metric": "ç•™å­˜çŽ‡é¢„æµ‹", "value": golden_three.retention_prediction},
                    {"metric": "é’©å­å¯†åº¦", "value": golden_three.hook_density}
                ]
            )
            dimensions.append(market_dim)
        
        # å¦‚æžœç»´åº¦ä¸è¶³ï¼Œæ·»åŠ é»˜è®¤ç»´åº¦
        if not dimensions:
            for dim_id, dim_config in self.SEMANTIC_DIMENSIONS.items():
                dimensions.append(SemanticDimension(
                    name=dim_config["name"],
                    score=5.0,
                    confidence=0.3,
                    analysis="æ•°æ®ä¸è¶³ï¼Œä½¿ç”¨é»˜è®¤è¯„ä¼°",
                    key_phrases=["å¾…è¯„ä¼°"],
                    evidence=[]
                ))
        
        return dimensions

    def _analyze_narrative_consistency(self, chapter_analyses: List[ChapterSemanticAnalysis]) -> Dict[str, Any]:
        """åˆ†æžå™äº‹ä¸€è‡´æ€§"""
        if not chapter_analyses:
            return {"score": 5.0, "issues": [], "strengths": [], "analysis": "æ— ç« èŠ‚æ•°æ®"}
        
        issues = []
        strengths = []
        
        # æ£€æŸ¥å™äº‹è§†è§’ä¸€è‡´æ€§
        perspectives = [analysis.narrative_perspective for analysis in chapter_analyses]
        perspective_changes = 0
        for i in range(1, len(perspectives)):
            if perspectives[i] != perspectives[i-1]:
                perspective_changes += 1
        
        if perspective_changes > len(chapter_analyses) * 0.3:  # è¶…è¿‡30%çš„ç« èŠ‚æœ‰è§†è§’å˜åŒ–
            issues.append({"type": "å™äº‹è§†è§’", "severity": "ä¸­ç­‰", 
                          "description": "å™äº‹è§†è§’åˆ‡æ¢é¢‘ç¹ï¼Œå¯èƒ½å½±å“é˜…è¯»è¿žè´¯æ€§"})
        else:
            strengths.append({"aspect": "å™äº‹è§†è§’", "description": "å™äº‹è§†è§’ä¿æŒè¾ƒå¥½çš„ä¸€è‡´æ€§"})
        
        # æ£€æŸ¥ç« èŠ‚ç±»åž‹è¿‡æ¸¡åˆç†æ€§
        type_transitions = []
        for i in range(1, len(chapter_analyses)):
            prev_type = chapter_analyses[i-1].chapter_type
            curr_type = chapter_analyses[i].chapter_type
            type_transitions.append((prev_type, curr_type))
        
        # å®šä¹‰åˆç†çš„ç±»åž‹è¿‡æ¸¡
        valid_transitions = [
            (ChapterType.SETUP, ChapterType.ACTION),
            (ChapterType.SETUP, ChapterType.EMOTIONAL),
            (ChapterType.ACTION, ChapterType.EMOTIONAL),
            (ChapterType.EMOTIONAL, ChapterType.ACTION),
            (ChapterType.TRANSITION, ChapterType.ACTION),
            (ChapterType.TRANSITION, ChapterType.EMOTIONAL),
            (ChapterType.ACTION, ChapterType.CLIMAX),
            (ChapterType.CLIMAX, ChapterType.RESOLUTION)
        ]
        
        invalid_count = 0
        for prev, curr in type_transitions:
            if (prev, curr) not in valid_transitions and prev != curr:
                invalid_count += 1
        
        if invalid_count > 0:
            issues.append({"type": "ç« èŠ‚ç±»åž‹è¿‡æ¸¡", "severity": "ä½Ž", 
                          "description": f"{invalid_count}å¤„ç« èŠ‚ç±»åž‹è¿‡æ¸¡å¯èƒ½ä¸å¤Ÿè‡ªç„¶"})
        else:
            strengths.append({"aspect": "ç« èŠ‚ç±»åž‹è¿‡æ¸¡", "description": "ç« èŠ‚ç±»åž‹è¿‡æ¸¡è‡ªç„¶åˆç†"})
        
        # æ£€æŸ¥å†²çªè¿žç»­æ€§
        conflict_chapters = [i+1 for i, analysis in enumerate(chapter_analyses) if analysis.conflict_present]
        if conflict_chapters:
            # æ£€æŸ¥å†²çªé—´éš”
            gaps = []
            for i in range(1, len(conflict_chapters)):
                gap = conflict_chapters[i] - conflict_chapters[i-1]
                gaps.append(gap)
            
            if gaps:
                avg_gap = statistics.mean(gaps)
                if avg_gap > 3:
                    issues.append({"type": "å†²çªé—´éš”", "severity": "ä¸­ç­‰", 
                                  "description": f"å†²çªç« èŠ‚å¹³å‡é—´éš”{avg_gap:.1f}ç« ï¼Œå¯èƒ½å½±å“ç´§å¼ æ„Ÿ"})
                else:
                    strengths.append({"aspect": "å†²çªè¿žç»­æ€§", "description": "å†²çªè®¾ç½®åˆç†ï¼Œä¿æŒè¯»è€…ç´§å¼ æ„Ÿ"})
        
        # è®¡ç®—ä¸€è‡´æ€§è¯„åˆ†
        base_score = 7.0
        for issue in issues:
            if issue["severity"] == "é«˜":
                base_score -= 2.0
            elif issue["severity"] == "ä¸­ç­‰":
                base_score -= 1.0
            else:
                base_score -= 0.5
        
        for strength in strengths:
            base_score += 0.3
        
        return {
            "score": max(0.0, min(10.0, base_score)),
            "issues": issues,
            "strengths": strengths,
            "analysis": f"åˆ†æžäº†{len(chapter_analyses)}ä¸ªç« èŠ‚çš„å™äº‹ä¸€è‡´æ€§",
            "perspective_changes": perspective_changes,
            "invalid_transitions": invalid_count,
            "conflict_chapters": conflict_chapters
        }

    def _analyze_emotional_arc(self, chapter_analyses: List[ChapterSemanticAnalysis]) -> Dict[str, Any]:
        """åˆ†æžæƒ…æ„Ÿå¼§çº¿"""
        if not chapter_analyses:
            return {"score": 5.0, "arc_type": "æœªçŸ¥", "emotional_range": 0, "analysis": "æ— ç« èŠ‚æ•°æ®"}
        
        # æå–æƒ…æ„Ÿå¼ºåº¦åºåˆ—
        emotional_intensities = [analysis.emotional_intensity for analysis in chapter_analyses]
        
        # åˆ†æžæƒ…æ„ŸåŸºè°ƒå˜åŒ–
        tone_sequences = []
        for analysis in chapter_analyses:
            primary_tone = analysis.emotional_tones[0] if analysis.emotional_tones else EmotionalTone.NEUTRAL
            tone_sequences.append(primary_tone.value)
        
        # è®¡ç®—æƒ…æ„ŸèŒƒå›´ï¼ˆæƒ…æ„Ÿå¼ºåº¦çš„å˜åŒ–èŒƒå›´ï¼‰
        if emotional_intensities:
            emotional_range = max(emotional_intensities) - min(emotional_intensities)
        else:
            emotional_range = 0
        
        # è¯†åˆ«æƒ…æ„Ÿå¼§çº¿ç±»åž‹
        arc_type = "å¹³ç¨³åž‹"
        if len(emotional_intensities) >= 3:
            # æ£€æŸ¥æ˜¯å¦æœ‰æ˜Žæ˜¾çš„æƒ…æ„Ÿèµ·ä¼
            variations = []
            for i in range(1, len(emotional_intensities)):
                variation = abs(emotional_intensities[i] - emotional_intensities[i-1])
                variations.append(variation)
            
            avg_variation = statistics.mean(variations) if variations else 0
            if avg_variation > 0.3:
                arc_type = "èµ·ä¼åž‹"
            elif avg_variation < 0.1:
                arc_type = "å¹³ç¼“åž‹"
            
            # æ£€æŸ¥æ˜¯å¦æœ‰æƒ…æ„Ÿé«˜æ½®
            if max(emotional_intensities) > 0.8:
                arc_type += "ï¼ˆæœ‰é«˜æ½®ï¼‰"
        
        # åˆ†æžæƒ…æ„ŸåŸºè°ƒå¤šæ ·æ€§
        unique_tones = len(set(tone_sequences))
        tone_diversity = unique_tones / len(tone_sequences) if tone_sequences else 0
        
        # è®¡ç®—æƒ…æ„Ÿå¼§çº¿è¯„åˆ†
        score = 5.0  # åŸºç¡€åˆ†
        if emotional_range > 0.5:
            score += 2.0  # æƒ…æ„Ÿå˜åŒ–ä¸°å¯Œ
        if tone_diversity > 0.5:
            score += 1.5  # æƒ…æ„ŸåŸºè°ƒå¤šæ ·
        if arc_type != "å¹³ç¼“åž‹":
            score += 1.0  # æœ‰æƒ…æ„Ÿèµ·ä¼
        
        return {
            "score": min(10.0, score),
            "arc_type": arc_type,
            "emotional_range": emotional_range,
            "tone_diversity": tone_diversity,
            "intensity_sequence": emotional_intensities,
            "tone_sequence": tone_sequences,
            "analysis": f"æƒ…æ„Ÿå¼§çº¿ç±»åž‹ï¼š{arc_type}ï¼Œæƒ…æ„ŸèŒƒå›´ï¼š{emotional_range:.2f}ï¼ŒåŸºè°ƒå¤šæ ·æ€§ï¼š{tone_diversity:.2f}"
        }

    def _analyze_pacing_patterns(self, chapter_analyses: List[ChapterSemanticAnalysis]) -> Dict[str, Any]:
        """åˆ†æžèŠ‚å¥æ¨¡å¼"""
        if not chapter_analyses:
            return {"score": 5.0, "pacing_type": "æœªçŸ¥", "analysis": "æ— ç« èŠ‚æ•°æ®"}
        
        pacing_scores = [analysis.pacing_score for analysis in chapter_analyses]
        hook_strengths = [analysis.hook_strength for analysis in chapter_analyses]
        
        # è®¡ç®—èŠ‚å¥ç¨³å®šæ€§
        if len(pacing_scores) >= 2:
            pacing_variation = statistics.stdev(pacing_scores) if len(pacing_scores) > 1 else 0
        else:
            pacing_variation = 0
        
        # è¯†åˆ«èŠ‚å¥æ¨¡å¼
        pacing_type = "å‡è¡¡åž‹"
        if pacing_scores:
            avg_pacing = statistics.mean(pacing_scores)
            if avg_pacing > 7.5:
                pacing_type = "å¿«é€Ÿåž‹"
            elif avg_pacing < 4.5:
                pacing_type = "ç¼“æ…¢åž‹"
            
            if pacing_variation > 2.0:
                pacing_type += "ï¼ˆæ³¢åŠ¨è¾ƒå¤§ï¼‰"
        
        # åˆ†æžé’©å­åˆ†å¸ƒ
        hook_distribution = "å‡åŒ€"
        if hook_strengths:
            # æ£€æŸ¥æ˜¯å¦æœ‰ç« èŠ‚é’©å­å¼ºåº¦ç‰¹åˆ«ä½Ž
            weak_hooks = sum(1 for strength in hook_strengths if strength < 4.0)
            if weak_hooks > len(hook_strengths) * 0.3:
                hook_distribution = "ä¸å‡åŒ€ï¼ˆå¼±é’©å­è¾ƒå¤šï¼‰"
            elif weak_hooks == 0:
                hook_distribution = "ä¼˜ç§€ï¼ˆæ— å¼±é’©å­ï¼‰"
        
        # åˆ†æžèŠ‚å¥ä¸Žç« èŠ‚ç±»åž‹çš„å…³è”
        pacing_by_type = {}
        for analysis in chapter_analyses:
            type_name = analysis.chapter_type.value
            if type_name not in pacing_by_type:
                pacing_by_type[type_name] = []
            pacing_by_type[type_name].append(analysis.pacing_score)
        
        type_pacing_analysis = []
        for type_name, scores in pacing_by_type.items():
            if scores:
                type_pacing_analysis.append({
                    "type": type_name,
                    "avg_pacing": statistics.mean(scores),
                    "count": len(scores)
                })
        
        # è®¡ç®—èŠ‚å¥è¯„åˆ†
        score = 6.0  # åŸºç¡€åˆ†
        if pacing_type == "å¿«é€Ÿåž‹":
            score += 1.0
        if pacing_type == "å‡è¡¡åž‹":
            score += 0.5
        if pacing_variation < 1.5:
            score += 1.0  # èŠ‚å¥ç¨³å®š
        if hook_distribution == "ä¼˜ç§€ï¼ˆæ— å¼±é’©å­ï¼‰":
            score += 1.5
        
        return {
            "score": min(10.0, score),
            "pacing_type": pacing_type,
            "pacing_variation": pacing_variation,
            "hook_distribution": hook_distribution,
            "avg_pacing": statistics.mean(pacing_scores) if pacing_scores else 5.0,
            "avg_hook_strength": statistics.mean(hook_strengths) if hook_strengths else 5.0,
            "type_pacing_analysis": type_pacing_analysis,
            "analysis": f"èŠ‚å¥æ¨¡å¼ï¼š{pacing_type}ï¼ŒèŠ‚å¥ç¨³å®šæ€§ï¼š{pacing_variation:.2f}ï¼Œé’©å­åˆ†å¸ƒï¼š{hook_distribution}"
        }

    def _generate_semantic_report(self, semantic_dimensions: List[SemanticDimension],
                                 golden_three: GoldenThreeChaptersAnalysis,
                                 chapter_analyses: List[ChapterSemanticAnalysis],
                                 narrative_consistency: Dict[str, Any],
                                 emotional_arc: Dict[str, Any],
                                 pacing_analysis: Dict[str, Any]) -> SeniorEditorReportV2:
        """ç”Ÿæˆè¯­ä¹‰åŒ–å®¡ç¨¿æŠ¥å‘Š"""
        # è®¡ç®—ç»¼åˆè¯„åˆ†
        if semantic_dimensions:
            weighted_score = 0
            total_weight = 0
            for dim in semantic_dimensions:
                dim_id = next((k for k, v in self.SEMANTIC_DIMENSIONS.items() 
                             if v["name"] == dim.name), None)
                if dim_id:
                    weight = self.SEMANTIC_DIMENSIONS[dim_id]["weight"]
                    weighted_score += dim.score * weight
                    total_weight += weight
            
            if total_weight > 0:
                overall_score = weighted_score / total_weight
            else:
                overall_score = 6.0
        else:
            overall_score = 6.0
        
        # è°ƒæ•´åŸºäºŽé»„é‡‘ä¸‰ç« çš„è¯„åˆ†
        golden_three_adjustment = golden_three.retention_prediction * 2  # 0-2åˆ†è°ƒæ•´
        overall_score = min(10.0, overall_score + golden_three_adjustment)
        
        # è¯†åˆ«è‡´å‘½ç¼ºé™·
        fatal_flaws = []
        if golden_three.retention_prediction < 0.3:
            fatal_flaws.append({"type": "å¼€ç¯‡ç•™å­˜çŽ‡", "severity": "é«˜", 
                              "description": "é»„é‡‘ä¸‰ç« ç•™å­˜çŽ‡é¢„æµ‹ä½ŽäºŽ30%ï¼Œå¼€ç¯‡å¸å¼•åŠ›ä¸¥é‡ä¸è¶³"})
        
        if narrative_consistency.get("score", 5.0) < 4.0:
            fatal_flaws.append({"type": "å™äº‹ä¸€è‡´æ€§", "severity": "ä¸­", 
                              "description": "å™äº‹ä¸€è‡´æ€§è¯„åˆ†è¾ƒä½Žï¼Œå¯èƒ½å½±å“é˜…è¯»ä½“éªŒ"})
        
        # è¯†åˆ«ä¼˜åŠ¿äº®ç‚¹
        strengths = []
        if golden_three.retention_prediction > 0.7:
            strengths.append({"aspect": "å¼€ç¯‡å¸å¼•åŠ›", "description": "é»„é‡‘ä¸‰ç« ç•™å­˜çŽ‡é¢„æµ‹è¶…è¿‡70%ï¼Œå¼€ç¯‡éžå¸¸å¸å¼•äºº"})
        
        if emotional_arc.get("score", 5.0) > 7.0:
            strengths.append({"aspect": "æƒ…æ„Ÿè¡¨è¾¾", "description": "æƒ…æ„Ÿå¼§çº¿è®¾è®¡ä¼˜ç§€ï¼Œæƒ…æ„Ÿè¡¨è¾¾ä¸°å¯Œæœ‰åŠ›"})
        
        if pacing_analysis.get("score", 5.0) > 7.0:
            strengths.append({"aspect": "èŠ‚å¥æŽ§åˆ¶", "description": "èŠ‚å¥æŠŠæŽ§å¾—å½“ï¼Œè¯»è€…é˜…è¯»ä½“éªŒæµç•…"})
        
        # ç”Ÿæˆæ”¹è¿›è®¡åˆ’
        improvement_plan = []
        
        # åŸºäºŽé»„é‡‘ä¸‰ç« çš„æ”¹è¿›å»ºè®®
        if golden_three.retention_prediction < 0.5:
            improvement_plan.append({
                "priority": "é«˜",
                "area": "å¼€ç¯‡ä¼˜åŒ–",
                "action": "åŠ å¼ºå‰500å­—çš„é’©å­è®¾ç½®ï¼Œç¡®ä¿ä¸»è§’å°½æ—©ç™»åœº",
                "expected_impact": "æå‡è¯»è€…ç•™å­˜çŽ‡"
            })
        
        # åŸºäºŽå™äº‹ä¸€è‡´æ€§çš„æ”¹è¿›å»ºè®®
        if narrative_consistency.get("score", 5.0) < 6.0:
            improvement_plan.append({
                "priority": "ä¸­",
                "area": "å™äº‹ä¸€è‡´æ€§",
                "action": "å‡å°‘å™äº‹è§†è§’åˆ‡æ¢ï¼Œä¼˜åŒ–ç« èŠ‚ç±»åž‹è¿‡æ¸¡",
                "expected_impact": "æå‡é˜…è¯»è¿žè´¯æ€§"
            })
        
        # åŸºäºŽæƒ…æ„Ÿå¼§çº¿çš„æ”¹è¿›å»ºè®®
        if emotional_arc.get("emotional_range", 0) < 0.3:
            improvement_plan.append({
                "priority": "ä½Ž",
                "area": "æƒ…æ„Ÿè¡¨è¾¾",
                "action": "å¢žåŠ æƒ…æ„Ÿå˜åŒ–å¹…åº¦ï¼Œè®¾è®¡æ›´ä¸°å¯Œçš„æƒ…æ„ŸåŸºè°ƒ",
                "expected_impact": "å¢žå¼ºæƒ…æ„Ÿå…±é¸£"
            })
        
        # ç”Ÿæˆç­¾çº¦å»ºè®®
        contract_recommendation = "æš‚ä¸æŽ¨è"
        if overall_score >= 8.0:
            contract_recommendation = "å¼ºçƒˆæŽ¨èç­¾çº¦"
        elif overall_score >= 6.5:
            contract_recommendation = "æŽ¨èç­¾çº¦ï¼Œéœ€é’ˆå¯¹æ€§ä¼˜åŒ–"
        elif overall_score >= 5.0:
            contract_recommendation = "å¯è€ƒè™‘ç­¾çº¦ï¼Œéœ€å¤§å¹…ä¼˜åŒ–"
        
        # å¸‚åœºå®šä½åˆ†æž
        market_positioning = {
            "target_audience": "ç½‘æ–‡è¯»è€…",
            "competitive_advantage": "å¾…åˆ†æž",
            "market_trend_alignment": "ä¸­ç­‰",
            "commercial_potential": "ä¸­ç­‰"
        }
        
        # ç¼–è¾‘æ·±åº¦æ´žå¯Ÿ
        editor_insights = f"""ç»¼åˆè¯„åˆ†ï¼š{overall_score:.1f}/10.0

ä¸»è¦ä¼˜åŠ¿ï¼š"
        if strengths:
            editor_insights += "\n" + "\n".join([f"- {s['description']}" for s in strengths])
        else:
            editor_insights += "\n- æ— æ˜Žæ˜¾çªå‡ºä¼˜åŠ¿"
        
        editor_insights += "\n\nä¸»è¦é—®é¢˜ï¼š"
        if fatal_flaws:
            editor_insights += "\n" + "\n".join([f"- {f['description']}" for f in fatal_flaws])
        else:
            editor_insights += "\n- æ— è‡´å‘½ç¼ºé™·"
        
        editor_insights += "\n\næ ¸å¿ƒå»ºè®®ï¼š"
        if improvement_plan:
            for item in improvement_plan:
                editor_insights += f"\n- [{item['priority']}] {item['area']}: {item['action']}"
        
        # åˆ›å»ºæŠ¥å‘Šå¯¹è±¡
        return SeniorEditorReportV2(
            novel_title=self.novel_info.get("title", "æœªçŸ¥ä½œå“"),
            overall_score=overall_score,
            semantic_dimensions=semantic_dimensions,
            golden_three_chapters=golden_three,
            chapter_analyses=chapter_analyses,
            narrative_consistency=narrative_consistency,
            emotional_arc=emotional_arc,
            pacing_analysis=pacing_analysis,
            fatal_flaws=fatal_flaws,
            strengths=strengths,
            improvement_plan=improvement_plan,
            contract_recommendation=contract_recommendation,
            market_positioning=market_positioning,
            editor_insights=editor_insights
        )

    def _create_empty_report(self) -> SeniorEditorReportV2:
        """åˆ›å»ºç©ºæŠ¥å‘Šï¼ˆå½“æ— æ³•ç”Ÿæˆå®Œæ•´æŠ¥å‘Šæ—¶ï¼‰"""
        return SeniorEditorReportV2(
            novel_title=self.novel_info.get("title", "æœªçŸ¥ä½œå“"),
            overall_score=5.0,
            semantic_dimensions=[
                SemanticDimension(
                    name="æ•°æ®ä¸è¶³",
                    score=5.0,
                    confidence=0.1,
                    analysis="ç« èŠ‚æ•°æ®ä¸è¶³ï¼Œæ— æ³•è¿›è¡Œè¯­ä¹‰åˆ†æž",
                    key_phrases=["å¾…è¯„ä¼°"],
                    evidence=[]
                )
            ],
            golden_three_chapters=self._create_default_golden_three_analysis(),
            chapter_analyses=[],
            narrative_consistency={"score": 5.0, "analysis": "æ•°æ®ä¸è¶³"},
            emotional_arc={"score": 5.0, "analysis": "æ•°æ®ä¸è¶³"},
            pacing_analysis={"score": 5.0, "analysis": "æ•°æ®ä¸è¶³"},
            fatal_flaws=[{"type": "æ•°æ®ä¸è¶³", "severity": "ä½Ž", "description": "ç« èŠ‚æ•°æ®ä¸è¶³ï¼Œæ— æ³•è¿›è¡Œå…¨é¢è¯„ä¼°"}],
            strengths=[],
            improvement_plan=[{"priority": "é«˜", "area": "æ•°æ®æ”¶é›†", "action": "ç”Ÿæˆæ›´å¤šç« èŠ‚å†…å®¹", "expected_impact": "æä¾›è¶³å¤Ÿçš„åˆ†æžæ•°æ®"}],
            contract_recommendation="æ•°æ®ä¸è¶³ï¼Œæ— æ³•è¯„ä¼°",
            market_positioning={"analysis": "æ•°æ®ä¸è¶³"},
            editor_insights="ç« èŠ‚æ•°æ®ä¸è¶³ï¼Œæ— æ³•ç”Ÿæˆæœ‰æ„ä¹‰çš„å®¡ç¨¿æŠ¥å‘Šã€‚è¯·å…ˆç”Ÿæˆè‡³å°‘3ä¸ªç« èŠ‚å†…å®¹ã€‚"
        )


if __name__ == "__main__":
    # æµ‹è¯•ä»£ç 
    class MockLLM:
        def generate(self, prompt, temperature, system_prompt, max_tokens):
            return '''{
                "chapter_type": "action",
                "narrative_perspective": "third_person_limited",
                "emotional_tones": ["suspenseful", "heroic"],
                "emotional_intensity": 0.8,
                "pacing_score": 7.5,
                "hook_strength": 8.0,
                "conflict_present": true,
                "character_development": 6.5,
                "world_building": 7.0,
                "semantic_summary": "æœ¬ç« ä¸ºæˆ˜æ–—å†²çªåž‹ç« èŠ‚ï¼Œä¸»è§’é¢ä¸´å¼ºæ•ŒæŒ‘æˆ˜ï¼Œå±•çŽ°è‹±é›„æ°”æ¦‚ã€‚",
                "key_scenes": [
                    {
                        "description": "ä¸»è§’ä¸Žåæ´¾çš„å¯¹å†³åœºæ™¯",
                        "core_event": "ç”Ÿæ­»å†³æˆ˜",
                        "emotional_value": "ç´§å¼ åˆºæ¿€",
                        "plot_role": "æŽ¨åŠ¨ä¸»çº¿å†²çª"
                    }
                ]
            }'''

    # åˆ›å»ºæµ‹è¯•é¡¹ç›®ç›®å½•
    test_dir = "test_project"
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(os.path.join(test_dir, "chapters"), exist_ok=True)
    
    # åˆ›å»ºæµ‹è¯•ç« èŠ‚æ–‡ä»¶
    test_chapter = """# ç¬¬1ç«  é‡ç”Ÿå½’æ¥

æž—é£Žçå¼€çœ¼ç›ï¼Œå‘çŽ°è‡ªå·±å›žåˆ°äº†åå¹´å‰ã€‚

å‰ä¸–ï¼Œä»–æ˜¯ä»™ç•Œè‡³å°Šï¼Œå´é­æŒšå‹èƒŒå›ï¼Œèº«æ­»é“æ¶ˆã€‚

è¿™ä¸€ä¸–ï¼Œä»–è¦è®©æ‰€æœ‰èƒŒå›è€…ä»˜å‡ºä»£ä»·ï¼

çªç„¶ï¼Œè„‘æµ·ä¸­å“èµ·ä¸€ä¸ªå£°éŸ³ï¼š"å®ï¼æ— æ•Œä¿®ç‚¼ç³»ç»Ÿå·²æ¿€æ´»ï¼"

æž—é£Žå˜´è§’å‹¾èµ·ä¸€æŠ¹å†·ç¬‘ï¼š"è¿™ä¸€ä¸–ï¼Œæˆ‘è¦ç™»ä¸´ç»å·…ï¼"""
    
    with open(os.path.join(test_dir, "chapters", "chapter-001.md"), "w", encoding="utf-8") as f:
        f.write(test_chapter)
    
    # åˆ›å»ºè¿›åº¦æ–‡ä»¶
    progress_data = {
        "title": "é‡ç”Ÿä¹‹æ— æ•Œä¿®ç‚¼ç³»ç»Ÿ",
        "genre": "çŽ„å¹»",
        "total_chapters": 10,
        "completed_chapters": 1,
        "total_word_count": 150
    }
    
    with open(os.path.join(test_dir, "novel-progress.txt"), "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    # æµ‹è¯•SeniorEditor v2
    mock_llm = MockLLM()
    editor = SeniorEditorV2(mock_llm, test_dir)
    
    print("\nðŸ§ª æµ‹è¯•SeniorEditor v2...")
    report = editor.review_novel((1, 1))
    
    print(f"\nðŸ“Š å®¡ç¨¿æŠ¥å‘Šç”ŸæˆæˆåŠŸï¼")
    print(f"ä½œå“æ ‡é¢˜: {report.novel_title}")
    print(f"ç»¼åˆè¯„åˆ†: {report.overall_score:.1f}/10.0")
    print(f"ç­¾çº¦å»ºè®®: {report.contract_recommendation}")
    print(f"\nç¼–è¾‘æ´žå¯Ÿ:\n{report.editor_insights}")
    
    # æ¸…ç†æµ‹è¯•æ–‡ä»¶
    import shutil
    shutil.rmtree(test_dir)