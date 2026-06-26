from manim import *


# ── Shared colour palette ─────────────────────────────────────────────────────
C_BG      = "#0f1117"
C_STATE   = "#1e2235"
C_BORDER  = "#4a5568"
C_ACCEPT  = "#68d391"
C_ARROW   = "#ffffff"
C_INPUT   = "#e2e8f0"
C_KEYWORD = "#b794f4"
C_IDENT   = "#63b3ed"
C_NUM     = "#f6ad55"
C_OP      = "#f6e05e"

STATE_R = 0.45   # node radius (bigger now that each DFA gets the full screen)

Text.set_default(font="Iosevka Nerd Font")

# ── Shared helpers ────────────────────────────────────────────────────────────
def make_state(label, radius=STATE_R, fill=C_STATE, border=C_BORDER):
    circle = Circle(radius=radius, color=border, stroke_width=3,
                    fill_color=fill, fill_opacity=1)
    text   = Text(label, font_size=20, color=C_INPUT)
    grp    = VGroup(circle, text)
    grp.node_radius = radius
    return grp

def make_accept(label, radius=STATE_R):
    outer = Circle(radius=radius + 0.12, color=C_ACCEPT, stroke_width=3, fill_opacity=0)
    inner = make_state(label, radius=radius)
    grp   = VGroup(outer, inner)
    grp.node_radius = radius + 0.12
    return grp

def get_inner_circle(st):
    """Return the fillable circle regardless of state type."""
    if hasattr(st, 'node_radius') and len(st) == 2 and isinstance(st[1], VGroup):
        return st[1][0]   # accept: VGroup(outer_ring, VGroup(circle, text))
    return st[0]           # normal: VGroup(circle, text)

def edge(s1, s2, label="", color=C_ARROW):
    r1 = getattr(s1, 'node_radius', STATE_R)
    r2 = getattr(s2, 'node_radius', STATE_R)
    d  = s2.get_center() - s1.get_center()
    u  = d / np.linalg.norm(d)
    a  = Arrow(s1.get_center() + u*(r1+0.06),
               s2.get_center() - u*(r2+0.06),
               buff=0, color=color, stroke_width=4,
               tip_length=0.22, max_stroke_width_to_length_ratio=999)
    lbl = Text(label, font_size=18, color=C_ARROW, weight=BOLD).next_to(a, UP, buff=0.10)
    return VGroup(a, lbl)

def start_arrow(state, color=C_ARROW):
    return Arrow(state.get_left() + LEFT*0.45, state.get_left(),
                 buff=0, color=color, stroke_width=4, tip_length=0.18,
                 max_stroke_width_to_length_ratio=999)

def self_loop(state, label="", color=C_ARROW):
    top = state.get_top()
    right = state.get_right()
    loop = CurvedArrow(top + RIGHT*0.12, right + UP*0.12,
                       angle=-TAU/3, color=color, stroke_width=4, tip_length=0.20)
    lbl  = Text(label, font_size=16, color=C_ARROW, weight=BOLD).next_to(loop, RIGHT, buff=0.10)
    return VGroup(loop, lbl)

def animate_states(scene, state_seq, tok_color):
    """Light up states one by one along state_seq, then flash the last one."""
    pc = get_inner_circle(state_seq[0])
    scene.play(pc.animate.set_fill(tok_color, opacity=0.5)
               .set_stroke(tok_color, width=5), run_time=0.3)
    for st in state_seq[1:]:
        sc = get_inner_circle(st)
        scene.play(
            pc.animate.set_fill(C_STATE, opacity=1).set_stroke(C_BORDER, width=3),
            sc.animate.set_fill(tok_color, opacity=0.5).set_stroke(tok_color, width=5),
            run_time=0.32
        )
        pc = sc
    scene.play(Flash(state_seq[-1], color=tok_color, flash_radius=0.65, num_lines=10), run_time=0.4)
    scene.play(pc.animate.set_fill(C_STATE, opacity=1).set_stroke(C_BORDER, width=3), run_time=0.2)

def emit_token(scene, tok_text, tok_color, position=DOWN*2.8):
    box_txt  = Text(tok_text, font_size=22, color=tok_color)
    box_rect = SurroundingRectangle(box_txt, color=tok_color, buff=0.18,
                                    corner_radius=0.10, stroke_width=2.5)
    box = VGroup(box_rect, box_txt).move_to(position)
    scene.play(FadeIn(box, scale=0.7), run_time=0.5)
    return box

