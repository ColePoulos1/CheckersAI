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
    # Possible Heuristics? : https://www.mini.pw.edu.pl/~mandziuk/PRACE/es_init.pdf (page 5) <- this paper has
    # a pretty long list of checkers heuristics that we could consider along the way, if we wanna get tryhard lol
    # Losing a king/Enemy gains a king: 0-10
    # Getting closer to an enemy instead of farther away : 0-5
    def heuristics(self, cur_color):
        diffInPieces = (self.board.white_count - self.board.black_count) if cur_color == 2 else (
                    self.board.black_count - self.board.white_count)
        value = diffInPieces * 10

        winningNumber = self.board.is_win(cur_color)
        if winningNumber == cur_color:  # win
            value += 1000
        elif winningNumber == -1:  # tie
            value -= 500
        else:  # loss
            value -= 1000
        return value

    # TODO : this still isn't monte carlo tree search I don't think, so that needs to be changed.
    # Uses recursion to traverse the move tree
    # depth = Most likely need to limit the search else it will take too long computation wise
    # cur_color = if it's our turn, we add value, else subtract it
    def r_traversal(self, depth):
        # Prevents from going deeper to save time on calculation
        if depth == 3:
            return 0
        cur_color = (depth % 2) + 1  # color of move we're making
        moves = self.board.get_all_possible_moves(cur_color)
        best_move = None
        best_val = -100000
        for pieces in moves:
            for m in pieces:
                self.board.make_move(m, cur_color)
                tmp_val = self.r_traversal(depth + 1)
                if cur_color == self.color:
                    tmp_val += self.heuristics(cur_color)
                else:
                    tmp_val -= self.heuristics(cur_color)
                if tmp_val > best_val:
                    best_move = m
                    best_val = tmp_val
                self.board.undo()

        # This is in the case there is no possible moves
        return 0 if best_move is None else best_val

    def get_move(self, move):
        # If a move has been made by the opponent, we are player 2
        # Else there has been no move, we are player 1
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        # Gets all the possible moves in the format : list of
        # Ex : [ [(1,3)-(3,1)-(5,3)], [(4,5)-(3,4), (4,5)-(3,6)] ]
        moves = self.board.get_all_possible_moves(self.color)
        best_move = None
        best_val = -100000
        for pieces in moves:
            for m in pieces:
                self.board.make_move(m, self.color)
                tmp_val = self.r_traversal(1)
                tmp_val += self.heuristics(self.color)
                if tmp_val > best_val:
                    best_move = m
                    best_val = tmp_val
                self.board.undo()

        # Makes the move in our copy of the board
        self.board.make_move(best_move, self.color)
        # returns the move
        return best_move
