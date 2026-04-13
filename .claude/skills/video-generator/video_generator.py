"""
Video Generator - 协调层（v10）
双 Agent 协作 + 自动评审：Content Agent 写脚本 → 评审优化 → Manim Agent 写动画 → 评审优化 → Python 执行
"""

import asyncio
import hashlib
import re
import time
from pathlib import Path
from typing import Optional, List

import yaml

from agents.content_agent import VideoScript, Section, Keyword
from pipeline.executor import (
    generate_audio, generate_subtitles, render_manim, compose_video,
    align_scene_durations, _measure_and_fix_wait,
)


def _load_config(config_path: Path) -> dict:
    """加载配置"""
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    raise FileNotFoundError(f"配置文件不存在: {config_path}")


def _build_keyword_map(config: dict) -> dict:
    """从配置构建 {关键词: 颜色} 映射"""
    mapping = {}
    for group in config["keyword_colors"].values():
        for word in group["words"]:
            mapping[word] = group["color"]
    return mapping


def _build_topic_map(config: dict) -> dict:
    return config.get("topic_names", {})


def _select_template(topic: str, config: dict, override: str = "") -> dict:
    """根据主题自动选择模板"""
    if override and override in config["templates"]:
        return config["templates"][override]
    if any(w in topic for w in ["历史", "演变", "历程", "发展", "进化"]):
        return config["templates"]["history_evolution"]
    if any(w in topic for w in ["对比", "区别", "vs", "选择"]):
        return config["templates"]["comparison"]
    return config["templates"]["concept_explanation"]


def _extract_keywords(text: str, keyword_map: dict) -> List[Keyword]:
    return [Keyword(word=w, color=c) for w, c in keyword_map.items() if w in text]


def _parse_script(content: str, keyword_map: dict) -> VideoScript:
    """解析 script.md 为 VideoScript 对象"""
    lines = content.split('\n')

    topic = ""
    for line in lines:
        if line.startswith('# ') and not line.startswith('# #'):
            topic = line[2:].strip()
            break

    sections_dict = []
    current = None

    for line in lines:
        if line.startswith('## '):
            if current:
                sections_dict.append(current)
            title_part = line[3:]
            dur_match = re.search(r'\((\d+)秒\)', title_part)
            title = re.sub(r'\s*\(\d+秒\)', '', title_part)
            current = {"title": title, "duration": int(dur_match.group(1)) if dur_match else 20,
                       "content": "", "visual": "", "key_points": [], "type": None}
        elif current:
            if line.startswith('**内容**:'):
                current["type"] = "content"
                part = line.split('**内容**:', 1)[-1].strip()
                if part:
                    current["content"] = part
            elif line.startswith('**视觉'):
                current["type"] = "visual"
                part = line.split(':', 1)[-1].strip()
                if part:
                    current["visual"] = part
            elif line.startswith('**要点**:') or line.startswith('**关键要点**'):
                current["type"] = "key_points"
            elif line.startswith('- ') and current["type"] == "key_points":
                current["key_points"].append(line[2:])
            elif line.strip() and not line.startswith('**') and not line.startswith('---'):
                if current["type"] == "content":
                    current["content"] += line + " "
                elif current["type"] == "visual":
                    current["visual"] += line + " "

    if current:
        sections_dict.append(current)

    all_kw = []
    sections = []
    for s in sections_dict:
        kw = _extract_keywords(s["title"] + s["content"], keyword_map)
        sections.append(Section(
            title=s["title"], duration=s["duration"],
            content=s["content"].strip(), visual=s["visual"].strip(),
            key_points=s["key_points"], keywords=kw,
        ))
        all_kw.extend(kw)

    seen = set()
    unique_kw = [k for k in all_kw if k.word not in seen and not seen.add(k.word)]
    return VideoScript(topic=topic, target_duration=0, sections=sections, all_keywords=unique_kw)