def section_title(text, color=C_INPUT):
    return Text(text, font_size=32, color=color, weight=BOLD).to_edge(UP, buff=0.35)

def input_banner(src_str):
    """Return (banner_group, chars_list) already positioned at top."""
    lbl   = Text("Input:", font_size=18, color=C_BORDER)
    chars = [Text(c if c != " " else "·", font_size=28, color=C_INPUT) for c in src_str]
    cg    = VGroup(*chars).arrange(RIGHT, buff=0.20)
    row   = VGroup(lbl, cg).arrange(RIGHT, buff=0.25)
    rect  = SurroundingRectangle(row, color=C_BORDER, buff=0.18, corner_radius=0.10)
    grp   = VGroup(rect, row).to_edge(UP, buff=1.0)
    return grp, chars

# ══════════════════════════════════════════════════════════════════════════════
# Scene 1 – Title
# ══════════════════════════════════════════════════════════════════════════════
class S1_Title(Scene):
    def construct(self):
        self.camera.background_color = C_BG
        title    = Text("DFAs in Lexical Analysis", font_size=44, color=C_INPUT)
        subtitle = Text("How a lexer tokenises source code", font_size=22, color=C_BORDER)
        VGroup(title, subtitle).arrange(DOWN, buff=0.25).move_to(ORIGIN)
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP*0.1), run_time=0.6)
        self.wait(1.5)
        self.play(FadeOut(VGroup(title, subtitle)), run_time=0.6)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 1b – What is a Compiler?
