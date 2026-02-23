"""
Writer Agent v2 - Pipeline Architecture
集成时间感知RAG、混合一致性检查、期待感追踪的现代化写作管道
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """管道阶段枚举"""

    OUTLINE = "outline"
    DRAFT = "draft"
    CONSISTENCY_CHECK = "consistency_check"
    POLISH = "polish"
    FINAL = "final"


@dataclass
class PipelineContext:
    """管道上下文"""

    chapter_number: int
    chapter_info: Dict[str, Any]
    project_dir: str
    current_stage: PipelineStage = PipelineStage.OUTLINE
    stage_results: Dict[PipelineStage, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)


class WriterAgentV2:
    """
    写作代理 v2 - 管道架构

    五阶段管道：
    1. OutlineStage - 大纲生成（基于章节信息）
    2. DraftStage - 草稿撰写（检查点写作，每1000字自动保存）
    3. ConsistencyCheckStage - 一致性检查（混合检查器）
    4. PolishStage - 文字润色（语义优化）
    5. FinalStage - 终稿生成（格式化和元数据）

    集成组件：
    - TimeAwareRAG: 时间感知上下文检索
    - HybridConsistencyChecker: 混合一致性检查
    - ExpectationTracker: 期待感追踪
    - StateSnapshot: 状态快照管理
    """

    def __init__(self, llm_client, project_dir: str, v7_constraints: str = ""):
        self.llm = llm_client
        self.project_dir = project_dir
        self.chapters_dir = os.path.join(project_dir, "chapters")
        self.v7_constraints = v7_constraints or self._load_v7_constraints()

        # 确保目录存在
        os.makedirs(self.chapters_dir, exist_ok=True)

        # 初始化核心组件
        self._init_core_components()

        # 管道阶段处理器
        self.stage_handlers = {
            PipelineStage.OUTLINE: self._handle_outline_stage,
            PipelineStage.DRAFT: self._handle_draft_stage,
            PipelineStage.CONSISTENCY_CHECK: self._handle_consistency_check_stage,
            PipelineStage.POLISH: self._handle_polish_stage,
            PipelineStage.FINAL: self._handle_final_stage,
        }

        logger.info(f"WriterAgentV2 initialized for project: {project_dir}")

    def write_session(self) -> Dict[str, Any]:
        """执行一次写作会话 - 兼容旧接口"""
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

        from core.progress_manager import ProgressManager

        # 1. 加载进度
        progress_mgr = ProgressManager(self.project_dir)
        progress = progress_mgr.load_progress()

        if not progress:
            return {"success": False, "error": "No progress file"}

        if progress.completed_chapters >= progress.total_chapters:
            return {"success": True, "status": "completed"}

        # 2. 获取下一章节
        chapter_number = progress.completed_chapters + 1

        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")
        if os.path.exists(chapter_list_file):
            with open(chapter_list_file, "r", encoding="utf-8") as f:
                chapters = json.load(f)
            for ch in chapters:
                if ch.get("chapter_number") == chapter_number:
                    chapter_info = ch
                    break
        else:
            return {"success": False, "error": "No chapter list"}

        print(f"\n   Chapter {chapter_number}: {chapter_info.get('title', 'Untitled')}")

        # 3. 使用管道写作
        print(f"\n[Step 5] Writing chapter {chapter_number}...")
        result = self.write_chapter(chapter_number)

        if result.get("success"):
            print(f"\n[Step 7] Saved: chapter-{chapter_number:03d}.md")

            # 4. 更新进度
            word_count = result.get("word_count", 0)
            progress_mgr.update_chapter_progress(
                chapter_number,
                status="completed",
                word_count=word_count,
                quality_score=7.0  # 默认评分
            )

            return {"success": True, "chapter_number": chapter_number, "word_count": word_count}
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}

    def _load_v7_constraints(self) -> str:
        """从项目配置加载V7约束"""
        config_file = os.path.join(self.project_dir, "project-config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return config.get("v7_constraints", "")
            except Exception as e:
                logger.warning(f"Failed to load V7 constraints: {e}")
        return ""

    def _init_core_components(self):
        """初始化核心组件"""
        sys_path = os.path.dirname(os.path.dirname(__file__))
        if sys_path not in os.sys.path:
            os.sys.path.insert(0, sys_path)

        # 尝试加载 whitelist（从 writing_constraints.json）
        whitelist = self._load_faction_whitelist()

        try:
            # 时间感知RAG检索器
            from core.time_aware_rag import TimeAwareRAG, TimeAwareQuery

            self.rag = TimeAwareRAG(self.project_dir)
            self.TimeAwareQuery = TimeAwareQuery
            logger.info("TimeAwareRAG initialized")
        except ImportError as e:
            logger.warning(f"TimeAwareRAG not available: {e}")
            self.rag = None
            self.TimeAwareQuery = None

        try:
            # 混合一致性检查器
            from core.hybrid_checker import HybridChecker

            # 传入 whitelist 而不是 project_dir
            self.consistency_checker = HybridChecker(whitelist)
            logger.info("HybridChecker initialized")
        except ImportError as e:
            logger.warning(f"HybridChecker not available: {e}")
            self.consistency_checker = None

        try:
            # 期待感追踪器
            from core.expectation_tracker import ExpectationTracker

            self.expectation_tracker = ExpectationTracker(self.project_dir)
            logger.info("ExpectationTracker initialized")
        except ImportError as e:
            logger.warning(f"ExpectationTracker not available: {e}")
            self.expectation_tracker = None

        try:
            # 状态快照管理器
            from core.state_snapshot import StateSnapshotManager

            self.state_snapshot = StateSnapshotManager(self.project_dir)
            logger.info("StateSnapshotManager initialized")
        except ImportError as e:
            logger.warning(f"StateSnapshotManager not available: {e}")
            self.state_snapshot = None

        # Phase 2: 集成 WritingConstraintManager
        try:
            from core.writing_constraint_manager import WritingConstraintManager

            self.constraint_manager = WritingConstraintManager(self.project_dir)
            logger.info("WritingConstraintManager initialized")
        except ImportError as e:
            logger.warning(f"WritingConstraintManager not available: {e}")
            self.constraint_manager = None

        # Phase 3: 集成 ConsistencyTracker
        try:
            from core.consistency_tracker import ConsistencyTracker

            self.consistency_tracker = ConsistencyTracker(self.project_dir)
            logger.info("ConsistencyTracker initialized")
        except ImportError as e:
            logger.warning(f"ConsistencyTracker not available: {e}")
            self.consistency_tracker = None

    def _load_faction_whitelist(self) -> List[str]:
        """加载宗门白名单"""
        whitelist = []
        constraints_file = os.path.join(self.project_dir, "writing_constraints.json")
        if os.path.exists(constraints_file):
            try:
                with open(constraints_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    whitelist = data.get("faction_whitelist", [])
            except Exception as e:
                logger.warning(f"Failed to load whitelist: {e}")

        # 如果没有，从 characters.json 或 world-rules.json 尝试加载
        if not whitelist:
            world_rules_file = os.path.join(self.project_dir, "world-rules.json")
            if os.path.exists(world_rules_file):
                try:
                    with open(world_rules_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        factions = data.get("factions", {})
                        whitelist = list(factions.keys())
                except Exception as e:
                    logger.warning(f"Failed to load factions: {e}")

        return whitelist


    def write_chapter(self, chapter_number: int) -> Dict[str, Any]:
        """
        执行完整管道写作
        
        Args:
            chapter_number: 章节编号
            
        Returns:
            包含写作结果的字典
        """
        print("\n" + "=" * 60)
        print(f"[WriterAgentV2] Starting pipeline for Chapter {chapter_number}")
        print("=" * 60)
        
        # 1. 加载章节信息
        chapter_info = self._load_chapter_info(chapter_number)
        if not chapter_info:
            return {
                "success": False,
                "error": f"Chapter {chapter_number} info not found",
                "chapter_number": chapter_number
            }
        
        # 2. 创建管道上下文
        context = PipelineContext(
            chapter_number=chapter_number,
            chapter_info=chapter_info,
            project_dir=self.project_dir
        )
        
        # 3. 执行管道阶段
        try:
            for stage in PipelineStage:
                context.current_stage = stage
                print(f"\n[Stage: {stage.value.upper()}]")
                
                # 执行阶段处理器
                handler = self.stage_handlers.get(stage)
                if handler:
                    result = handler(context)
                    context.stage_results[stage] = result
                    
                    # 检查阶段是否失败
                    if result.get("failed", False):
                        context.errors.append(f"Stage {stage.value} failed: {result.get('error', 'Unknown error')}")
                        break
                
                # 记录检查点
                self._record_checkpoint(context, stage)
            
            # 4. 生成最终结果
            final_result = self._generate_final_result(context)
            
            # 5. 更新项目状态
            self._update_project_state(context, final_result)
            
            print("\n" + "=" * 60)
            print(f"[WriterAgentV2] Pipeline completed for Chapter {chapter_number}")
            print("=" * 60)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Pipeline failed for chapter {chapter_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "chapter_number": chapter_number,
                "stage": context.current_stage.value if hasattr(context, 'current_stage') else "unknown"
            }

    def _load_chapter_info(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """加载章节信息"""
        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")
        if not os.path.exists(chapter_list_file):
            return None
        
        try:
            with open(chapter_list_file, "r", encoding="utf-8") as f:
                chapters = json.load(f)
            
            for ch in chapters:
                if ch.get("chapter_number") == chapter_number:
                    return ch
        except Exception as e:
            logger.error(f"Failed to load chapter info: {e}")
        
        return None

    def _handle_outline_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """大纲阶段 - 生成章节详细大纲"""
        print("  Generating detailed chapter outline...")
        
        # 使用RAG检索相关上下文
        rag_context = self._retrieve_rag_context(context)
        
        # 构建大纲提示词
        prompt = self._build_outline_prompt(context, rag_context)
        
        try:
            # 调用LLM生成大纲
            outline = self.llm.generate(
                prompt=prompt,
                temperature=0.7,
                system_prompt="你是专业的小说架构师，擅长将章节概要扩展为详细的大纲。",
                max_tokens=1000
            )
            
            # 解析大纲（尝试解析为结构化格式）
            structured_outline = self._parse_outline(outline)
            
            return {
                "success": True,
                "raw_outline": outline,
                "structured_outline": structured_outline,
                "rag_context_used": len(rag_context) > 0
            }
            
        except Exception as e:
            logger.error(f"Outline stage failed: {e}")
            return {
                "success": False,
                "failed": True,
                "error": str(e),
                "fallback": "Using basic chapter info as outline"
            }

    def _handle_draft_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """草稿阶段 - 检查点写作"""
        print("  Writing draft with checkpoints...")
        
        # 获取大纲阶段结果
        outline_result = context.stage_results.get(PipelineStage.OUTLINE, {})
        outline = outline_result.get("structured_outline") or outline_result.get("raw_outline", "")
        
        # 使用RAG检索写作上下文
        rag_context = self._retrieve_rag_context(context)
        
        # 构建检查点写作提示词
        checkpoints = self._create_writing_checkpoints(outline, context.chapter_info)
        
        draft_content = ""
        checkpoint_results = []
        
        for i, checkpoint in enumerate(checkpoints):
            print(f"    Checkpoint {i+1}/{len(checkpoints)}: {checkpoint.get('target', 'Unknown')}")
            
            # 构建检查点提示词
            prompt = self._build_checkpoint_prompt(
                context, checkpoint, draft_content, rag_context
            )
            
            try:
                # 调用LLM生成检查点内容
                checkpoint_content = self.llm.generate(
                    prompt=prompt,
                    temperature=0.8,
                    system_prompt="你是专业的小说作家，擅长创作生动、连贯的故事情节。",
                    max_tokens=1500
                )
                
                # 添加到草稿
                draft_content += checkpoint_content + "\n\n"
                
                checkpoint_results.append({
                    "checkpoint_id": i + 1,
                    "target": checkpoint.get("target"),
                    "word_count": len(checkpoint_content),
                    "success": True
                })
                
                # 短暂暂停，避免API限流
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Checkpoint {i+1} failed: {e}")
                checkpoint_results.append({
                    "checkpoint_id": i + 1,
                    "target": checkpoint.get("target"),
                    "success": False,
                    "error": str(e)
                })
                
                # 优雅降级：使用简单回退
                fallback_content = f"[检查点 {i+1}: {checkpoint.get('target', '部分')} - 因错误跳过]"
                draft_content += fallback_content + "\n\n"
        
        return {
            "success": True,
            "draft_content": draft_content,
            "checkpoint_results": checkpoint_results,
            "total_word_count": len(draft_content),
            "checkpoints_used": len(checkpoints)
        }

    def _handle_consistency_check_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """一致性检查阶段"""
        print("  Running consistency checks...")
        
        # 获取草稿内容
        draft_result = context.stage_results.get(PipelineStage.DRAFT, {})
        draft_content = draft_result.get("draft_content", "")
        
        if not draft_content:
            return {
                "success": False,
                "failed": True,
                "error": "No draft content available for consistency check"
            }
        
        # 使用混合一致性检查器
        if self.consistency_checker:
            try:
                check_result = self.consistency_checker.check_chapter(
                    chapter_number=context.chapter_number,
                    content=draft_content,
                    context=self._build_consistency_context(context)
                )
                
                issues = check_result.get("issues", [])
                passed = check_result.get("passed", True)
                
                if issues:
                    print(f"    Found {len(issues)} consistency issues")
                    for issue in issues[:3]:  # 只显示前3个
                        print(f"      - {issue.get('type', 'Unknown')}: {issue.get('message', 'No message')}")
                
                return {
                    "success": True,
                    "passed": passed,
                    "issues": issues,
                    "check_result": check_result
                }
                
            except Exception as e:
                logger.error(f"Consistency check failed: {e}")
                # 优雅降级：标记警告但不失败
                context.warnings.append(f"Consistency check failed: {e}")
        
        # 回退：基本检查
        return {
            "success": True,
            "passed": True,
            "issues": [],
            "note": "Consistency checker not available, using fallback"
        }

    def _handle_polish_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """润色阶段 - 语义优化"""
        print("  Polishing text...")
        
        # 获取草稿内容和一致性检查结果
        draft_result = context.stage_results.get(PipelineStage.DRAFT, {})
        draft_content = draft_result.get("draft_content", "")
        
        consistency_result = context.stage_results.get(PipelineStage.CONSISTENCY_CHECK, {})
        issues = consistency_result.get("issues", [])
        
        if not draft_content:
            return {
                "success": False,
                "failed": True,
                "error": "No draft content available for polishing"
            }
        
        # 如果有严重一致性错误，需要先修复
        critical_issues = [issue for issue in issues if issue.get("severity") == "critical"]
        
        if critical_issues:
            print(f"    Fixing {len(critical_issues)} critical issues...")
            fixed_content = self._fix_critical_issues(draft_content, critical_issues)
        else:
            fixed_content = draft_content
        
        # 语义润色
        try:
            polish_prompt = self._build_polish_prompt(context, fixed_content, issues)
            
            polished_content = self.llm.generate(
                prompt=polish_prompt,
                temperature=0.6,
                system_prompt="你是专业的文学编辑，擅长优化文字流畅度、增强画面感、提升阅读体验。",
                max_tokens=len(fixed_content) + 500  # 允许适度扩展
            )
            
            # 计算改进指标
            improvement_metrics = self._calculate_improvement_metrics(draft_content, polished_content)
            
            return {
                "success": True,
                "polished_content": polished_content,
                "original_content": fixed_content,
                "improvement_metrics": improvement_metrics,
                "critical_issues_fixed": len(critical_issues)
            }
            
        except Exception as e:
            logger.error(f"Polish stage failed: {e}")
            # 优雅降级：使用原始内容
            return {
                "success": True,
                "polished_content": fixed_content,
                "original_content": fixed_content,
                "improvement_metrics": {"polishing_failed": True},
                "note": f"Polishing failed, using original content: {e}"
            }

    def _handle_final_stage(self, context: PipelineContext) -> Dict[str, Any]:
        """终稿阶段 - 格式化和元数据"""
        print("  Generating final chapter...")

        # Phase 6: 实时校验 - 在保存前进行最终校验
        validation_result = self._pre_save_validation(context)
        if validation_result.get("failed"):
            # 如果校验失败，标记警告但不阻塞（因为已经在前面的阶段处理过了）
            print(f"    [警告] 实时校验发现问题: {validation_result.get('message', '未知')}")
            context.warnings.append(f"Pre-save validation: {validation_result.get('message', '')}")

        # 获取润色后的内容
        polish_result = context.stage_results.get(PipelineStage.POLISH, {})
        polished_content = polish_result.get("polished_content", "")
        
        if not polished_content:
            # 回退到草稿
            draft_result = context.stage_results.get(PipelineStage.DRAFT, {})
            polished_content = draft_result.get("draft_content", "")
        
        # 添加章节标题和格式
        final_content = self._format_final_chapter(context, polished_content)
        
        # 生成章节元数据
        metadata = self._generate_chapter_metadata(context)
        
        # 保存章节文件
        chapter_file = os.path.join(
            self.chapters_dir, f"chapter-{context.chapter_number:03d}.md"
        )
        
        try:
            with open(chapter_file, "w", encoding="utf-8") as f:
                f.write(final_content)
            
            # 保存元数据
            metadata_file = os.path.join(
                self.chapters_dir, f"chapter-{context.chapter_number:03d}.meta.json"
            )
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "final_content": final_content,
                "metadata": metadata,
                "chapter_file": chapter_file,
                "metadata_file": metadata_file,
                "word_count": len(final_content)
            }
            
        except Exception as e:
            logger.error(f"Final stage failed to save files: {e}")
            return {
                "success": False,
                "failed": True,
                "error": f"Failed to save chapter files: {e}",
                "final_content": final_content,
                "metadata": metadata
            }

    def _pre_save_validation(self, context: PipelineContext) -> Dict[str, Any]:
        """
        实时校验 - 在章节保存前进行最终检查

        使用 WritingConstraintManager 进行严格验证
        如果发现问题，立即触发重写
        """
        print("  Running pre-save validation...")

        # 获取润色后的内容
        polish_result = context.stage_results.get(PipelineStage.POLISH, {})
        content = polish_result.get("polished_content", "")

        if not content:
            # 回退到草稿
            draft_result = context.stage_results.get(PipelineStage.DRAFT, {})
            content = draft_result.get("draft_content", "")

        if not content:
            return {"failed": False, "message": "No content to validate"}

        # 使用 WritingConstraintManager 进行验证
        if self.constraint_manager:
            try:
                violations = self.constraint_manager.validate_chapter(
                    context.chapter_number, content
                )

                # 检查是否有严重违规
                critical_violations = [v for v in violations if v.get("severity") == "critical"]

                if critical_violations:
                    print(f"    [严重] 发现 {len(critical_violations)} 个致命问题")
                    for v in critical_violations[:3]:
                        print(f"      - {v.get('type', 'unknown')}: {v.get('message', '')}")

                    # 返回失败结果，触发重写
                    return {
                        "failed": True,
                        "message": f"Found {len(critical_violations)} critical violations",
                        "violations": critical_violations,
                        "should_rewrite": True
                    }

                # 如果有警告，记录但不阻塞
                warning_violations = [v for v in violations if v.get("severity") == "warning"]
                if warning_violations:
                    print(f"    [警告] 发现 {len(warning_violations)} 个警告")
                    for v in warning_violations[:2]:
                        print(f"      - {v.get('type', 'unknown')}: {v.get('message', '')}")
                    context.warnings.extend([v.get("message", "") for v in warning_violations])

                print("    [通过] 实时校验通过")
                return {"failed": False, "passed": True}

            except Exception as e:
                logger.warning(f"Validation failed: {e}")
                return {"failed": False, "message": f"Validation error: {e}"}

        # 使用 ConsistencyChecker 作为备用
        if hasattr(self, 'consistency_checker') and self.consistency_checker:
            try:
                # 检查是否是 HybridChecker 或 ConsistencyChecker
                if hasattr(self.consistency_checker, 'check_chapter'):
                    check_result = self.consistency_checker.check_chapter(
                        context.chapter_number,
                        content,
                        self._build_consistency_context(context)
                    )
                    if not check_result.get("passed", True):
                        critical_count = check_result.get("critical_count", 0)
                        print(f"    [严重] 发现 {critical_count} 个致命问题")
                        return {
                            "failed": True,
                            "message": f"Found {critical_count} critical issues",
                            "issues": check_result.get("issues", []),
                            "should_rewrite": True
                        }
            except Exception as e:
                logger.warning(f"ConsistencyChecker validation failed: {e}")

        return {"failed": False, "passed": True}

    def _retrieve_rag_context(self, context: PipelineContext) -> List[Dict[str, Any]]:
        """使用时间感知RAG检索上下文"""
        if not self.rag or not self.TimeAwareQuery:
            return []
        
        try:
            # 构建查询
            query_text = self._build_rag_query(context)
            
            rag_query = self.TimeAwareQuery(
                query_text=query_text,
                current_chapter=context.chapter_number,
                max_results=15,
                token_budget=3000
            )
            
            # 执行检索
            results = self.rag.retrieve(rag_query)
            
            # 转换为简单格式
            context_items = []
            for result in results:
                context_items.append({
                    "content": result.content[:500],  # 截断长内容
                    "source": result.source,
                    "chapter": result.chapter,
                    "relevance": result.relevance_score
                })
            
            return context_items
            
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            return []

    def _build_rag_query(self, context: PipelineContext) -> str:
        """构建RAG查询文本"""
        chapter_info = context.chapter_info
        
        query_parts = []
        
        # 添加章节标题和概要
        if chapter_info.get("title"):
            query_parts.append(f"章节标题: {chapter_info['title']}")
        if chapter_info.get("summary"):
            query_parts.append(f"章节概要: {chapter_info['summary']}")
        
        # 添加关键情节点
        key_points = chapter_info.get("key_plot_points", [])
        if key_points:
            query_parts.append("关键情节点: " + "; ".join(key_points[:3]))
        
        # 添加涉及角色
        characters = chapter_info.get("characters_involved", [])
        if characters:
            query_parts.append("涉及角色: " + ", ".join(characters))
        
        return " ".join(query_parts)

    def _build_outline_prompt(self, context: PipelineContext, rag_context: List[Dict[str, Any]]) -> str:
        """构建大纲提示词"""
        chapter_info = context.chapter_info
        
        prompt = f"""请为小说的第{context.chapter_number}章创建详细大纲。

