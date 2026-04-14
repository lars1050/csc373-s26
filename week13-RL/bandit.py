import tkinter as tk
from tkinter import font as tkfont
import random

# ── True reward probabilities, shuffled at start ──────────────────────────────
TRUE_PROBS = [0.60, 0.30, 0.10]

ICONS   = ["7️⃣", "🔔", "🍒"]
LABELS  = ["Lever A", "Lever B", "Lever C"]
COLORS  = {
    "bg":        "#F8F7F4",
    "card":      "#FFFFFF",
    "border":    "#D6D4CC",
    "text":      "#1A1A18",
    "muted":     "#6B6A66",
    "win_bg":    "#EAF3DE",
    "win_fg":    "#3B6D11",
    "lose_bg":   "#FCEBEB",
    "lose_fg":   "#A32D2D",
    "neutral_bg":"#EFEFEC",
    "neutral_fg":"#6B6A66",
    "btn_hover": "#EDEDEA",
    "bar_fill":  "#378ADD",
    "bar_bg":    "#E4E3DF",
}

class BanditApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("One-Armed Bandit")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        self._setup_fonts()
        self._init_game()
        self._build_ui()

    # ── Fonts ─────────────────────────────────────────────────────────────────
    def _setup_fonts(self):
        self.f_title   = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.f_sub     = tkfont.Font(family="Helvetica", size=11)
        self.f_icon    = tkfont.Font(family="Helvetica", size=28)
        self.f_btn     = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.f_result  = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.f_head    = tkfont.Font(family="Helvetica", size=11, weight="bold")
        self.f_cell    = tkfont.Font(family="Helvetica", size=12)
        self.f_reset   = tkfont.Font(family="Helvetica", size=10)

    # ── Game state ────────────────────────────────────────────────────────────
    def _init_game(self):
        self.probs = random.sample(TRUE_PROBS, len(TRUE_PROBS))
        self.pulls = [0, 0, 0]
        self.wins  = [0, 0, 0]

    # ── UI build ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self, bg=COLORS["bg"], padx=24, pady=20)
        outer.pack()

        # Title
        tk.Label(outer, text="One-Armed Bandit", font=self.f_title,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(outer, text="Each lever has a hidden reward probability. Find the best one!",
                 font=self.f_sub, bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(2, 16))

        # Lever buttons
        btn_frame = tk.Frame(outer, bg=COLORS["bg"])
        btn_frame.pack(fill="x", pady=(0, 14))

        self.btn_widgets = []
        for i in range(3):
            col = tk.Frame(btn_frame, bg=COLORS["bg"])
            col.pack(side="left", expand=True, fill="x", padx=(0 if i == 0 else 8, 0))

            card = tk.Frame(col, bg=COLORS["card"], highlightbackground=COLORS["border"],
                            highlightthickness=1, cursor="hand2")
            card.pack(fill="x")

            icon_lbl = tk.Label(card, text=ICONS[i], font=self.f_icon,
                                bg=COLORS["card"], fg=COLORS["text"], pady=8)
            icon_lbl.pack()
            name_lbl = tk.Label(card, text=LABELS[i], font=self.f_btn,
                                bg=COLORS["card"], fg=COLORS["text"])
            name_lbl.pack(pady=(0, 10))

            for widget in (card, icon_lbl, name_lbl):
                widget.bind("<Button-1>", lambda e, idx=i: self._pull(idx))
                widget.bind("<Enter>",    lambda e, c=card, il=icon_lbl, nl=name_lbl: self._hover(c, il, nl, True))
                widget.bind("<Leave>",    lambda e, c=card, il=icon_lbl, nl=name_lbl: self._hover(c, il, nl, False))

            self.btn_widgets.append((card, icon_lbl, name_lbl))

        # Result banner
        self.result_var = tk.StringVar(value="Pick a lever to pull…")
        self.result_lbl = tk.Label(outer, textvariable=self.result_var,
                                   font=self.f_result, bg=COLORS["neutral_bg"],
                                   fg=COLORS["neutral_fg"], pady=10, padx=16,
                                   relief="flat", anchor="center")
        self.result_lbl.pack(fill="x", pady=(0, 16))

        # Stats table
        tk.Label(outer, text="RESULTS", font=tkfont.Font(family="Helvetica", size=9, weight="bold"),
                 bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w")

        tbl_outer = tk.Frame(outer, bg=COLORS["card"], highlightbackground=COLORS["border"],
                             highlightthickness=1)
        tbl_outer.pack(fill="x", pady=(4, 0))
        tbl = tk.Frame(tbl_outer, bg=COLORS["card"], padx=12, pady=10)
        tbl.pack(fill="x")

        headers = ["Lever", "Wins", "Pulls", "Win %", ""]
        col_w   = [90, 50, 50, 55, 120]
        for c, (h, w) in enumerate(zip(headers, col_w)):
            tk.Label(tbl, text=h, font=self.f_head, bg=COLORS["card"],
                     fg=COLORS["muted"], width=w//7, anchor="w").grid(
                         row=0, column=c, sticky="w", padx=(0, 8), pady=(0, 6))

        sep = tk.Frame(tbl, bg=COLORS["border"], height=1)
        sep.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(0, 8))

        self.row_vars = []
        for i in range(3):
            wins_v  = tk.StringVar(value="0")
            pulls_v = tk.StringVar(value="0")
            pct_v   = tk.StringVar(value="—")

            tk.Label(tbl, text=f"{ICONS[i]}  {LABELS[i]}", font=self.f_cell,
                     bg=COLORS["card"], fg=COLORS["text"], anchor="w").grid(
                         row=i+2, column=0, sticky="w", padx=(0, 8), pady=4)
            tk.Label(tbl, textvariable=wins_v, font=self.f_cell,
                     bg=COLORS["card"], fg=COLORS["text"], anchor="w").grid(
                         row=i+2, column=1, sticky="w", padx=(0, 8))
            tk.Label(tbl, textvariable=pulls_v, font=self.f_cell,
                     bg=COLORS["card"], fg=COLORS["text"], anchor="w").grid(
                         row=i+2, column=2, sticky="w", padx=(0, 8))
            tk.Label(tbl, textvariable=pct_v, font=self.f_cell,
                     bg=COLORS["card"], fg=COLORS["text"], anchor="w").grid(
                         row=i+2, column=3, sticky="w", padx=(0, 8))

            # Mini bar canvas
            bar_canvas = tk.Canvas(tbl, width=110, height=10,
                                   bg=COLORS["card"], highlightthickness=0)
            bar_canvas.grid(row=i+2, column=4, sticky="w")

            self.row_vars.append((wins_v, pulls_v, pct_v, bar_canvas))

        # Reset button
        reset_btn = tk.Button(outer, text="Reset & reshuffle probabilities",
                              font=self.f_reset, bg=COLORS["bg"], fg=COLORS["muted"],
                              relief="flat", bd=0, cursor="hand2",
                              activebackground=COLORS["btn_hover"],
                              command=self._reset)
        reset_btn.pack(anchor="e", pady=(12, 0))

    # ── Interactions ──────────────────────────────────────────────────────────
    def _hover(self, card, icon_lbl, name_lbl, entering):
        bg = COLORS["btn_hover"] if entering else COLORS["card"]
        card.configure(bg=bg)
        icon_lbl.configure(bg=bg)
        name_lbl.configure(bg=bg)

    def _pull(self, i):
        self.pulls[i] += 1
        won = random.random() < self.probs[i]
        if won:
            self.wins[i] += 1

        if won:
            self.result_lbl.configure(bg=COLORS["win_bg"], fg=COLORS["win_fg"])
            self.result_var.set(f"{ICONS[i]}  {LABELS[i]} paid out — you won! 🎉")
        else:
            self.result_lbl.configure(bg=COLORS["lose_bg"], fg=COLORS["lose_fg"])
            self.result_var.set(f"{ICONS[i]}  {LABELS[i]} didn't pay out — try again.")

        self._update_table()

    def _update_table(self):
        for i, (wins_v, pulls_v, pct_v, bar_canvas) in enumerate(self.row_vars):
            w = self.wins[i]
            p = self.pulls[i]
            wins_v.set(str(w))
            pulls_v.set(str(p))
            pct = (w / p * 100) if p > 0 else 0
            pct_v.set(f"{pct:.0f}%" if p > 0 else "—")

            bar_canvas.delete("all")
            bar_canvas.create_rectangle(0, 2, 110, 8, fill=COLORS["bar_bg"], outline="")
            if p > 0:
                bar_canvas.create_rectangle(0, 2, int(pct / 100 * 110), 8,
                                            fill=COLORS["bar_fill"], outline="")

    def _reset(self):
        self._init_game()
        self.result_var.set("Pick a lever to pull…")
        self.result_lbl.configure(bg=COLORS["neutral_bg"], fg=COLORS["neutral_fg"])
        for wins_v, pulls_v, pct_v, bar_canvas in self.row_vars:
            wins_v.set("0")
            pulls_v.set("0")
            pct_v.set("—")
            bar_canvas.delete("all")
            bar_canvas.create_rectangle(0, 2, 110, 8, fill=COLORS["bar_bg"], outline="")


if __name__ == "__main__":
    app = BanditApp()
    app.mainloop()
