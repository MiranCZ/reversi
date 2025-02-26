from game import Game
from player import Player
from bot.mcts import Mcts

import threading


class GameManager:

    def __init__(self, p1_bot, p2_bot, set_player_turn, bot_think_seconds=1):
        self.p1 = Player(p1_bot)
        self.p2 = Player(p2_bot)
        self.set_player_turn = set_player_turn

        self.game = Game(self.p1, self.p2)
        self.mcts = Mcts(bot_think_seconds)

        self.should_play_turn = True
        self.game_ended = False

        set_player_turn(not p2_bot)

    def get_bot_move(self, board, is_white):
        result = self.mcts.get_best_move(board, is_white)
        if result is None:
            raise AssertionError("ur bad, go fix code")

        score = result[1]
        if score is not None:
            # TODO call ui to update score bar
            pass

        x, y = result[0]
        self.game.make_move(x, y)

        self.should_play_turn = True
        self.game.stridani()

    def tick(self):
        if self.game_ended:
            return
        if self.should_play_turn:
            self.should_play_turn = False
            self.__game_turn()

    def on_player_move(self, x, y):
        if self.game.natahu.is_bot:
            raise AssertionError("Why the heck is player moving when bot is supposed to :(")

        if self.game.make_move(x, y):
            self.should_play_turn = True
            self.game.stridani()
            self.set_player_turn(False)

    def __game_turn(self):
        moves = self.game.get_moves_for_now_player()
        # print("Turn, ", moves)

        # hrac nema zadny tah
        if len(moves) == 0:

            # TODO callback to UI that the move was skipped?
            self.game.stridani()

            moves = self.game.get_moves_for_now_player()

            # game end
            if len(moves) == 0:
                # TODO call UI that the game ended and who won
                self.game_ended = True
                exit(0)

        current_player = self.game.kdo_hraje()

        if current_player.is_bot:
            bot_thread = threading.Thread(target=self.get_bot_move,args=[self.game.board.board, self.is_white_playing()])
            bot_thread.start()
        else:
            self.set_player_turn(True)

    def is_white_playing(self):
        return self.game.kdo_hraje() == self.game.white

    def is_black_playing(self):
        return self.game.kdo_hraje() == self.game.black
