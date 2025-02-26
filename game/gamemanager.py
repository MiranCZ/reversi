from game import Game
from player import Player
from bot.mcts import Mcts

import threading


# TODO callback to UI for move change??????
class GameManager:

    def __init__(self, p1_bot, p2_bot, bot_think_seconds=1):
        self.p1 = Player(p1_bot)
        self.p2 = Player(p2_bot)

        self.game = Game(self.p1, self.p2)
        self.mcts = Mcts(bot_think_seconds)

        self.should_play_turn = True


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


    # TODO this should be called by UI
    def tick(self):
        if self.should_play_turn:
            self.should_play_turn = False
            self.__game_turn()

    def get_player_move(self, board):
        # TODO call UI to get player input :)
        pass

    def on_player_move(self, x, y):
        if self.game.natahu.is_bot:
            raise AssertionError("Why the heck is player moving when bot is supposed to :(")

        self.game.make_move(x, y)

        self.should_play_turn = True
        self.game.stridani()


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
                exit(0)


        current_player = self.game.kdo_hraje()

        if current_player.is_bot:
            bot_thread = threading.Thread(target = self.get_bot_move, args = [self.game.board.board, current_player == self.game.white])
            bot_thread.start()
        else:
            # TODO call UI to handle move
            pass




if __name__ == '__main__':

    m = GameManager(True, True)

    import time

    while True:
        m.tick()
        m.game.board.print_board()
        time.sleep(1)