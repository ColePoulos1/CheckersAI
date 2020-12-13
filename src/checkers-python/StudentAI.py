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
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        # Add a timer to not exceed 8 minutes

    def get_move(self, move):
        # If a move has been made by the opponent, we are player 2
        # Else there has been no move, we are player 1
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        # TODO : Add heuristics to improve MCTS
        rootnode = MCTSNode(self.color, self.board, self.color)
        mcts = MCTS(rootnode)
        move = (mcts.best_move(500)).move #TODO: not sure about this number
        self.board.make_move(move, self.color)
        return move

class MCTS:
    def __init__(self, node):
        self.root = node

    def best_move(self, simulations_number):
        start = time.time()
        for _ in range(simulations_number):
            if time.time() - start >= 20: # TODO : not sure if it should be exactly 20 seconds
                break
            selected = self.mcts_tree()
            selected.rollout()

        return self.root.best_child(0.0) if self.root.children else self.root

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
    def __init__(self, mycolor, board, rootcolor, parent=None, move = None):
        self.mycolor = mycolor
        self.board = board # TODO : reusing a board for later optimization?
        self.parent = parent
        self.rootcolor = rootcolor
        self.children = []
        self.n = 0.0
        self.results = {}
        #flatten 2d move list
        self.unknown_moves = [i for x in self.board.get_all_possible_moves(self.mycolor) for i in x]
        self.is_win = self.board.is_win(self.mycolor) != 0
        self.move = move

    def q(self):
        # Results can be either 2 for W or 1 for B
        wins = 0.0 if self.results.get(self.rootcolor) is None else self.results[self.rootcolor]
        losses = 0.0 if self.results.get(other(self.rootcolor)) is None else self.results[other(self.rootcolor)]
        return wins - losses

    def expand(self): #expand this node out one child
        cb = copy.deepcopy(self.board) #this deep copy is expensive, idk how to fix that
        move = self.unknown_moves.pop()
        cb.make_move(move, self.mycolor)
        cn = MCTSNode(other(self.mycolor), cb, self.rootcolor, self, move)
        self.children.append(cn)
        return cn

    def rollout(self): #randomly rollout to a win state
        num_rolls = 0
        cur_col = self.mycolor
        while self.board.is_win(self.rootcolor) == 0:
            possible_moves = self.board.get_all_possible_moves(cur_col)
            if possible_moves:
                self.board.make_move(random.choice(random.choice(possible_moves)), cur_col)
                num_rolls += 1
            cur_col = other(cur_col)
        ret_win = self.board.is_win(self.rootcolor)
        for _ in range(num_rolls):
            self.board.undo()
        self.backpropagate(ret_win)

    def backpropagate(self, result): #send results up the chain of nodes
        self.n += 1.
        # Ties are considered wins for us, and results are listed as -1.
        result = self.rootcolor if result == -1 else result
        if result not in self.results:
            self.results[result] = 1.0
        else:
            self.results[result] += 1.0
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, cp=1.4): #choose the most promising child node
        # TODO : Sometimes, this program will crash because max(choices_weights) will be empty. I don't know why.
        choices_weights = [(c.q() / c.n) + cp * sqrt((2 * log(self.n) / c.n)) for c in self.children]
        return self.children[choices_weights.index(max(choices_weights))]


def other(color): #just easily see who the other player is
    return 2 if color == 1 else 1

