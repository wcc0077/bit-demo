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