# ══════════════════════════════════════════════════════════════════════════════
class S1b_WhatIsCompilation(Scene):
    def construct(self):
        self.camera.background_color = C_BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Text("What is a Compiler?", font_size=40, color=C_INPUT, weight=BOLD)
        title.to_edge(UP, buff=0.40)
        self.play(Write(title), run_time=0.9)
        self.wait(0.2)

        # ── Definition text ───────────────────────────────────────────────────
        defn_top = Text(
            "A compiler is a program that translates code written in a",
            font_size=21, color=C_INPUT, line_spacing=1.4
        )

        # Build defn_mid from coloured pieces so we avoid set_color_by_text
        mid_hl   = Text("higher-level programming language", font_size=21, color="#68d391")
        mid_arr  = Text("  →  ", font_size=21, color=C_INPUT)
        mid_ll   = Text("lower-level language", font_size=21, color="#fc8181")
        defn_mid = VGroup(mid_hl, mid_arr, mid_ll).arrange(RIGHT, buff=0)

        defn_bot = Text(
            "such as machine language that a computer can execute.",
            font_size=21, color=C_INPUT, line_spacing=1.4
        )

        defn = VGroup(defn_top, defn_mid, defn_bot).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        defn.next_to(title, DOWN, buff=0.40)
        defn.center().shift(UP * 0.3)

        self.play(FadeIn(defn_top, shift=UP*0.08), run_time=0.5)
        self.play(FadeIn(defn_mid, shift=UP*0.08), run_time=0.5)
        self.play(FadeIn(defn_bot, shift=UP*0.08), run_time=0.5)
        self.wait(0.6)

        # ── High-level ──compiler──▶ Machine code mini-visual ─────────────────
        hl_box_txt = Text("High-Level\nCode\n(C / Python / Java)", font_size=17,
                          color="#68d391", line_spacing=1.25, weight=BOLD)
        hl_rect = RoundedRectangle(width=2.6, height=1.55, corner_radius=0.15,
                                   color="#68d391", fill_color="#68d391",
                                   fill_opacity=0.13, stroke_width=2.5)
        hl_box_txt.move_to(hl_rect)
        hl_group = VGroup(hl_rect, hl_box_txt)

        ml_box_txt = Text("Machine\nCode\n(Binary / Assembly)", font_size=17,
                          color="#fc8181", line_spacing=1.25, weight=BOLD)
        ml_rect = RoundedRectangle(width=2.6, height=1.55, corner_radius=0.15,
                                   color="#fc8181", fill_color="#fc8181",
                                   fill_opacity=0.13, stroke_width=2.5)
        ml_box_txt.move_to(ml_rect)
        ml_group = VGroup(ml_rect, ml_box_txt)

        comp_box_txt = Text("COMPILER", font_size=18, color="#f6e05e",
                            weight=BOLD)
        comp_rect = RoundedRectangle(width=2.2, height=1.0, corner_radius=0.12,
                                     color="#f6e05e", fill_color="#f6e05e",
                                     fill_opacity=0.15, stroke_width=2.5)
        comp_box_txt.move_to(comp_rect)
        comp_group = VGroup(comp_rect, comp_box_txt)

        trio = VGroup(hl_group, comp_group, ml_group).arrange(RIGHT, buff=0.80)
        trio.next_to(defn, DOWN, buff=0.55)

        arr_in  = Arrow(hl_group.get_right(), comp_group.get_left(),
                        buff=0.10, color=C_ARROW, stroke_width=3.5,
                        tip_length=0.20, max_stroke_width_to_length_ratio=999)
        arr_out = Arrow(comp_group.get_right(), ml_group.get_left(),
                        buff=0.10, color=C_ARROW, stroke_width=3.5,
                        tip_length=0.20, max_stroke_width_to_length_ratio=999)

        self.play(FadeIn(hl_group, shift=RIGHT*0.15), run_time=0.45)
        self.play(GrowArrow(arr_in), FadeIn(comp_group, scale=0.85), run_time=0.45)
        self.play(GrowArrow(arr_out), FadeIn(ml_group, shift=LEFT*0.15), run_time=0.45)
        self.wait(2.0)

        # ── Fade out scene ────────────────────────────────────────────────────
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.75)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 2 – Compilation Pipeline
# ══════════════════════════════════════════════════════════════════════════════
class S2_Pipeline(Scene):
    def construct(self):
        self.camera.background_color = C_BG

        pipeline_stages = [
            ("Source\nCode",       "#e2e8f0", "Raw text file\n(.c, .py, .js …)"),
            ("Lexical\nAnalysis",  "#b794f4", "Breaks text into\nTokens via DFAs"),
            ("Syntax\nAnalysis",   "#63b3ed", "Builds a Parse\nTree (CFG)"),
            ("Semantic\nAnalysis", "#68d391", "Type checks &\nscope resolution"),
            ("IR\nGeneration",     "#f6ad55", "Platform-agnostic\nintermediate code"),
            ("Code\nGeneration",   "#fc8181", "Target machine\ncode / bytecode"),
        ]

        BOX_W, BOX_H = 1.75, 1.45

        stage_groups = []
        for name, color, desc in pipeline_stages:
            name_txt = Text(name, font_size=16, color=color, weight=BOLD, line_spacing=1.1)
            desc_txt = Text(desc, font_size=11, color=C_INPUT, line_spacing=1.2)
            content  = VGroup(name_txt, desc_txt).arrange(DOWN, buff=0.14)
            rect     = RoundedRectangle(width=BOX_W, height=BOX_H, corner_radius=0.14,
                                        color=color, fill_color=color,
                                        fill_opacity=0.15, stroke_width=2.5)
            content.move_to(rect.get_center())
            stage_groups.append(VGroup(rect, content))

        pipeline_row = VGroup(*stage_groups).arrange(RIGHT, buff=0.30)
        pipeline_row.move_to(ORIGIN)

        conn_arrows = VGroup()
        for i in range(len(stage_groups) - 1):
            a = Arrow(stage_groups[i].get_right(), stage_groups[i+1].get_left(),
                      buff=0.06, color="#718096", stroke_width=3,
                      tip_length=0.18, max_stroke_width_to_length_ratio=999)
            conn_arrows.add(a)

        ptitle = Text("Stages of Compilation", font_size=26, color=C_INPUT, weight=BOLD)
        ptitle.next_to(pipeline_row, UP, buff=0.45)

        self.play(FadeIn(ptitle, shift=DOWN*0.15), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sg, shift=UP*0.15) for sg in stage_groups],
                              lag_ratio=0.15), run_time=1.5)
        self.play(LaggedStart(*[GrowArrow(a) for a in conn_arrows], lag_ratio=0.12), run_time=1.0)
        self.wait(0.7)

        # Highlight lexical analysis
        lex_box   = stage_groups[1]
        lex_color = pipeline_stages[1][1]
        self.play(lex_box[0].animate.set_fill(lex_color, opacity=0.42)
                             .set_stroke(lex_color, width=5), run_time=0.5)
        callout = Text("We'll focus here", font_size=15, color=lex_color, weight=BOLD)
        callout.next_to(lex_box, DOWN, buff=0.55)
        c_arr = Arrow(callout.get_top(), lex_box.get_bottom(),
                      buff=0.08, color=lex_color, stroke_width=2.5, tip_length=0.15,
                      max_stroke_width_to_length_ratio=999)
        self.play(FadeIn(callout, shift=UP*0.1), GrowArrow(c_arr), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 2b – What is a DFA?
# ══════════════════════════════════════════════════════════════════════════════
class S2b_WhatIsDFA(Scene):
    def construct(self):
        self.camera.background_color = C_BG

        # ── Title ─────────────────────────────────────────────────────────────
        title = Text("What is a DFA?", font_size=38, color=C_INPUT, weight=BOLD).to_edge(UP, buff=0.35)
        self.play(Write(title))
        self.wait(0.3)

        # ── Part 1: States are nodes ──────────────────────────────────────────
        concept1 = Text("A DFA is a graph of states connected by transitions.",
                        font_size=22, color=C_INPUT).next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(concept1, shift=UP*0.1))
        self.wait(0.3)

        # Draw 4 states spread across the middle of the screen
        sA = make_state("A"); sB = make_state("B")
        sC = make_state("C"); sD = make_accept("D")

        sA.move_to(LEFT*4.5 + DOWN*0.5)
        sB.move_to(LEFT*1.5 + DOWN*0.5)
        sC.move_to(RIGHT*1.5 + DOWN*0.5)
        sD.move_to(RIGHT*4.5 + DOWN*0.5)

        self.play(LaggedStart(
            FadeIn(sA, scale=0.7), FadeIn(sB, scale=0.7),
            FadeIn(sC, scale=0.7), FadeIn(sD, scale=0.7),
            lag_ratio=0.2
        ))
        self.wait(0.4)

        # Label: "Each circle is a state"
        state_lbl = Text("Each circle = a state", font_size=18, color=C_BORDER)
        state_lbl.next_to(VGroup(sA,sB,sC,sD), DOWN, buff=0.35)
        self.play(FadeIn(state_lbl, shift=UP*0.08))
        self.wait(0.6)

        # ── Part 2: Transitions connect states ────────────────────────────────
        eAB = edge(sA, sB, "x")
        eBC = edge(sB, sC, "y")
        eCD = edge(sC, sD, "z")

        concept2 = Text("Transitions (arrows) move the machine from state to state.",
                        font_size=22, color=C_INPUT)
        concept2.next_to(title, DOWN, buff=0.4)

        self.play(FadeOut(concept1), FadeIn(concept2, shift=UP*0.1))
        self.play(LaggedStart(GrowArrow(eAB[0]), GrowArrow(eBC[0]), GrowArrow(eCD[0]), lag_ratio=0.25))
        self.play(LaggedStart(FadeIn(eAB[1]), FadeIn(eBC[1]), FadeIn(eCD[1]), lag_ratio=0.2))
        self.wait(0.4)

        trans_lbl = Text("Each arrow = a transition (labelled with a character)",
                         font_size=18, color=C_BORDER)
        trans_lbl.next_to(VGroup(sA,sB,sC,sD), DOWN, buff=0.35)
        self.play(FadeTransform(state_lbl, trans_lbl))
        self.wait(0.7)

        # ── Part 3: Exactly one active state ─────────────────────────────────
        concept3 = Text("At any moment the machine is in exactly one state.",
                        font_size=22, color=C_INPUT)
        concept3.next_to(title, DOWN, buff=0.4)
        self.play(FadeOut(concept2), FadeIn(concept3, shift=UP*0.1))
        self.wait(0.2)

        # Highlight the "current" state marker
        C_ACTIVE = "#f6e05e"
        marker = Circle(radius=sA.node_radius + 0.18, color=C_ACTIVE,
                        stroke_width=4, fill_opacity=0).move_to(sA.get_center())
        cur_lbl = Text("current state", font_size=16, color=C_ACTIVE)
        cur_lbl.next_to(sA, UP, buff=0.15)
        self.play(Create(marker), FadeIn(cur_lbl, shift=DOWN*0.1))
        self.wait(0.5)

        # Walk the marker through the states
        for (nxt, arrow) in [(sB, eAB), (sC, eBC), (sD, eCD)]:
            # Flash the arrow being followed
            self.play(arrow[0].animate.set_color(C_ACTIVE), run_time=0.25)
            self.play(
                marker.animate.move_to(nxt.get_center()),
                cur_lbl.animate.next_to(nxt, UP, buff=0.15),
                run_time=0.45
            )
            self.play(arrow[0].animate.set_color(C_ARROW), run_time=0.2)
            self.wait(0.2)

        self.wait(0.4)

        # ── Part 4: Accepting state ───────────────────────────────────────────
        concept4 = Text("Some states are accepting states — the machine stops and accepts the input.",
                        font_size=20, color=C_INPUT, line_spacing=1.2)
        concept4.next_to(title, DOWN, buff=0.4)
        self.play(FadeOut(concept3), FadeIn(concept4, shift=UP*0.1))
        self.wait(0.3)

        # Pulse the accept state
        self.play(Flash(sD, color=C_ACCEPT, flash_radius=0.8, num_lines=12), run_time=0.6)
        accept_lbl = Text("double ring = accepting state", font_size=18, color=C_ACCEPT)
        accept_lbl.next_to(VGroup(sA,sB,sC,sD), DOWN, buff=0.35)
        self.play(FadeTransform(trans_lbl, accept_lbl))
        self.wait(0.8)

        # ── Part 5: In lexical analysis ───────────────────────────────────────
        concept5 = Text("In lexical analysis, each transition is a character read from the source code.",
                        font_size=20, color=C_INPUT, line_spacing=1.2)
        concept5.next_to(title, DOWN, buff=0.4)
        self.play(FadeOut(concept4), FadeIn(concept5, shift=UP*0.1))
        self.wait(0.3)

        # Re-label arrows as characters to make the analogy concrete
        new_lbls = []
        for arr_grp, ch in [(eAB, "'i'"), (eBC, "'f'"), (eCD, "...")]:
            new_lbl = Text(ch, font_size=18, color="#f6ad55", weight=BOLD)
            new_lbl.move_to(arr_grp[1].get_center())
            new_lbls.append(new_lbl)
        self.play(LaggedStart(*[FadeTransform(eAB[1], new_lbls[0]),
                                FadeTransform(eBC[1], new_lbls[1]),
                                FadeTransform(eCD[1], new_lbls[2])], lag_ratio=0.2))

        char_lbl = Text("Each arrow label = a character (or set of characters) matched from input",
                        font_size=16, color=C_BORDER, line_spacing=1.2)
        char_lbl.next_to(VGroup(sA,sB,sC,sD), DOWN, buff=0.35)
        self.play(FadeTransform(accept_lbl, char_lbl))
        self.wait(1.5)

        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)


