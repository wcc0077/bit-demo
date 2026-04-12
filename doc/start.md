# 🌟 《计算机中的 Bit》Manim 完整代码 & 自动化指南

这是一套**开箱即用**的 Manim 代码，专为小白设计，用“开关隐喻”讲解 Bit 概念。代码已优化布局、时间轴和中文字体兼容性，直接复制即可渲染。

---

## 📜 完整 Manim 代码（`bit_demo.py`）
```python
from manim import *

# 全局配置：1080P、白底、中文字体
config.background_color = WHITE
config.frame_width = 16
config.frame_height = 9
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30

class BitExplained(Scene):
    def construct(self):
        # 设置中文字体（按需替换为你的系统字体）
        config.tex_template.preamble = r"""\usepackage{ctex}"""
        
        # 🟦 0-5s：钩子（痛点提问）
        title = Text("计算机里最小的单位是什么？", font_size=38, color=DARK_BLUE).to_edge(UP)
        self.play(Write(title, run_time=1.5))
        self.wait(0.5)
        
        # 🟦 5-20s：核心隐喻（开关 = 0/1）
        # 状态 0
        box0 = Square(side_length=1.2, fill_color="#E5E7EB", fill_opacity=1, stroke_width=2, stroke_color="#9CA3AF")
        icon0 = Text("关", font_size=30, color="#6B7280")
        state0 = VGroup(box0, icon0).move_to(box0.get_center()).shift(LEFT * 2.5)
        
        # 状态 1
        box1 = Square(side_length=1.2, fill_color="#3B82F6", fill_opacity=1, stroke_width=2, stroke_color="#2563EB")
        icon1 = Text("开", font_size=30, color=WHITE)
        state1 = VGroup(box1, icon1).move_to(box1.get_center()).shift(RIGHT * 2.5)
        
        # 标签
        lbl0 = Text("0", font_size=42, color="#4B5563").next_to(state0, DOWN, buff=0.3)
        lbl1 = Text("1", font_size=42, color="#1E40AF").next_to(state1, DOWN, buff=0.3)
        
        self.play(Create(state0), Create(state1))
        self.play(FadeIn(lbl0), FadeIn(lbl1))
        self.wait(1)
        
        # 定义 Bit
        def_text = Text("Binary Digit → Bit", font_size=32, color="#059669").to_edge(DOWN, buff=1.5)
        self.play(Write(def_text))
        self.wait(2)
        
        # 🟦 20-35s：组合威力（指数增长）
        self.play(FadeOut(def_text), FadeOut(lbl0), FadeOut(lbl1))
        self.wait(0.3)
        
        # 2 bits 组合动画
        bit1 = state0.copy().scale(0.7)
        bit2 = state1.copy().scale(0.7)
        bits_2 = VGroup(bit1, bit2).arrange(RIGHT, buff=0.8).move_to(ORIGIN)
        
        combo_text = Text("2个bit → 4种组合 (00, 01, 10, 11)", font_size=26, color="#059669").next_to(bits_2, UP, buff=0.8)
        
        self.play(ReplacementTransform(state0, bit1), ReplacementTransform(state1, bit2))
        self.play(Write(combo_text))
        self.wait(2)
        
        # 🟦 35-50s：现实映射（1字节 = 8bit = 1个字符）
        self.play(FadeOut(bits_2), FadeOut(combo_text))
        self.wait(0.5)
        
        # 生成 8 个 bit
        bits_8 = VGroup()
        pattern = [0, 1, 0, 0, 0, 0, 0, 1] # ASCII 'A' 的简化示意
        for i, val in enumerate(pattern):
            col = "#3B82F6" if val else "#D1D5DB"
            bit_box = Square(side_length=0.45, fill_color=col, fill_opacity=1, stroke_width=1.5, stroke_color="#6B7280")
            bits_8.add(bit_box)
        bits_8.arrange(RIGHT, buff=0.15).scale(0.8).move_to(ORIGIN)
        
        byte_lbl = Text("8 bits = 1 Byte", font_size=30, color="#111827").next_to(bits_8, UP, buff=0.6)
        char_lbl = Text("可表示字母 'A'", font_size=34, color="#059669").next_to(bits_8, DOWN, buff=0.6)
        
        self.play(Create(bits_8), FadeIn(byte_lbl), FadeIn(char_lbl))
        self.wait(2.5)
        
        # 🟦 50-60s：总结金句
        self.play(FadeOut(bits_8), FadeOut(byte_lbl), FadeOut(char_lbl), FadeOut(title))
        summary = Text("万物皆由 0 和 1 构成", font_size=40, color="#1E40AF").move_to(ORIGIN)
        self.play(Write(summary, run_time=2))
        self.wait(2)
        self.play(FadeOut(summary))
```

