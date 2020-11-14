from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

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

    # TODO : Future heuristic function
    # Possible Heuristics? :
    # Enemy loses a normal piece/we lose a piece : +1 / -1
    # Gaining a king/Taking enemy's king : +3
    # Losing a king/Enemy gains a king: -3
    # we move with multiple jumps/Enemy moves with multiple jumps : +5 / -5 (if enemy has multiple jumps)
    # Game Win / over : +100/-100
    def heuristics(self):
        return

    # TODO : an actual tree traversal function for Monte Carlo Tree Search
    def rTraversal(self, board):
        return

    def get_move(self,move):
        # If a move has been made by the opponent, we are player 2
        # Else there has been no move, we are player 1
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        # Gets all the moves in the format : list of
        # Ex : [ [(1,3)-(3,1)-(5,3)], [(4,5)-(3,4), (4,5)-(3,6)] ]
        moves = self.board.get_all_possible_moves(self.color)

        # Temporary
        move = 0
        diffInPieces = 0;
        for pieces in moves:
            for moves in pieces:
                # Init move based on first/only move
                if move == 0:
                    move = moves
                    self.board.make_move(move,self.color)
                    diffInPieces = (self.board.white_count - self.board.black_count) if self.color == 1 else (self.board.black_count - self.board.white_count)
                    self.board.undo()
                else:
                    self.board.make_move(moves,self.color)
                    tmp = (self.board.white_count - self.board.black_count) if self.color == 1 else (self.board.black_count - self.board.white_count)
                    if (tmp > diffInPieces):
                        move = moves
                        diffInPieces = tmp
                    self.board.undo()

        # Makes the move in our copy of the board
        self.board.make_move(move,self.color)
        # returns the move
        return move