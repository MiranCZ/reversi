from core.board import *

class Game:
    def __init__(self, white, black):
        self.white = white
        self.black = black
        self.board = Board()
        self.natahu = black

    def kdo_hraje(self):
        return self.natahu

    def stridani(self):
        if self.natahu == self.black:
            self.natahu = self.white
        else:
            self.natahu = self.black
        return self.natahu

    def make_move(self, row, col):
        if self.natahu == self.black:
            player = "B"
        else:
            player = "W"
        return self.board.play_move(row, col, player)

    def winner(self):
        if self.board.get_b_sutry() > self.board.get_w_sutry():
            winner = "B"
        elif self.board.get_w_sutry() > self.board.get_b_sutry():
            winner = "W"
        else:
            winner = None
        return winner

    def get_moves_for_now_player(self):
        if self.natahu == self.black:
            player = "B"
        else:
            player = "W"
        return self.board.get_moves(player)

