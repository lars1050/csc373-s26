"""
Animation test — 3x2 grid, Reset + Start buttons only.
"""
import tkinter as tk
import random

COLS, ROWS = 3, 2
GOAL       = (2, 0)
TRAP       = (2, 1)
TERMINALS  = {GOAL, TRAP}
NON_TERM   = [(c,r) for r in range(ROWS) for c in range(COLS) if (c,r) not in TERMINALS]
DELTAS     = {"U":(0,-1), "D":(0,1), "L":(-1,0), "R":(1,0)}

CELL  = 120
OX    = CELL   # one-cell off-grid border on each side
OY    = CELL
CW    = (COLS + 2) * CELL
CH    = (ROWS + 2) * CELL

MOVE_DELAY  = 200   # ms between moves
HOLD_DELAY  = 1500  # ms to hold on final state

# colours
C_BG       = "#F5F4F0"
C_OFFGRID  = "#DEDAD2"
C_PANEL    = "#FFFFFF"
C_BORDER   = "#C0BDB5"
C_GRIDLINE = "#D0CEC6"
C_GOAL_BG  = "#D8EEC8"
C_GOAL_FG  = "#2D5A0E"
C_TRAP_BG  = "#F5D5D5"
C_TRAP_FG  = "#8B1A1A"
C_MUTED    = "#888480"

