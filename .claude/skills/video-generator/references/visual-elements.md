# 视觉元素库

Manim 动画中使用的视觉元素清单。**每个元素记录：用途 → 实现方式 → 首次使用的场景。**

## 使用说明

生成动画时遵循此流程：
1. **查库**：脚本需要的视觉元素是否已在元素库中？
2. **复用**：如果已有，直接复用其实现方式，保持风格一致
3. **新增**：如果没有，创建新元素并添加到元素库
   - **选择标准：视觉表现力第一，实现难度第二**。能更好表达概念的方法，就是更好的方法。
   - 可选：简笔画、Unicode 图标、`FunctionGraph` 波形、`VMobject` 自定义路径、`MathTex`、`BarChart`、SVG、形状组合

## 元素清单

### 简笔画元素

用 `VMobject` 绘制，每个 5-15 条线，风格统一为线框描边。

#### 天文类

| 元素 | 实现方式 |
|------|---------|
| 太阳 | `Circle` + 8 条放射 `Line`，见 manim-agent.md 简笔画指南 |
| 月亮 | `Arc(start_angle=-PI/3, angle=4*PI/3)` + 小圆弧 |
| 星星 | `Star(n=5, outer_radius=0.3)` |

#### 人物/人体类

| 元素 | 实现方式 |
|------|---------|
| 简笔画小人 | `Circle` 头 + `Line` 身体 + `Line` 四肢 |
| 眼睛 | `Ellipse` 外框 + `Circle` 瞳孔 |
| 手 | `VMobject` 5 条线勾勒轮廓 |
| 大脑 | 左右两瓣 `VMobject` 曲线勾勒 + 中间折线 |
| 耳朵 | 外耳廓 `Arc` + 内耳 `CubicBezier` |

#### 工具类

| 元素 | 实现方式 |
|------|---------|
| 放大镜 | `Circle` 框 + `Line` 手柄 |
| 书 | `VMobject` 轮廓 + 书脊 `Line` |
| 笔 | `Rectangle` 细长 + 顶部 `Triangle` 笔尖 |
| 灯泡 | `Circle` + 底部 `Rectangle` 螺口 |
| 钥匙 | `Circle` 头部 + `Line` 杆 + `Line` 齿 |

#### 自然/建筑类

| 元素 | 实现方式 |
|------|---------|
| 房子 | `Polygon` 方形墙体 + `Polygon` 三角形屋顶 |
| 山 | `Polygon` 大三角 + `Polygon` 小三角背景 |
| 树 | `Line` 树干 + `Circle` 树冠 |
| 云 | `VMobject` + `add_cubic_bezier_curve` 3 段曲线 |
| 花 | `Circle` 花心 + 5 个 `Ellipse` 花瓣 |

### 已实现元素

| 元素 | 用途 | Manim 实现 | 首次场景 |
|------|------|-----------|---------|
| 音符 ♪ | 音乐/声音 | `Text("♪", font_size=60, color=CONCEPT_COLOR)` | 比特变声音/结尾 |
| 扬声器 🔊 | 播放设备 | `Text("🔊 扬声器", font_size=20)` | 比特变声音 |
| 齿轮 ⚙ | 处理/压缩 | `Text("⚙", font_size=40)` + `Rotate(gear, PI*2)` | 压缩重要性/手机存储 |
| 声波波形 | 模拟信号 | `FunctionGraph(lambda x: 0.5*np.sin(3*x), x_range=(-5,5), color=CONCEPT_COLOR)` | 比特变声音 |
| ADC 芯片 | 模数转换 | `RoundedRectangle` + `Text("ADC", weight=BOLD)` | 比特变声音/模拟到数字 |
| 像素网格 | 图像像素 | `VGroup` + 嵌套循环 `Square` + `set_fill` | 比特变图像 |
| RGB 色条 | 颜色值分解 | `Rectangle` 宽度映射数值，`set_fill(color=RED/GREEN/BLUE)` | 比特变图像 |
| 柱状对比 | WAV vs MP3 | 两个 `RoundedRectangle` + `arrange(RIGHT, buff=1.0)` | 压缩重要性 |
| 流程图箭头 | 信号流向 | `Arrow` 或 `CurvedArrow` | 完整旅程/比特到电信号 |
| 16位/8位对比 | 精度差异 | 两个 `RoundedRectangle` + 尺寸对比 | 采样率位深度 |
| 手机播放器 | 移动设备界面 | `RoundedRectangle` + `Circle` 播放按钮 + `Polygon` 三角 | 手机音乐开场 |
| 空气分子疏密 | 声波物理 | `VGroup` + `Dot` 不同间距排列 | 声音的本质 |
| 采样虚线 | ADC采样点 | `DashedLine` 从波形到采样高度 | 模拟到数字 |
| 阶梯电压波形 | DAC输出 | `Rectangle` 宽度固定、高度递增排列 | 比特到电信号 |
| 三角形放大器 | 信号放大 | `Triangle(color=TECH_COLOR, fill_opacity=0.3)` | 比特到电信号 |
| 圆弧无线电波 | 无线信号 | `Arc(radius=r, start_angle=-PI/4, angle=PI/2)` 半径递增 | 蓝牙旅程 |
| 链路图标串联 | 完整流程 | `VGroup` + Unicode 图标 `arrange(RIGHT)` | 结尾 |
| 闪存芯片 | 存储单元 | `RoundedRectangle` + 电荷状态对比(`有电荷=1`/`无电荷=0`) | 手机存储 |
| 人耳流程图 | 听觉链路 | `VGroup` + `arrange(DOWN)` + `Arrow` 连接 | 声音的本质 |