---

## 🛠️ 如何运行（3步搞定）

### 1️⃣ 安装环境（仅需 2 分钟）
```bash
# 安装 Manim（自动带 ffmpeg/cairo/pango）
pip install manim

# Windows 用户若缺中文字体支持，额外安装：
# pip install manim-fonts
```

### 2️⃣ 配置中文字体（关键！）
Manim 默认不支持中文。修改你的 `manim.cfg`（位于 `~/.config/manim/` 或 `C:\Users\用户名\.config\manim\`）：
```ini
[CLI]
font = Noto Sans CJK SC  # 或 Microsoft YaHei / PingFang SC
```
> 💡 找不到字体？在代码顶部加：`config.tex_template = TexTemplate(library_additions=r"\usepackage{ctex}")`

### 3️⃣ 渲染视频
```bash
# 预览质量（快速，720P）
manim -pql bit_demo.py BitExplained

# 发布质量（1080P，高清）
manim -pqh bit_demo.py BitExplained
```
输出文件：`media/videos/bit_demo/1080p30/BitExplained.mp4`

---

## 📐 时间轴 & 教学逻辑映射

| 时间段 | 画面内容 | 教学目的 | 动画手法 |
|--------|----------|----------|----------|
| `0-5s` | 大标题提问 | 抓住注意力，制造认知缺口 | `Write` 逐字出现 |
| `5-20s` | 左右对比：灰方块(0) vs 蓝方块(1) | 用“开关”具象化抽象概念 | `Create` + 位置对称 |
| `20-35s` | 2个方块组合，显示4种状态 | 展示二进制组合威力 | `ReplacementTransform` 平滑过渡 |
| `35-50s` | 8个方块排列，高亮特定模式 → 字母'A' | 建立“Bit→Byte→字符”认知桥梁 | 逐格 `Create` + 颜色映射 |
| `50-60s` | 全屏金句 | 强化记忆，引导点赞/评论 | 居中 `Write` + 淡出 |

---

## 🤖 如何接入你的全自动化流水线？

### 🔁 LLM → Manim 自动化提示词模板
```text
你是一位精通 manim v0.18+ 的教育动画工程师。请将以下JSON转换为完整可运行的Python代码。
要求：
1. 继承 Scene，使用基础动画(Create/FadeIn/ReplacementTransform/Write)
2. 严格遵循时间轴，总时长控制在 55~65 秒
3. 元素布局使用 arrange/move_to，避免重叠或越界
4. 中文使用 Text()，英文/符号可用 MathTex()
5. 仅输出 Python 代码，无额外解释

JSON: {"concept": "bit", "steps": ["提问", "开关隐喻0/1", "组合威力", "现实映射", "总结"]}
```

### 📦 自动校验 & 渲染脚本（Python）
```python
import subprocess, os

def render_manim(script_path, scene_name, quality="h"):
    cmd = ["manim", f"-pq{quality}", script_path, scene_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ 渲染成功: media/videos/{os.path.basename(script_path).replace('.py','')}/{quality}1080p30/{scene_name}.mp4")
    else:
        print(f"❌ 渲染失败:\n{result.stderr}")

# 使用：render_manim("bit_demo.py", "BitExplained", "h")
```

---

## 🚀 下一步优化建议

1. **透明背景导出**：加参数 `--transparent`，方便后期叠加 BGM/字幕
2. **语速控制**：Manim 只负责画面，配音用剪映/Azure TTS，FFmpeg 对齐时间轴
3. **批量生成**：将 JSON 模板化，用 `for` 循环替换 `concept` 字段，一键渲染系列视频（TCP、CPU、内存等）

需要我直接提供：
- 📜 `FFmpeg + TTS 自动对齐脚本`（Manim 视频 + 配音 + 字幕一键合成）
- 📦 `Docker 镜像`（预装 Manim + 中文字体 + 渲染队列，开箱即用）
- 🎨 `下一期主题代码`（如：`CPU如何工作` / `IP地址是什么`）

告诉我你的偏好，我直接输出对应工程包。祝第一条视频顺利跑通！ 🎬