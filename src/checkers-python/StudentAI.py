from random import randint
from BoardClasses import Move
from BoardClasses import Board
# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.


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
    # Possible Heuristics? :
    # Losing a king/Enemy gains a king: -3
    def heuristics(self, old_diff, board, color):
        diffInPieces = (board.white_count - board.black_count) if self.color == 1 else (
                    board.black_count - board.white_count)
        value = 0
        difference = old_diff - diffInPieces
        # There's no switch/case for python but I'm sure
        # there's a better way for this part.  - There kindaaa was?
        if abs(difference) == 1:
            value += 10 * difference
        else:
            value += 50 * difference

        # There will be a secondary value heuristic here for getting closer to an enemy maybe?
        # adding value in the order of like 1-5 points, just enough to be better than moving away

        # https://www.mini.pw.edu.pl/~mandziuk/PRACE/es_init.pdf <- this paper has a pretty long list of
        # checkers heuristics that we could consider along the way, if we wanna get tryhard lol

        # A tie is listed as a 0 as a return
        # not sure what a tie's impact on the value should be. - maybe -500? not good but not as bad as losing
        winningNumber = board.is_win(color)
        if winningNumber == color:
            value += 1000
        elif winningNumber != color and winningNumber != 0:
            value -= 1000
        return value

    # TODO : this still isn't monte carlo tree search I don't think, so that needs to be changed.
    # Uses recursion to traverse the move tree, but
    # board = a copy of the board after a move has been made.
    # depth = Most likely need to limit the search else it will take too long computation wise
    # color = if it's our turn, we choose most advantageous, else choose least advantageous
    def r_traversal(self, board, depth, color):
        # Prevents from going deeper to save time on calculation
        if depth == 3:
            return 0

        moves = self.board.get_all_possible_moves(self.color)
        cur_value = None

        for pieces in moves:
            for m in pieces:
                board.make_move(m, self.color)
                tmp = self.r_traversal(board, depth + 1, self.opponent[color])
                board.undo()
                # Init the first move if not initialized.
                if cur_value is None:
                    cur_value = tmp
                # If it's our turn, pick the higher value
                if color == self.color:
                    cur_value = tmp if tmp > cur_value else cur_value
                # Else pick the lower one
                else:
                    cur_value = tmp if tmp < cur_value else cur_value
        # This is in the case there is no possible moves, so curValue is left as None bc the
        # loop does not run.
        return 0 if cur_value is None else cur_value

    def get_move(self,move):
        # If a move has been made by the opponent, we are player 2
        # Else there has been no move, we are player 1
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        # Gets all the possible moves in the format : list of
        # Ex : [ [(1,3)-(3,1)-(5,3)], [(4,5)-(3,4), (4,5)-(3,6)] ]
        moves = self.board.get_all_possible_moves(self.color)

        #
        move = None
        curValue = None
        for pieces in moves:
            for m in pieces:
                # Init move based on first/only move
                if move is None:
                    move = m
                    self.board.make_move(move,self.color)
                    curValue = self.r_traversal(self.board, 0, self.color)
                    self.board.undo()
                else:
                    self.board.make_move(m,self.color)
                    tmp = self.r_traversal(self.board, 0, self.color)
                    if tmp > curValue:
                        move = m
                        curValue = tmp
                    self.board.undo()

        # Makes the move in our copy of the board
        self.board.make_move(move,self.color)
        # returns the move
        return move