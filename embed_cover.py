import subprocess
import os

def create_video_with_embedded_cover():
    """创建带内嵌封面的视频 - 封面作为视频前几秒展示"""

    # 方案1: 封面作为独立片段 + 原视频
    # 先创建一个仅包含封面图片的视频片段（3秒）

    # 步骤1: 将封面图片转换为3秒视频片段
    cover_video_cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", "thumbnails/cover_02_switch.jpg",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-t", "3",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "cover_segment.mp4"
    ]

    print("[步骤1] 生成封面视频片段...")
    subprocess.run(cover_video_cmd, capture_output=True)

    # 步骤2: 合并封面片段和原视频（带淡入淡出过渡）
    # 创建 concat 列表文件
    with open("concat_list.txt", "w") as f:
        f.write("file 'cover_segment.mp4'\n")
        f.write("file 'bit_with_styled_subs.mp4'\n")

    merge_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",
        "-c", "copy",
        "bit_final_with_cover.mp4"
    ]

    print("[步骤2] 合并封面和视频...")
    result = subprocess.run(merge_cmd, capture_output=True)

    if result.returncode == 0:
        print("[完成] 带封面的视频已生成!")

        # 清理临时文件
        os.remove("cover_segment.mp4")
        os.remove("concat_list.txt")

        return "bit_final_with_cover.mp4"
    else:
        print("[错误] 合并失败，尝试备用方案...")
        return None


def create_video_with_fade_transition():
    """创建带淡入效果的封面+视频"""

    # 使用 filter_complex 实现封面到视频的平滑过渡
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "3", "-i", "thumbnails/cover_02_switch.jpg",
        "-i", "bit_with_styled_subs.mp4",
        "-f", "lavfi", "-t", "0.5", "-i", "anullsrc=r=24000:cl=mono",
        "-filter_complex",
        # 视频部分：封面(3s) + 原视频，中间加淡出效果
        "[0:v]fade=t=out:st=2.5:d=0.5[v0];" +
        "[1:v]fade=t=in:st=0:d=0.5[v1];" +
        "[v0][v1]concat=n=2:v=1:a=0[vout];" +
        # 音频部分：静音(3s) + 原视频音频
        "[2:a][1:a]concat=n=2:v=0:a=1[aout]",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "128k",
        "bit_final_with_cover.mp4"
    ]

    print("[生成] 创建带淡入过渡的封面视频...")
    subprocess.run(cmd, capture_output=False)

    if os.path.exists("bit_final_with_cover.mp4"):
        print("[完成] 视频已生成!")
        return "bit_final_with_cover.mp4"
    return None


def embed_thumbnail_metadata():
    """将封面嵌入视频文件元数据（作为文件缩略图）"""
    # 这种方式需要 atomicparsley 工具，或者用 ffmpeg 的 disposition

    # 检查是否有 atomicparsley
    check_cmd = ["where", "atomicparsley"]
    result = subprocess.run(check_cmd, capture_output=True)

    if result.returncode != 0:
        print("[提示] 未找到 AtomicParsley，尝试其他方式...")

        # 使用 ffmpeg 的 thumbnail 方式（作为 video stream）
        cmd = [
            "ffmpeg", "-y",
            "-i", "thumbnails/cover_02_switch.jpg",
            "-i", "bit_with_styled_subs.mp4",
            "-map", "1:v:0",    # 主视频
            "-map", "1:a:0",    # 音频
            "-map", "0:v:0",    # 封面图作为附加视频流
            "-disposition:v:0", "default",
            "-disposition:v:1", "attached_pic",  # 设为封面
            "-c:v", "copy",
            "-c:a", "copy",
            "bit_with_metadata_cover.mp4"
        ]

        print("[生成] 嵌入元数据封面...")
        subprocess.run(cmd, capture_output=False)

        if os.path.exists("bit_with_metadata_cover.mp4"):
            print("[完成] 带元数据封面的视频已生成!")
            return "bit_with_metadata_cover.mp4"

    return None


if __name__ == "__main__":
    print("="*50)
    print("视频封面嵌入工具")
    print("="*50)

    # 提供两种方案

    print("\n方案1: 封面作为视频开头（前3秒展示封面，然后过渡）")
    file1 = create_video_with_fade_transition()

    print("\n方案2: 封面嵌入文件元数据（播放器缩略图）")
    file2 = embed_thumbnail_metadata()

    print("\n" + "="*50)
    print("生成结果:")
    if file1:
        print(f"  - {file1} (推荐：封面+视频一体化)")
    if file2:
        print(f"  - {file2} (元数据封面)")
    print("="*50)