# ══════════════════════════════════════════════════════════════════════════════
# Scene 3 – Keyword DFA  ("if")
# ══════════════════════════════════════════════════════════════════════════════
class S3_KeywordDFA(Scene):
    def construct(self):
        self.camera.background_color = C_BG

        title = section_title('Keyword DFA  —  recognises "if"', color=C_KEYWORD)
        self.play(FadeIn(title, shift=DOWN*0.1))

        # Build DFA
        q0 = make_state("q0"); q1 = make_state("q1"); q2 = make_accept("q2")
        states = VGroup(q0, q1, q2).arrange(RIGHT, buff=1.6)
        states.move_to(ORIGIN + UP*0.3)

        e01 = edge(q0, q1, "i")
        e12 = edge(q1, q2, "f")
        s0  = start_arrow(q0)

        dfa = VGroup(states, e01, e12, s0)
        self.play(FadeIn(dfa, shift=UP*0.1))
        self.wait(0.5)

        # Input banner
        banner, chars = input_banner("if")
        self.play(FadeIn(banner))
        self.wait(0.3)

        # Animate: i → q1, f → q2
        self.play(chars[0].animate.set_color(C_KEYWORD), run_time=0.25)
        animate_states(self, [q0, q1], C_KEYWORD)
        self.wait(0.1)
        self.play(chars[1].animate.set_color(C_KEYWORD), run_time=0.25)
        animate_states(self, [q1, q2], C_KEYWORD)

        tok = emit_token(self, 'KEYWORD  "if"', C_KEYWORD)
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

