import asyncio
import edge_tts
import os
from pydub import AudioSegment
from datetime import timedelta, datetime
import subprocess
import shutil

class EduVideoAudioPipeline:
    def __init__(self, voice="zh-CN-YunxiNeural", rate="+5%", volume="+0%"):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.temp_dir = "audio_temp"
        os.makedirs(self.temp_dir, exist_ok=True)

    async def generate_tts_segments(self, sentences):
        """为每句生成音频并记录时长"""
        audio_files = []
        durations = []

        for i, text in enumerate(sentences):
            out_path = f"{self.temp_dir}/seg_{i}.mp3"
            communicate = edge_tts.Communicate(
                text, self.voice, rate=self.rate, volume=self.volume
            )
            await communicate.save(out_path)
            audio_files.append(out_path)

            # 精确获取时长
            seg = AudioSegment.from_mp3(out_path)
            durations.append(len(seg))
            print(f"[生成] [{i}] {text[:20]}... ({len(seg)}ms)")

        return audio_files, durations

    def concatenate_audio(self, audio_files, output_path="final_audio.mp3"):
        """拼接所有音频片段"""
        combined = AudioSegment.empty()
        for f in audio_files:
            seg = AudioSegment.from_mp3(f)
            # 添加淡入淡出效果
            seg = seg.fade_in(50).fade_out(50)
            combined += seg
        combined.export(output_path, format="mp3")
        print(f"[音频] 已合并: {output_path}")
        return output_path, len(combined)

    def generate_ass(self, sentences, durations, output_path="subtitles.ass"):
        """生成高级 ASS 字幕，支持关键词高亮"""

        # ASS 文件头（样式定义）
        ass_header = """[Script Info]
Title: Bit Explained Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
Timing: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,10,10,60,1
Style: Highlight,Microsoft YaHei,48,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,10,10,60,1
Style: Keyword,Microsoft YaHei,52,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,110,110,0,0,1,4,1,2,10,10,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        # 关键词定义（会被高亮显示）
        keywords = ["Bit", "开关", "零", "一", "字节", "Byte"]

        events = []
        current_ms = 500  # 开头留 0.5 秒空白

        for i, (text, dur) in enumerate(zip(sentences, durations)):
            start_time = self._ms_to_ass_time(current_ms)
            end_time = self._ms_to_ass_time(current_ms + dur - 100)

            # 处理关键词高亮：将关键词用 {\rKeyword}...{\rDefault} 包裹
            display_text = self._highlight_keywords(text, keywords)

            # 添加淡入淡出效果标签
            display_text = f"{{\\fade(200,200)}}" + display_text

            event = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{display_text}"
            events.append(event)

            current_ms += dur + 200  # 句间留 0.2 秒

        ass_content = ass_header + "\n".join(events)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

        print(f"[字幕] ASS 已生成: {output_path}")
        return output_path

    def _ms_to_ass_time(self, ms):
        """将毫秒转换为 ASS 时间格式 HH:MM:SS.cc"""
        td = timedelta(milliseconds=ms)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        centiseconds = int((ms % 1000) / 10)
        return f"{hours:01d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    def _highlight_keywords(self, text, keywords):
        """高亮关键词"""
        result = text
        for kw in keywords:
            if kw in result:
                # 使用 ASS 样式切换标签
                result = result.replace(kw, f"{{\\rKeyword}}{kw}{{\\rDefault}}")
        return result

    async def run(self, script_sentences, video_path, output_path="final_video.mp4"):
        """端到端执行"""
        print(f"[处理] 开始处理视频: {video_path}")

        audio_files, durations = await self.generate_tts_segments(script_sentences)
        audio_path, total_duration = self.concatenate_audio(audio_files)
        ass_path = self.generate_ass(script_sentences, durations)

        # FFmpeg 合并视频+音频+ASS字幕
        self._merge_with_ffmpeg(video_path, audio_path, ass_path, output_path)
        print(f"[完成] 最终视频输出: {output_path}")

        # 清理临时文件
        self._cleanup(audio_files, audio_path, ass_path)

    def _merge_with_ffmpeg(self, video, audio, ass, output):
        """使用 FFmpeg 合并视频、音频和 ASS 字幕"""

        # 确保字体文件存在
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
        ]

        fonts_dir = os.path.expanduser("~/.fonts")
        if os.path.exists(fonts_dir):
            font_paths.extend([
                f"{fonts_dir}/NotoSansCJK-Regular.ttc",
                f"{fonts_dir}/NotoSansSC-Regular.otf",
            ])

        # 复制字体到临时目录以便 FFmpeg 使用
        temp_font_dir = "audio_temp/fonts"
        os.makedirs(temp_font_dir, exist_ok=True)

        for fp in font_paths:
            if os.path.exists(fp):
                dest = os.path.join(temp_font_dir, os.path.basename(fp))
                if not os.path.exists(dest):
                    shutil.copy2(fp, dest)
                print(f"[字体] 已加载: {os.path.basename(fp)}")
                break

        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-i", audio,
            "-vf", f"ass='{ass.replace('\\', '/').replace(':', '\\:')}'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            output
        ]

        print(f"[执行] FFmpeg 命令...")
        try:
            subprocess.run(cmd, check=True, capture_output=False)
        except subprocess.CalledProcessError as e:
            print(f"[错误] FFmpeg 执行失败")
            print(f"尝试备用方案...")
            self._merge_fallback(video, audio, output)

    def _merge_fallback(self, video, audio, output):
        """备用方案：仅合并音视频，字幕单独保留"""
        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-i", audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            output
        ]
        subprocess.run(cmd, check=True)
        print(f"[完成] 视频+音频已合并（字幕单独保留为 subtitles.ass）")

    def _cleanup(self, audio_files, audio_path, ass_path):
        """清理临时文件"""
        for f in audio_files:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        # 保留 ASS 文件供参考
        # if os.path.exists(ass_path):
        #     os.remove(ass_path)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        print("[清理] 临时文件已清理")


async def main():
    pipeline = EduVideoAudioPipeline(voice="zh-CN-YunxiNeural", rate="+5%")

    # 配音脚本（按视频时间轴设计）
    sentences = [
        "计算机里最小的单位是什么？",
        "其实就是一个开关。关代表零，开代表一。",
        "这就是二进制比特，Bit。",
        "两个比特，能组合出四种状态。",
        "八个比特组成一个字节，就能表示字母A。",
        "记住，万物皆由零和一构成。"
    ]

    # Manim 生成的视频路径
    manim_video = "media/videos/bit_demo/1080p30/BitExplained.mp4"

    if os.path.exists(manim_video):
        await pipeline.run(sentences, manim_video, "bit_with_styled_subs.mp4")
    else:
        print(f"[错误] 视频文件不存在: {manim_video}")
        print("请先运行: .venv/Scripts/manim -pqh bit_demo.py BitExplained")

if __name__ == "__main__":
    asyncio.run(main())
