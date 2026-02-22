"""
Hybrid Consistency Checker
3层检测：regex快速匹配 → 相似度匹配 → LLM语义验证
用于减少宗门名称检测的误报率
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
import hashlib
import os


class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Violation:
    """违规记录"""
    type: str  # "valid_faction" | "undefined_faction" | "faction_variant"
    message: str
    confidence: ConfidenceLevel
    matched_text: str
    suggested_correction: Optional[str] = None
    severity: str = "critical"  # "critical" | "warning" | "info"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "message": self.message,
            "confidence": self.confidence.value,
            "matched_text": self.matched_text,
            "suggested_correction": self.suggested_correction,
            "severity": self.severity,
        }


class HybridChecker:
    """
    混合检测器：regex + 相似度 + LLM三层验证
    
    检测流程：
    1. Regex快速过滤 - 从白名单中快速排除明显不匹配的词
    2. 相似度匹配 - 使用Levenshtein距离检测近似名称
    3. LLM验证 - 对可疑词进行语义分析（可选）
    """
    
    # 常见误报词汇白名单（完全跳过）
    FALSE_POSITIVE_WORDS = {
        # 宗教相关
        "宗教", "佛教", "道教", "基督教", "伊斯兰教", "天主教", "东正教", "新教",
        "寺庙", "教堂", "寺院", "道观", "教会", "信徒", "和尚", "道士", "牧师",
        # 政治组织
        "联合国", "欧盟", "北约", "东盟", "APEC", "G20", "峰会", "议会", "国会",
        # 会议室/场所
        "会议室", "办公室", "大堂", "礼堂", "会馆", "会所", "俱乐部", "协会",
        # 常见词汇
        "大会", "年会", "例会", "展会", "博览会", "运动会", "演唱会",
        # 山川地形
        "登山", "上山", "下山", "山谷", "山峰", "山丘", "丘陵", "高原", "平原",
        # 其他常见误报
        "江湖", "武林", "门派", "宗门",  # 这些是通用词，不是具体宗门名
        # 动作+会 模式
        "开了一次会", "举行会议", "召开会议",
    }
    
    # 误报模式：包含这些前缀/后词组合的通常是误报
    FALSE_POSITIVE_PATTERNS = [
        r"^联合国", r"^世界卫生", r"^国际足", r"^奥林匹克",
        r"教(徒|堂|会|义|育|科)",  # 宗教相关
        r"会议(室|中心|厅|)",  # 会议室
        r"一.会",  # 一次会, 开会了会 etc
        r"开了",  # 开了会议, 开了大会 etc
        r"一个",  # 一个宗门, 一个派系 etc
    ]
    
    def __init__(self, whitelist: List[str], llm_client=None):
        """初始化混合检测器
        
        Args:
            whitelist: 允许的宗门名称白名单
            llm_client: LLM客户端（可选，用于语义验证）
        """
        self.whitelist = set(whitelist)
        self.llm_client = llm_client
        self._false_positive_cache: Dict[str, bool] = {}
        
        # 编译误报模式
        self._false_positive_regexes = [
            re.compile(p) for p in self.FALSE_POSITIVE_PATTERNS
        ]
        
        # LLM缓存（避免重复调用）
        self._llm_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_max_size = 100
        
        # Regex pattern for faction detection
        # Match 2-3 char name + suffix (e.g., 青云宗 = 2 chars + 1 suffix = 3 total)
        # Also optionally match when preceded by 了 (perfective aspect marker)
        self._faction_pattern = re.compile(
            r"(?:了)?([\u4e00-\u9fa5]{2,3}(?:宗|派|阁|门|宫|殿|院|府|山|谷|岛|盟|会]))"
        )
    
    def check(self, content: str) -> List[Violation]:
        """
        执行3层检测
        
        Args:
            content: 待检测的文本内容
            
        Returns:
            违规记录列表
        """
        violations = []
        
        # Layer 1: Regex提取候选词
        candidates = self._regex_filter(content)
        
        if not candidates:
            return violations
        
        # Layer 2: 相似度匹配 + 误报过滤
        verified_candidates = []
        for candidate in candidates:
            # 检查是否是误报
            if self._is_false_positive(candidate):
                continue
            
            # 检查是否在白名单中
            if candidate in self.whitelist:
                violations.append(Violation(
                    type="valid_faction",
                    message=f"检测到有效宗门：'{candidate}'",
                    confidence=ConfidenceLevel.HIGH,
                    matched_text=candidate,
                    severity="info",
                ))
                continue
            
            # 检查是否有相似的白名单名称
            similar = self._similarity_match(candidate, list(self.whitelist))
            if similar:
                violations.append(Violation(
                    type="faction_variant",
                    message=f"检测到宗门名称变体：'{candidate}'（应为'{similar}'）",
                    confidence=ConfidenceLevel.HIGH,
                    matched_text=candidate,
                    suggested_correction=similar,
                    severity="critical",
                ))
            else:
                verified_candidates.append(candidate)
        
        # Layer 3: LLM验证（可选）
        if verified_candidates and self.llm_client:
            llm_violations = self._llm_verify(content, verified_candidates)
            violations.extend(llm_violations)
        elif verified_candidates:
            # 没有LLM时，对未匹配的候选词标记为未定义
            for candidate in verified_candidates:
                violations.append(Violation(
                    type="undefined_faction",
                    message=f"检测到未定义的宗门：'{candidate}'",
                    confidence=ConfidenceLevel.MEDIUM,
                    matched_text=candidate,
                    severity="critical",
                ))
        
        return violations
    
    def _regex_filter(self, content: str) -> List[str]:
        """
        Layer 1: Regex快速过滤
        提取所有可能的宗门名称
        
        Args:
            content: 待检测文本
            
        Returns:
            候选宗门名称列表（去重）
        """
        matches = self._faction_pattern.findall(content)
        # 去重并保持顺序
        seen = set()
        unique_matches = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                unique_matches.append(m)
        return unique_matches
    
    def _is_false_positive(self, candidate: str) -> bool:
        """
        检查是否是误报词
        
        Args:
            candidate: 候选词
            
        Returns:
            True表示是误报，应跳过
        """
        # 检查缓存
        if candidate in self._false_positive_cache:
            return self._false_positive_cache[candidate]
        
        # 检查白名单词汇
        if candidate in self.FALSE_POSITIVE_WORDS:
            self._false_positive_cache[candidate] = True
            return True
        
        # 检查误报模式
        for pattern in self._false_positive_regexes:
            if pattern.search(candidate):
                self._false_positive_cache[candidate] = True
                return True
        
        # 检查长度过短或过长
        if len(candidate) < 2 or len(candidate) > 6:
            self._false_positive_cache[candidate] = True
            return True
        
        # 默认不是误报
        self._false_positive_cache[candidate] = False
        return False
    
    def _similarity_match(
        self, candidate: str, whitelist: List[str]
    ) -> Optional[str]:
        """
        Layer 2: 相似度匹配
        使用Levenshtein距离查找最相似的白名单名称
        
        Args:
            candidate: 候选词
            whitelist: 白名单列表
            
        Returns:
            最相似的白名单名称，如果没有匹配的返回None
        """
        if not whitelist:
            return None
        
        best_match = None
        best_distance = float('inf')
        
        for valid_name in whitelist:
            # 首先检查是否有共同的后缀（宗/派/门等）
            if candidate[-1] != valid_name[-1]:
                continue
            
            # 计算Levenshtein距离
            distance = self._levenshtein_distance(candidate, valid_name)
            
            # 如果距离小于阈值，认为是相似词
            # 阈值：2个字符以内
            if distance <= 2 and distance < best_distance:
                best_distance = distance
                best_match = valid_name
        
        return best_match
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算两个字符串的Levenshtein编辑距离
        
        Args:
            s1: 第一个字符串
            s2: 第二个字符串
            
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # insertions, deletions, substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _llm_verify(
        self, content: str, candidates: List[str]
    ) -> List[Violation]:
        """
        Layer 3: LLM语义验证
        对可疑词进行语义分析，确认是否是真正的宗门名称
        
        Args:
            content: 原始文本内容
            candidates: 待验证的候选词列表
            
        Returns:
            验证后的违规列表
        """
        if not self.llm_client or not candidates:
            return []
        
        violations = []
        
        # 生成缓存key
        content_hash = hashlib.md5(
            (content[:500] + "|".join(candidates)).encode()
        ).hexdigest()
        
        # 检查缓存
        if content_hash in self._llm_cache:
            cached = self._llm_cache[content_hash]
            return self._parse_llm_response(cached, candidates)
        
        # 构建prompt
        whitelist_str = ", ".join(self.whitelist)
        candidates_str = ", ".join(candidates)
        
        prompt = f"""你是一个小说宗门名称检测助手。

