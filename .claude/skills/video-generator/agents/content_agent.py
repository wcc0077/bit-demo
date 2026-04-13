"""
Content Agent - 数据结构定义
只保留 VideoScript 等数据结构，不定义内容生成逻辑
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Keyword:
    word: str
    color: str
    category: str = ""


@dataclass
class Section:
    title: str
    duration: int
    content: str
    visual: str
    key_points: List[str] = field(default_factory=list)
    keywords: List[Keyword] = field(default_factory=list)
    animation_type: str = "center"


@dataclass
class VideoScript:
    topic: str
    target_duration: int
    sections: List[Section]
    hook: str = ""
    takeaway: str = ""
    all_keywords: List[Keyword] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# {self.topic}",
            "",
            f"**目标时长**: {self.target_duration}秒",
            f"**实际时长**: {sum(s.duration for s in self.sections)}秒",
            "",
            "---",
            ""
        ]
        for i, s in enumerate(self.sections, 1):
            lines.extend([
                f"## {i}. {s.title} ({s.duration}秒)",
                "",
                "**内容**:",
                s.content,
                "",
                "**视觉**:",
                s.visual,
                "",
            ])
            if s.key_points:
                lines.extend(["**要点**:", *[f"- {kp}" for kp in s.key_points], ""])
            lines.extend(["---", ""])
        return "\n".join(lines)
