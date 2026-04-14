"""
Q-Learning Demo  —  3×2 Grid World
====================================
Grid layout (col, row):
  (0,0)  (1,0)  (2,0)=GOAL+5
  (0,1)  (1,1)  (2,1)=TRAP-5

Off-grid move  → reward -1, episode ends, agent shown outside grid
Step button    → animates one full episode move-by-move
+1/+10/+100   → run N episodes silently, refresh Q-table
Reset          → wipe everything
"""

import tkinter as tk
from tkinter import font as tkfont
import random

# ── Hyperparameters ───────────────────────────────────────────────────────────
ALPHA         = 0.10
GAMMA         = 0.90
EPS_START     = 1.00
EPS_MIN       = 0.05
EPS_DECAY     = 0.98

# ── World ─────────────────────────────────────────────────────────────────────
COLS, ROWS    = 3, 2
GOAL          = (2, 0)
TRAP          = (2, 1)
TERMINALS     = {GOAL: +5, TRAP: -5}
NON_TERM      = [(c, r) for r in range(ROWS) for c in range(COLS)
                 if (c, r) not in TERMINALS]
ACTIONS       = ["U", "D", "L", "R"]
DELTAS        = {"U": (0,-1), "D": (0,1), "L": (-1,0), "R": (1,0)}
ARROWS        = {"U": "↑", "D": "↓", "L": "←", "R": "→"}

# ── Colours ───────────────────────────────────────────────────────────────────
BG          = "#F5F4F0"
PANEL       = "#FFFFFF"
BORDER      = "#D0CEC6"
TEXT        = "#1C1B19"
MUTED       = "#6E6D69"
GOAL_BG     = "#EAF3DE"
GOAL_FG     = "#3B6D11"
TRAP_BG     = "#FCEBEB"
TRAP_FG     = "#A32D2D"
OFFGRID_BG  = "#E2E0D8"
OFFGRID_FG  = "#A8A59E"
GRID_LINE   = "#C8C7C0"
NEUTRAL     = "#EFEFEC"
HDR_BG      = "#F0EFE9"

AGENT_FILL  = {"start":"#F0A500","move":"#378ADD","goal":"#3B6D11","trap":"#A32D2D","offgrid":"#A32D2D"}
AGENT_RING  = {"start":"#8B5E00","move":"#0C447C","goal":"#1A3A07","trap":"#6B1010","offgrid":"#6B1010"}
AGENT_LABEL = {"start":"S","move":"●","goal":"★","trap":"✕","offgrid":"✕"}

def lerp(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t))


# ── Agent / Q-learning ────────────────────────────────────────────────────────
class Agent:
    def __init__(self):
        self.reset()

    def reset(self):
        self.Q           = {(c,r): {a:0.0 for a in ACTIONS}
                            for r in range(ROWS) for c in range(COLS)}
        self.epsilon     = EPS_START
        self.episodes    = 0
        self.last_action = None
        self.last_reward = None
        self.new_episode()

    def new_episode(self):
        self.state        = random.choice(NON_TERM)
        self.done         = False
        self.mode         = "start"
        self.off_grid_pos = None
        self.ep_steps     = 0

    def step(self):
        if self.done:
            return
        s      = self.state
        a      = (random.choice(ACTIONS) if random.random() < self.epsilon
                  else max(self.Q[s], key=self.Q[s].get))
        dc, dr = DELTAS[a]
        nc, nr = s[0]+dc, s[1]+dr
        off    = not (0 <= nc < COLS and 0 <= nr < ROWS)

        if off:
            reward            = -1
            ns                = s
            self.off_grid_pos = (nc, nr)
            self.mode         = "offgrid"
            target            = reward
            terminal          = True
        else:
            ns                = (nc, nr)
            self.off_grid_pos = None
            reward            = TERMINALS.get(ns, 0)
            terminal          = ns in TERMINALS
            target            = reward if terminal else reward + GAMMA*max(self.Q[ns].values())
            self.mode         = ("goal" if ns==GOAL else
                                 "trap" if ns==TRAP else "move")

        self.Q[s][a]     += ALPHA * (target - self.Q[s][a])
        self.state        = s if off else ns
        self.done         = off or terminal
        self.last_action  = a
        self.last_reward  = reward
        self.ep_steps    += 1

        if self.done:
            self.episodes += 1
            self.epsilon   = max(EPS_MIN, self.epsilon * EPS_DECAY)

    def run_n(self, n):
        for _ in range(n):
            self.new_episode()
            while not self.done:
                self.step()


