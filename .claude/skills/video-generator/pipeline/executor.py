"""
Pipeline - 执行层：配音、字幕、渲染、合成
"""

import asyncio
import re
import subprocess
from pathlib import Path
from typing import List, Optional

from agents.content_agent import VideoScript


async def generate_audio(script: VideoScript, audio_dir: Path, audio_file: Path, config: dict) -> List[float]:
    """生成配音，返回每段实际时长"""
    print("\n[STEP3] 生成配音...")
    audio_dir.mkdir(exist_ok=True)

    voice = config["audio"]["voice"]
    rate = config["audio"]["rate"]
    temp_files = []
    durations = []

    for i, section in enumerate(script.sections):
        temp = audio_dir / f"voice_{i:02d}.mp3"
        proc = await asyncio.create_subprocess_exec(
            "edge-tts", "-v", voice, "-t", section.content,
            "--write-media", str(temp), f"--rate={rate}"
        )
        await proc.wait()
        temp_files.append(temp)

        probe = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(temp),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await probe.communicate()
        dur = float(stdout.decode().strip())
        durations.append(dur)
        print(f"  - 第{i+1}段完成 ({dur:.1f}秒)")

    list_file = audio_dir / "list.txt"
    with open(list_file, 'w') as f:
        for t in temp_files:
            f.write(f"file '{t.name}'\n")

    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_file), "-c", "copy", str(audio_file)], check=True)

    print(f"[OK] 配音已生成: {audio_file} (总时长: {sum(durations):.1f}秒)")
    return durations


def generate_subtitles(script: VideoScript, audio_durations: List[float], subtitle_file: Path):
    """生成字幕，使用实际语音时长"""
    print("\n[STEP4] 生成字幕...")
    srt = ""
    current = 0.0

    def fmt(t):
        h, m, s = int(t // 3600), int((t % 3600) // 60), int(t % 60)
        return f"{h:02d}:{m:02d}:{s:02d},{int((t % 1) * 1000):03d}"

    for section, dur in zip(script.sections, audio_durations):
        sentences = [s.strip() for s in section.content.split("。") if s.strip()]
        seg = dur / max(1, len(sentences))
        for j, sentence in enumerate(sentences):
            srt += f"{len(srt.split())}_{j}\n{fmt(current)} --> {fmt(current + seg)}\n{sentence}\n\n"
            current += seg

    subtitle_file.write_text(srt, encoding='utf-8')
    print(f"[OK] 字幕已生成: {subtitle_file}")


def _get_scene_video_duration(video_path: Path) -> float:
    """获取单个视频文件的时长"""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True
    )
    if probe.returncode != 0:
        return 0
    return float(probe.stdout.strip())


def _render_scene(manim_file: Path, output_dir: Path, scene_name: str, quality: str = "ql"):
    """渲染单个场景"""
    media_base = output_dir / "media" / "videos" / "animation" / f"1080p60"
    media_base.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["manim", f"-q{quality}", "--format=mp4", str(manim_file), scene_name],
        cwd=output_dir, check=True, capture_output=(quality == "l")
    )


