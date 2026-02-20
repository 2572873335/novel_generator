"""
角色管理系统
管理小说角色的设定和一致性
"""

import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class Character:
    """角色数据类"""
    name: str
    role: str  # protagonist, antagonist, supporting, minor
    age: int
    appearance: str
    personality: str
    background: str
    motivation: str
    character_arc: str  # 角色成长弧线
    relationships: Dict[str, str] = field(default_factory=dict)
    distinctive_features: List[str] = field(default_factory=list)
    speech_patterns: str = ""  # 说话风格
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        return cls(**data)
    
    def get_profile_text(self) -> str:
        """获取角色档案文本"""
        return f"""# {self.name}

**角色定位**: {self.role}
**年龄**: {self.age}

## 外貌特征
{self.appearance}

## 性格特点
{self.personality}

## 背景故事
{self.background}

## 动机与目标
{self.motivation}

## 成长弧线
{self.character_arc}

## 人际关系
{chr(10).join(f'- {k}: {v}' for k, v in self.relationships.items())}

## 显著特征
{chr(10).join(f'- {f}' for f in self.distinctive_features)}

## 说话风格
{self.speech_patterns}

## 备注
{self.notes}
"""


class CharacterManager:
    """角色管理器"""
    
    def __init__(self, project_dir: str, characters_file: str = "characters.json"):
        self.project_dir = project_dir
        self.characters_file = os.path.join(project_dir, characters_file)
        self.characters: List[Character] = []
        self.name_index: Dict[str, Character] = {}
    
    def create_characters(self, characters_data: List[Dict[str, Any]]) -> List[Character]:
        """基于数据创建角色"""
        self.characters = []
        for char_data in characters_data:
            character = Character(**char_data)
            self.characters.append(character)
            self.name_index[character.name] = character
        
        self._save_characters()
        return self.characters
    
    def load_characters(self) -> List[Character]:
        """加载角色数据"""
        if not os.path.exists(self.characters_file):
            return []
        
        try:
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.characters = [Character.from_dict(ch) for ch in data]
            self.name_index = {ch.name: ch for ch in self.characters}
            return self.characters
        except Exception as e:
            print(f"加载角色数据失败: {e}")
            return []
    
    def _save_characters(self):
        """保存角色数据"""
        os.makedirs(self.project_dir, exist_ok=True)
        
        data = [ch.to_dict() for ch in self.characters]
        
        with open(self.characters_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_character(self, name: str) -> Optional[Character]:
        """获取特定角色"""
        return self.name_index.get(name)
    
    def get_main_characters(self) -> List[Character]:
        """获取主要角色"""
        return [ch for ch in self.characters if ch.role in ['protagonist', 'antagonist']]
    
    def get_supporting_characters(self) -> List[Character]:
        """获取配角"""
        return [ch for ch in self.characters if ch.role == 'supporting']
    
    def update_character(self, name: str, **kwargs):
        """更新角色信息"""
        character = self.get_character(name)
        if not character:
            return
        
        for key, value in kwargs.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        self._save_characters()
    
    def generate_character_guide(self) -> str:
        """生成角色写作指南"""
        guide = "# 角色写作指南\n\n"
        
        # 主要角色
        main_chars = self.get_main_characters()
        if main_chars:
            guide += "## 主要角色\n\n"
            for char in main_chars:
                guide += f"### {char.name} ({char.role})\n"
                guide += f"- **性格**: {char.personality[:100]}...\n"
                guide += f"- **动机**: {char.motivation[:100]}...\n"
                guide += f"- **说话风格**: {char.speech_patterns[:100]}...\n\n"
        
        # 配角
        supporting_chars = self.get_supporting_characters()
        if supporting_chars:
            guide += "## 配角\n\n"
            for char in supporting_chars:
                guide += f"- **{char.name}**: {char.personality[:80]}...\n"
        
        # 一致性检查清单
        guide += """\n## 角色一致性检查清单
写作时请注意：
1. [ ] 角色的行为是否符合其性格设定？
2. [ ] 角色的对话是否符合其说话风格？
3. [ ] 角色的动机是否一致？
4. [ ] 角色的成长弧线是否自然展现？
5. [ ] 角色之间的关系是否准确？
"""
        
        return guide
    
    def check_character_consistency(self, chapter_content: str, characters_involved: List[str]) -> Dict[str, Any]:
        """
        检查角色一致性（简化版本）
        实际可以使用LLM进行更复杂的检查
        """
        issues = []
        
        for char_name in characters_involved:
            character = self.get_character(char_name)
            if not character:
                issues.append(f"未找到角色 '{char_name}' 的设定")
                continue
            
            # 检查角色名是否出现在章节中
            if char_name not in chapter_content:
                issues.append(f"角色 '{char_name}' 未在章节中出现")
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues
        }