AGENT_FILL = {"idle":"#F0A500", "move":"#3080CC", "goal":"#2D7A1F", "trap":"#CC2222", "offgrid":"#CC2222"}
AGENT_TEXT = {"idle":"S",       "move":"●",        "goal":"★",        "trap":"✕",        "offgrid":"✕"}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grid Animation Test")
        self.resizable(False, False)
        self.configure(bg=C_BG)

        self.pos    = None   # current (col, row) of agent; None = not placed
        self.mode   = None   # idle / move / goal / trap / offgrid
        self.off_pos = None  # (col,row) attempted when off-grid
        self._tid   = None   # pending after() id

        self._build()
        self._do_reset()

    def _build(self):
        self.canvas = tk.Canvas(self, width=CW, height=CH,
                                bg=C_OFFGRID, highlightthickness=0)
        self.canvas.pack(padx=16, pady=(16, 8))

        self.status = tk.Label(self, text="", font=("Helvetica", 12),
                               bg=C_BG, fg=C_MUTED)
        self.status.pack()

        btn_row = tk.Frame(self, bg=C_BG)
        btn_row.pack(pady=(8, 16))

        self.reset_btn = tk.Button(btn_row, text="Reset",
                                   command=self._do_reset,
                                   font=("Helvetica", 12, "bold"),
                                   bg="#E8E0D0", fg="#333", relief="flat",
                                   padx=20, pady=8, cursor="hand2")
        self.reset_btn.pack(side="left", padx=(0, 12))

        self.start_btn = tk.Button(btn_row, text="Start",
                                   command=self._do_start,
                                   font=("Helvetica", 12, "bold"),
                                   bg="#1A1A18", fg="white", relief="flat",
                                   padx=20, pady=8, cursor="hand2")
        self.start_btn.pack(side="left")

    # ── Actions ───────────────────────────────────────────────────────────────
    def _do_reset(self):
        self._cancel()
        self.pos     = random.choice(NON_TERM)
        self.mode    = "idle"
        self.off_pos = None
        self.start_btn.config(state="normal")
        self.status.config(text=f"Agent placed at {self.pos}. Press Start.")
        self._draw()

    def _do_start(self):
        if self.pos is None or self.mode not in ("idle", None):
            return
        self.start_btn.config(state="disabled")
        self._schedule_move()

    def _schedule_move(self):
        self._tid = self.after(MOVE_DELAY, self._move)

    def _move(self):
        self._tid = None
        action = random.choice(list(DELTAS))
        dc, dr = DELTAS[action]
        nc, nr = self.pos[0] + dc, self.pos[1] + dr
        off    = not (0 <= nc < COLS and 0 <= nr < ROWS)

        if off:
            self.off_pos = (nc, nr)
            # clamp draw position to one cell outside the grid
            draw_c = max(-1, min(COLS, nc))
            draw_r = max(-1, min(ROWS, nr))
            self.off_pos = (draw_c, draw_r)
            self.mode    = "offgrid"
            self.status.config(text=f"Moved {action} → off grid!  Reward = −1")
            self._draw()
            # episode done — wait, then re-enable reset
            self._tid = self.after(HOLD_DELAY, self._episode_done)

        elif (nc, nr) in TERMINALS:
            self.pos  = (nc, nr)
            self.mode = "goal" if self.pos == GOAL else "trap"
            reward    = 5 if self.pos == GOAL else -5
            label     = "GOAL" if self.pos == GOAL else "TRAP"
            self.status.config(text=f"Moved {action} → {label}!  Reward = {reward:+d}")
            self._draw()
            self._tid = self.after(HOLD_DELAY, self._episode_done)

        else:
            self.pos  = (nc, nr)
            self.mode = "move"
            self.status.config(text=f"Moved {action} → {self.pos}")
            self._draw()
            self._schedule_move()

    def _episode_done(self):
        self._tid = None
        self.status.config(text=self.status.cget("text") + "   Press Reset to go again.")
        self.start_btn.config(state="disabled")

    def _cancel(self):
        if self._tid is not None:
            self.after_cancel(self._tid)
            self._tid = None
        self.mode = None

    # ── Drawing ───────────────────────────────────────────────────────────────
    def _draw(self):
        cv = self.canvas
        cv.delete("all")

        # Grid cells
        for r in range(ROWS):
            for c in range(COLS):
                s  = (c, r)
                x0 = OX + c*CELL;  y0 = OY + r*CELL
                x1 = x0 + CELL;    y1 = y0 + CELL
                fill = C_GOAL_BG if s==GOAL else (C_TRAP_BG if s==TRAP else C_PANEL)
                cv.create_rectangle(x0, y0, x1, y1,
                                    fill=fill, outline=C_GRIDLINE, width=1)
                if s == GOAL:
                    cv.create_text(x0+CELL//2, y0+CELL//2-10, text="GOAL",
                                   fill=C_GOAL_FG, font=("Helvetica",10,"bold"))
                    cv.create_text(x0+CELL//2, y0+CELL//2+12, text="+5",
                                   fill=C_GOAL_FG, font=("Helvetica",16,"bold"))
                elif s == TRAP:
                    cv.create_text(x0+CELL//2, y0+CELL//2-10, text="TRAP",
                                   fill=C_TRAP_FG, font=("Helvetica",10,"bold"))
                    cv.create_text(x0+CELL//2, y0+CELL//2+12, text="−5",
                                   fill=C_TRAP_FG, font=("Helvetica",16,"bold"))
                else:
                    cv.create_text(x1-6, y1-6, text=f"({c},{r})",
                                   fill=C_GRIDLINE, font=("Helvetica",8), anchor="se")

        # Dashed border around valid grid
        cv.create_rectangle(OX, OY, OX+COLS*CELL, OY+ROWS*CELL,
                            outline=C_BORDER, width=2, dash=(8, 4))

        # Off-grid zone labels
        mid_x = OX + COLS*CELL // 2
        mid_y = OY + ROWS*CELL // 2
        for txt, ax, ay in [
            ("off grid", OX//2,                mid_y),
            ("off grid", OX+COLS*CELL+OX//2,   mid_y),
            ("off grid", mid_x,                OY//2),
            ("off grid", mid_x,                OY+ROWS*CELL+OY//2),
        ]:
            cv.create_text(ax, ay, text=txt, fill=C_MUTED,
                           font=("Helvetica", 9, "italic"))

        # Agent
        if self.mode == "offgrid" and self.off_pos:
            ac, ar = self.off_pos
        elif self.pos:
            ac, ar = self.pos
        else:
            return

        cx  = OX + ac*CELL + CELL//2
        cy  = OY + ar*CELL + CELL//2
        rad = 26
        fill = AGENT_FILL.get(self.mode, "#888")
        txt  = AGENT_TEXT.get(self.mode, "?")
        cv.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                       fill=fill, outline="white", width=3)
        cv.create_text(cx, cy, text=txt, fill="white",
                       font=("Helvetica", 14, "bold"))


if __name__ == "__main__":
    App().mainloop()