### 待补充元素

| 元素 | 用途 | 建议实现 |
|------|------|---------|
| CPU/芯片 | 处理器 | `Rectangle` + 四周 `Line` 引脚 |
| 显示器 | 电脑屏幕 | `Rectangle(width=2.4, height=1.5)` + `Line` 底座 |
| 数据库 | 存储 | `Cylinder(radius=0.6, height=0.8)` 或 3 层 `Ellipse` 堆叠 |
| 网络节点 | 互联网 | 多个 `Circle` + `DashedLine` 连接 |
| 时钟 | 时间 | `Circle` + 2 条 `Line` 指针 |
| 锁 | 安全 | `Rectangle` + `Arc` 简笔画 |
| 文件夹 | 文件存储 | `VMobject` 简笔画 |
| 云朵 ☁ | 云计算 | 见「简笔画元素 → 自然/建筑类 → 云」 |
| 对勾 ✓ | 正确标记 | `Text("✓", font_size=32, color=GREEN)` |
| 叉号 ✗ | 错误标记 | `Cross` 或 `Text("✗", font_size=32, color=RED)` |
| 放大镜 | 搜索/发现 | 见「简笔画元素 → 工具类 → 放大镜」 |
| 眼睛 👁 | 视觉/观看 | 见「简笔画元素 → 人物/人体类 → 眼睛」 |
| 树 | 层次结构 | 见「简笔画元素 → 自然/建筑类 → 树」 |
| 漏斗 | 过滤/压缩 | `Polygon` 倒三角形 + `Arrow` 穿过 |
| 百分比 % | 压缩率 | `Text("90%", font_size=36, color=TECH_COLOR)` |
| 括号标注 | 范围/区间 | `Brace` + `BraceLabel` |
| 坐标轴+曲线 | 函数关系 | `Axes` + `plot(lambda x: ...)` |
| 耳机剖面 | 扬声器单元 | `Circle` + 内部 `Arc` 线圈 + `Rectangle` 振膜 |

### 强调效果元素

| 效果 | Manim 实现 | 使用场景 |
|------|-----------|---------|
| 圈出重点 | `Circumscribe(text, color=TECH_COLOR)` | 关键词高亮 |
| 闪烁提醒 | `Flash(dot, color=RED)` | 错误/异常提示 |
| 指示强调 | `Indicate(text, color=TECH_COLOR)` | 重要概念 |
| 晃动提醒 | `Wiggle(wrong_element)` | 错误对比 |
| 下划线 | `Create(Underline(text))` | 定义/术语 |
| 放大聚焦 | `box.animate.scale(2.0)` | 像素放大、细节展示 |

### 数学/公式元素

| 类型 | 示例 | 实现 |
|------|------|------|
| 幂运算 | 2¹⁰ = 1024 | `MathTex(r"2^{10} = 1024", font_size=36)` |
| 比例转换 | 30MB → 3MB | `MathTex(r"30\text{MB} \to 3\text{MB}", font_size=32)` |
| 奈奎斯特 | fs ≥ 2f_max | `MathTex(r"f_s \geq 2f_{\max}", font_size=28)` |
| 单位换算 | 1MB = 1024×1024 | `MathTex(r"\text{1MB} = 1024 \times 1024", font_size=24)` |
| 百分比 | 10:1 压缩 | `MathTex(r"30\text{MB} : 3\text{MB} = 10:1", font_size=28)` |