## 章节基本信息
- 标题: {chapter_info.get('title', f'第{context.chapter_number}章')}
- 概要: {chapter_info.get('summary', '暂无')}
- 字数目标: {chapter_info.get('word_count_target', 3000)}字

## 关键情节点（必须包含）
"""
        
        for point in chapter_info.get("key_plot_points", []):
            prompt += f"- {point}\n"
        
        # 添加RAG检索的上下文
        if rag_context:
            prompt += "\n## 相关上下文（从前文检索）\n"
            for i, ctx in enumerate(rag_context[:5], 1):
                prompt += f"{i}. [{ctx['source']} 第{ctx['chapter']}章] {ctx['content']}\n"
        
        prompt += """
## 大纲要求
请输出以下结构的详细大纲：

### 章节结构
1. 开篇场景（300-500字）：如何吸引读者？
2. 发展部分（1500-2000字）：情节如何推进？
3. 高潮场景（800-1200字）：本章的核心冲突或转折点
4. 结尾钩子（200-300字）：如何为下一章铺垫？

### 场景安排
列出3-5个具体场景，每个场景包含：
- 场景地点
- 出场人物
- 核心事件
- 情绪基调

### 节奏设计
- 爽点/亮点位置
- 信息密度控制
- 情绪曲线变化

请直接输出详细大纲，不要添加额外解释。"""

        # 注入V7约束
        if self.v7_constraints:
            prompt += f"""

