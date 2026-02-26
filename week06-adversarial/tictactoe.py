# ─────────────────────────────────────────────
#  Game state
# ─────────────────────────────────────────────

class TicTacToe:
    """
    Board is a list of 9 cells: 0 = empty, 1 = X, -1 = O
    Indices:
        0 | 1 | 2
        ---------
        3 | 4 | 5
        ---------
        6 | 7 | 8
    """

    LINES = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
        (0, 4, 8), (2, 4, 6),              # diagonals
    ]

    def __init__(self, board=None, turn=1):
        self.board = board or [0] * 9
        self.turn = turn  # 1 = X's turn, -1 = O's turn

    def print_directions(self):
        print("You are X. Enter a cell number 0-8.")
        print("0 | 1 | 2\n---------\n3 | 4 | 5\n---------\n6 | 7 | 8\n")

    def legal_moves(self):
        return [i for i, cell in enumerate(self.board) if cell == 0]

    def apply(self, move):
        board = self.board[:]
        board[move] = self.turn
        return TicTacToe(board, -self.turn)

    def winner(self):
        """Return 1 (X wins), -1 (O wins), or 0 (no winner yet)."""
        for a, b, c in self.LINES:
            s = self.board[a] + self.board[b] + self.board[c]
            if s == 3:
                return 1
            if s == -3:
                return -1
        return 0

    def report_winner(self):
        w = self.winner()
        if w == 1:
            print("\nX wins!")
        elif w == -1:
            print("\nO wins!")
        else:
            print("\nDraw!")


    def is_terminal(self):
        return self.winner() != 0 or not self.legal_moves()

    def __repr__(self):
        symbols = {1: "X", -1: "O", 0: "."}
        rows = []
        for r in range(3):
            rows.append(" | ".join(symbols[self.board[r * 3 + c]] for c in range(3)))
        return "\n---------\n".join(rows)

