---
name: video-generator
description: Automatically generates educational animated videos (自动生成教育动画视频). Use when the user requests: "generate a video", "create an animated video", "make an explainer video", OR Chinese: "生成视频", "制作动画视频", "创建讲解视频", "为XX主题制作视频". Supports three content types: historical evolution, concept explanation, and comparison analysis. Input: topic + duration. Output: HD educational animation video with voiceover and subtitles. Fully automated pipeline including auto-review and optimization.
---

# Video Generator Skill

Fully automated pipeline:

```
Topic → Content Agent → script.md → Auto-review → Auto-fix
                                               ↓
            Manim Agent → Check visual element library → Generate animation.py + cover.py → Auto-review → Auto-fix
                                                                                                ↓
                                      Python execution → final.mp4
```

## Workflow

### Phase 1: Content Creation

1. Run `python video_generator.py -t "topic" -d duration` to create directory
2. Read `references/content-agent.md`, generate `script.md`
3. **Auto-review**: Read `references/script-review.md`, check script quality item by item
   - Opening hook, analogy usage, data/cases, visual description, language style
   - If issues found, **fix directly**, don't wait for manual confirmation

### Phase 2: Animation Generation

1. **Check visual element library**: Read `references/visual-elements.md`, check if needed visual elements already have implementations
   - Exists → Reuse implementation code directly, keep style consistent
   - Doesn't exist → Create new element (priority: Unicode > shape combination > SVG), append to "Implemented Elements" table in the library

2. **Read `references/manim-agent.md`**, generate `animation.py` and `cover.py`
   - **Mobile adaptation**: All body text font_size >= 20, titles >= 36, labels >= 14
   - **Layout review**: After generation, check element spacing, arrow length, text size for vertical phone screen viewing

3. **Auto-review**: Read `references/animation-review.md`, check animation code item by item
   - Timing match, no overlapping elements, layout rules, color scheme, code structure, visual richness
   - **Mobile readability**: font size, element spacing, arrow clarity
   - If issues found, **fix directly**, don't wait for manual confirmation

### Phase 3: Video Composition

```bash
python video_generator.py -t "topic" --regenerate
```

Auto-execution: voiceover → subtitles → low-quality wait correction → parallel high-quality rendering → FFmpeg composition

**Render optimization**: Scenes render in parallel (Popen starts simultaneously), FFmpeg uses fast preset for acceleration.

## Review Standards

- Script: `references/script-review.md`
- Animation: `references/animation-review.md`
- Render safety: `references/pre-render-checks.md`

Review rules are built into the pipeline — auto-check and auto-fix after generation, no manual intervention needed.