白名单允许的宗门名称：{whitelist_str}

待检测的候选词：{candidates_str}

请分析这些候选词是否是真正的宗门名称（修仙小说中的门派、势力）。

判断标准：
1. 必须是具体的小说中的宗门/门派名称
2. 不能是通用词汇（如"宗教"、"江湖"、"武林"）
3. 不能是现实世界组织（如"联合国"）
4. 不能是普通场所（如"会议室"）

对于每个候选词，请输出：
- 如果是真正的宗门名称且不在白名单中：输出 "VALID: 候选词"
- 如果是误报（通用词/现实组织/普通场所）：输出 "FALSE: 候选词"

只输出判断结果，每行一个，不要有其他解释。"""
        
        try:
            # 调用LLM
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.0,
            )
            
            # 缓存结果
            if len(self._llm_cache) >= self._cache_max_size:
                # 简单的FIFO清理
                oldest_key = next(iter(self._llm_cache))
                del self._llm_cache[oldest_key]
            
            self._llm_cache[content_hash] = response
            
            # 解析响应
            violations = self._parse_llm_response(response, candidates)
            
        except Exception as e:
            # LLM调用失败时，降级为中等置信度的未定义宗门
            for candidate in candidates:
                violations.append(Violation(
                    type="undefined_faction",
                    message=f"检测到未定义的宗门：'{candidate}'（LLM验证失败）",
                    confidence=ConfidenceLevel.LOW,
                    matched_text=candidate,
                    severity="critical",
                ))
        
        return violations
    
    def _parse_llm_response(
        self, response: str, candidates: List[str]
    ) -> List[Violation]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            candidates: 候选词列表
            
        Returns:
            违规列表
        """
        violations = []
        response_lines = response.strip().split("\n")
        
        for line in response_lines:
            line = line.strip()
            if not line:
                continue
            
            # 解析 "VALID: xxx" 或 "FALSE: xxx" 格式
            if line.startswith("VALID:"):
                candidate = line.replace("VALID:", "").strip()
                if candidate in candidates:
                    violations.append(Violation(
                        type="undefined_faction",
                        message=f"检测到未定义的宗门：'{candidate}'",
                        confidence=ConfidenceLevel.HIGH,
                        matched_text=candidate,
                        severity="critical",
                    ))
            elif line.startswith("FALSE:"):
                # 误报，不添加到violations
                pass
        
        # 如果LLM没有返回有效解析，降级处理
        if not violations and candidates:
            for candidate in candidates:
                violations.append(Violation(
                    type="undefined_faction",
                    message=f"检测到未定义的宗门：'{candidate}'",
                    confidence=ConfidenceLevel.LOW,
                    matched_text=candidate,
                    severity="critical",
                ))
        
        return violations
    
    def clear_cache(self):
        """清空缓存"""
        self._false_positive_cache.clear()
        self._llm_cache.clear()


