# Pre-Render Safety Checks

Code-level checks that must be executed during animation code review to prevent runtime errors.

## Required Checks

### 1. NumPy Array Shape Errors (Most Common)

**Dangerous pattern**: Mixing Manim constants and Python scalars inside `np.array([...])`

```python
# ❌ Wrong: LEFT * 4.5 is a vector, mixed with float → ValueError
dot.move_to(np.array([LEFT * 4.5 + x, UP * 0.5 + y, 0]))

# ✅ Correct: pure numeric coordinates
dot.move_to([-4.5 + x, 0.5 + y, 0])

# ✅ Recommended: use VGroup + next_to for positioning
box = RoundedRectangle(...)
label = Text("Label")
label.next_to(box, DOWN, buff=0.1)
```

**Fix rules**:
- `np.array()` or `move_to()` coordinate parameters must be pure numbers (`float/int`)
- Prefer `next_to()`, `arrange()` over manual coordinate calculation

### 2. `.next_to()` Chaining Returns None

**Dangerous pattern**: Chaining `.next_to()` inside VGroup construction

```python
# ❌ Wrong: next_to() returns None, VGroup receives None elements
rgb_labels = VGroup(
    Text("8bit").next_to(r_bar, DOWN),
    Text("8bit").next_to(g_bar, DOWN),
)

# ✅ Correct: create first, then position
rgb_labels = VGroup()
for bar in [r_bar, g_bar, b_bar]:
    lbl = Text("8bit")
    lbl.next_to(bar, DOWN)
    rgb_labels.add(lbl)
```

### 3. Manim API Incompatibilities

**Known issues**:
- `axes.get_graph()` does not support `x_range` parameter (Manim 0.20.1) → use `axes.plot()` or place Dots directly
- `MathTex` with Chinese characters fails to compile on Windows LaTeX → use `Text()` instead

```python
# ❌ Wrong: get_graph + x_range not supported
axes.get_graph(lambda x: 0, x_range=[1.5, 1.5])

# ❌ Wrong: MathTex with Chinese
MathTex(r"3\text{minutes}")

# ✅ Correct: use Text
Text("3 minutes = 180 seconds")
```

### 4. Undefined Color Constants

**Dangerous pattern**: Using colors not exported by `from manim import *`

```python
# ❌ Wrong: MAGENTA not in manim exports
MAGENTA

# ✅ Correct: use defined constants or hex
MAROON         # built-in to manim
"#DDA0DD"      # or write hex directly
```

## Quick Self-Check (30 Seconds Before Render)

```bash
# Render the first scene to catch errors fastest
manim -ql animation.py Scene01 2>&1 | grep -i "error\|traceback"
```

If Scene01 passes, subsequent scenes likely pass too (errors tend to appear in complex scenes).
