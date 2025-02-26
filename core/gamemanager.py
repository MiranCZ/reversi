from core.game import Game
from core.player import Player
from bot.mcts import Mcts

import time
import threading


class GameManager:

    def __init__(self, p1_bot, p2_bot, set_player_turn, on_game_ended, bar, bot_think_seconds=1):
        self.p1 = Player(p1_bot)
        self.p2 = Player(p2_bot)
        self.set_player_turn = set_player_turn
        self.on_game_ended = on_game_ended
        self.bar = bar

        self.game = Game(self.p1, self.p2)
        self.mcts = Mcts(bot_think_seconds)

        self.should_play_turn = True
        self.game_ended = False

        set_player_turn(not p2_bot)

    def get_bot_move(self, board, is_white):
        time_start = time.time()


        result = self.mcts.get_best_move(board, is_white)
        if result is None:
            # this should not happen...
            raise AssertionError("ur bad, go fix code")

        # prevent bot from moving too fast
        diff = 1 -(time.time() - time_start)

        if diff > 0:
            time.sleep(diff)

        score = result[1]
        if score is not None:
            update_score = score
            if not is_white:
                update_score = 1 - update_score
            self.bar.percentage = update_score

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
            print("Why the heck is player moving when bot is supposed to :(")
            return

        if self.game.make_move(x, y):
            self.should_play_turn = True
            self.game.stridani()
            self.set_player_turn(False)

    def __game_turn(self):
        moves = self.game.get_moves_for_now_player()

        # hrac nema zadny tah
        if len(moves) == 0:

            # TODO callback to UI that the move was skipped?
            self.game.stridani()

            moves = self.game.get_moves_for_now_player()

            # core end
            if len(moves) == 0:
                self.game_ended = True
                self.on_game_ended()
                return

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