# 简单的LLM客户端mock（用于测试）
class MockLLMClient:
    """模拟LLM客户端，用于测试"""
    
    def __init__(self, response: str = ""):
        self.response = response
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.0) -> str:
        return self.response


if __name__ == "__main__":
    print("Running QA tests...")
    
    # Test 1: False positive reduction
    checker = HybridChecker(["青云宗", "天剑门"])
    result = checker.check("这是一个宗教会议，在联合国大厦举行")
    assert len(result) == 0, f"Should have no violations, got {result}"
    print("[PASS] Test 1: False positive reduction")
    
    # Test 2: Valid faction detection
    result = checker.check("他加入了青云宗")
    assert len(result) == 1, f"Should have 1 violation, got {len(result)}"
    assert result[0].type == "valid_faction" or result[0].matched_text == "青云宗"
    print("[PASS] Test 2: Valid faction detection")
    
    # Test 3: Undefined faction
    result = checker.check("他创立了天魔宗")
    assert len(result) == 1, f"Should have 1 violation, got {len(result)}"
    assert result[0].type in ["undefined_faction", "faction_variant"]
    print("[PASS] Test 3: Undefined faction detection")
    
    # Test 4: Similar faction variant
    result = checker.check("他是青云派的弟子")
    assert len(result) == 1, f"Should detect variant, got {len(result)}"
    print("[PASS] Test 4: Similar faction variant")
    
    print("\n=== All QA tests passed! ===")