class VideoGenerator:
    """视频生成协调器 — 只负责目录创建和媒体执行"""

    def __init__(self, topic: str, output_dir: Optional[Path] = None,
                 target_duration: int = 150, template: str = ""):
        self.topic = topic
        self.target_duration = target_duration
        config_path = Path(__file__).parent / "config.yaml"
        self.config = _load_config(config_path)

        self.keyword_map = _build_keyword_map(self.config)
        self.topic_map = _build_topic_map(self.config)
        self.template = _select_template(topic, self.config, template)

        folder = self._sanitize_topic_name(topic)
        project_root = Path(__file__).parent.parent.parent.parent
        output_base = project_root / "videos_generated"
        output_base.mkdir(parents=True, exist_ok=True)

        self.output_dir = Path(output_dir) if output_dir else output_base / folder
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.script_file = self.output_dir / "script.md"
        self.manim_file = self.output_dir / "animation.py"
        self.cover_file = self.output_dir / "cover.py"
        self.audio_dir = self.output_dir / "audio"
        self.audio_file = self.audio_dir / "voice.mp3"
        self.subtitle_file = self.output_dir / "subtitles.srt"
        self.final_video = self.output_dir / "final.mp4"

    def _sanitize_topic_name(self, topic: str) -> str:
        for cn, en in self.topic_map.items():
            if cn in topic:
                base = en
                break
        else:
            name = re.sub(r'[\u4e00-\u9fff]', '', topic)
            name = re.sub(r'[^\w\s-]', '', name)
            name = re.sub(r'\s+', '-', name.strip())
            name = re.sub(r'-+', '-', name).strip('-')
            base = name.lower() if name else f"topic-{hashlib.md5(topic.encode()).hexdigest()[:6]}"
        return f"{base}_{int(time.time())}"

    # ── 脚本读写 ──────────────────────────────────────────

    def load_script(self) -> Optional[VideoScript]:
        if not self.script_file.exists():
            return None
        return _parse_script(self.script_file.read_text(encoding='utf-8'), self.keyword_map)

    def save_script(self, script: VideoScript):
        self.script_file.write_text(script.to_markdown(), encoding='utf-8')

    # ── 流程 ──────────────────────────────────────────

    def regenerate(self):
        """从已有脚本和动画代码生成媒体"""
        script = self.load_script()
        if not script:
            print("[WARN] 未找到已有脚本")
            return

        if not self.manim_file.exists() or not self.cover_file.exists():
            print("\n[WARN] animation.py 或 cover.py 不存在")
            print("   请先根据 prompts/manim-agent.md 生成动画代码")
            return

        # 1. 生成音频 → 获取真实时长（先于渲染）
        audio_durations = asyncio.run(generate_audio(script, self.audio_dir, self.audio_file, self.config))
        generate_subtitles(script, audio_durations, self.subtitle_file)

        # 2. 更新脚本中的设计时长
        print(f"\n[STEP] 更新时长...")
        for i, (sec, dur) in enumerate(zip(script.sections, audio_durations)):
            print(f"   - 第{i+1}段: 设计{sec.duration}秒 → 实际音频{dur:.1f}秒")
            sec.duration = int(dur)
        self.save_script(script)

        # 3. 低质量试渲染 → 测量真实时长 → 修正 wait → 高质量渲染
        print(f"\n[STEP] 精确对齐动画时长...")
        if _measure_and_fix_wait(self.manim_file, audio_durations, self.output_dir):
            print("[OK] wait 值已修正，开始高质量渲染")
        else:
            print("[OK] 时长已匹配，无需修正")

        # 4. 高质量渲染动画
        if not render_manim(self.cover_file, self.manim_file, self.output_dir):
            return

        # 5. 合成最终视频（ffmpeg 裁剪兜底）
        compose_video(self.audio_file, self.final_video, self.output_dir, self.config)

    async def run(self):
        """只创建目录，输出文件路径给 Claude 参考"""
        if self.load_script():
            print(f"\n[WARN] 发现已有脚本: {self.script_file}")
            print("   使用 --regenerate 参数重新生成媒体")
            return

        print(f"\n[INFO] 输出目录: {self.output_dir}")
        print(f"[INFO] 脚本文件: {self.script_file}")
        print(f"[INFO] 动画文件: {self.cover_file}, {self.manim_file}")
        print(f"[INFO] 音频文件: {self.audio_file}")
        print(f"[INFO] 字幕文件: {self.subtitle_file}")
        print(f"[INFO] 最终视频: {self.final_video}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="教育视频生成器 — 双 Agent 协作")
    parser.add_argument("--topic", "-t", required=True, help="视频主题")
    parser.add_argument("--duration", "-d", type=int, default=150, help="目标时长（秒）")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--template", help="模板类型（history_evolution/concept_explanation/comparison）")
    parser.add_argument("--regenerate", action="store_true", help="从已有脚本和动画代码生成媒体")

    args = parser.parse_args()
    gen = VideoGenerator(
        topic=args.topic, target_duration=args.duration,
        output_dir=args.output, template=args.template
    )

    if args.regenerate:
        gen.regenerate()
    else:
        asyncio.run(gen.run())