# ══════════════════════════════════════════════════════════════════════════════
# Scene 4 – Identifier DFA  ("x12")
# ══════════════════════════════════════════════════════════════════════════════
class S4_IdentDFA(Scene):
    def construct(self):
        self.camera.background_color = C_BG

        title = section_title('Identifier DFA  —  recognises "x12"', color=C_IDENT)
        self.play(FadeIn(title, shift=DOWN*0.1))

        # Build DFA
        q0 = make_state("q0"); q1 = make_accept("q1")
        states = VGroup(q0, q1).arrange(RIGHT, buff=2.2)
        states.move_to(ORIGIN + UP*0.3)

        e01  = edge(q0, q1, "a-z")
        loop = self_loop(q1, "a-z, 0-9")
        s0   = start_arrow(q0)

        dfa = VGroup(states, e01, loop, s0)
        self.play(FadeIn(dfa, shift=UP*0.1))
        self.wait(0.5)

        # Input banner
        banner, chars = input_banner("x12")
        self.play(FadeIn(banner))
        self.wait(0.3)

        # x → q1,  1 → stay q1,  2 → stay q1
        self.play(chars[0].animate.set_color(C_IDENT), run_time=0.25)
        animate_states(self, [q0, q1], C_IDENT)
        for ch in chars[1:]:
            self.play(ch.animate.set_color(C_IDENT), run_time=0.25)
            animate_states(self, [q1, q1], C_IDENT)

        tok = emit_token(self, 'IDENT  "x12"', C_IDENT)
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

