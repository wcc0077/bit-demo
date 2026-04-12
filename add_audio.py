import asyncio
import edge_tts
import os
from pydub import AudioSegment
import srt
from datetime import timedelta
import subprocess

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
            # 添加淡入淡出效果，减少拼接噪音
            seg = seg.fade_in(50).fade_out(50)
            combined += seg
        combined.export(output_path, format="mp3")
        print(f"[音频] 已合并: {output_path}")
        return output_path, len(combined)

    def generate_srt(self, sentences, durations, output_path="subtitles.srt"):
        """根据句子和时长生成精准SRT字幕"""
        subtitles = []
        current_ms = 0

        for i, (text, dur) in enumerate(zip(sentences, durations)):
            start = timedelta(milliseconds=current_ms)
            end = timedelta(milliseconds=current_ms + dur)
            subtitles.append(srt.Subtitle(index=i+1, start=start, end=end, content=text))
            current_ms += dur + 200  # 句间留0.2秒呼吸间隔

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt.compose(subtitles))
        print(f"[字幕] 已生成: {output_path}")
        return output_path

    async def run(self, script_sentences, video_path, output_path="final_video.mp4"):
        """端到端执行"""
        print(f"[处理] 开始处理视频: {video_path}")

        audio_files, durations = await self.generate_tts_segments(script_sentences)
        audio_path, total_duration = self.concatenate_audio(audio_files)
        srt_path = self.generate_srt(script_sentences, durations)

        # FFmpeg 合并视频+音频+烧录字幕
        self._merge_with_ffmpeg(video_path, audio_path, srt_path, output_path)
        print(f"[完成] 最终视频输出: {output_path}")

        # 清理临时文件
        self._cleanup(audio_files, audio_path, srt_path)

    def _merge_with_ffmpeg(self, video, audio, srt, output):
        """使用 FFmpeg 合并视频、音频和字幕"""
        # 检测操作系统并设置字体路径
        if os.name == 'nt':  # Windows
            font_path = "C:/Windows/Fonts/msyh.ttc"
            if not os.path.exists(font_path):
                font_path = "C:/Windows/Fonts/simhei.ttf"
        else:  # macOS/Linux
            font_path = "/System/Library/Fonts/PingFang.ttc"

        # 如果找不到字体，使用默认字体
        if not os.path.exists(font_path):
            print(f"警告: 字体文件不存在 {font_path}，使用默认字体")
            font_name = "Arial"
        else:
            font_name = "Microsoft YaHei" if "msyh" in font_path else "SimHei"

        cmd = [
            "ffmpeg", "-y",
            "-i", video,
            "-i", audio,
            "-vf", f"subtitles='{srt}':force_style='FontName={font_name},FontSize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,MarginV=50'",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            output
        ]

        print("执行 FFmpeg 命令...")
        subprocess.run(cmd, check=True)

    def _cleanup(self, audio_files, audio_path, srt_path):
        """清理临时文件"""
        import shutil
        for f in audio_files:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(srt_path):
            os.remove(srt_path)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        print("[清理] 临时文件已清理")


async def main():
    pipeline = EduVideoAudioPipeline(voice="zh-CN-YunxiNeural", rate="+5%")

    # 配音脚本（按视频时间轴设计，共约60秒）
    sentences = [
        "计算机里最小的单位是什么？",                          # 0-5s
        "其实就是一个开关。关代表零，开代表一。",              # 5-20s
        "这就是二进制比特，Bit。",                              # 20-35s
        "两个比特，能组合出四种状态。",                        # 35-50s
        "八个比特组成一个字节，就能表示字母A。",               # 50-60s
        "记住，万物皆由零和一构成。"                           # 结尾
    ]

    # Manim 生成的视频路径
    manim_video = "media/videos/bit_demo/1080p30/BitExplained.mp4"

    if os.path.exists(manim_video):
        await pipeline.run(sentences, manim_video, "bit_with_audio.mp4")
    else:
        print(f"错误: 视频文件不存在: {manim_video}")
        print("请先运行: .venv/Scripts/manim -pqh bit_demo.py BitExplained")

if __name__ == "__main__":
    asyncio.run(main())
