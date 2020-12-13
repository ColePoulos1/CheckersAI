from BoardClasses import Board
# The following part should be completed by students.
# Students can modify anything except the class name and existing functions and variables.
import random
from math import sqrt, log
import copy

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

    # TODO : improve this function
    # Possible Heuristics? : https://www.mini.pw.edu.pl/~mandziuk/PRACE/es_init.pdf (page 5) <- this paper has
    # a pretty long list of checkers heuristics that we could consider along the way, if we wanna get try-hard lol
    # Losing a king/Enemy gains a king: 0-10
    # Getting closer to an enemy instead of farther away : 0-5
    # def heuristics(self, cur_color):
    #     diffInPieces = (self.board.white_count - self.board.black_count) if cur_color == 2 else (
    #                 self.board.black_count - self.board.white_count)
    #     value = diffInPieces * 10
    #
    #     winningNumber = self.board.is_win(cur_color)
    #     if winningNumber == cur_color:  # win
    #         value += 1000
    #     elif winningNumber == -1:  # tie
    #         value -= 500
    #     elif winningNumber != 0:  # loss
    #         value -= 1000
    #     return value

    def get_move(self, move):
        # If a move has been made by the opponent, we are player 2
        # Else there has been no move, we are player 1
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        # TODO : Add heuristics to improve MCTS
        rootnode = MCTSNode(self.color, self.board)
        mcts = MCTS(rootnode)
        move = (mcts.best_move(50)).move #TODO: not sure about this number
        self.board.make_move(move, self.color)
        return move


class MCTS:
    def __init__(self, node):
        self.root = node

    def best_move(self, simulations_number):
        for _ in range(simulations_number):
            v = self.mcts_tree()
            reward = v.rollout()
            v.backpropagate(reward)
        # to select best child go for exploitation only
        # we can also use sqrt(2) bc book says that's a good value for exploration if we want that too
        return self.root.best_child(0.0)

    def mcts_tree(self): #selects node to run rollout/play out for
        cur = self.root
        while not cur.is_win:
            if cur.unknown_moves:
                return cur.expand()
            else:
                cur = cur.best_child()
        return cur


class MCTSNode:
    def __init__(self, mycolor, board, parent=None, move = None):
        self.mycolor = mycolor
        self.board = board # TODO : reusing a board for later optimization?
        self.parent = parent
        self.children = []
        self.n = 0.
        self.results = {}
        #flatten 2d move list
        self.unknown_moves = [i for x in self.board.get_all_possible_moves(self.mycolor) for i in x]
        self.is_win = self.board.is_win(self.mycolor) != 0
        self.move = move # TODO : I think it's fine to store the move, its just a couple tuples (int,int)

    def q(self):
        # Results can be either 2 for W or 1 for B
        wins = self.results[self.parent.mycolor]
        opponent = other(self.parent.mycolor)
        # key error occurs in scenarios where the opponent hasn't won yet, so there's no key for it.
        losses = 0 if self.results.get(opponent) is None else self.results[opponent]
        return wins - losses

    def expand(self): #expand this node out one child
        cb = copy.deepcopy(self.board) #this deep copy is expensive, idk how to fix that
        move = self.unknown_moves.pop()
        cb.make_move(move, self.mycolor)
        cn = MCTSNode(self.mycolor, cb, self, move) #TODO: should we be alternating the color here or no?
        self.children.append(cn)
        return cn

    def rollout(self): #randomly rollout to a win state
        num_rolls = 0
        cur_turn = self.mycolor
        while self.board.is_win(self.mycolor) == 0:
            cur_turn = 1 if cur_turn == 2 else 2
            possible_moves = self.board.get_all_possible_moves(cur_turn)
            if possible_moves:
                self.board.make_move(random.choice(random.choice(possible_moves)), cur_turn)
                num_rolls += 1
        ret_win = self.board.is_win(self.mycolor)
        for _ in range(num_rolls):
            self.board.undo()
        return ret_win

    def backpropagate(self, result): #send results up the chain of nodes
        self.n += 1.
        # Ties are considered wins for us, and results are listed as -1.
        result = self.mycolor if result == -1 else result
        if result not in self.results:
            self.results[result] = 1
        else:
            self.results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, cp=1.4): #choose the most promising child node
        # TODO : Sometimes, this program will crash because max(choices_weights) will be empty. I don't know why.
        choices_weights = [(c.q() / c.n) + cp * sqrt((2 * log(self.n) / c.n)) for c in self.children]
        return self.children[choices_weights.index(max(choices_weights))]


def other(color): #just easily see who the other player is
    return 2 if color == 1 else 1