def _measure_and_fix_wait(manim_file: Path, audio_durations: List[float], output_dir: Path):
    """低质量试渲染 → 测量真实时长 → 修正 wait 值"""
    content = manim_file.read_text(encoding='utf-8')
    scene_pattern = re.compile(
        r'class (Scene\d+)\(Scene\):.*?def construct\(self\):'
        r'(.*?)(?=(?:class Scene\d+\(Scene\)|$))',
        re.DOTALL
    )
    scenes = scene_pattern.findall(content)
    if not scenes:
        return False

    # 1. 低质量试渲染
    for scene_name, _ in scenes:
        _render_scene(manim_file, output_dir, scene_name, quality="l")

    # 2. 测量 + 修正
    need_rerender = False
    for scene_name, scene_body in scenes:
        m = re.search(r'\d+', scene_name)
        if not m:
            continue
        idx = int(m.group()) - 1
        if idx >= len(audio_durations):
            continue

        # 找到低质量渲染的视频
        video = output_dir / "media" / "videos" / "animation" / "480p15" / f"{scene_name}.mp4"
        actual_dur = _get_scene_video_duration(video)
        if actual_dur <= 0:
            continue

        target_dur = audio_durations[idx]
        diff = actual_dur - target_dur

        # 查找 self.wait(X) 后接 FadeOut
        wait_pattern = re.compile(
            r'(self\.wait\()\s*([\d.]+)\s*\)(\s*self\.play\(FadeOut\(\*self\.mobjects\))'
        )
        wait_match = wait_pattern.search(scene_body)
        if not wait_match:
            continue

        current_wait = float(wait_match.group(2))
        # 新 wait = 当前 wait - (实际时长 - 目标时长)
        new_wait = round(current_wait - diff, 1)
        new_wait = max(0.5, new_wait)

        if abs(new_wait - current_wait) > 0.05:
            old_text = wait_match.group(0)
            new_text = f'self.wait({new_wait}){wait_match.group(3)}'
            scene_start = content.index(scene_body)
            content = (content[:scene_start] +
                      content[scene_start:].replace(old_text, new_text, 1))
            print(f"  {scene_name}: 实测{actual_dur:.1f}s → 目标{target_dur:.1f}s, "
                  f"wait({current_wait:.1f}) → wait({new_wait:.1f})")
            need_rerender = True

    if need_rerender:
        manim_file.write_text(content, encoding='utf-8')
        # 清除低质量缓存，触发高质量重渲染
        import shutil
        cache480 = output_dir / "media" / "videos" / "animation" / "480p15"
        if cache480.exists():
            shutil.rmtree(cache480)
        return True
    return False


