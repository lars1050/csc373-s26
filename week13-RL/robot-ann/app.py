"""
app.py  —  Stochastic Gridworld Q-Learning Visualizer
=======================================================
Run:  python app.py

Toggle between Tabular Q-Learning and DQN using the buttons at the top.
Each mode has its own agent and episode counter — switching resets.

Controls:
  +1  — animate one full episode
  +10 / +100 — run silently, refresh display
  Reset — wipe agent and episode count
"""

import tkinter as tk
from tkinter import font as tkfont
import random

from world import (World, COLS, ROWS, HOME, FOODS, HAZARDS, PITFALLS,
                   START, ACTIONS, ARROWS, DELTAS, PERP,
                   STEP_PENALTY, FOOD_REWARD, HAZARD_PENALTY,
                   PITFALL_PENALTY, HOME_REWARD, OFFGRID_PENALTY,
                   sample_action)
from agent_tabular import TabularAgent
from agent_dqn import DQNAgent, TRAIN_START, BATCH_SIZE, TARGET_UPDATE

# ── Layout ────────────────────────────────────────────────────────────────────
CELL         = 56
BORDER_CELLS = 1
MOVE_DELAY   = 120

OX = BORDER_CELLS * CELL
OY = BORDER_CELLS * CELL
CW = (COLS + 2*BORDER_CELLS) * CELL
CH = (ROWS + 2*BORDER_CELLS) * CELL

# ── Colours ───────────────────────────────────────────────────────────────────
BG         = "#F5F4F0"
PANEL      = "#FFFFFF"
BORDER_C   = "#D0CEC6"
TEXT       = "#1C1B19"
MUTED      = "#6E6D69"
GRID_LINE  = "#E0DED8"
OFFGRID_BG = "#E2E0D8"
OFFGRID_FG = "#B0ADA8"
NEUTRAL    = "#EFEFEC"
HDR_BG     = "#F0EFE9"
TAB_ACT    = "#1C1B19"   # active mode tab
TAB_INACT  = "#EFEFEC"

HOME_BG    = "#D8EEC8";  HOME_FG    = "#2D5A0E"
FOOD_BG    = "#FFF3CC";  FOOD_FG    = "#7A5500"
HAZARD_BG  = "#FFE0B2";  HAZARD_FG  = "#8B4500"
PITFALL_BG = "#F5D5D5";  PITFALL_FG = "#8B1A1A"
START_BG   = "#E8F0FE";  START_FG   = "#1A3A8B"

AGENT_FILL  = {"start":"#F0A500","move":"#3080CC",
               "home":"#2D7A1F","pitfall":"#CC2222",
               "offgrid":"#CC2222","hazard":"#E07000",
               "food":"#CC9900"}
AGENT_RING  = {"start":"#8B5E00","move":"#0C447C",
               "home":"#1A4A0A","pitfall":"#6B1010",
               "offgrid":"#6B1010","hazard":"#7A3800",
               "food":"#7A5500"}
AGENT_LABEL = {"start":"S","move":"●","home":"★",
               "pitfall":"✕","offgrid":"✕",
               "hazard":"!","food":"●"}

def lerp(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t))