# ══════════════════════════════════════════════════════════════════════════════
# Scene 5 – Number DFA  ("42")
# ══════════════════════════════════════════════════════════════════════════════
class S5_NumberDFA(Scene):
    def construct(self):
        self.camera.background_color = C_BG

        title = section_title('Number DFA  —  recognises "42"', color=C_NUM)
        self.play(FadeIn(title, shift=DOWN*0.1))

        # Build DFA
        q0 = make_state("q0"); q1 = make_accept("q1")
        states = VGroup(q0, q1).arrange(RIGHT, buff=2.2)
        states.move_to(ORIGIN + UP*0.3)

        e01  = edge(q0, q1, "0-9")
        loop = self_loop(q1, "0-9")
        s0   = start_arrow(q0)

        dfa = VGroup(states, e01, loop, s0)
        self.play(FadeIn(dfa, shift=UP*0.1))
        self.wait(0.5)

        # Input banner
        banner, chars = input_banner("42")
        self.play(FadeIn(banner))
        self.wait(0.3)

        # 4 → q1,  2 → stay q1
        self.play(chars[0].animate.set_color(C_NUM), run_time=0.25)
        animate_states(self, [q0, q1], C_NUM)
        self.play(chars[1].animate.set_color(C_NUM), run_time=0.25)
        animate_states(self, [q1, q1], C_NUM)

        tok = emit_token(self, 'NUMBER  "42"', C_NUM)
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)

