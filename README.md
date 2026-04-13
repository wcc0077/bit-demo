# bit-demo: 教育视频自动生成系统

基于多Agent协作的自动化教育视频生成工具

> 用 Manim 制作的计算机基础知识教育短视频，讲解 Bit、Byte、二进制等核心概念。

## 🎬 演示视频

项目包含完整示例：**AI中的Token概念** 教育动画

- 📁 位置: `theme-token/TokenExplained_Final.mp4`
- ⏱️ 时长: 2分34秒
- 📺 内容: 8个场景完整讲解Token概念
- 🎨 质量: 1080p60 + 中文配音 + 硬编码字幕

## 🚀 快速开始

### 安装

```bash
cd .claude/skills
pip install -r requirements.txt

# Windows
install.bat
```

### 生成视频

```bash
python .claude/skills/video_generator.py --topic "AI中的Token概念"
```

### Python API

```python
from .claude.skills.video_generator import VideoGenerator
import asyncio

generator = VideoGenerator(
    topic="你的主题",
    target_duration=150
)

asyncio.run(generator.run())
```

## 🏗️ 架构设计

### 多Agent协作

```
┌─────────────────────────────────────────┐
│         Video Generator (主协调器)        │
└────────────┬─────────────────┬──────────┘
             │                 │
    ┌────────▼──────┐ ┌────────▼──────┐
    │ Content Agent │ │  Manim Agent  │
    │   内容创作     │ │   动画生成     │
    └────────┬──────┘ └────────┬──────┘
             │                 │
             └────────┬────────┘
                      │
              ┌───────▼───────┐
              │   输出文件     │
              │ • script.md   │
              │ • animation.py│
              │ • final.mp4   │
              └───────────────┘
```

### Content Agent

**职责**: 生成高质量教育脚本

- 分析主题 → 提取知识点
- 设计结构 → 8段标准教学流程
- 编写脚本 → 逐字稿+视觉描述
- 质量检查 → 5项检查清单

### Manim Agent

**职责**: 生成Manim动画代码

- 解析视觉 → 提取动画元素
- 设计布局 → 避免文字重叠
- 编写代码 → 完整Python脚本
- 优化节奏 → 70%展示时间

## 📁 项目结构

```
bit-demo/
├── theme-token/                    # Token视频示例
│   ├── TokenExplained_Final.mp4   # 最终成品
│   ├── token_explained_final.py   # Manim源码
│   ├── subtitles.srt              # 字幕
│   └── ...
│
├── .claude/skills/                 # Video Generator Skill
│   ├── video_generator.py         # 主程序
│   ├── config.yaml                # 配置
│   ├── agents/                    # Agent实现
│   │   ├── content_agent.py      # 内容Agent
│   │   └── manim_agent.py        # 动画Agent
│   ├── prompts/                   # 提示词配置
│   │   ├── content-agent.yaml    # 内容提示词
│   │   └── manim-agent.yaml      # 动画提示词
│   └── examples/                  # 示例
│       ├── token_script.md       # Token脚本
│       └── token_animation.py    # Token动画
│
├── CLAUDE.md                      # 详细文档
└── README.md                      # 本文件
```

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 主题驱动 | 输入主题，自动生成分段脚本 |
| 📝 结构化脚本 | 8段标准教学结构（钩子→概念→应用→总结）|
| 🎨 专业动画 | 基于Manim的精美数学动画 |
| 🔊 AI配音 | 微软Edge-TTS中文女声 |
| 📄 字幕支持 | 自动硬编码SRT字幕 |
| 🎬 高清输出 | 1080p60 H.264编码 |

## 🎓 Token视频示例

### 内容结构

| # | 场景 | 时长 | 视觉呈现 |
|---|------|------|----------|
| 1 | 开场钩子 | 10s | 问题+神秘代码 |
| 2 | 什么是Token | 15s | 乐高积木动画 |
| 3 | 为什么需要 | 20s | 左右对比 |
| 4 | 处理流程 | 25s | 三步流程图 |
| 5 | Token类型 | 25s | 三种切分对比 |
| 6 | 实际影响 | 25s | 要点列表 |
| 7 | 中英文差异 | 20s | 数据对比 |
| 8 | 总结 | 15s | 五大要点 |

### 技术规格

- **分辨率**: 1920×1080 @ 60fps
- **编码**: H.264 (libx264) + AAC
- **配音**: 中文女声 (Xiaoxiao)
- **字幕**: 宋体 15号 黄色 底部
- **背景**: 深蓝黑 #1a1a2e

## 🎨 Bit 视频（原始项目）

这是一个 20 秒的教育短视频，用直观的动画讲解计算机最基础的单位——Bit（比特）。

### 内容大纲
1. **提问引入** (0-3s) - "计算机里最小的单位是什么？"
2. **开关隐喻** (3-8s) - 用开关形象化 0 和 1
3. **Bit 定义** (8-11s) - Binary Digit → Bit
4. **组合威力** (11-14s) - 2 bits 组合出 4 种状态
5. **实际应用** (14-18s) - 8 bits = 1 Byte，可表示字母 A
6. **金句总结** (18-21s) - "万物皆由 0 和 1 构成"

## 🔧 配置

编辑 `.claude/skills/config.yaml`:

```yaml
output:
  quality: "high"
  resolution: [1920, 1080]
  fps: 60

audio:
  voice: "zh-CN-XiaoxiaoNeural"
  rate: "-5%"

subtitles:
  font: "SimSun"
  size: 15
  position: "bottom"
  margin: 20
```

## 📚 文档

- [CLAUDE.md](CLAUDE.md) - 完整项目文档
- [.claude/skills/README.md](.claude/skills/README.md) - Skill使用指南
- [.claude/skills/examples/](.claude/skills/examples/) - 示例脚本和代码

## 🛠️ 依赖

- Python 3.8+
- Manim ≥0.20
- FFmpeg
- edge-tts
- PyYAML

## 📄 许可证

MIT License
