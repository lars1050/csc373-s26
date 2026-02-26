import math
import random
from tictactoe import TicTacToe

# ─────────────────────────────────────────────
#  Monte Carlo Tree Search
# ─────────────────────────────────────────────
'''
1. Selection — find a promising node to expand
    leaf = select(root)

2. Expansion — grow the tree by one node (unless terminal)
    if not leaf.is_terminal():
        leaf = expand(leaf)

3. Simulation — random playout from the new node
    result = simulate(leaf)

4. Backpropagation — update stats all the way to root
    backpropagate(leaf, result)

Choose the move with the most visits
    best_child = max(root.children, key=lambda n: n.visits)
    return best_child.move
'''

# ─────────────────────────────────────────────
#  MCTS Node
# ─────────────────────────────────────────────

class Node:
    def __init__(self, state: TicTacToe, parent=None, move=None):
        self.state = state          # game state at this node
        self.parent = parent        # parent Node (None for root)
        self.move = move            # move that led here from parent

        self.children = []
        self.untried_moves = state.legal_moves()

        self.visits = 0
        self.wins = 0.0             # wins from the perspective of the node's *parent*
                                    # (i.e. the player who made the move to get here)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return self.state.is_terminal()

    def ucb1(self, exploration=1.414):
        """
        Upper Confidence Bound applied to trees.

        exploitation = wins / visits          (how good this node looks so far)
        exploration  = C * sqrt(ln(N) / n)   (how rarely this node has been visited)

        C (exploration constant) trades off between exploring new nodes
        and exploiting nodes that already look promising.
        """
        exploitation = self.wins / self.visits
        exploration_term = exploration * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration_term


# ─────────────────────────────────────────────
#  The four MCTS phases
# ─────────────────────────────────────────────

def select(node: Node) -> Node:
    """
    PHASE 1 — SELECTION
    Walk down the tree, always choosing the child with the highest UCB1 score,
    until we reach a node that is not fully expanded or is terminal.
    """
    while not node.is_terminal():
        
        # any children not yet explored?
        if not node.is_fully_expanded():
            return node         # hand off to expansion
        
        # select the "best" child
        node = max(node.children, key=lambda n: n.ucb1())
        
    return node


def expand(node: Node) -> Node:
    """
    PHASE 2 — EXPANSION
    Pick one untried move at random, create a child node for it,
    and return that child.
    """
    move = random.choice(node.untried_moves)
    node.untried_moves.remove(move)
    child = Node(state=node.state.apply(move), parent=node, move=move)
    node.children.append(child)
    return child


def simulate(node: Node) -> float:
    """
    PHASE 3 — SIMULATION (rollout)
    From the new node, play random moves until the game ends.
    Return the result from the perspective of the player who
    made the move to reach `node` (i.e. node.state.turn is the
    *next* player, so we check against -node.state.turn).
    """
    state = node.state
    while not state.is_terminal():
        # apply a random move.
        # -- creates a new board. changes whose turn it is
        # notice new nodes are not being created -- only states are being changed
        state = state.apply(random.choice(state.legal_moves()))

    # report on who won: 1 (human), -1 (AI), or it was a tie
    the_winner = state.winner()

    # player for whom this simulation was run.
    # -node.state.turn because it reflects the NEXT player's turn
    mover = -node.state.turn

    # report the results from the perspective of the mover (root of this tree)
    if the_winner == mover:
        return 1.0   # win
    elif the_winner == 0:
        return 0.5   # draw
    else:
        return 0.0   # loss


def backpropagate(node: Node, result: float):
    """
    PHASE 4 — BACKPROPAGATION
    Walk back up the tree, updating visit counts and win scores.
    The result flips at each level because the two players alternate.
    """
    while node is not None:
        node.visits += 1
        node.wins += result
        result = 1.0 - result   # flip perspective for the parent
        node = node.parent


# ─────────────────────────────────────────────
#  Pretty-print the search tree (one level deep)
# ─────────────────────────────────────────────

def print_tree(root: Node):
    print(f"\nRoot: {root.visits} visits")
    print(f"{'Move':>6}  {'Visits':>7}  {'Win rate':>10}  {'UCB1':>8}")
    print("-" * 40)
    for child in sorted(root.children, key=lambda n: n.visits, reverse=True):
        win_rate = child.wins / child.visits if child.visits else 0
        ucb = child.ucb1() if child.parent and child.parent.visits else 0
        print(f"{child.move:>6}  {child.visits:>7}  {win_rate:>10.3f}  {ucb:>8.3f}")
    print()


# ─────────────────────────────────────────────
#  Play a game: human (X) vs MCTS (O)
# ─────────────────────────────────────────────

def play(problem):

    # give the player some guidance on how to play
    problem.print_directions()
    
    # define current state as the initial problem
    state = problem

    # take turns moving (human/AI) until somebody wins
    while not state.is_terminal():

        # show what has been played so far
        print(state)
        print()

        if state.turn == 1:
            # Human move
            move = None
            while move not in state.legal_moves():
                try:
                    move = int(input("Your move: "))
                except ValueError:
                    pass
        else:
            # MCTS move
            print("MCTS is thinking...")
            
            # create a new tree rooted at current state
            root = Node(state)

            # playout the game many, many times to gather stats on wins
            for _ in range(1000):
                
                # find a node ready for expansion (i.e. with unexplored children)
                leaf = select(root)

                # create a new leaf (child node) not yet explored
                if not leaf.is_terminal():
                    leaf = expand(leaf)

                # playout from here. return 1 (win), 0.5 (tie), 0 (loss)
                result = simulate(leaf)

                # record win/loss (alternates going up tree) at each node
                # note that this is for already expanded nodes only
                backpropagate(leaf, result)

            print_tree(root)
            move = max(root.children, key=lambda n: n.visits).move
            print(f"MCTS plays: {move}\n")

        state = state.apply(move)

    print(state)
    state.report_winner()


if __name__ == "__main__":
    play(TicTacToe())
