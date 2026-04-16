"""
dqn_simple.py  —  Simple DQN Educational Demo
===============================================
4×4 grid world. One goal (+5), one trap (-5), off-grid = -1.
Deterministic transitions. No food, no hazards.

Two phases:
  TRAINING  — epsilon decays, network learns, loss tracked
  TESTING   — epsilon = 0, pure exploitation, no weight updates

Network diagram drawn in the UI so students can see the architecture.
Loss curve shown as training progresses.

Run:  python dqn_simple.py
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import math
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

# ── World ─────────────────────────────────────────────────────────────────────
COLS, ROWS  = 4, 4
GOAL        = (3, 0)   # top-right   +5 terminal
TRAP        = (3, 3)   # bottom-right -5 terminal
START       = (0, 3)   # bottom-left
TERMINALS   = {GOAL: +5.0, TRAP: -5.0}
ACTIONS     = ["U", "D", "L", "R"]
DELTAS      = {"U":(0,-1), "D":(0,1), "L":(-1,0), "R":(1,0)}
ARROWS      = {"U":"↑", "D":"↓", "L":"←", "R":"→"}
OFF_REWARD  = -1.0
STEP_REWARD = -0.1

# ── DQN Hyperparameters ───────────────────────────────────────────────────────
LR            = 0.001
GAMMA         = 0.90
EPS_START     = 1.00
EPS_MIN       = 0.05
EPS_DECAY     = 0.97    # faster decay — small world converges quickly
BUFFER_SIZE   = 2_000
BATCH_SIZE    = 32
TARGET_UPDATE = 20      # steps between target net syncs
TRAIN_START   = 50      # fill buffer before training

# ── Colours ───────────────────────────────────────────────────────────────────
BG          = "#F7F6F2"
PANEL       = "#FFFFFF"
BORDER      = "#D4D2CA"
TEXT        = "#1A1918"
MUTED       = "#6B6A66"
NEUTRAL     = "#EEEDE9"
GRID_LINE   = "#E2E0DA"
OFFGRID_BG  = "#E4E2DA"
OFFGRID_FG  = "#AEACA6"

GOAL_BG     = "#D6ECC4";  GOAL_FG  = "#2A5A0A"
TRAP_BG     = "#F2D4D4";  TRAP_FG  = "#8A1A1A"
START_BG    = "#DCE8FC";  START_FG = "#1A3A8A"

TRAIN_ACTIVE = "#1A1918"
TEST_ACTIVE  = "#1A6B3A"

AGENT_FILL  = {"start":"#E09800","move":"#2878CC",
               "goal":"#2A7A1A","trap":"#CC2020","offgrid":"#CC2020"}
AGENT_RING  = {"start":"#805500","move":"#0A3E8A",
               "goal":"#144A0A","trap":"#6A1010","offgrid":"#6A1010"}
AGENT_LABEL = {"start":"S","move":"●","goal":"★","trap":"✕","offgrid":"✕"}

# Node colours for network diagram
NN_INPUT_C  = "#BDD4F0"
NN_HIDDEN_C = "#C8E6C9"
NN_OUTPUT_C = "#FFE0B2"
NN_LINE_C   = "#CCCCCC"
NN_ACT_C    = "#FF7043"   # highlighted active neuron

def lerp(c1, c2, t):
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t))


# ── Network ───────────────────────────────────────────────────────────────────
class QNet(nn.Module):
    """2 inputs → 16 → 16 → 4 outputs"""
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(2, 16)
        self.fc2 = nn.Linear(16, 16)
        self.fc3 = nn.Linear(16, 4)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


# ── Replay Buffer ─────────────────────────────────────────────────────────────
class ReplayBuffer:
    def __init__(self, cap):
        self.buf = deque(maxlen=cap)

    def push(self, s, a, r, ns, done):
        self.buf.append((s, a, r, ns, done))

    def sample(self, n):
        return random.sample(self.buf, n)

    def __len__(self):
        return len(self.buf)


# ── DQN Agent ─────────────────────────────────────────────────────────────────
class DQNAgent:
    def __init__(self):
        self.reset()

    def reset(self):
        self.policy  = QNet()
        self.target  = QNet()
        self.target.load_state_dict(self.policy.state_dict())
        self.target.eval()
        self.opt     = optim.Adam(self.policy.parameters(), lr=LR)
        self.buf     = ReplayBuffer(BUFFER_SIZE)
        self.epsilon = EPS_START
        self.episodes= 0
        self.steps   = 0
        self.loss_history = []   # for loss curve
        self.last_loss    = None
        self.last_q_vals  = None  # for network diagram highlighting

    def encode(self, col, row):
        return torch.tensor([col / (COLS-1), row / (ROWS-1)],
                            dtype=torch.float32)

    def q_values(self, col, row):
        with torch.no_grad():
            q = self.policy(self.encode(col, row).unsqueeze(0)).squeeze(0)
        self.last_q_vals = q.tolist()
        return {a: self.last_q_vals[i] for i, a in enumerate(ACTIONS)}

    def choose_action(self, col, row, force_greedy=False):
        if not force_greedy and random.random() < self.epsilon:
            return random.choice(ACTIONS)
        q = self.q_values(col, row)
        return max(q, key=q.get)

    def push(self, col, row, action, reward, nc, nr, done):
        self.buf.push(
            self.encode(col, row),
            ACTIONS.index(action),
            reward,
            self.encode(nc, nr),
            float(done)
        )

    def train_step(self):
        if len(self.buf) < TRAIN_START:
            return
        batch   = self.buf.sample(BATCH_SIZE)
        states  = torch.stack([b[0] for b in batch])
        actions = torch.tensor([b[1] for b in batch], dtype=torch.long)
        rewards = torch.tensor([b[2] for b in batch], dtype=torch.float32)
        nstates = torch.stack([b[3] for b in batch])
        dones   = torch.tensor([b[4] for b in batch], dtype=torch.float32)

        cur_q   = self.policy(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            max_nq  = self.target(nstates).max(1)[0]
            tgt_q   = rewards + GAMMA * max_nq * (1 - dones)

        loss = nn.MSELoss()(cur_q, tgt_q)
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

        self.steps    += 1
        self.last_loss = loss.item()
        self.loss_history.append(loss.item())

        if self.steps % TARGET_UPDATE == 0:
            self.target.load_state_dict(self.policy.state_dict())

    def end_episode(self, training=True):
        self.episodes += 1
        if training:
            self.epsilon = max(EPS_MIN, self.epsilon * EPS_DECAY)

    def run_n(self, n):
        """Run n training episodes silently."""
        for _ in range(n):
            col, row = START
            done = False
            while not done:
                a = self.choose_action(col, row)
                dc, dr = DELTAS[a]
                nc, nr = col+dc, row+dr
                off = not (0 <= nc < COLS and 0 <= nr < ROWS)
                if off:
                    r, done = OFF_REWARD, True
                    nc, nr  = col, row
                else:
                    r    = TERMINALS.get((nc, nr), STEP_REWARD)
                    done = (nc, nr) in TERMINALS
                self.push(col, row, a, r, nc, nr, done)
                self.train_step()
                col, row = nc, nr
            self.end_episode()


# ── App ───────────────────────────────────────────────────────────────────────
CELL         = 90
BORDER_CELLS = 1
MOVE_DELAY   = 250
OX = BORDER_CELLS * CELL
OY = BORDER_CELLS * CELL
CW = (COLS + 2*BORDER_CELLS) * CELL
CH = (ROWS + 2*BORDER_CELLS) * CELL

# Loss curve dimensions
CURVE_W = 260
CURVE_H = 80

# Network diagram dimensions
NET_W   = 260
NET_H   = 200

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DQN — Simple 4×4 Grid")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.agent      = DQNAgent()
        self.phase      = "training"   # "training" or "testing"
        self._tid       = None
        self._busy      = False
        self._amode     = "start"
        self._pos       = list(START)
        self._off_pos   = None
        self._ep_total  = 0

        self._build_ui()
        self._redraw()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self, bg=BG, padx=18, pady=14)
        outer.pack()

        # Title
        hdr = tk.Frame(outer, bg=BG)
        hdr.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,12))
        tk.Label(hdr, text="DQN Demo",
                 font=tkfont.Font(family="Helvetica",size=17,weight="bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hdr, text="  —  4×4 Grid World  —  Training & Testing",
                 font=tkfont.Font(family="Helvetica",size=12),
                 bg=BG, fg=MUTED).pack(side="left", pady=(3,0))

        # ── Col 0: grid ───────────────────────────────────────────────────────
        left = tk.Frame(outer, bg=BG)
        left.grid(row=1, column=0, sticky="n", padx=(0,16))

        self.canvas = tk.Canvas(left, width=CW, height=CH,
                                bg=OFFGRID_BG, highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack()

        # Phase toggle
        phase_row = tk.Frame(left, bg=BG)
        phase_row.pack(fill="x", pady=(10,0))
        tk.Label(phase_row, text="Phase:",
                 font=tkfont.Font(family="Helvetica",size=10),
                 bg=BG, fg=MUTED).pack(side="left")
        self.train_btn = tk.Button(phase_row, text="Training",
                                   command=lambda: self._set_phase("training"),
                                   font=tkfont.Font(family="Helvetica",size=10,weight="bold"),
                                   relief="flat", cursor="hand2", padx=10, pady=4)
        self.train_btn.pack(side="left", padx=(6,0))
        self.test_btn = tk.Button(phase_row, text="Testing",
                                  command=lambda: self._set_phase("testing"),
                                  font=tkfont.Font(family="Helvetica",size=10,weight="bold"),
                                  relief="flat", cursor="hand2", padx=10, pady=4)
        self.test_btn.pack(side="left", padx=(6,0))
        self._update_phase_btns()

        # Stats
        stats = tk.Frame(left, bg=BG)
        stats.pack(fill="x", pady=(8,0))
        self.v_ep    = tk.StringVar(value="Episodes: 0")
        self.v_eps   = tk.StringVar(value="ε = 1.000")
        self.v_phase = tk.StringVar(value="Phase: Training  (learning ON)")
        self.v_act   = tk.StringVar(value="Action: —")
        self.v_rew   = tk.StringVar(value="Reward: —")
        self.v_loss  = tk.StringVar(value="Loss: —")
        self.v_buf   = tk.StringVar(value="Buffer: 0")
        for v in (self.v_phase, self.v_ep, self.v_eps,
                  self.v_act, self.v_rew, self.v_loss, self.v_buf):
            tk.Label(stats, textvariable=v,
                     font=tkfont.Font(family="Helvetica",size=10),
                     bg=BG, fg=MUTED, anchor="w").pack(fill="x")

        # Controls
        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(fill="x", pady=(10,0))
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
                  bg="#f0dede", fg=TRAP_FG, relief="flat",
                  cursor="hand2", padx=12, pady=6).pack(side="right")

        # ── Col 1: network diagram ────────────────────────────────────────────
        mid = tk.Frame(outer, bg=BG)
        mid.grid(row=1, column=1, sticky="n", padx=(0,16))

        tk.Label(mid, text="Network  (policy)",
                 font=tkfont.Font(family="Helvetica",size=11,weight="bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0,6))
        self.net_canvas = tk.Canvas(mid, width=NET_W, height=NET_H,
                                    bg=PANEL, highlightthickness=1,
                                    highlightbackground=BORDER)
        self.net_canvas.pack()

        # Network legend
        net_leg = tk.Frame(mid, bg=BG)
        net_leg.pack(anchor="w", pady=(6,0))
        for col, lbl in [(NN_INPUT_C,"Input"),(NN_HIDDEN_C,"Hidden"),
                         (NN_OUTPUT_C,"Output"),(NN_ACT_C,"Best action")]:
            tk.Frame(net_leg, bg=col, width=12, height=12).pack(side="left")
            tk.Label(net_leg, text=f" {lbl}   ",
                     font=tkfont.Font(family="Helvetica",size=9),
                     bg=BG, fg=MUTED).pack(side="left")

        # Input encoding explanation
        enc = tk.Frame(mid, bg=PANEL, highlightthickness=1,
                       highlightbackground=BORDER, padx=8, pady=6)
        enc.pack(fill="x", pady=(10,0))
        tk.Label(enc, text="State encoding",
                 font=tkfont.Font(family="Helvetica",size=10,weight="bold"),
                 bg=PANEL, fg=TEXT).pack(anchor="w")
        tk.Label(enc, text="input[0] = col / 3\ninput[1] = row / 3\n\n"
                           "Output = Q-value for\neach of 4 actions",
                 font=tkfont.Font(family="Courier",size=9),
                 bg=PANEL, fg=MUTED, justify="left").pack(anchor="w")

        # ── Col 2: loss curve + legend ────────────────────────────────────────
        right = tk.Frame(outer, bg=BG)
        right.grid(row=1, column=2, sticky="n")

        tk.Label(right, text="Training loss",
                 font=tkfont.Font(family="Helvetica",size=11,weight="bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(0,6))
        self.curve_canvas = tk.Canvas(right, width=CURVE_W, height=CURVE_H,
                                      bg=PANEL, highlightthickness=1,
                                      highlightbackground=BORDER)
        self.curve_canvas.pack()

        # Legend
        tk.Label(right, text="Legend",
                 font=tkfont.Font(family="Helvetica",size=11,weight="bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(12,6))
        leg = tk.Frame(right, bg=PANEL, highlightthickness=1,
                       highlightbackground=BORDER)
        leg.pack(fill="x")
        for bg_, fg_, lbl, note in [
            (GOAL_BG,    GOAL_FG,    "★ Goal",    "+5  terminal"),
            (TRAP_BG,    TRAP_FG,    "✕ Trap",    "−5  terminal"),
            (START_BG,   START_FG,   "S  Start",  "bottom-left"),
            (OFFGRID_BG, OFFGRID_FG, "   Off-grid","−1  terminal"),
            (NEUTRAL,    MUTED,      "   Empty",  "−0.1/step"),
        ]:
            r = tk.Frame(leg, bg=PANEL)
            r.pack(fill="x", padx=8, pady=2)
            tk.Frame(r, bg=bg_, width=14, height=14).pack(side="left")
            tk.Label(r, text=f"  {lbl}",
                     font=tkfont.Font(family="Helvetica",size=10,weight="bold"),
                     bg=PANEL, fg=fg_, width=10, anchor="w").pack(side="left")
            tk.Label(r, text=note,
                     font=tkfont.Font(family="Helvetica",size=10),
                     bg=PANEL, fg=MUTED).pack(side="left")

        # Formula
        note = tk.Frame(outer, bg=NEUTRAL)
        note.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(14,0))
        tk.Label(note,
                 text="  Training:  L = MSE( Q_policy(s,a),  r + γ · max Q_target(s',·) )"
                      "      γ=0.90   α=0.001   batch=32   target sync every 20 steps",
                 font=tkfont.Font(family="Courier",size=10),
                 bg=NEUTRAL, fg=MUTED, pady=6).pack(anchor="w")
        tk.Label(note,
                 text="  Testing:   ε = 0  →  always picks argmax Q(s,·)   "
                      "no weight updates",
                 font=tkfont.Font(family="Courier",size=10),
                 bg=NEUTRAL, fg=MUTED, pady=6).pack(anchor="w", pady=(0,6))

    def _update_phase_btns(self):
        if self.phase == "training":
            self.train_btn.config(bg=TRAIN_ACTIVE, fg="white")
            self.test_btn.config(bg=NEUTRAL, fg=TEXT)
        else:
            self.train_btn.config(bg=NEUTRAL, fg=TEXT)
            self.test_btn.config(bg=TEST_ACTIVE, fg="white")

    def _set_phase(self, p):
        if self._busy:
            return
        self.phase = p
        self._update_phase_btns()
        self._pos = list(START)
        self._amode = "start"
        self._off_pos = None
        self._redraw()

    # ── Drawing ───────────────────────────────────────────────────────────────
    def _redraw(self):
        self._draw_grid()
        self._draw_network()
        self._draw_curve()
        self._draw_stats()

    def _draw_grid(self):
        cv = self.canvas
        cv.delete("all")
        col, row = self._pos

        # Off-grid labels
        mx = OX + COLS*CELL//2
        my = OY + ROWS*CELL//2
        for txt, ax, ay in [
            ("off grid", OX//2,              my),
            ("off grid", OX+COLS*CELL+OX//2, my),
            ("off grid", mx,                 OY//2),
            ("off grid", mx,                 OY+ROWS*CELL+OY//2),
        ]:
            cv.create_text(ax, ay, text=txt, fill=OFFGRID_FG,
                           font=("Helvetica",9,"italic"))

        for r in range(ROWS):
            for c in range(COLS):
                pos = (c, r)
                x0  = OX + c*CELL;  y0 = OY + r*CELL
                x1  = x0+CELL;      y1 = y0+CELL

                if pos == GOAL:
                    bg_, fg_, sym = GOAL_BG, GOAL_FG, "★"
                elif pos == TRAP:
                    bg_, fg_, sym = TRAP_BG, TRAP_FG, "✕"
                elif pos == START:
                    bg_, fg_, sym = START_BG, START_FG, ""
                else:
                    bg_, fg_, sym = PANEL, MUTED, ""

                cv.create_rectangle(x0, y0, x1, y1,
                                    fill=bg_, outline=GRID_LINE, width=1)

                if sym:
                    cv.create_text(x0+CELL//2, y0+CELL//2-8,
                                   text=sym, fill=fg_,
                                   font=("Helvetica",18,"bold"))
                    reward_txt = "+5" if pos==GOAL else "−5"
                    cv.create_text(x0+CELL//2, y0+CELL//2+14,
                                   text=reward_txt, fill=fg_,
                                   font=("Helvetica",12,"bold"))

                # Best action arrow
                if pos not in TERMINALS:
                    q = self.agent.q_values(c, r)
                    if any(v != 0 for v in q.values()):
                        best = max(q, key=q.get)
                        cv.create_text(x0+CELL//2, y0+CELL//2+10,
                                       text=ARROWS[best], fill=MUTED,
                                       font=("Helvetica",16))

                cv.create_text(x1-4, y1-4, text=f"{c},{r}",
                               fill=GRID_LINE, font=("Helvetica",7), anchor="se")

        # Dashed boundary
        cv.create_rectangle(OX, OY, OX+COLS*CELL, OY+ROWS*CELL,
                            outline=BORDER, width=2, dash=(6,3))

        # Agent
        mode = self._amode
        if mode == "offgrid" and self._off_pos:
            ac, ar = self._off_pos
        else:
            ac, ar = self._pos

        cx  = OX + ac*CELL + CELL//2
        cy  = OY + ar*CELL + CELL//2
        rad = 24
        cv.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                       fill=AGENT_FILL.get(mode,"#888"),
                       outline=AGENT_RING.get(mode,"#333"), width=2)
        cv.create_text(cx, cy, text=AGENT_LABEL.get(mode,"●"),
                       fill="white", font=("Helvetica",14,"bold"))

    def _draw_network(self):
        """Draw the network architecture with current activation highlighted."""
        cv  = self.net_canvas
        cv.delete("all")
        W, H = NET_W, NET_H

        # Layer x positions
        layers = [
            {"x": 40,  "n": 2,  "col": NN_INPUT_C,  "labels": ["col/3","row/3"]},
            {"x": 120, "n": 6,  "col": NN_HIDDEN_C, "labels": None},   # show 6 of 16
            {"x": 200, "n": 6,  "col": NN_HIDDEN_C, "labels": None},
            {"x": 280, "n": 4,  "col": NN_OUTPUT_C,
             "labels": ["U","D","L","R"]},
        ]
        # Clamp canvas — network diagram is inside NET_W
        # Reposition layers to fit NET_W=260
        xs = [30, 95, 160, 225]
        for i, l in enumerate(layers):
            l["x"] = xs[i]

        node_r = 10
        spacing = 22

        # Get current Q values for output highlighting
        q_vals = None
        if self.agent.last_q_vals:
            q_vals = self.agent.last_q_vals
            best_idx = q_vals.index(max(q_vals))
        else:
            best_idx = -1

        # Precompute node y positions
        def node_ys(n):
            total = (n-1)*spacing
            return [H//2 - total//2 + i*spacing for i in range(n)]

        all_ys = [node_ys(l["n"]) for l in layers]

        # Draw connections (before nodes so nodes sit on top)
        for li in range(len(layers)-1):
            for y1 in all_ys[li]:
                for y2 in all_ys[li+1]:
                    cv.create_line(layers[li]["x"]+node_r, y1,
                                   layers[li+1]["x"]-node_r, y2,
                                   fill=NN_LINE_C, width=1)

        # Draw nodes
        for li, layer in enumerate(layers):
            ys = all_ys[li]
            for ni, y in enumerate(ys):
                x = layer["x"]
                is_best = (li == len(layers)-1 and ni == best_idx and q_vals)
                fill = NN_ACT_C if is_best else layer["col"]
                cv.create_oval(x-node_r, y-node_r, x+node_r, y+node_r,
                               fill=fill, outline=BORDER, width=1)
                if layer["labels"]:
                    lbl = layer["labels"][ni]
                    cv.create_text(x, y, text=lbl,
                                   fill=TEXT if not is_best else "white",
                                   font=("Helvetica",7,"bold"))

                # Q value labels on output nodes
                if li == len(layers)-1 and q_vals:
                    val = q_vals[ni]
                    cv.create_text(x + node_r + 18, y,
                                   text=f"{val:+.2f}",
                                   fill=GOAL_FG if val>0 else (TRAP_FG if val<0 else MUTED),
                                   font=("Helvetica",8))

        # "..." indicators for hidden layers (16 nodes shown as 6)
        for li in [1, 2]:
            x = layers[li]["x"]
            cv.create_text(x, H - 14, text="(16 nodes)",
                           fill=MUTED, font=("Helvetica",7,"italic"))

        # Layer labels at top
        for li, lbl in enumerate(["Input\n(2)","Hidden\n(16)","Hidden\n(16)","Output\n(4)"]):
            cv.create_text(layers[li]["x"], 10, text=lbl.split("\n")[0],
                           fill=MUTED, font=("Helvetica",8))

    def _draw_curve(self):
        cv = self.curve_canvas
        cv.delete("all")
        hist = self.agent.loss_history
        W, H = CURVE_W, CURVE_H
        pad  = 8

        if len(hist) < 2:
            cv.create_text(W//2, H//2, text="Loss will appear after training starts",
                           fill=MUTED, font=("Helvetica",9,"italic"))
            return

        # Smooth with rolling average
        window = max(1, len(hist)//40)
        smoothed = []
        for i in range(len(hist)):
            lo = max(0, i-window)
            smoothed.append(sum(hist[lo:i+1])/(i+1-lo))

        max_v = max(smoothed) or 1.0
        min_v = min(smoothed)
        rng   = max_v - min_v or 1.0

        pts = []
        for i, v in enumerate(smoothed):
            x = pad + (i / (len(smoothed)-1)) * (W - 2*pad)
            y = H - pad - ((v - min_v) / rng) * (H - 2*pad)
            pts.append((x, y))

        # Axes
        cv.create_line(pad, pad, pad, H-pad, fill=BORDER, width=1)
        cv.create_line(pad, H-pad, W-pad, H-pad, fill=BORDER, width=1)

        # Curve
        if len(pts) > 1:
            flat = [coord for pt in pts for coord in pt]
            cv.create_line(*flat, fill="#3080CC", width=2, smooth=True)

        # Labels
        cv.create_text(pad+2, pad+2, text=f"{max_v:.3f}",
                       fill=MUTED, font=("Helvetica",7), anchor="nw")
        cv.create_text(pad+2, H-pad-2, text=f"{min_v:.3f}",
                       fill=MUTED, font=("Helvetica",7), anchor="sw")
        cv.create_text(W-pad, H-pad+2, text=f"{len(hist)} steps",
                       fill=MUTED, font=("Helvetica",7), anchor="ne")

    def _draw_stats(self):
        ag = self.agent
        self.v_ep.set(f"Episodes: {ag.episodes}")
        if self.phase == "training":
            self.v_eps.set(f"ε = {ag.epsilon:.3f}  (exploring → exploiting)")
            self.v_phase.set("Phase: Training  —  learning ON,  ε-greedy")
        else:
            self.v_eps.set("ε = 0.000  (pure exploitation)")
            self.v_phase.set("Phase: Testing  —  learning OFF,  greedy only")
        if ag.last_loss is not None:
            self.v_loss.set(f"Loss: {ag.last_loss:.4f}")
        else:
            status = f"warming up ({len(ag.buf)}/{TRAIN_START})" if len(ag.buf)<TRAIN_START else "—"
            self.v_loss.set(f"Loss: {status}")
        self.v_buf.set(f"Replay buffer: {len(ag.buf)} experiences")

    # ── Controls ─────────────────────────────────────────────────────────────
    def _cancel(self):
        if self._tid is not None:
            self.after_cancel(self._tid)
            self._tid = None

    def _on_step(self):
        if self._busy:
            return
        self._cancel()
        self._busy    = True
        self._pos     = list(START)
        self._amode   = "start"
        self._off_pos = None
        self._ep_total= 0
        self._redraw()
        self._tid = self.after(MOVE_DELAY, self._tick)

    def _tick(self):
        self._tid = None
        try:
            col, row = self._pos
            training = (self.phase == "training")
            action   = self.agent.choose_action(col, row, force_greedy=not training)

            dc, dr = DELTAS[action]
            nc, nr = col+dc, row+dr
            off    = not (0 <= nc < COLS and 0 <= nr < ROWS)

            if off:
                reward, done = OFF_REWARD, True
                self._off_pos = (max(-1,min(COLS,nc)), max(-1,min(ROWS,nr)))
                self._amode   = "offgrid"
                nc, nr        = col, row
            else:
                reward = TERMINALS.get((nc,nr), STEP_REWARD)
                done   = (nc,nr) in TERMINALS
                self._off_pos = None
                if (nc,nr) == GOAL:    self._amode = "goal"
                elif (nc,nr) == TRAP:  self._amode = "trap"
                else:                  self._amode = "move"

            if training:
                self.agent.push(col, row, action, reward, nc, nr, done)
                self.agent.train_step()

            # Update action display
            self.v_act.set(f"Action: {ARROWS[action]} {action}   "
                           f"Reward: {reward:+.1f}"
                           + ("  (no learning)" if not training else ""))
            self.v_rew.set(f"Position: ({col},{row}) → ({nc},{nr})")

            self._pos = [nc, nr]
            self._ep_total += reward
            self._redraw()

            if done:
                if training:
                    self.agent.end_episode(training=True)
                else:
                    self.agent.end_episode(training=False)
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
        if self.phase == "training":
            self.agent.run_n(n)
        # testing fast-forward just resets position — no learning
        self._pos   = list(START)
        self._amode = "start"
        self._off_pos = None
        self._redraw()

    def _on_reset(self):
        self._cancel()
        self._busy  = False
        self.agent  = DQNAgent()
        self._pos   = list(START)
        self._amode = "start"
        self._off_pos = None
        self._ep_total = 0
        self._redraw()


if __name__ == "__main__":
    App().mainloop()
