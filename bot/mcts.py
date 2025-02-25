try:
    import bot.optimized.montecarlo as montecarlo
except ImportError:
    print(
        "Failed to import cython package!\n"
        "Using pure python as fallback, this means the bot will be significantly slower!\n"
    )

    import bot.pure_python.montecarlo as montecarlo


def get_best_move(board, is_white_playing):
    # FIXME maybe return (None, None) tuple instead of just None
    """
    Parses given board and internally calls supported MCTS implementation to get the best move for the playing side.

    `board` is a 2d character array where '.' means empty space, 'W' means white piece and 'B' means black piece
    `is_white_playing` is a boolean, `True` if you want to get the best move for white, `False` if you want to get the best move for black

    Returns either:
    1) tuple in the form of `((x, y), score)` where `x` and `y` represents the x and y coordinates of the new placed piece
    and `score` is either
        a) a float in the range of 0-1 representing the predicted "win-percentage"
        b) `None` meaning the bot did not evaluate the board (most-likely because there was only one move available)

    2) None - this means no valid moves were found
    """
    white, black = parse_board(board)

    move, score = montecarlo.best_move(white, black, is_white_playing)

    if move is None:
        return None

    x = move // 8
    y = move % 8

    return (x, y), score


def parse_board(board: list[list[str]]):
    white: int = 0
    black: int = 0

    # parse board to a bitboard representation
    for i in range(8):
        for j in range(8):
            piece = board[i][j]

            index = i * 8 + j

            if piece == 'W':
                white |= 1 << index
            elif piece == 'B':
                black |= 1 << index

    return white, black