# ── GUI ───────────────────────────────────────────────────────────────────────
CELL         = 110
BORDER_CELLS = 1

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Q-Learning — 3×2 Grid World")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.agent = Agent()
        self._tid  = None
        self._busy = False
        self._build_ui()
        self._redraw()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self, bg=BG, padx=20, pady=16)
        outer.pack()

        # Title
        hdr = tk.Frame(outer, bg=BG)
        hdr.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,12))
        tk.Label(hdr, text="Q-Learning Demo",
                 font=tkfont.Font(family="Helvetica",size=17,weight="bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hdr, text="  —  3×2 Grid World",
                 font=tkfont.Font(family="Helvetica",size=13),
                 bg=BG, fg=MUTED).pack(side="left", pady=(3,0))

        # Left column
        left = tk.Frame(outer, bg=BG)
        left.grid(row=1, column=0, sticky="n", padx=(0,20))

        cw = (COLS + 2*BORDER_CELLS) * CELL
        ch = (ROWS + 2*BORDER_CELLS) * CELL
        self.canvas = tk.Canvas(left, width=cw, height=ch,
                                bg=OFFGRID_BG, highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack()

        stats = tk.Frame(left, bg=BG)
        stats.pack(fill="x", pady=(10,0))
        self.v_ep  = tk.StringVar(value="Episodes: 0")
        self.v_eps = tk.StringVar(value="ε = 1.000  (exploring)")
        self.v_act = tk.StringVar(value="Action: —")
        self.v_rew = tk.StringVar(value="Reward: —")
        for v in (self.v_ep, self.v_eps, self.v_act, self.v_rew):
            tk.Label(stats, textvariable=v,
                     font=tkfont.Font(family="Helvetica",size=11),
                     bg=BG, fg=MUTED, anchor="w").pack(fill="x")

        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(fill="x", pady=(14,0))

        tk.Label(ctrl, text="Run episodes:",
                 font=tkfont.Font(family="Helvetica",size=10),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(0,4))

        btn_row = tk.Frame(ctrl, bg=BG)
        btn_row.pack(fill="x", pady=(0,8))

        # +1 = animated step
        tk.Button(btn_row, text="+1  ▶",
                  command=self._on_step,
                  font=tkfont.Font(family="Helvetica",size=11,weight="bold"),
                  bg=NEUTRAL, fg=TEXT, relief="flat",
                  cursor="hand2", padx=14, pady=6).pack(side="left")

        # +10 and +100 = silent fast-forward
        for n in (10, 100):
            tk.Button(btn_row, text=f"+{n}",
                      command=lambda x=n: self._on_ff(x),
                      font=tkfont.Font(family="Helvetica",size=11),
                      bg=NEUTRAL, fg=TEXT, relief="flat",
                      cursor="hand2", padx=14, pady=6).pack(side="left", padx=(8,0))

        tk.Button(btn_row, text="Reset",
                  command=self._on_reset,
                  font=tkfont.Font(family="Helvetica",size=11),
                  bg="#f0dede", fg=TRAP_FG, relief="flat",
                  cursor="hand2", padx=14, pady=6).pack(side="right")

        # Right column: Q-table
        right = tk.Frame(outer, bg=BG)
        right.grid(row=1, column=1, sticky="n")

        tk.Label(right, text="Q-Table",
                 font=tkfont.Font(family="Helvetica",size=13,weight="bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0,6))

        wrap = tk.Frame(right, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        wrap.pack()
        tbl = tk.Frame(wrap, bg=PANEL, padx=10, pady=8)
        tbl.pack()

        fh = tkfont.Font(family="Helvetica", size=9, weight="bold")
        fc = tkfont.Font(family="Helvetica", size=9)
        fa = tkfont.Font(family="Helvetica", size=14)

        for ci, (txt, w) in enumerate([("State",7),("↑ U",5),("↓ D",5),("← L",5),("→ R",5),("Best",4)]):
            tk.Label(tbl, text=txt, font=fh, bg=HDR_BG, fg=MUTED,
                     width=w, anchor="center", relief="flat",
                     padx=4, pady=3).grid(row=0, column=ci, sticky="nsew", padx=1, pady=1)

        self._cells = {}
        for r in range(ROWS):
            for c in range(COLS):
                s   = (c, r)
                row = r*COLS + c + 1
                slbl = "GOAL" if s==GOAL else ("TRAP" if s==TRAP else f"({c},{r})")
                sbg  = GOAL_BG if s==GOAL else (TRAP_BG if s==TRAP else HDR_BG)
                sfg  = GOAL_FG if s==GOAL else (TRAP_FG if s==TRAP else MUTED)
                tk.Label(tbl, text=slbl, font=fh, bg=sbg, fg=sfg,
                         anchor="center", relief="flat",
                         padx=6, pady=4).grid(row=row, column=0,
                                              sticky="nsew", padx=1, pady=1)
                albl = {}
                for ci, a in enumerate(ACTIONS):
                    l = tk.Label(tbl, text=" 0.00", font=fc, bg=PANEL, fg=MUTED,
                                 width=5, anchor="center", relief="flat", padx=4, pady=4)
                    l.grid(row=row, column=ci+1, sticky="nsew", padx=1, pady=1)
                    albl[a] = l
                best = tk.Label(tbl, text="—", font=fa, bg=PANEL, fg=MUTED,
                                width=3, anchor="center", relief="flat", padx=4, pady=3)
                best.grid(row=row, column=5, sticky="nsew", padx=1, pady=1)
                self._cells[s] = (albl, best)

        # Legend
        leg = tk.Frame(right, bg=BG)
        leg.pack(anchor="w", pady=(10,0))
        for fill, lbl in [(GOAL_BG,"Goal +5"),(TRAP_BG,"Trap −5"),
                          (AGENT_FILL["start"],"Start (S)"),
                          (AGENT_FILL["move"],"Moving"),
                          (AGENT_FILL["goal"],"Reached goal"),
                          (AGENT_FILL["offgrid"],"Off-grid / trap")]:
            tk.Frame(leg, bg=fill, width=12, height=12).pack(side="left")
            tk.Label(leg, text=f" {lbl}   ",
                     font=tkfont.Font(family="Helvetica",size=10),
                     bg=BG, fg=MUTED).pack(side="left")

        # Formula
        note = tk.Frame(outer, bg=NEUTRAL)
        note.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14,0))
        tk.Label(note,
                 text="  Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',·) − Q(s,a)]"
                      "      α=0.10   γ=0.90   ε decays ×0.98/episode",
                 font=tkfont.Font(family="Courier",size=10),
                 bg=NEUTRAL, fg=MUTED, pady=6).pack(anchor="w")

    # ── Draw ──────────────────────────────────────────────────────────────────
    def _redraw(self):
        self._draw_grid()
        self._draw_qtable()
        self._draw_stats()

    def _draw_grid(self):
        cv  = self.canvas
        cv.delete("all")
        ag  = self.agent
        OX  = BORDER_CELLS * CELL
        OY  = BORDER_CELLS * CELL

        # Off-grid labels
        mid_x = OX + COLS*CELL//2
        mid_y = OY + ROWS*CELL//2
        for txt, ax, ay in [
            ("← off grid", OX//2,              mid_y),
            ("→ off grid", OX+COLS*CELL+OX//2, mid_y),
            ("↑ off grid", mid_x,              OY//2),
            ("↓ off grid", mid_x,              OY+ROWS*CELL+OY//2),
        ]:
            cv.create_text(ax, ay, text=txt, fill=OFFGRID_FG,
                           font=("Helvetica",8,"italic"))

        # Cells
        for r in range(ROWS):
            for c in range(COLS):
                s  = (c, r)
                x0 = OX + c*CELL;  y0 = OY + r*CELL
                x1 = x0+CELL;      y1 = y0+CELL
                fill = GOAL_BG if s==GOAL else (TRAP_BG if s==TRAP else PANEL)
                cv.create_rectangle(x0,y0,x1,y1, fill=fill, outline=GRID_LINE)
                if s == GOAL:
                    cv.create_text(x0+CELL//2, y0+20, text="GOAL",
                                   fill=GOAL_FG, font=("Helvetica",9,"bold"))
                    cv.create_text(x0+CELL//2, y0+42, text="+5",
                                   fill=GOAL_FG, font=("Helvetica",16,"bold"))
                elif s == TRAP:
                    cv.create_text(x0+CELL//2, y0+20, text="TRAP",
                                   fill=TRAP_FG, font=("Helvetica",9,"bold"))
                    cv.create_text(x0+CELL//2, y0+42, text="−5",
                                   fill=TRAP_FG, font=("Helvetica",16,"bold"))
                else:
                    q = ag.Q[s]
                    if any(v!=0 for v in q.values()):
                        cv.create_text(x0+CELL//2, y0+CELL//2,
                                       text=ARROWS[max(q,key=q.get)],
                                       fill=MUTED, font=("Helvetica",24))
                    cv.create_text(x1-5, y1-5, text=f"({c},{r})",
                                   fill=BORDER, font=("Helvetica",8), anchor="se")

        # Dashed boundary
        cv.create_rectangle(OX, OY, OX+COLS*CELL, OY+ROWS*CELL,
                            outline=BORDER, width=2, dash=(6,3))

        # Agent position
        mode = ag.mode
        if mode == "offgrid" and ag.off_grid_pos:
            ac, ar = ag.off_grid_pos
            ac = max(-BORDER_CELLS, min(COLS+BORDER_CELLS-1, ac))
            ar = max(-BORDER_CELLS, min(ROWS+BORDER_CELLS-1, ar))
        else:
            ac, ar = ag.state

        cx = OX + ac*CELL + CELL//2
        cy = OY + ar*CELL + CELL//2
        r  = 22
        cv.create_oval(cx-r,cy-r,cx+r,cy+r,
                       fill=AGENT_FILL[mode], outline=AGENT_RING[mode], width=2)
        cv.create_text(cx, cy, text=AGENT_LABEL[mode],
                       fill="white", font=("Helvetica",12,"bold"))

    def _draw_qtable(self):
        ag      = self.agent
        all_q   = [v for s in ag.Q for v in ag.Q[s].values()]
        max_abs = max((abs(v) for v in all_q), default=0.01)
        max_abs = max(max_abs, 0.01)

        for s, (albl, best_lbl) in self._cells.items():
            q      = ag.Q[s]
            is_t   = s in TERMINALS
            best_a = max(q, key=q.get)
            for a, lbl in albl.items():
                v   = q[a]
                txt = f"{v:+.2f}" if v != 0 else " 0.00"
                if is_t:
                    lbl.config(text=txt, bg=NEUTRAL, fg=MUTED)
                elif v > 0:
                    t = min(v/max_abs, 1.0)
                    lbl.config(text=txt, bg=lerp(PANEL,GOAL_BG,t),
                               fg=GOAL_FG if t>0.4 else TEXT)
                elif v < 0:
                    t = min(abs(v)/max_abs, 1.0)
                    lbl.config(text=txt, bg=lerp(PANEL,TRAP_BG,t),
                               fg=TRAP_FG if t>0.4 else TEXT)
                else:
                    lbl.config(text=txt, bg=PANEL, fg=MUTED)
            if is_t:
                best_lbl.config(text="—", bg=NEUTRAL, fg=MUTED)
            else:
                best_lbl.config(text=ARROWS[best_a], bg=PANEL,
                                fg=GOAL_FG if q[best_a]>0 else
                                   (TRAP_FG if q[best_a]<0 else MUTED))

    def _draw_stats(self):
        ag = self.agent
        self.v_ep.set(f"Episodes: {ag.episodes}   Steps this ep: {ag.ep_steps}")
        self.v_eps.set(f"ε = {ag.epsilon:.3f}  "
                       f"({'exploiting' if ag.epsilon<=EPS_MIN+0.01 else 'exploring'})")
        self.v_act.set(f"Action: {ARROWS[ag.last_action]} {ag.last_action}"
                       if ag.last_action else "Action: —")
        if ag.last_reward is not None:
            suffix = {"offgrid":"  ✕ off grid","goal":"  ★ goal!","trap":"  ✕ trap"}.get(ag.mode,"")
            self.v_rew.set(f"Reward: {ag.last_reward:+.0f}{suffix}")
        else:
            self.v_rew.set("Reward: —")

    # ── Controls ─────────────────────────────────────────────────────────────
    def _cancel(self):
        if self._tid is not None:
            self.after_cancel(self._tid)
            self._tid = None

    def _on_step(self):
        #print(f"_on_step called, _busy={self._busy}")
        if self._busy:
            return
        self._cancel()
        self._busy = True
        ag = self.agent
        ag.new_episode()
        #print(f"new_episode: state={ag.state} mode={ag.mode}")
        self._redraw()
        self._tid = self.after(200, self._tick)
        #print(f"after() scheduled, _tid={self._tid}")

    def _tick(self):
        self._tid = None
        try:
            ag = self.agent

            s = ag.state
            a = (random.choice(ACTIONS) if random.random() < ag.epsilon
                 else max(ag.Q[s], key=ag.Q[s].get))
            dc, dr = DELTAS[a]
            nc, nr = s[0]+dc, s[1]+dr
            off = not (0 <= nc < COLS and 0 <= nr < ROWS)

            if off:
                reward   = -1
                ns       = s
                ag.off_grid_pos = (max(-1, min(COLS, nc)), max(-1, min(ROWS, nr)))
                ag.mode  = "offgrid"
                terminal = True
            else:
                ns       = (nc, nr)
                ag.off_grid_pos = None
                reward   = TERMINALS.get(ns, 0)
                terminal = ns in TERMINALS
                ag.mode  = "goal" if ns==GOAL else ("trap" if ns==TRAP else "move")

            target = reward if (off or terminal) else reward + GAMMA * max(ag.Q[ns].values())
            ag.Q[s][a] += ALPHA * (target - ag.Q[s][a])

            ag.state       = s if off else ns
            ag.done        = off or terminal
            ag.last_action = a
            ag.last_reward = reward
            ag.ep_steps   += 1

            if ag.done:
                ag.episodes += 1
                ag.epsilon   = max(EPS_MIN, ag.epsilon * EPS_DECAY)

            #$print(f"tick: {s} -{a}-> mode={ag.mode} new_state={ag.state} done={ag.done}")
            self._redraw()

            if ag.done:
                self._busy = False
            else:
                self._tid = self.after(200, self._tick)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._busy = False

    def _on_ff(self, n):
        if self._busy:
            return
        self.agent.run_n(n)
        self.agent.new_episode()
        self._redraw()

    def _on_reset(self):
        self._cancel()
        self._busy = False
        self.agent.reset()
        self._redraw()


if __name__ == "__main__":
    App().mainloop()