# ── App ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stochastic Gridworld — Q-Learning vs DQN")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.world          = World()
        self.tab_agent      = TabularAgent()
        self.dqn_agent      = DQNAgent()
        self.mode           = "tabular"   # "tabular" or "dqn"
        self._tid           = None
        self._busy          = False
        self._agent_mode    = "start"
        self._reward_history= {"tabular": [], "dqn": []}
        self._ep_total      = 0

        self._build_ui()
        self.world.reset()
        self._agent_mode = "start"
        self._redraw()

    @property
    def agent(self):
        return self.tab_agent if self.mode == "tabular" else self.dqn_agent

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self, bg=BG, padx=16, pady=14)
        outer.pack()

        # ── Mode toggle ───────────────────────────────────────────────────────
        toggle_row = tk.Frame(outer, bg=BG)
        toggle_row.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))

        tk.Label(toggle_row, text="Mode:",
                 font=tkfont.Font(family="Helvetica",size=11),
                 bg=BG, fg=MUTED).pack(side="left", padx=(0,8))

        self.tab_btn = tk.Button(toggle_row, text="Tabular Q-Learning",
                                 command=lambda: self._set_mode("tabular"),
                                 font=tkfont.Font(family="Helvetica",size=11,weight="bold"),
                                 relief="flat", cursor="hand2",
                                 padx=14, pady=5)
        self.tab_btn.pack(side="left")

        self.dqn_btn = tk.Button(toggle_row, text="DQN (Neural Network)",
                                 command=lambda: self._set_mode("dqn"),
                                 font=tkfont.Font(family="Helvetica",size=11,weight="bold"),
                                 relief="flat", cursor="hand2",
                                 padx=14, pady=5)
        self.dqn_btn.pack(side="left", padx=(8,0))

        self._update_toggle_style()

        # ── Left column: canvas ───────────────────────────────────────────────
        left = tk.Frame(outer, bg=BG)
        left.grid(row=1, column=0, sticky="n", padx=(0,16))

        self.canvas = tk.Canvas(left, width=CW, height=CH,
                                bg=OFFGRID_BG, highlightthickness=1,
                                highlightbackground=BORDER_C)
        self.canvas.pack()

        # Stats
        stats = tk.Frame(left, bg=BG)
        stats.pack(fill="x", pady=(8,0))
        self.v_ep     = tk.StringVar(value="Episodes: 0")
        self.v_eps    = tk.StringVar(value="ε = 1.000")
        self.v_act    = tk.StringVar(value="Action: —")
        self.v_rew    = tk.StringVar(value="Reward: —")
        self.v_tot    = tk.StringVar(value="Episode total: —")
        self.v_extra  = tk.StringVar(value="")   # tabular: Q entries; DQN: loss/buffer
        for v in (self.v_ep, self.v_eps, self.v_act,
                  self.v_rew, self.v_tot, self.v_extra):
            tk.Label(stats, textvariable=v,
                     font=tkfont.Font(family="Helvetica",size=10),
                     bg=BG, fg=MUTED, anchor="w").pack(fill="x")

        # Controls
        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(fill="x", pady=(12,0))
        tk.Label(ctrl, text="Run episodes:",
                 font=tkfont.Font(family="Helvetica",size=10),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(0,4))
        btn_row = tk.Frame(ctrl, bg=BG)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="+1  ▶",
                  command=self._on_step,
                  font=tkfont.Font(family="Helvetica",size=11,weight="bold"),
                  bg=NEUTRAL, fg=TEXT, relief="flat",
                  cursor="hand2", padx=12, pady=6).pack(side="left")
        for n in (10, 100):
            tk.Button(btn_row, text=f"+{n}",
                      command=lambda x=n: self._on_ff(x),
                      font=tkfont.Font(family="Helvetica",size=11),
                      bg=NEUTRAL, fg=TEXT, relief="flat",
                      cursor="hand2", padx=12, pady=6).pack(side="left", padx=(8,0))
        tk.Button(btn_row, text="Reset",
                  command=self._on_reset,
                  font=tkfont.Font(family="Helvetica",size=11),
                  bg="#f0dede", fg=PITFALL_FG, relief="flat",
                  cursor="hand2", padx=12, pady=6).pack(side="right")

        # ── Right column ──────────────────────────────────────────────────────
        right = tk.Frame(outer, bg=BG)
        right.grid(row=1, column=1, sticky="n")

        # Legend
        tk.Label(right, text="Legend",
                 font=tkfont.Font(family="Helvetica",size=12,weight="bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0,6))
        leg = tk.Frame(right, bg=PANEL, highlightthickness=1,
                       highlightbackground=BORDER_C)
        leg.pack(fill="x", pady=(0,10))
        for bg, fg, label, note in [
            (HOME_BG,    HOME_FG,    "★ Home",       f"+{HOME_REWARD:.0f}  terminal"),
            (FOOD_BG,    FOOD_FG,    "◆ Food/Fuel",  f"+{FOOD_REWARD:.0f}  disappears"),
            (HAZARD_BG,  HAZARD_FG,  "! Hazard",     f"{HAZARD_PENALTY:.0f}  continues"),
            (PITFALL_BG, PITFALL_FG, "✕ Pitfall",    f"{PITFALL_PENALTY:.0f}  terminal"),
            (START_BG,   START_FG,   "S Start",      "bottom-left"),
            (OFFGRID_BG, OFFGRID_FG, "  Off-grid",   f"{OFFGRID_PENALTY:.0f}  terminal"),
            (NEUTRAL,    MUTED,      "  Empty",      f"{STEP_PENALTY:.1f}/step"),
        ]:
            r = tk.Frame(leg, bg=PANEL)
            r.pack(fill="x", padx=8, pady=2)
            tk.Frame(r, bg=bg, width=16, height=16).pack(side="left")
            tk.Label(r, text=f"  {label}",
                     font=tkfont.Font(family="Helvetica",size=10,weight="bold"),
                     bg=PANEL, fg=fg, width=16, anchor="w").pack(side="left")
            tk.Label(r, text=note,
                     font=tkfont.Font(family="Helvetica",size=10),
                     bg=PANEL, fg=MUTED).pack(side="left")

        # Mode info panel
        tk.Label(right, text="About this mode",
                 font=tkfont.Font(family="Helvetica",size=12,weight="bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0,6))
        self.info_frame = tk.Frame(right, bg=PANEL, highlightthickness=1,
                                   highlightbackground=BORDER_C,
                                   padx=10, pady=8)
        self.info_frame.pack(fill="x", pady=(0,10))
        self.info_lbl = tk.Label(self.info_frame, text="",
                                 font=tkfont.Font(family="Helvetica",size=10),
                                 bg=PANEL, fg=MUTED, justify="left", anchor="w")
        self.info_lbl.pack(fill="x")
        self._update_info_panel()

        # Formula
        self.formula_var = tk.StringVar()
        note = tk.Frame(outer, bg=NEUTRAL)
        note.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12,0))
        tk.Label(note, textvariable=self.formula_var,
                 font=tkfont.Font(family="Courier",size=10),
                 bg=NEUTRAL, fg=MUTED, pady=5).pack(anchor="w")
        self._update_formula()

    def _update_toggle_style(self):
        if self.mode == "tabular":
            self.tab_btn.config(bg=TAB_ACT, fg="white")
            self.dqn_btn.config(bg=TAB_INACT, fg=TEXT)
        else:
            self.tab_btn.config(bg=TAB_INACT, fg=TEXT)
            self.dqn_btn.config(bg=TAB_ACT, fg="white")

    def _update_info_panel(self):
        if self.mode == "tabular":
            txt = ("State: (col, row, foods_remaining)\n"
                   "Q stored in a dictionary — one entry\n"
                   "per (state, action) pair visited.\n"
                   "Arrows show best action per cell\n"
                   "given current food configuration.")
        else:
            txt = (f"State vector: [col/9, row/9, food×4]\n"
                   f"Network: 6 → 128 → 128 → 4 outputs\n"
                   f"Replay buffer: {TRAIN_START} exp. before training\n"
                   f"Batch size: {BATCH_SIZE}   "
                   f"Target sync: every {TARGET_UPDATE} steps\n"
                   f"Arrows show network's best action.")
        self.info_lbl.config(text=txt)

    def _update_formula(self):
        if self.mode == "tabular":
            self.formula_var.set(
                "  Tabular:  Q(s,a) ← Q(s,a) + α[r + γ·maxQ(s',·) − Q(s,a)]"
                "      α=0.10   γ=0.90")
        else:
            self.formula_var.set(
                "  DQN:  L = MSE( Q(s,a) ,  r + γ·max Q_target(s',·) )    "
                "optimized via Adam   α=0.001   γ=0.90")

    def _set_mode(self, new_mode):
        if self._busy:
            return
        if new_mode == self.mode:
            return
        self.mode = new_mode
        self._update_toggle_style()
        self._update_info_panel()
        self._update_formula()
        self.world.reset()
        self._agent_mode = "start"
        self._redraw()

    # ── Drawing ───────────────────────────────────────────────────────────────
    def _redraw(self):
        self._draw_grid()
        self._draw_stats()

    def _draw_grid(self):
        cv = self.canvas
        cv.delete("all")
        w  = self.world
        ag = self.agent

        mid_x = OX + COLS*CELL//2
        mid_y = OY + ROWS*CELL//2
        for txt, ax, ay in [
            ("off grid", OX//2,              mid_y),
            ("off grid", OX+COLS*CELL+OX//2, mid_y),
            ("off grid", mid_x,              OY//2),
            ("off grid", mid_x,              OY+ROWS*CELL+OY//2),
        ]:
            cv.create_text(ax, ay, text=txt, fill=OFFGRID_FG,
                           font=("Helvetica",8,"italic"))

        for r in range(ROWS):
            for c in range(COLS):
                pos = (c, r)
                x0  = OX + c*CELL;  y0 = OY + r*CELL
                x1  = x0+CELL;      y1 = y0+CELL

                if pos == HOME:
                    bg, fg, sym = HOME_BG, HOME_FG, "⌂"
                elif pos in PITFALLS:
                    bg, fg, sym = PITFALL_BG, PITFALL_FG, "✕"
                elif pos in HAZARDS:
                    bg, fg, sym = HAZARD_BG, HAZARD_FG, "!"
                elif pos in w.foods_left:
                    bg, fg, sym = FOOD_BG, FOOD_FG, "◆"
                elif pos in FOODS and pos not in w.foods_left:
                    bg, fg, sym = NEUTRAL, MUTED, "○"
                elif pos == START:
                    bg, fg, sym = START_BG, START_FG, ""
                else:
                    bg, fg, sym = PANEL, MUTED, ""

                cv.create_rectangle(x0, y0, x1, y1,
                                    fill=bg, outline=GRID_LINE, width=1)
                if sym:
                    cv.create_text(x0+CELL//2, y0+CELL//2-6,
                                   text=sym, fill=fg,
                                   font=("Helvetica",13,"bold"))

                # Best-action arrow
                if pos not in [HOME]+PITFALLS+HAZARDS:
                    q_vals = ag.q_values_for_pos(pos, w.foods_left)
                    if any(v != 0 for v in q_vals.values()):
                        best = max(q_vals, key=q_vals.get)
                        cv.create_text(x0+CELL//2, y0+CELL//2+8,
                                       text=ARROWS[best], fill=MUTED,
                                       font=("Helvetica",11))

                cv.create_text(x1-3, y1-3, text=f"{c},{r}",
                               fill=GRID_LINE, font=("Helvetica",6), anchor="se")

        cv.create_rectangle(OX, OY, OX+COLS*CELL, OY+ROWS*CELL,
                            outline=BORDER_C, width=2, dash=(6,3))

        # Agent
        mode = self._agent_mode
        if mode == "offgrid" and w.off_grid_pos:
            ac, ar = w.off_grid_pos
        else:
            ac, ar = w.pos

        cx  = OX + ac*CELL + CELL//2
        cy  = OY + ar*CELL + CELL//2
        rad = min(CELL//2 - 4, 20)
        cv.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                       fill=AGENT_FILL.get(mode, "#888"),
                       outline=AGENT_RING.get(mode, "#333"), width=2)
        cv.create_text(cx, cy, text=AGENT_LABEL.get(mode, "●"),
                       fill="white", font=("Helvetica",10,"bold"))

    def _draw_stats(self):
        ag = self.agent
        w  = self.world
        hist = self._reward_history[self.mode]

        self.v_ep.set(f"Episodes: {ag.episodes}")
        self.v_eps.set(f"ε = {ag.epsilon:.3f}  "
                       f"({'exploiting' if ag.epsilon <= 0.06 else 'exploring'})")

        if w.last_action:
            intended = ARROWS[w.last_action]
            actual   = ARROWS[w.last_actual] if w.last_actual else "?"
            slip     = "  (slipped!)" if w.last_action != w.last_actual else ""
            self.v_act.set(f"Intended: {intended}  Actual: {actual}{slip}")
        else:
            self.v_act.set("Action: —")

        if w.last_reward is not None:
            self.v_rew.set(f"Last reward: {w.last_reward:+.1f}")
        else:
            self.v_rew.set("Last reward: —")

        if hist:
            self.v_tot.set(f"Last ep total: {hist[-1]:+.1f}   "
                           f"Best: {max(hist):+.1f}   "
                           f"Avg(last 20): {sum(hist[-20:])/len(hist[-20:]):+.1f}")
        else:
            self.v_tot.set("Episode total: —")

        if self.mode == "tabular":
            self.v_extra.set(f"Q-table entries: {len(ag.Q)}")
        else:
            buf = len(ag.buffer)
            loss_txt = f"{ag.last_loss:.4f}" if ag.last_loss is not None else "—"
            status = "warming up..." if buf < TRAIN_START else "training"
            self.v_extra.set(f"Buffer: {buf}/{ag.buffer.buffer.maxlen}  "
                             f"Loss: {loss_txt}  ({status})")

    # ── Animation ─────────────────────────────────────────────────────────────
    def _cancel(self):
        if self._tid is not None:
            self.after_cancel(self._tid)
            self._tid = None

    def _on_step(self):
        if self._busy:
            return
        self._cancel()
        self._busy    = True
        self._ep_total = 0
        self.world.reset()
        self._agent_mode = "start"
        self._redraw()
        self._tid = self.after(MOVE_DELAY, self._tick)

    def _tick(self):
        self._tid = None
        try:
            w  = self.world
            ag = self.agent

            state  = w.state()
            action = ag.choose_action(state)
            reward, done, actual, off_grid = w.step(action)
            next_state = w.state()

            # Agent-specific update
            if self.mode == "tabular":
                ag.update(state, action, reward, next_state, done)
            else:
                ag.push(state, action, reward, next_state, done)
                ag.train_step()

            self._ep_total += reward

            # Display mode
            if off_grid:
                self._agent_mode = "offgrid"
            elif w.pos == HOME:
                self._agent_mode = "home"
            elif w.pos in PITFALLS:
                self._agent_mode = "pitfall"
            elif w.pos in HAZARDS:
                self._agent_mode = "hazard"
            elif reward > 0:
                self._agent_mode = "food"
            else:
                self._agent_mode = "move"

            self._redraw()

            if done:
                ag.end_episode()
                self._reward_history[self.mode].append(self._ep_total)
                self._draw_stats()
                self._busy = False
            else:
                self._tid = self.after(MOVE_DELAY, self._tick)

        except Exception:
            import traceback
            traceback.print_exc()
            self._busy = False

    def _on_ff(self, n):
        if self._busy:
            return
        rewards = self.agent.run_n_episodes(self.world, n)
        self._reward_history[self.mode].extend(rewards)
        self.world.reset()
        self._agent_mode = "start"
        self._redraw()

    def _on_reset(self):
        self._cancel()
        self._busy = False
        if self.mode == "tabular":
            self.tab_agent = TabularAgent()
        else:
            self.dqn_agent = DQNAgent()
        self._reward_history[self.mode] = []
        self.world.reset()
        self._agent_mode = "start"
        self._redraw()


if __name__ == "__main__":
    App().mainloop()
