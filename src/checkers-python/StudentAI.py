from BoardClasses import Board
# The following part should be completed by students.
# Students can modify anything except the class name and existing functions and variables.
import random
from math import sqrt, log
import copy
import time

random.seed()


class StudentAI:
    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = 2
        # Add a timer to not exceed 8 minutes

    def get_move(self, move):
        # If a move has been made by the opponent, we are player 2
        # Else there has been no move, we are player 1
        if len(move) != 0:
            self.board.make_move(move, other(self.color))
        else:
            self.color = 1

        mcts = MCTS(MCTSNode(self.color, self.board, self.color, []))
        movenode = mcts.best_move(800) #TODO: decide number
        self.board.make_move(movenode.moves[0], self.color)
        return movenode.moves[0]

class MCTS:
    def __init__(self, node):
        self.root = node

    def best_move(self, simulations_number):
        start = time.time()
        for _ in range(simulations_number):
            if time.time() - start >= 25: # TODO : not sure if it should be exactly 20 seconds
                break
            selected = self.mcts_tree()
            selected.rollout()

        return self.root.best_child() if self.root.children else self.root

    def mcts_tree(self): #selects node to run rollout/play out for
        cur = self.root
        while not cur.is_win:
            if cur.unknown_moves:
                return cur.expand()
            else:
                if cur.children:
                    cur = cur.best_child()
                # without this else statement it will go in an infinite loop
                # as the game will never end while the ai is still "deciding".
                else:
                    break
        return cur


class MCTSNode:
    def __init__(self, mycolor, board, rootcolor, moves, parent=None):
        self.mycolor = mycolor
        self.board = board # TODO : reusing a board for later optimization?
        self.parent = parent
        self.rootcolor = rootcolor
        self.children = []
        self.n = 0.0
        self.results = {}

        self.moves = moves
        self.boardprep(True)
        self.unknown_moves = [i for x in self.board.get_all_possible_moves(self.mycolor) for i in x]
        self.is_win = self.board.is_win(self.mycolor) != 0
        self.boardprep(False)

    def boardprep(self, starting):
        if starting:
            cur_col = self.rootcolor
            for m in self.moves:
                self.board.make_move(m, cur_col)
                cur_col = other(cur_col)
        else:
            for _ in range(len(self.moves)):
                self.board.undo()

    def q(self):
        losses = 0.0 if self.results.get(self.parent.mycolor) is None else self.results[self.parent.mycolor]
        wins = 0.0 if self.results.get(self.mycolor) is None else self.results[self.mycolor]
        return wins - losses

    def expand(self): #expand this node out one child
        move = self.unknown_moves.pop()
        cn = MCTSNode(other(self.mycolor), self.board, self.rootcolor, self.moves+[move], self)
        self.children.append(cn)
        return cn

    def rollout(self): #randomly rollout to a win state
        num_rolls = 0
        cur_col = self.mycolor
        self.boardprep(True)
        while self.board.is_win(self.rootcolor) == 0:
            possible_moves = self.board.get_all_possible_moves(cur_col)
            if possible_moves:
                self.board.make_move(random.choice(random.choice(possible_moves)), cur_col)
                num_rolls += 1
            cur_col = other(cur_col)

        ret_win = self.board.is_win(self.rootcolor)
        for _ in range(num_rolls):
            self.board.undo()
        self.boardprep(False)
        self.backpropagate(ret_win)

    def backpropagate(self, result): #send results up the chain of nodes
        self.n += 1.0
        # Ties are considered losses for us, and results are listed as -1.
        result = other(self.rootcolor) if result == -1 else result
        if result not in self.results:
            self.results[result] = 1.0
        else:
            self.results[result] += 1.0
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self): #choose the most promising child node
        choices_weights = [(c.q() / c.n) + sqrt(2) * sqrt((2 * log(self.n) / c.n)) for c in self.children]
        return self.children[choices_weights.index(max(choices_weights))]


def other(color): #just easily see who the other player is
    return 2 if color == 1 else 1

