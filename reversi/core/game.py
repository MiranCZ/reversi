from reversi.core.board import *

class Game:
    def __init__(self, white, black):
        self.white = white
        self.black = black
        self.board = Board()
        self.to_move = black

    def get_to_move(self):
        return self.to_move

    def switch_player(self):
        if self.to_move == self.black:
            self.to_move = self.white
        else:
            self.to_move = self.black
        return self.to_move

    def make_move(self, row, col):
        if self.to_move == self.black:
            player = "B"
        else:
            player = "W"
        return self.board.play_move(row, col, player)

    def winner(self):
        if self.board.get_b_stones() > self.board.get_w_stones():
            winner = "B"
        elif self.board.get_w_stones() > self.board.get_b_stones():
            winner = "W"
        else:
            winner = None
        return winner

    def get_moves_for_now_player(self):
        if self.to_move == self.black:
            player = "B"
        else:
            player = "W"
        return self.board.get_moves(player)