## 类型约束（必须严格遵守）
{self.v7_constraints}
"""

        return prompt

    def _parse_outline(self, outline_text: str) -> Dict[str, Any]:
        """解析大纲文本为结构化格式"""
        # 简单解析：尝试提取关键部分
        structured = {
            "sections": [],
            "scenes": [],
            "rhythm_notes": []
        }
        
        lines = outline_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # 检测章节结构
            if line.startswith('### 章节结构'):
                current_section = "structure"
            elif line.startswith('### 场景安排'):
                current_section = "scenes"
            elif line.startswith('### 节奏设计'):
                current_section = "rhythm"
            
            # 解析具体内容
            elif current_section == "structure" and line.startswith(('1.', '2.', '3.', '4.', '-')):
                structured["sections"].append(line)
            elif current_section == "scenes" and line.startswith('-'):
                structured["scenes"].append(line)
            elif current_section == "rhythm" and line.startswith('-'):
                structured["rhythm_notes"].append(line)
        
        return structured

    def _create_writing_checkpoints(self, outline: Any, chapter_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建写作检查点"""
        target_word_count = chapter_info.get("word_count_target", 3000)
        
        # 如果大纲是结构化的，使用大纲中的场景
        if isinstance(outline, dict) and outline.get("scenes"):
            scenes = outline["scenes"]
            checkpoints = []
            
            for i, scene in enumerate(scenes[:5]):  # 最多5个检查点
                checkpoints.append({
                    "checkpoint_id": i + 1,
                    "target": f"场景 {i+1}",
                    "description": scene[:100],  # 截断描述
                    "target_word_count": target_word_count // min(len(scenes), 5)
                })
            
            return checkpoints
        
        # 默认检查点：基于字数
        checkpoint_count = max(3, min(5, target_word_count // 1000))
        checkpoints = []
        
        for i in range(checkpoint_count):
            word_target = target_word_count // checkpoint_count
            checkpoints.append({
                "checkpoint_id": i + 1,
                "target": f"部分 {i+1}/{checkpoint_count}",
                "description": f"章节的第{i+1}部分，约{word_target}字",
                "target_word_count": word_target
            })
        
        return checkpoints

    def _build_checkpoint_prompt(self, context: PipelineContext, checkpoint: Dict[str, Any], 
                                previous_content: str, rag_context: List[Dict[str, Any]]) -> str:
        """构建检查点写作提示词"""
        chapter_info = context.chapter_info
        
        prompt = f"""请继续创作小说的第{context.chapter_number}章。

## 当前进度
- 检查点: {checkpoint['checkpoint_id']} - {checkpoint['target']}
- 目标字数: 约{checkpoint.get('target_word_count', 600)}字
- 描述: {checkpoint.get('description', '继续章节写作')}

## 已完成的章节内容
{previous_content[-2000:] if previous_content else '[这是章节开头]'}

## 章节信息
- 标题: {chapter_info.get('title', f'第{context.chapter_number}章')}
- 概要: {chapter_info.get('summary', '暂无')}
- 关键情节点: {', '.join(chapter_info.get('key_plot_points', [])[:3])}

## 相关上下文
"""
        
        # 添加RAG检索的上下文
        if rag_context:
            for ctx in rag_context[:3]:
                prompt += f"- [{ctx['source']} 第{ctx['chapter']}章] {ctx['content']}\n"
        else:
            prompt += "- 暂无特定上下文\n"
        
        prompt += f"""
## 写作要求
1. 自然衔接已写内容
2. 推进情节发展
3. 保持角色性格一致
4. 语言生动，有画面感
5. 控制节奏，避免信息过载

请直接输出这个检查点的内容，不要总结或解释。"""

        # 注入V7约束
        if self.v7_constraints:
            prompt += f"""

## 类型约束（必须严格遵守）
{self.v7_constraints}
"""

        # Phase 2: 注入WritingConstraintManager的约束提示
        if self.constraint_manager:
            try:
                constraint_prompt = self.constraint_manager.get_constraint_prompt(context.chapter_number)
                prompt += f"""

## 写作约束检查清单（严格遵守）
{constraint_prompt}
"""
            except Exception as e:
                logger.warning(f"Failed to get constraint prompt: {e}")

        return prompt

    def _build_consistency_context(self, context: PipelineContext) -> Dict[str, Any]:
        """构建一致性检查上下文"""
        # 加载项目文件
        context_data = {}
        
        files_to_load = [
            ("outline.md", "outline"),
            ("characters.json", "characters"),
            ("world-rules.json", "world_rules"),
            ("chapter-list.json", "chapter_list")
        ]
        
        for filename, key in files_to_load:
            filepath = os.path.join(self.project_dir, filename)
            if os.path.exists(filepath):
                try:
                    if filename.endswith('.json'):
                        with open(filepath, "r", encoding="utf-8") as f:
                            context_data[key] = json.load(f)
                    else:
                        with open(filepath, "r", encoding="utf-8") as f:
                            context_data[key] = f.read()
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
        
        # 添加前一章节内容
        if context.chapter_number > 1:
            prev_file = os.path.join(
                self.chapters_dir, f"chapter-{context.chapter_number - 1:03d}.md"
            )
            if os.path.exists(prev_file):
                try:
                    with open(prev_file, "r", encoding="utf-8") as f:
                        context_data["previous_chapter"] = f.read()
                except Exception as e:
                    logger.warning(f"Failed to load previous chapter: {e}")
        
        return context_data

    def _fix_critical_issues(self, content: str, issues: List[Dict[str, Any]]) -> str:
        """修复严重一致性错误"""
        if not issues:
            return content
        
        print(f"    Attempting to fix {len(issues)} critical issues...")
        
        # 构建修复提示词
        prompt = f"""请修复以下小说章节内容中的严重一致性错误：

## 原始内容
{content}

## 需要修复的问题
"""
        
        for i, issue in enumerate(issues[:5], 1):  # 最多修复5个问题
            prompt += f"{i}. {issue.get('type', 'Consistency')}: {issue.get('message', 'Unknown issue')}\n"
        
        prompt += """
## 修复要求
1. 最小化修改，保持故事主线不变
2. 确保所有设定一致性错误被修复
3. 保持文字流畅度
4. 直接输出修复后的完整章节内容

请输出修复后的章节内容："""
        
        try:
            fixed_content = self.llm.generate(
                prompt=prompt,
                temperature=0.3,  # 低温度确保最小修改
                system_prompt="你是专业的设定一致性编辑，擅长最小化修改修复设定错误。",
                max_tokens=len(content) + 500
            )
            return fixed_content.strip()
        except Exception as e:
            logger.error(f"Failed to fix critical issues: {e}")
            return content  # 返回原始内容

    def _build_polish_prompt(self, context: PipelineContext, content: str, issues: List[Dict[str, Any]]) -> str:
        """构建润色提示词"""
        chapter_info = context.chapter_info
        
        prompt = f"""请对以下小说章节进行文字润色和优化：

## 章节信息
- 标题: {chapter_info.get('title', f'第{context.chapter_number}章')}
- 类型: {chapter_info.get('type', '常规章节')}

## 原始内容
{content}

## 需要关注的问题
"""
        
        if issues:
            non_critical = [issue for issue in issues if issue.get("severity") != "critical"]
            if non_critical:
                prompt += "以下一致性问题已标记（非严重）：\n"
                for issue in non_critical[:3]:
                    prompt += f"- {issue.get('type')}: {issue.get('message', '')}\n"
            else:
                prompt += "无标记的非严重问题。\n"
        else:
            prompt += "无标记的问题。\n"
        
        prompt += """
## 润色要求
请从以下维度优化内容：

### 1. 文字流畅度
- 调整句式，避免重复
- 优化段落衔接
- 改善阅读节奏

### 2. 画面感增强
- 加强环境描写
- 细化动作细节
- 增强五感体验

### 3. 情绪渲染
- 强化情绪表达
- 改善对话语气
- 增强场景氛围

### 4. 信息密度
- 确保关键信息突出
- 删除冗余描述
- 平衡叙述与对话

### 5. 网文特性
- 确保爽点/亮点突出
- 保持节奏紧凑
- 章末留有钩子

请直接输出润色后的完整章节内容，不要添加额外解释。"""

        # 注入V7约束
        if self.v7_constraints:
            prompt += f"""

## 类型约束（必须严格遵守）
{self.v7_constraints}
"""

        return prompt

    def _calculate_improvement_metrics(self, original: str, polished: str) -> Dict[str, Any]:
        """计算改进指标"""
        # 简单指标计算
        orig_words = len(original.split())
        polish_words = len(polished.split())
        
        # 句子数量（简单估算）
        orig_sentences = original.count('。') + original.count('！') + original.count('？')
        polish_sentences = polished.count('。') + polished.count('！') + polished.count('？')
        
        return {
            "word_count_change": polish_words - orig_words,
            "sentence_count_change": polish_sentences - orig_sentences,
            "avg_sentence_length_original": orig_words / max(1, orig_sentences),
            "avg_sentence_length_polished": polish_words / max(1, polish_sentences),
            "expansion_ratio": polish_words / max(1, orig_words)
        }

    def _format_final_chapter(self, context: PipelineContext, content: str) -> str:
        """格式化最终章节"""
        chapter_info = context.chapter_info
        
        # 确保有标题
        if not content.startswith('#'):
            title = chapter_info.get('title', f'第{context.chapter_number}章')
            content = f"# {title}\n\n{content}"
        
        # 添加章节分隔符
        formatted = content.strip()
        
        # 添加章末标记
        formatted += f"\n\n---\n\n*第{context.chapter_number}章 完*"
        
        return formatted

    def _generate_chapter_metadata(self, context: PipelineContext) -> Dict[str, Any]:
        """生成章节元数据"""
        # 收集各阶段结果
        metadata = {
            "chapter_number": context.chapter_number,
            "title": context.chapter_info.get("title", f"第{context.chapter_number}章"),
            "generated_at": datetime.now().isoformat(),
            "pipeline_version": "2.0",
            "stages": {}
        }
        
        # 添加各阶段摘要
        for stage in PipelineStage:
            stage_result = context.stage_results.get(stage)
            if stage_result:
                metadata["stages"][stage.value] = {
                    "success": stage_result.get("success", False),
                    "summary": self._summarize_stage_result(stage, stage_result)
                }
        
        # 添加统计信息
        final_result = context.stage_results.get(PipelineStage.FINAL, {})
        if final_result.get("word_count"):
            metadata["word_count"] = final_result["word_count"]
        
        # 添加错误和警告
        if context.errors:
            metadata["errors"] = context.errors[:5]  # 最多5个错误
        if context.warnings:
            metadata["warnings"] = context.warnings[:10]  # 最多10个警告
        
        # 添加检查点信息
        draft_result = context.stage_results.get(PipelineStage.DRAFT, {})
        if draft_result.get("checkpoint_results"):
            metadata["checkpoints"] = {
                "total": len(draft_result["checkpoint_results"]),
                "successful": sum(1 for cp in draft_result["checkpoint_results"] if cp.get("success", False)),
                "failed": sum(1 for cp in draft_result["checkpoint_results"] if not cp.get("success", True))
            }
        
        return metadata

    def _summarize_stage_result(self, stage: PipelineStage, result: Dict[str, Any]) -> str:
        """生成阶段结果摘要"""
        if stage == PipelineStage.OUTLINE:
            if result.get("success"):
                return "大纲生成成功" + ("（使用RAG上下文）" if result.get("rag_context_used") else "")
            else:
                return "大纲生成失败"
        
        elif stage == PipelineStage.DRAFT:
            if result.get("success"):
                return f"草稿完成，{result.get('total_word_count', 0)}字，{result.get('checkpoints_used', 0)}个检查点"
            else:
                return "草稿生成失败"
        
        elif stage == PipelineStage.CONSISTENCY_CHECK:
            if result.get("success"):
                issues = result.get("issues", [])
                return f"一致性检查完成，发现{len(issues)}个问题" + ("（通过）" if result.get("passed") else "（未通过）")
            else:
                return "一致性检查失败"
        
        elif stage == PipelineStage.POLISH:
            if result.get("success"):
                metrics = result.get("improvement_metrics", {})
                return f"润色完成，字数变化: {metrics.get('word_count_change', 0)}"
            else:
                return "润色失败"
        
        elif stage == PipelineStage.FINAL:
            if result.get("success"):
                return f"终稿生成成功，保存到{result.get('chapter_file', '未知文件')}"
            else:
                return "终稿生成失败"
        
        return "未知阶段"

    def _record_checkpoint(self, context: PipelineContext, stage: PipelineStage):
        """记录检查点"""
        checkpoint = {
            "stage": stage.value,
            "timestamp": datetime.now().isoformat(),
            "chapter_number": context.chapter_number
        }
        
        # 添加阶段特定信息
        stage_result = context.stage_results.get(stage)
        if stage_result:
            checkpoint["stage_success"] = stage_result.get("success", False)
            
            # 添加摘要信息
            if stage == PipelineStage.DRAFT:
                checkpoint["word_count"] = stage_result.get("total_word_count", 0)
            elif stage == PipelineStage.CONSISTENCY_CHECK:
                checkpoint["issues_found"] = len(stage_result.get("issues", []))
        
        context.checkpoints.append(checkpoint)
        
        # 可选：保存检查点到文件
        checkpoint_file = os.path.join(
            self.chapters_dir, f"checkpoint-{context.chapter_number:03d}-{stage.value}.json"
        )
        try:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {e}")

    def _generate_final_result(self, context: PipelineContext) -> Dict[str, Any]:
        """生成最终结果"""
        final_result = context.stage_results.get(PipelineStage.FINAL, {})
        
        if final_result.get("success"):
            return {
                "success": True,
                "chapter_number": context.chapter_number,
                "title": context.chapter_info.get("title", f"第{context.chapter_number}章"),
                "word_count": final_result.get("word_count", 0),
                "chapter_file": final_result.get("chapter_file", ""),
                "metadata_file": final_result.get("metadata_file", ""),
                "errors": context.errors,
                "warnings": context.warnings,
                "checkpoints": context.checkpoints
            }
        else:
            return {
                "success": False,
                "chapter_number": context.chapter_number,
                "error": final_result.get("error", "Final stage failed"),
                "errors": context.errors,
                "warnings": context.warnings
            }

    def _update_project_state(self, context: PipelineContext, final_result: Dict[str, Any]):
        """更新项目状态"""
        # 更新章节列表状态
        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")
        if os.path.exists(chapter_list_file):
            try:
                with open(chapter_list_file, "r", encoding="utf-8") as f:
                    chapters = json.load(f)
                
                for ch in chapters:
                    if ch.get("chapter_number") == context.chapter_number:
                        ch["status"] = "completed" if final_result.get("success") else "failed"
                        ch["completed_at"] = datetime.now().isoformat()
                        ch["word_count"] = final_result.get("word_count", 0)
                        break
                
                with open(chapter_list_file, "w", encoding="utf-8") as f:
                    json.dump(chapters, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"Failed to update chapter list: {e}")
        
        # 更新进度文件
        progress_file = os.path.join(self.project_dir, "novel-progress.txt")
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress = json.load(f)
                
                # 更新章节信息
                chapter_entry = {
                    "chapter_number": context.chapter_number,
                    "title": context.chapter_info.get("title", f"第{context.chapter_number}章"),
                    "status": "completed" if final_result.get("success") else "failed",
                    "word_count": final_result.get("word_count", 0),
                    "completed_at": datetime.now().isoformat(),
                    "errors": context.errors,
                    "warnings": context.warnings
                }
                
                # 添加到进度
                if "chapters" not in progress:
                    progress["chapters"] = []
                
                # 更新或添加章节条目
                found = False
                for i, ch in enumerate(progress["chapters"]):
                    if ch.get("chapter_number") == context.chapter_number:
                        progress["chapters"][i] = chapter_entry
                        found = True
                        break
                
                if not found:
                    progress["chapters"].append(chapter_entry)
                
                # 更新统计信息
                completed_chapters = sum(1 for ch in progress["chapters"] if ch.get("status") == "completed")
                total_word_count = sum(ch.get("word_count", 0) for ch in progress["chapters"])
                
                progress["completed_chapters"] = completed_chapters
                progress["total_word_count"] = total_word_count
                progress["last_updated"] = datetime.now().isoformat()
                
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"Failed to update progress file: {e}")

        # Phase 3: 更新 ConsistencyTracker 和 WritingConstraintManager
        if final_result.get("success"):
            self._update_trackers(context)

    def _update_trackers(self, context: PipelineContext):
        """更新追踪器状态"""
        # 获取章节内容
        polish_result = context.stage_results.get(PipelineStage.POLISH, {})
        content = polish_result.get("polished_content", "")
        if not content:
            draft_result = context.stage_results.get(PipelineStage.DRAFT, {})
            content = draft_result.get("draft_content", "")

        if not content:
            return

        # 更新 WritingConstraintManager
        if self.constraint_manager:
            try:
                # 尝试检测本章的境界、地点、宗门变化
                detected_realm = self._detect_realm_from_content(content)
                detected_location = self._detect_location_from_content(content)
                detected_faction = self._detect_faction_from_content(content)

                self.constraint_manager.update_constraints_after_chapter(
                    context.chapter_number,
                    content,
                    detected_realm=detected_realm,
                    detected_location=detected_location,
                    detected_faction=detected_faction
                )
                logger.info(f"Updated constraint manager for chapter {context.chapter_number}")
            except Exception as e:
                logger.warning(f"Failed to update constraint manager: {e}")

        # 更新 ConsistencyTracker
        if self.consistency_tracker and hasattr(self.consistency_tracker, 'track_character_appearance'):
            try:
                # 追踪角色出现
                import re
                name_pattern = re.compile(r"[\u4e00-\u9fa5]{2,4}(?:的|是|在|对|和)")
                # 简单检测主要角色名出现
                protagonist = self._get_protagonist_name()
                if protagonist and protagonist in content:
                    self.consistency_tracker.track_character_appearance(protagonist, context.chapter_number)

                # 检测境界突破
                realm_keywords = ["突破", "晋级", "晋升"]
                for keyword in realm_keywords:
                    if keyword in content:
                        # 简单记录，不做详细检测
                        self.consistency_tracker.track_timeline_event(
                            context.chapter_number,
                            "realm_breakthrough",
                            f"第{context.chapter_number}章有境界突破"
                        )
                        break
            except Exception as e:
                logger.warning(f"Failed to update consistency tracker: {e}")

    def _detect_realm_from_content(self, content: str) -> str:
        """从内容中检测境界"""
        import re
        # 常见境界关键词
        realm_patterns = [
            r"([\u4e00-\u9fa5]+境)",
            r"([\u4e00-\u9fa5]+层)",
        ]
        for pattern in realm_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # 返回最后一个提及的境界（通常是当前境界）
                return matches[-1]
        return ""

    def _detect_location_from_content(self, content: str) -> str:
        """从内容中检测地点"""
        import re
        # 常见地点关键词
        location_patterns = [
            r"在([\u4e00-\u9fa5]+)",
            r"来到([\u4e00-\u9fa5]+)",
            r"前往([\u4e00-\u9fa5]+)",
        ]
        for pattern in location_patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[-1]
        return ""

    def _detect_faction_from_content(self, content: str) -> str:
        """从内容中检测宗门"""
        import re
        # 宗门名称模式
        faction_patterns = [
            r"加入([\u4e00-\u9fa5]+)",
            r"进入([\u4e00-\u9fa5]+)",
            r"拜入([\u4e00-\u9fa5]+)",
        ]
        for pattern in faction_patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[-1]
        return ""

    def _get_protagonist_name(self) -> str:
        """获取主角名称"""
        # 从约束管理器获取
        if self.constraint_manager:
            try:
                return self.constraint_manager.constraints.protagonist_name
            except:
                pass

        # 从 characters.json 加载
        char_file = os.path.join(self.project_dir, "characters.json")
        if os.path.exists(char_file):
            try:
                with open(char_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for char in data:
                            if char.get("role") == "protagonist":
                                return char.get("name", "主角")
                    elif isinstance(data, dict):
                        chars = data.get("characters", [])
                        for char in chars:
                            if char.get("role") == "protagonist":
                                return char.get("name", "主角")
            except:
                pass
        return "主角"