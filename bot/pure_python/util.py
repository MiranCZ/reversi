__masks = [0x7F7F7F7F7F7F7F7F,
           0x007F7F7F7F7F7F7F,
           0xFFFFFFFFFFFFFFFF,
           0x00FEFEFEFEFEFEFE,
           0xFEFEFEFEFEFEFEFE,
           0xFEFEFEFEFEFEFE00,
           0xFFFFFFFFFFFFFFFF,
           0x7F7F7F7F7F7F7F00]

__lshifts = [0, 0, 0, 0, 1, 9, 8, 7]
__rshifts = [1, 9, 8, 7, 0, 0, 0, 0]

pos_infinity = float('inf')
neg_infinity = float('-inf')

filled_board = (1<<64)-1

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


def shift(disks, dir):
    """
    via: https://www.hanshq.net/othello.html#bitboards
    """
    if dir < 4:
        return (disks >> __rshifts[dir]) & __masks[dir]
    else:
        return (disks << __lshifts[dir]) & __masks[dir]


def get_moves(white: int, black: int, is_white: bool):
    if is_white:
        return __get_moves(white, black)
    else:
        return __get_moves(black, white)


def __get_moves(player: int, opponent: int):
    """
    via: https://www.hanshq.net/othello.html#moves
    """

    empty_cells = ~(player | opponent)
    legal_moves = 0

    for dir in range(8):
        x = shift(player, dir) & opponent

        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent

        legal_moves |= shift(x, dir) & empty_cells

    return legal_moves


def get_captured(white: int, black: int, is_white: bool, move):
    return get_captured_shifted(white, black, is_white, 1 << move)

def get_captured_shifted(white: int, black: int, is_white: bool, move_shifted):
    if is_white:
        return __get_captured(white, black, move_shifted)
    else:
        return __get_captured(black, white, move_shifted)


def __get_captured(player: int, opponent: int, move: int):
    """
    via: https://www.hanshq.net/othello.html#moves
    """
    player |= move
    captured = 0

    for dir in range(8):
        x = shift(move, dir) & opponent

        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent
        x |= shift(x, dir) & opponent

        closing_disk = shift(x, dir) & player
        captured |= (x if closing_disk != 0 else 0)

    return captured
