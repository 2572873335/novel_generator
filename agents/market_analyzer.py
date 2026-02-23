"""
Market Analyzer for genre benchmarking and competitive analysis.

This module analyzes novel content against genre patterns to provide
market positioning and differentiation recommendations.

Key features:
- Genre pattern analysis (Xianxia, Urban, Fantasy, etc.)
- Golden finger timing analysis
- Conflict type extraction
- Chapter length benchmarking
- Differentiation opportunity identification
- Market trend alignment scoring
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import statistics
from pathlib import Path


class Genre(Enum):
    """Novel genre classification."""

    XIANXIA = "仙侠"  # Immortal heroes, cultivation
    XUANHUAN = "玄幻"  # Fantasy with Chinese elements
    URBAN = "都市"  # Modern city life
    FANTASY = "奇幻"  # Western fantasy
    GAME = "游戏"  # Game world
    SCIENCE_FICTION = "科幻"  # Science fiction
    HISTORICAL = "历史"  # Historical fiction
    SUSPENSE = "悬疑"  # Mystery/suspense
    ROMANCE = "言情"  # Romance
    GENERAL = "通用"  # General/unspecified


class GoldFingerType(Enum):
    """Types of golden fingers (special advantages)."""

    SYSTEM = "系统"  # System interface
    REINCARNATION = "重生"  # Reincarnation with memories
    TIME_TRAVEL = "穿越"  # Time travel
    CHEAT_ITEM = "作弊物品"  # Magical item
    BLOODLINE = "血脉"  # Special bloodline
    TALENT = "天赋"  # Innate talent
    KNOWLEDGE = "知识"  # Future knowledge
    CONNECTION = "人脉"  # Social connections
    WEALTH = "财富"  # Wealth advantage


class ConflictType(Enum):
    """Types of conflicts in novels."""

    POWER_STRUGGLE = "权力斗争"  # Power struggle
    RESOURCE_COMPETITION = "资源争夺"  # Resource competition
    PERSONAL_VENDETTA = "个人恩怨"  # Personal vendetta
    ROMANTIC_RIVALRY = "情敌竞争"  # Romantic rivalry
    IDEOLOGICAL = "理念冲突"  # Ideological conflict
    SURVIVAL = "生存危机"  # Survival crisis
    IDENTITY = "身份危机"  # Identity crisis
    MORAL_DILEMMA = "道德困境"  # Moral dilemma
    FACTION_WAR = "宗门战争"  # Faction war


@dataclass
class GenrePattern:
    """Patterns for a specific genre."""

    genre: Genre
    avg_chapter_length: int  # Average words per chapter
    golden_finger_timing: Dict[
        str, float
    ]  # Chapter when golden finger appears (probability)
    conflict_distribution: Dict[ConflictType, float]  # Distribution of conflict types
    pacing_indicators: Dict[str, Any]  # Pacing indicators (conflicts per chapter, etc.)
    common_tropes: List[str]  # Common tropes in this genre
    success_factors: List[str]  # Factors contributing to success in this genre
    reader_expectations: List[str]  # Reader expectations for this genre


@dataclass
class MarketAnalysis:
    """Market analysis results for a novel."""

    identified_genre: Genre
    confidence_score: float  # 0-1 confidence in genre identification
    genre_pattern_match: Dict[str, float]  # Match scores for each genre
    golden_finger_analysis: Dict[str, Any]  # Analysis of golden finger usage
    conflict_analysis: Dict[ConflictType, float]  # Analysis of conflict types
    pacing_analysis: Dict[str, float]  # Pacing analysis
    differentiation_opportunities: List[str]  # Opportunities for differentiation
    market_trend_alignment: float  # 0-1 alignment with current market trends
    recommendations: List[str]  # Specific recommendations
    competitive_benchmark: Dict[str, Any]  # Benchmark against successful works


@dataclass
class BenchmarkComparison:
    """Comparison against benchmark works."""

    benchmark_title: str
    similarity_score: float
    strengths: List[str]
    weaknesses: List[str]
    differentiation_points: List[str]


class MarketAnalyzer:
    """Market analysis agent for genre benchmarking and competitive analysis."""

    def __init__(self, model_manager=None):
        """Initialize the market analyzer.

        Args:
            model_manager: Optional model manager for LLM calls
        """
        self.model_manager = model_manager
        self.genre_patterns = self._load_genre_patterns()
        self.market_trends = self._load_market_trends()

    
    def _load_genre_patterns(self) -> Dict[Genre, GenrePattern]:
        """Load predefined genre patterns."""
        return {
            Genre.XIANXIA: GenrePattern(
                genre=Genre.XIANXIA,
                avg_chapter_length=3200,
                golden_finger_timing={
                    "chapter_1": 0.8,  # 80% appear in chapter 1
                    "chapter_3": 0.95,  # 95% appear by chapter 3
                    "chapter_10": 0.99,  # 99% appear by chapter 10
                },
                conflict_distribution={
                    ConflictType.POWER_STRUGGLE: 0.35,
                    ConflictType.RESOURCE_COMPETITION: 0.25,
                    ConflictType.PERSONAL_VENDETTA: 0.20,
                    ConflictType.FACTION_WAR: 0.15,
                    ConflictType.SURVIVAL: 0.05,
                },
                pacing_indicators={
                    "conflicts_per_chapter": 1.2,
                    "power_ups_per_chapter": 0.8,
                    "face_slaps_per_chapter": 1.5,
                    "cliffhanger_frequency": 0.7,  # 70% of chapters end with cliffhanger
                },
                common_tropes=[
                    "cultivation system",
                    "sect politics",
                    "ancient inheritance",
                    "heavenly tribulation",
                    "realm breakthrough",
                    "face-slapping young masters",
                    "hidden expert mentor",
                ],
                success_factors=[
                    "clear power progression",
                    "satisfying face-slapping",
                    "consistent cultivation logic",
                    "interesting sect dynamics",
                    "meaningful character growth",
                ],
                reader_expectations=[
                    "regular power-ups",
                    "sect ranking improvements",
                    "treasure discoveries",
                    "rival confrontations",
                    "realm breakthroughs",
                ]
            ),
            Genre.URBAN: GenrePattern(
                genre=Genre.URBAN,
                avg_chapter_length=2800,
                golden_finger_timing={
                    "chapter_1": 0.6,
                    "chapter_3": 0.85,
                    "chapter_10": 0.98,
                },
                conflict_distribution={
                    ConflictType.POWER_STRUGGLE: 0.25,
                    ConflictType.RESOURCE_COMPETITION: 0.30,
                    ConflictType.ROMANTIC_RIVALRY: 0.20,
                    ConflictType.PERSONAL_VENDETTA: 0.15,
                    ConflictType.MORAL_DILEMMA: 0.10,
                },
                pacing_indicators={
                    "conflicts_per_chapter": 1.0,
                    "plot_twists_per_chapter": 0.5,
                    "emotional_beats_per_chapter": 1.2,
                    "cliffhanger_frequency": 0.6,
                },
                common_tropes=[
                    "rags to riches",
                    "business empire building",
                    "school/academic competition",
                    "celebrity life",
                    "family drama",
                    "corporate intrigue",
                    "urban supernatural",
                ],
                success_factors=[
                    "relatable protagonist",
                    "realistic character motivations",
                    "satisfying career progression",
                    "emotional depth",
                    "social commentary",
                ],
                reader_expectations=[
                    "career advancement",
                    "wealth accumulation",
                    "social status improvement",
                    "relationship development",
                    "personal growth",
                ]
            ),
        }
    
    def _load_market_trends(self) -> Dict[str, Any]:
        """Load current market trends."""
        return {
            "current_hot_genres": [Genre.XIANXIA, Genre.URBAN, Genre.XUANHUAN],
            "rising_genres": [Genre.GAME, Genre.SCIENCE_FICTION],
            "declining_genres": [Genre.HISTORICAL, Genre.ROMANCE],
            "trending_tropes": [
                "system novels",
                "reincarnation with memories",
                "slow life after overpowered",
                "academy arcs",
                "kingdom building",
            ],
            "reader_preferences": {
                "fast_pacing": 0.7,  # 70% prefer fast pacing
                "clear_power_progression": 0.8,
                "regular_payoffs": 0.9,
                "minimal_info_dumps": 0.6,
                "strong_emotional_hooks": 0.75,
            },
            "market_saturation": {
                Genre.XIANXIA: 0.8,  # 80% saturated
                Genre.URBAN: 0.7,
                Genre.XUANHUAN: 0.75,
                Genre.FANTASY: 0.6,
                Genre.GAME: 0.4,
                Genre.SCIENCE_FICTION: 0.3,
            }
        }

    def analyze_novel(self, novel_data: Dict[str, Any]) -> MarketAnalysis:
        """Analyze a novel against market patterns.
        
        Args:
            novel_data: Dictionary containing novel information
                - title: Novel title
                - genre: Initial genre guess
                - chapters: List of chapter contents or metadata
                - word_counts: List of word counts per chapter
                - metadata: Additional metadata
        
        Returns:
            MarketAnalysis object with analysis results
        """
        # Extract features from novel data
        features = self._extract_features(novel_data)
        
        # Identify genre
        genre_result = self._identify_genre(features)
        
        # Analyze golden finger usage
        golden_finger_analysis = self._analyze_golden_finger(features)
        
        # Analyze conflicts
        conflict_analysis = self._analyze_conflicts(features)
        
        # Analyze pacing
        pacing_analysis = self._analyze_pacing(features)
        
        # Generate differentiation opportunities
        differentiation_opportunities = self._generate_differentiation_opportunities(
            features, genre_result["genre"]
        )
        
        # Calculate market trend alignment
        market_trend_alignment = self._calculate_market_trend_alignment(
            features, genre_result["genre"]
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            features, genre_result["genre"], differentiation_opportunities
        )
        
        # Create competitive benchmark
        competitive_benchmark = self._create_competitive_benchmark(
            features, genre_result["genre"]
        )
        
        return MarketAnalysis(
            identified_genre=genre_result["genre"],
            confidence_score=genre_result["confidence"],
            genre_pattern_match=genre_result["match_scores"],
            golden_finger_analysis=golden_finger_analysis,
            conflict_analysis=conflict_analysis,
            pacing_analysis=pacing_analysis,
            differentiation_opportunities=differentiation_opportunities,
            market_trend_alignment=market_trend_alignment,
            recommendations=recommendations,
            competitive_benchmark=competitive_benchmark,
        )
    
    def _extract_features(self, novel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from novel data for analysis."""
        features = {
            "title": novel_data.get("title", ""),
            "initial_genre": novel_data.get("genre", Genre.GENERAL),
            "chapters": novel_data.get("chapters", []),
            "word_counts": novel_data.get("word_counts", []),
            "metadata": novel_data.get("metadata", {}),
        }
        
        # Calculate basic statistics
        if features["word_counts"]:
            features["avg_chapter_length"] = statistics.mean(features["word_counts"])
            features["chapter_length_std"] = statistics.stdev(features["word_counts"]) if len(features["word_counts"]) > 1 else 0
        else:
            features["avg_chapter_length"] = 3000  # Default
            features["chapter_length_std"] = 0
        
        # Extract text for analysis (first few chapters if available)
        sample_text = ""
        if features["chapters"]:
            # Use first 3 chapters or all available
            sample_chapters = features["chapters"][:min(3, len(features["chapters"]))]
            if isinstance(sample_chapters[0], dict):
                sample_text = " ".join([ch.get("content", "") for ch in sample_chapters])
            else:
                sample_text = " ".join(sample_chapters)
        
        features["sample_text"] = sample_text
        
        # Extract keywords from metadata
        features["keywords"] = novel_data.get("metadata", {}).get("keywords", [])
        
        return features

    def _identify_genre(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Identify the most likely genre for the novel."""
        match_scores = {}
        
        for genre, pattern in self.genre_patterns.items():
            score = 0.0
            
            # Check chapter length match
            if "avg_chapter_length" in features:
                length_diff = abs(features["avg_chapter_length"] - pattern.avg_chapter_length)
                length_score = max(0, 1 - (length_diff / 1000))  # 1000 words tolerance
                score += length_score * 0.2
            
            # Check keyword overlap
            if "keywords" in features:
                keyword_overlap = self._calculate_keyword_overlap(
                    features["keywords"], pattern.common_tropes
                )
                score += keyword_overlap * 0.3
            
            # Check sample text for genre indicators
            if "sample_text" in features:
                text_score = self._analyze_text_for_genre(
                    features["sample_text"], genre
                )
                score += text_score * 0.5
            
            match_scores[genre.value] = score
        
        # Find best matching genre
        best_genre = max(match_scores.items(), key=lambda x: x[1])
        
        return {
            "genre": Genre(best_genre[0]),
            "confidence": best_genre[1],
            "match_scores": match_scores,
        }
    
    def _calculate_keyword_overlap(self, keywords: List[str], tropes: List[str]) -> float:
        """Calculate overlap between keywords and genre tropes."""
        if not keywords or not tropes:
            return 0.0
        
        # Simple word matching
        keyword_set = set(keywords)
        trope_set = set(tropes)
        
        # Calculate Jaccard similarity
        intersection = len(keyword_set.intersection(trope_set))
        union = len(keyword_set.union(trope_set))
        
        return intersection / union if union > 0 else 0.0
    
    def _analyze_text_for_genre(self, text: str, genre: Genre) -> float:
        """Analyze text for genre-specific indicators."""
        if not text:
            return 0.0
        
        score = 0.0
        text_lower = text.lower()
        
        # Genre-specific keyword patterns
        genre_patterns = {
            Genre.XIANXIA: [
                r"修炼|真气|元婴|金丹|筑基|宗门|法宝|飞剑|天劫",
                r"cultivation|qi|core formation|nascent soul|sect|treasure",
            ],
            Genre.URBAN: [
                r"公司|总裁|职场|校园|都市|商业|投资|房产|豪车",
                r"company|ceo|workplace|campus|city|business|investment",
            ],
        }
        
        patterns = genre_patterns.get(genre, [])
        matches = 0
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matches += 1
        
        # Normalize score
        if patterns:
            score = matches / len(patterns)
        
        return score

    def _analyze_golden_finger(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze golden finger usage in the novel."""
        analysis = {
            "types_found": [],
            "timing": {},
            "effectiveness_score": 0.0,
            "recommendations": [],
        }
        
        if not features.get("sample_text"):
            return analysis
        
        text = features["sample_text"]
        
        # Detect golden finger types
        golden_finger_patterns = {
            GoldFingerType.SYSTEM: [r"系统|System|面板|interface|任务|quest"],
            GoldFingerType.REINCARNATION: [r"重生|reincarnation|前世|previous life|记忆|memory"],
            GoldFingerType.TIME_TRAVEL: [r"穿越|time travel|时空|time and space|未来|future"],
            GoldFingerType.CHEAT_ITEM: [r"神器|artifact|法宝|treasure|作弊|cheat"],
            GoldFingerType.BLOODLINE: [r"血脉|bloodline|血统|lineage|天赋|innate"],
            GoldFingerType.TALENT: [r"天赋|talent|资质|aptitude|悟性|comprehension"],
            GoldFingerType.KNOWLEDGE: [r"知识|knowledge|记忆|memory|经验|experience"],
            GoldFingerType.CONNECTION: [r"人脉|connection|关系|relationship|背景|background"],
            GoldFingerType.WEALTH: [r"财富|wealth|金钱|money|资产|assets"],
        }
        
        found_types = []
        for gf_type, patterns in golden_finger_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found_types.append(gf_type)
                    break
        
        analysis["types_found"] = [t.value for t in found_types]
        
        # Analyze timing (which chapter golden finger appears)
        chapters = features.get("chapters", [])
        if chapters:
            for i, chapter in enumerate(chapters[:5]):  # Check first 5 chapters
                chapter_text = chapter.get("content", "") if isinstance(chapter, dict) else str(chapter)
                if any(re.search(pattern, chapter_text, re.IGNORECASE) 
                       for gf_type in found_types 
                       for pattern in golden_finger_patterns.get(gf_type, [])):
                    analysis["timing"][f"chapter_{i+1}"] = True
        
        # Calculate effectiveness score
        if found_types:
            # More unique golden fingers = higher score
            uniqueness_bonus = min(len(found_types) * 0.1, 0.3)
            
            # Early appearance bonus
            early_bonus = 0.0
            if "chapter_1" in analysis["timing"]:
                early_bonus = 0.3
            elif "chapter_2" in analysis["timing"]:
                early_bonus = 0.2
            elif "chapter_3" in analysis["timing"]:
                early_bonus = 0.1
            
            analysis["effectiveness_score"] = 0.4 + uniqueness_bonus + early_bonus
        
        # Generate recommendations
        if not found_types:
            analysis["recommendations"].append("考虑添加金手指系统以增强主角优势")
        elif analysis["effectiveness_score"] < 0.6:
            analysis["recommendations"].append("优化金手指的展示时机和效果")
        
        return analysis

    def _analyze_conflicts(self, features: Dict[str, Any]) -> Dict[ConflictType, float]:
        """Analyze conflict types in the novel."""
        conflict_scores = {ct: 0.0 for ct in ConflictType}
        
        if not features.get("sample_text"):
            return conflict_scores
        
        text = features["sample_text"]
        
        # Conflict detection patterns
        conflict_patterns = {
            ConflictType.POWER_STRUGGLE: [
                r"权力|power|地位|position|争夺|compete|统治|rule",
                r"宗主|sect master|掌门|leader|职位|position",
            ],
            ConflictType.RESOURCE_COMPETITION: [
                r"资源|resource|灵石|spirit stone|宝物|treasure|争夺|compete",
                r"秘境|secret realm|传承|inheritance|机遇|opportunity",
            ],
            ConflictType.PERSONAL_VENDETTA: [
                r"恩怨|vendetta|仇恨|hatred|报仇|revenge|羞辱|humiliate",
                r"杀父|kill father|灭门|exterminate|侮辱|insult",
            ],
            ConflictType.ROMANTIC_RIVALRY: [
                r"情敌|love rival|感情|emotion|爱情|love|争夺|compete",
                r"喜欢|like|爱|love|追求|pursue|拒绝|reject",
            ],
            ConflictType.IDEOLOGICAL: [
                r"理念|ideology|信仰|belief|道义|morality|正义|justice",
                r"正邪|good and evil|善恶|good and bad|立场|standpoint",
            ],
            ConflictType.SURVIVAL: [
                r"生存|survival|生命|life|危险|danger|危机|crisis",
                r"死亡|death|威胁|threat|逃命|escape|追杀|pursue",
            ],
        }
        
        total_matches = 0
        for conflict_type, patterns in conflict_patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, text, re.IGNORECASE))
            
            conflict_scores[conflict_type] = matches
            total_matches += matches
        
        # Normalize scores
        if total_matches > 0:
            for conflict_type in conflict_scores:
                conflict_scores[conflict_type] /= total_matches
        
        return conflict_scores
    
    def _analyze_pacing(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Analyze pacing of the novel."""
        pacing = {
            "conflict_density": 0.0,
            "plot_progression": 0.0,
            "emotional_variation": 0.0,
            "info_dump_ratio": 0.0,
        }
        
        if not features.get("sample_text"):
            return pacing
        
        text = features["sample_text"]
        
        # Simple heuristic analysis
        # Count action/conflict words
        action_words = len(re.findall(r"战斗|fight|攻击|attack|冲突|conflict|危险|danger", text))
        total_words = len(text.split())
        
        if total_words > 0:
            pacing["conflict_density"] = action_words / (total_words / 1000)  # per 1000 words
        
        # Estimate plot progression (chapter-based)
        chapters = features.get("chapters", [])
        if chapters:
            # Check if early chapters establish plot
            early_chapters = chapters[:min(3, len(chapters))]
            plot_keywords = ["目标|goal", "任务|quest", "阴谋|conspiracy", "秘密|secret"]
            plot_matches = 0
            
            for chapter in early_chapters:
                chapter_text = chapter.get("content", "") if isinstance(chapter, dict) else str(chapter)
                for keyword in plot_keywords:
                    if re.search(keyword, chapter_text, re.IGNORECASE):
                        plot_matches += 1
                        break
            
            pacing["plot_progression"] = plot_matches / len(early_chapters)
        
        return pacing
    
    def _generate_differentiation_opportunities(
        self, features: Dict[str, Any], genre: Genre
    ) -> List[str]:
        """Generate opportunities for differentiation within the genre."""
        opportunities = []
        
        # Get genre pattern for comparison
        genre_pattern = self.genre_patterns.get(genre)
        if not genre_pattern:
            return opportunities
        
        # Check for overused tropes
        sample_text = features.get("sample_text", "")
        if sample_text:
            overused_tropes = self._identify_overused_tropes(sample_text, genre_pattern.common_tropes)
            if overused_tropes:
                opportunities.append(f"避免过度使用常见套路: {', '.join(overused_tropes[:3])}")
        
        # Check pacing differences
        pacing = self._analyze_pacing(features)
        genre_pacing = genre_pattern.pacing_indicators
        
        if "conflict_density" in pacing and "conflicts_per_chapter" in genre_pacing:
            if pacing["conflict_density"] < genre_pacing["conflicts_per_chapter"] * 0.7:
                opportunities.append("可以考虑增加冲突密度以符合流派期待")
            elif pacing["conflict_density"] > genre_pacing["conflicts_per_chapter"] * 1.3:
                opportunities.append("可以考虑降低冲突密度以创造差异化")
        
        # Check golden finger uniqueness
        golden_finger_analysis = self._analyze_golden_finger(features)
        found_types = golden_finger_analysis.get("types_found", [])
        
        if len(found_types) == 0:
            opportunities.append("添加独特的金手指系统可以显著提升作品吸引力")
        elif len(found_types) == 1:
            opportunities.append("考虑组合多种金手指类型以创造独特优势")
        
        return opportunities[:5]  # Return top 5 opportunities
    
    def _identify_overused_tropes(self, text: str, common_tropes: List[str]) -> List[str]:
        """Identify which common tropes are overused in the text."""
        overused = []
        
        for trope in common_tropes[:10]:  # Check first 10 tropes
            # Simple keyword matching
            keywords = trope.split()
            matches = 0
            for keyword in keywords:
                if re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
                    matches += 1
            
            if matches >= len(keywords):  # All keywords found
                overused.append(trope)
        
        return overused
    
    def _calculate_market_trend_alignment(
        self, features: Dict[str, Any], genre: Genre
    ) -> float:
        """Calculate alignment with current market trends."""
        alignment_score = 0.0
        
        # Genre popularity
        current_hot = self.market_trends["current_hot_genres"]
        rising = self.market_trends["rising_genres"]
        
        if genre in current_hot:
            alignment_score += 0.3
        elif genre in rising:
            alignment_score += 0.4  # Rising genres have higher potential
        else:
            alignment_score += 0.1
        
        # Market saturation
        saturation = self.market_trends["market_saturation"].get(genre, 0.5)
        # Lower saturation = higher opportunity
        saturation_factor = 1 - saturation
        alignment_score += saturation_factor * 0.3
        
        return min(alignment_score, 1.0)
    
    def _generate_recommendations(
        self, features: Dict[str, Any], genre: Genre, opportunities: List[str]
    ) -> List[str]:
        """Generate specific recommendations for the novel."""
        recommendations = []
        
        # Genre-specific recommendations
        genre_pattern = self.genre_patterns.get(genre)
        if genre_pattern:
            # Check against success factors
            sample_text = features.get("sample_text", "")
            if sample_text:
                for factor in genre_pattern.success_factors[:3]:
                    # Simple check for factor presence
                    factor_keywords = factor.split()
                    matches = 0
                    for keyword in factor_keywords:
                        if re.search(rf"\b{re.escape(keyword)}\b", sample_text, re.IGNORECASE):
                            matches += 1
                    
                    if matches < len(factor_keywords) * 0.5:
                        recommendations.append(f"加强{factor}")
        
        # Add differentiation opportunities as recommendations
        recommendations.extend(opportunities[:3])
        
        # Market trend recommendations
        market_alignment = self._calculate_market_trend_alignment(features, genre)
        if market_alignment < 0.5:
            recommendations.append("考虑调整以更好契合当前市场趋势")
        
        # Pacing recommendations
        pacing = self._analyze_pacing(features)
        if pacing.get("conflict_density", 0) < 0.5:
            recommendations.append("增加冲突密度以提升阅读节奏")
        elif pacing.get("conflict_density", 0) > 2.0:
            recommendations.append("适当降低冲突密度以避免读者疲劳")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _create_competitive_benchmark(
        self, features: Dict[str, Any], genre: Genre
    ) -> Dict[str, Any]:
        """Create competitive benchmark against successful works."""
        # This is a simplified version - in production, this would query a database
        # of successful novels in the same genre
        
        benchmark_titles = {
            Genre.XIANXIA: ["凡人修仙传", "仙逆", "我欲封天"],
            Genre.URBAN: ["全职高手", "大王饶命", "修真聊天群"],
        }
        
        titles = benchmark_titles.get(genre, [])
        
        if not titles:
            return {"benchmarks": [], "average_similarity": 0.0}
        
        # Simplified similarity calculation
        sample_text = features.get("sample_text", "")
        similarities = []
        
        for title in titles[:2]:  # Compare with top 2 benchmarks
            # In production, this would compare actual content
            # Here we use a placeholder similarity
            similarity = 0.5  # Placeholder
            similarities.append(similarity)
        
        average_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        return {
            "benchmarks": titles[:2],
            "average_similarity": average_similarity,
            "recommendations": [
                "研究成功作品的开篇节奏",
                "学习优秀作品的人物塑造",
                "借鉴成功作品的冲突设计",
            ]
        }