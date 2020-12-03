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
    #
    # def r_traversal(self, depth):
    #     # Prevents from going deeper to save time on calculation
    #     if depth == 3:
    #         return 0
    #     cur_color = (depth % 2) + 1  # color of move we're making
    #     moves = self.board.get_all_possible_moves(cur_color)
    #     best_move = None
    #     best_val = -100000
    #     for pieces in moves:
    #         for m in pieces:
    #             self.board.make_move(m, cur_color)
    #             tmp_val = self.r_traversal(depth + 1)
    #             if cur_color == self.color:
    #                 tmp_val += self.heuristics(cur_color)
    #             else:
    #                 tmp_val -= self.heuristics(cur_color)
    #             if tmp_val > best_val:
    #                 best_move = m
    #                 best_val = tmp_val
    #             self.board.undo()
    #
    #     # This is in the case there is no possible moves
    #     return 0 if best_move is None else best_val

    def get_move(self, move):
        # If a move has been made by the opponent, we are player 2
        # Else there has been no move, we are player 1
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        rootnode = MCTSNode(self.color, self.board)
        mcts = MCTS(rootnode)
        self.board = mcts.best_move(100) #TODO: not sure about this number
        # TODO: return the move (this best_move function returns a board state not a move)
        return None


class MCTS:
    def __init__(self, node):
        self.root = node

    def best_move(self, simulations_number):
        for _ in range(simulations_number):
            v = self.mcts_tree()
            reward = v.rollout()
            v.backpropagate(reward)
        # to select best child go for exploitation only
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
    def __init__(self, mycolor, board, parent=None):
        self.mycolor = mycolor
        self.board = board
        self.parent = parent
        self.children = []
        self.n = 0.
        self.results = {}
        #flatten 2d move list
        self.unknown_moves = [i for x in self.board.get_all_possible_moves(self.mycolor) for i in x]
        self.is_win = self.board.is_win(self.mycolor) != 0

    def q(self):
        wins = self.results[self.parent.board.next_to_move] #TODO: implement next_to_move
        losses = self.results[-1 * self.parent.board.next_to_move] #TODO: implement next_to_move
        return wins - losses

    def expand(self): #expand this node out one child
        cb = copy.deepcopy(self.board) #this deep copy is expensive, idk how to fix that
        cb.make_move(self.unknown_moves.pop(), self.mycolor)
        cn = MCTSNode(self.mycolor, cb, self)
        self.children.append(cn)
        return cn

    def rollout(self): #randomly rollout to a win state
        num_rolls = 0
        while self.board.is_win(self.mycolor) == 0:
            possible_moves = self.board.get_all_possible_moves(self.mycolor)
            self.board.make_move(random.choice(possible_moves))
            num_rolls += 1
        ret_win = self.board.is_win(self.mycolor)
        for _ in range(num_rolls):
            self.board.undo()
        return ret_win

    def backpropagate(self, result): #send results up the chain of nodes
        self.n += 1.
        if result not in self.results:
            self.results[result] = 1
        else:
            self.results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, cp=1.4): #choose the most promising child node
        choices_weights = [(c.q / c.n) + cp * sqrt((2 * log(self.n) / c.n)) for c in self.children]
        # TODO: not sure how this function works
        return self.children[choices_weights.index(max(choices_weights))]