def render_manim(cover_file: Path, manim_file: Path, output_dir: Path):
    """渲染 Manim 动画"""
    print("\n[STEP5] 渲染动画...")

    if not cover_file.exists():
        print("[WARN] cover.py 不存在")
        return False
    if not manim_file.exists():
        print("[WARN] animation.py 不存在")
        return False

    print("  渲染封面（MP4）...")
    subprocess.run(["manim", "-qm", "--format=mp4", str(cover_file), "CoverScene"],
                   cwd=output_dir, check=True)

    scenes = re.findall(r'class (Scene\d+)\(Scene\)', manim_file.read_text(encoding='utf-8'))
    print(f"  渲染主动画（{len(scenes)}个场景）...")
    # 并行渲染：使用 Popen 同时启动多个 manim 进程
    processes = []
    for name in scenes:
        print(f"    {name}...")
        p = subprocess.Popen(["manim", "-qh", "--format=mp4", str(manim_file), name],
                             cwd=output_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append((name, p))

    # 等待所有进程完成
    for name, p in processes:
        p.wait()
        if p.returncode != 0:
            print(f"    [WARN] {name} 渲染失败，请检查")

    print("[OK] 动画渲染完成")
    return True


def align_scene_durations(output_dir: Path, audio_durations: List[float]) -> List[Path]:
    """将每个场景视频变速以精确匹配音频时长。

    Manim 每个 self.play() 有不可预测的开销（0.05-0.4s），
    纯靠 run_time 求和无法精确对齐。用 ffmpeg setpts/atempo 变速解决。
    """
    media_dir = output_dir / "media" / "videos" / "animation" / "1080p60"
    aligned_dir = output_dir / "aligned"
    aligned_dir.mkdir(exist_ok=True)

    # 第一阶段：先 probe 所有场景时长
    tasks = []
    for i, dur in enumerate(audio_durations):
        scene_name = f"Scene{i+1:02d}"
        src = media_dir / f"{scene_name}.mp4"
        if not src.exists():
            print(f"  [WARN] {scene_name}.mp4 未找到，跳过")
            continue

        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(src)],
            capture_output=True, text=True, check=True
        )
        src_dur = float(probe.stdout.strip())
        dst = aligned_dir / f"{scene_name}.mp4"

        tasks.append((scene_name, src, dst, src_dur, dur))

    # 第二阶段：并行执行 FFmpeg 变速
    processes = []
    for scene_name, src, dst, src_dur, dur in tasks:
        if abs(src_dur - dur) < 0.1:
            # 差异 < 0.1s，直接复制
            p = subprocess.Popen(["ffmpeg", "-y", "-i", str(src), "-c", "copy", str(dst)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processes.append((scene_name, p, src_dur, dur, True))
        else:
            # 用 setpts 变速视频
            speed = src_dur / dur
            p = subprocess.Popen([
                "ffmpeg", "-y", "-i", str(src),
                "-filter:v", f"setpts={speed}*PTS",
                "-c:v", "libx264", "-preset", "fast", "-an",
                "-t", str(dur), str(dst)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processes.append((scene_name, p, src_dur, dur, False))

    # 第三阶段：等待并输出结果
    result = []
    for scene_name, p, src_dur, dur, _ in processes:
        p.wait()
        print(f"  {scene_name}: {src_dur:.1f}s → {dur:.1f}s")
        result.append(aligned_dir / f"{scene_name}.mp4")

    print(f"[OK] {len(result)} 个场景已对齐")
    return result


def compose_video(audio_file: Path, final_video: Path, output_dir: Path, config: dict,
                  scene_videos: Optional[List[Path]] = None):
    """合成最终视频"""
    print("\n[STEP6] 合成视频...")

    aligned_dir = output_dir / "aligned"
    media_dir = output_dir / "media" / "videos" / "animation" / "1080p60"
    cover_media = output_dir / "media" / "videos" / "cover" / "1080p60"

    all_videos = []

    # 封面视频（如有）
    if cover_media.exists():
        cover_mp4 = cover_media / "CoverScene.mp4"
        if cover_mp4.exists():
            all_videos.append(cover_mp4)

    # 场景视频：优先使用传入的对齐视频，其次扫描 aligned 目录，最后扫描 1080p60 渲染目录
    if scene_videos:
        all_videos.extend(scene_videos)
    elif aligned_dir.exists():
        aligned_videos = sorted(aligned_dir.glob("Scene*.mp4"))
        if aligned_videos:
            all_videos.extend(aligned_videos)
        else:
            all_videos.extend(sorted(media_dir.glob("Scene*.mp4")))
    else:
        all_videos.extend(sorted(media_dir.glob("Scene*.mp4")))

    if not all_videos:
        print("[WARN] 无场景视频")
        return

    print(f"  合并 {len(all_videos)} 个视频片段:")
    for v in all_videos:
        print(f"    - {v.name}")

    _concat_scenes(all_videos, output_dir)
    _add_audio_subtitles(audio_file, final_video, output_dir, config)

    # 清理临时文件
    for name in ["scenes_combined.mp4", "scenes_list.txt"]:
        f = output_dir / name
        f.unlink(missing_ok=True)

    print(f"[OK] 最终视频: {final_video}")


def _concat_scenes(scene_videos: list, output_dir: Path):
    """合并所有场景（含封面）"""
    list_file = output_dir / "scenes_list.txt"
    with open(list_file, 'w') as f:
        for v in scene_videos:
            f.write(f"file '{v}'\n")

    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_file), "-c", "copy", str(output_dir / "scenes_combined.mp4")], check=True)


def _add_audio_subtitles(audio_file: Path, final_video: Path, output_dir: Path, config: dict):
    """添加配音和字幕（字幕使用相对路径 subtitles.srt，避免 Windows 路径问题）"""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)],
        capture_output=True, text=True, check=True
    )
    audio_dur = float(probe.stdout.strip())

    style = (f"FontName={config['subtitles']['font']},"
             f"FontSize={config['subtitles']['size']},"
             f"PrimaryColour={config['subtitles']['color']},"
             f"Alignment=2,MarginV=20")

    subprocess.run(["ffmpeg", "-y",
                    "-i", "scenes_combined.mp4",
                    "-i", str(audio_file),
                    "-filter_complex",
                    f"[0:v]subtitles=subtitles.srt:force_style='{style}'[v];[1:a]anull[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "fast", "-c:a", "aac",
                    "-t", str(audio_dur), "-r", "60",
                    str(final_video)], cwd=output_dir, check=True)