# ══════════════════════════════════════════════════════════════════════════════
# Scene 6 – Full lexer in action  ("if x12 >= 42")
# ══════════════════════════════════════════════════════════════════════════════
class S6_FullLexer(Scene):
    def construct(self):
        self.camera.background_color = C_BG

        title = section_title("Lexer in Action  —  all DFAs together", color=C_INPUT)
        self.play(FadeIn(title, shift=DOWN*0.1))

        # Source input
        src = "if x12 >= 42"
        src_lbl = Text("Source:", font_size=18, color=C_BORDER)
        chars   = [Text(c if c != " " else "·", font_size=26, color=C_INPUT) for c in src]
        cg      = VGroup(*chars).arrange(RIGHT, buff=0.18)
        row     = VGroup(src_lbl, cg).arrange(RIGHT, buff=0.22)
        banner  = VGroup(SurroundingRectangle(row, color=C_BORDER, buff=0.18, corner_radius=0.10), row)
        banner.next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(banner))
        self.wait(0.3)

        dfa_y = 0.4

        def ms(l): return make_state(l, radius=0.36)
        def ma(l): return make_accept(l, radius=0.36)

        # Keyword DFA (small)
        kA0=ms("q0"); kA1=ms("q1"); kA2=ma("q2")
        VGroup(kA0,kA1,kA2).arrange(RIGHT,buff=0.85).move_to(LEFT*4.3+UP*dfa_y)
        kw_title = Text('Keyword DFA', font_size=14, color=C_KEYWORD).next_to(VGroup(kA0,kA1,kA2), UP, buff=0.18)
        ke01=edge(kA0,kA1,"i"); ke12=edge(kA1,kA2,"f")
        ks=start_arrow(kA0); kw_full=VGroup(kw_title,kA0,kA1,kA2,ke01,ke12,ks)

        # Identifier DFA (small)
        iB0=ms("q0"); iB1=ma("q1")
        VGroup(iB0,iB1).arrange(RIGHT,buff=0.95).move_to(UP*dfa_y)
        id_title = Text('Identifier DFA', font_size=14, color=C_IDENT).next_to(VGroup(iB0,iB1), UP, buff=0.18)
        ie01=edge(iB0,iB1,"a-z"); il=self_loop(iB1,"a-z,0-9")
        is0=start_arrow(iB0); id_full=VGroup(id_title,iB0,iB1,ie01,il,is0)

        # Number DFA (small)
        nC0=ms("q0"); nC1=ma("q1")
        VGroup(nC0,nC1).arrange(RIGHT,buff=0.95).move_to(RIGHT*4.3+UP*dfa_y)
        num_title = Text('Number DFA', font_size=14, color=C_NUM).next_to(VGroup(nC0,nC1), UP, buff=0.18)
        ne01=edge(nC0,nC1,"0-9"); nl=self_loop(nC1,"0-9")
        ns0=start_arrow(nC0); num_full=VGroup(num_title,nC0,nC1,ne01,nl,ns0)

        self.play(LaggedStart(FadeIn(kw_full), FadeIn(id_full), FadeIn(num_full), lag_ratio=0.25))
        self.wait(0.4)

        # Token output row
        tok_lbl = Text("Tokens:", font_size=18, color=C_BORDER).to_edge(LEFT, buff=0.5).shift(DOWN*2.9)
        self.play(FadeIn(tok_lbl))
        tok_x = tok_lbl.get_right()[0] + 0.6

        tokens_info = [
            ("if",  [kA0,kA1,kA2], 'KEYWORD\n"if"',  C_KEYWORD),
            ("x12", [iB0,iB1,iB1,iB1], 'IDENT\n"x12"', C_IDENT),
            (">=",  [],              'OP\n">="',       C_OP),
            ("42",  [nC0,nC1,nC1],  'NUMBER\n"42"',   C_NUM),
        ]

        char_idx = 0
        for word, seq, tok_text, tok_color in tokens_info:
            # skip spaces
            while char_idx < len(src) and src[char_idx] == ' ':
                char_idx += 1
            wchars = chars[char_idx:char_idx+len(word)]
            self.play(*[c.animate.set_color(tok_color) for c in wchars], run_time=0.25)

            if seq:
                animate_states(self, seq, tok_color)

            bt = Text(tok_text, font_size=13, color=tok_color).set_line_spacing(-0.1)
            br = SurroundingRectangle(bt, color=tok_color, buff=0.12, corner_radius=0.08, stroke_width=2)
            tb = VGroup(br, bt).move_to([tok_x+0.5, tok_lbl.get_center()[1], 0])
            tok_x += 1.35
            self.play(FadeIn(tb, scale=0.75), run_time=0.4)
            self.wait(0.1)
            char_idx += len(word) + 1

        self.wait(0.6)

        summary = Text(
            "Each DFA recognises one token class.\nThe lexer runs them in parallel — longest match wins.",
            font_size=18, color=C_INPUT, line_spacing=1.3
        ).to_edge(DOWN, buff=0.22)
        summary_bg = BackgroundRectangle(summary, color=C_BG, fill_opacity=0.92, buff=0.18)
        self.play(FadeIn(summary_bg), Write(summary), run_time=1.4)
        self.wait(2.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)

class FullVideo(Scene):
    def construct(self):
        for SceneClass in [
            S1_Title, S1b_WhatIsCompilation, S2_Pipeline,
            S2b_WhatIsDFA, S3_KeywordDFA, S4_IdentDFA,
            S5_NumberDFA, S6_FullLexer
        ]:
            SceneClass.construct(self)
